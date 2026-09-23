#!/usr/bin/env python
"""GLEIF (Global LEI Foundation) — enrich existing CRM records, and surface fund managers we missed.

Who this is for: Andre Geha and the sourcing agents, run from the laptop (or anywhere with normal
internet — GLEIF is not geo-blocked). `python tools/connectors/gleif_enrich.py --help` for usage.

**What GLEIF is.** The free global Legal Entity Identifier database, no auth, no key:
`https://api.gleif.org/api/v1/lei-records`. Verified live: France 170,615 entities (19,464 marked
`entity.category=FUND`) · UAE 9,100 (131 funds) · Saudi Arabia 5,647 (16 funds) · Lebanon 282 (1 fund).

**What GLEIF is NOT.** It carries no industry classification at all, so it cannot answer "who is an
asset manager" — it cannot source prospects. Do not use it that way. It answers two different,
narrower questions well:

1. **ENRICHMENT.** For a firm we already hold, does it have an LEI record, and does that record know
   a legal name / city / legal form / parent we do not? A hit requires the normalized name from our
   record to match a name GLEIF holds for that entity (its `legalName` or one of its `otherNames`)
   **AND** GLEIF's own country filter to agree with our record's country. Name alone is never
   accepted as proof — two firms can share a name — which is why every match is logged with "matched
   on name + country" in the record's activity log, so a human can challenge it.

   Measured limitation, worth knowing before trusting a low hit rate: **an LEI is not universal.**
   Plenty of real, currently-licensed asset managers (e.g. a small AMF-registered SGP with no
   derivatives/EMIR reporting obligation) simply have no LEI at all. A "no match" from this tool is
   evidence of absence from GLEIF, not evidence the firm does not exist.

   `crm/SCHEMA.md` has no `lei` field and none is added here — inventing a schema field was
   explicitly out of scope for this tool. The LEI, GLEIF's legal name (when it differs and our
   `legal_name` was already non-null so we could not write it there), the legal form, and a direct
   parent (when GLEIF asserts one) go into a `research` activity entry instead. `legal_name` and
   `city` DO have schema fields, and are filled there — but **only when our field is currently
   `null`.** An existing value is never overwritten, per the CRM's own rule.

   Runs are cached in `crm/gleif/checked.json` (slug -> last result) so a daily run only spends
   network calls on genuinely new records; pass `--recheck` to re-query everything.

2. **FUND -> MANAGER DISCOVERY.** A GLEIF fund record (`entity.category=FUND`) that asserts a
   `fund-manager` relationship points straight at its managing entity's own LEI record — this
   is a real GLEIF relationship type, confirmed live (most French/UAE/Saudi funds that have a
   manager on file expose it this way; a fund with no such relationship key simply has not had
   one reported, and is skipped, not guessed at). A managing entity that (a) is domiciled in one
   of our four markets and (b) does not match anything already in the CRM by name + country is a
   fund manager we have missed. These are written as CANDIDATES, never as CRM records, via the
   shared `tools/candidates.py` queue (`crm/candidates/gleif-<YYYY-MM-DD>.jsonl`) — the same
   append-only, evidence-carrying, never-auto-promoted mechanism `sirene_france.py` uses. Every
   candidate's `matched_slug` is `null` by construction: if a manager matched an existing record it
   would not have been emitted as a candidate in the first place.

   ⚠ **France alone has 19,464 GLEIF-registered funds.** Listing them (200 per page, GLEIF's hard
   maximum) and following each fund-manager relationship is one HTTP request per fund with a link —
   at the ~0.3s-plus-latency pace this tool uses to be polite to a free public service, a full French
   sweep is on the order of hours, not minutes. `--max-funds-per-country` bounds a run; the un-swept
   remainder is simply not covered *yet*, and this script says so out loud rather than pretending a
   partial sweep was exhaustive.

Non-negotiables (from `CLAUDE.md` and `plan/source-architecture.md`):
- Read-only. This only ever GETs from `api.gleif.org` and reads/writes files in this repo.
- Never invent a contact detail, a name, or a fact. Unknown stays `null`.
- Deterministic output: sorted keys, stable ordering. `crm/gleif/checked.json` and every candidate
  line are written with `sort_keys=True`; nothing here depends on wall-clock time except the `date`
  fields the rest of the CRM already carries.
- Identify honestly (`base.USER_AGENT`) and rate-limit politely (~0.3s between GLEIF requests).
- FAIL LOUDLY. A GLEIF outage or an unrecognised response shape raises `ConnectorError` and this
  script exits non-zero — it never quietly reports "nothing to enrich" or "no managers found".
  A genuine "no match" for one company (a legitimate, common GLEIF answer) is not a failure; an
  unreachable API or a malformed response is.

Usage:
    python tools/connectors/gleif_enrich.py --dry-run
    python tools/connectors/gleif_enrich.py                              # enrich + discover, all 4 markets
    python tools/connectors/gleif_enrich.py --skip-funds                 # enrichment only
    python tools/connectors/gleif_enrich.py --skip-enrich --countries "Saudi Arabia,Lebanon,UAE"
    python tools/connectors/gleif_enrich.py --skip-enrich --max-funds-per-country 500   # bounded France-safe sweep
    python tools/connectors/gleif_enrich.py --recheck --limit 50         # re-check the first 50 records regardless of cache
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Iterator, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import candidates as cq  # noqa: E402
import crm  # noqa: E402
from base import ConnectorError, USER_AGENT, normalize_name  # noqa: E402

GLEIF_API = "https://api.gleif.org/api/v1"
SOURCE = "gleif"

#: Politeness delay after every GLEIF request, success or failure alike.
REQUEST_DELAY_SECONDS = 0.3

#: GLEIF's own hard ceiling — verified live: `page[size]` above this returns HTTP 400.
PAGE_SIZE = 200

#: Our territory only. GLEIF speaks ISO 3166-1 alpha-2; the CRM writes the display name.
COUNTRY_ISO = {"France": "FR", "UAE": "AE", "Saudi Arabia": "SA", "Lebanon": "LB"}
ISO_COUNTRY = {v: k for k, v in COUNTRY_ISO.items()}

CACHE_PATH = crm.REPO_ROOT / "crm" / "gleif" / "checked.json"


# ---------------------------------------------------------------------------
# HTTP — a single seam, so tests can stub exactly one function.
# ---------------------------------------------------------------------------

def _sleep() -> None:
    time.sleep(REQUEST_DELAY_SECONDS)


def _get_json(url: str, *, allow_404: bool = False) -> Optional[dict]:
    """GET a GLEIF URL and parse its JSON body.

    Returns ``None`` only when ``allow_404`` is set and the resource genuinely does not exist —
    GLEIF's way of saying "this entity has no such relationship", which is normal and common (most
    entities have no asserted parent; many funds have no reported manager). Every other failure —
    unreachable host, non-200, unparsable body, a shape with no ``data`` key — raises
    :class:`ConnectorError`. A connector that swallowed those would turn a dead source into a
    result that reads exactly like "nothing to enrich today", which is the one thing this tool must
    never do.
    """
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.api+json"})
    try:
        with urlopen(req, timeout=60) as resp:
            if resp.status != 200:
                raise ConnectorError(f"GLEIF returned HTTP {resp.status} for {url}")
            body = resp.read()
    except HTTPError as e:
        if allow_404 and e.code == 404:
            return None
        raise ConnectorError(f"GLEIF returned HTTP {e.code} ({e.reason}) for {url}") from e
    except URLError as e:
        raise ConnectorError(f"GLEIF unreachable: {e.reason} ({url})") from e
    finally:
        _sleep()

    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise ConnectorError(f"GLEIF returned unparsable JSON for {url}: {e}") from e
    if "data" not in data:
        raise ConnectorError(
            f"GLEIF response for {url} has no 'data' key — unexpected shape: {sorted(data)}"
        )
    return data


# ---------------------------------------------------------------------------
# Part 1 — enrichment
# ---------------------------------------------------------------------------

def _record_names(rec: dict) -> set[str]:
    """Every name GLEIF holds for one lei-record, normalized: the legal name plus any other names
    (previous legal names, trading names) it has on file."""
    ent = rec["attributes"]["entity"]
    names = [ent.get("legalName", {}).get("name")]
    names += [o.get("name") for o in (ent.get("otherNames") or [])]
    return {normalize_name(n) for n in names if n}


def search_records(name: str, country_iso: str, *, size: int = 20) -> list[dict]:
    q = urllib.parse.quote(name, safe="")
    url = (
        f"{GLEIF_API}/lei-records?filter[fulltext]={q}"
        f"&filter[entity.legalAddress.country]={country_iso}&page[size]={size}"
    )
    return _get_json(url)["data"]


def find_match(name: str, legal_name: Optional[str], country_iso: str) -> tuple[Optional[dict], str]:
    """Search GLEIF for one firm. Returns ``(record_or_None, note)``.

    A hit requires BOTH a normalized-name match AND the record's own
    ``entity.legalAddress.country`` to equal ``country_iso`` — name alone is never proof, which is
    why ``note`` always states the match was on name + country, so a human reading the CRM record
    can challenge it if the coincidence looks wrong. The country check is done here, on the
    record itself, rather than trusted purely from the query's own country filter — belt and
    braces against a filter that silently did nothing.
    """
    if not name:
        return None, "no name to search on"
    targets = {normalize_name(name)}
    if legal_name:
        targets.add(normalize_name(legal_name))

    results = search_records(name, country_iso)
    by_lei = {
        r["attributes"]["lei"]: r
        for r in results
        if targets & _record_names(r)
        and (r["attributes"]["entity"].get("legalAddress") or {}).get("country") == country_iso
    }
    if len(by_lei) == 1:
        return next(iter(by_lei.values())), "matched on name + country"
    if len(by_lei) > 1:
        return None, f"ambiguous — {len(by_lei)} distinct GLEIF records share this name in {country_iso}"
    return None, "no GLEIF record found"


def _relationship_record(gleif_rec: dict, key: str) -> Optional[dict]:
    """Follow a relationship link (e.g. ``direct-parent``) IF GLEIF asserts one.

    The relationship key is present on almost every record regardless (it is part of the schema),
    but it only carries a ``lei-record`` link when a related entity actually exists; otherwise it
    carries a ``reporting-exception`` link (e.g. "no parent required"), which is not a failure and
    not followed.
    """
    rel = (gleif_rec.get("relationships") or {}).get(key) or {}
    link = (rel.get("links") or {}).get("lei-record")
    if not link:
        return None
    data = _get_json(link, allow_404=True)
    return data["data"] if data else None


def _legal_form_text(ent: dict) -> Optional[str]:
    form = ent.get("legalForm") or {}
    return form.get("other") or form.get("id") or None


def enrich_one(rec: dict, gleif_rec: dict) -> tuple[list[tuple[str, str]], str, Optional[str], Optional[str]]:
    """What ONE matched GLEIF record offers a CRM record.

    Returns ``(field_gains, lei, legal_form_text, parent_name)``. ``field_gains`` is only the
    fields the CRM schema actually has (``legal_name``, ``city``) and only where ``rec`` currently
    holds ``null`` — the caller still re-checks this against the freshly-loaded file before writing,
    since "never overwrite" is worth checking twice.
    """
    ent = gleif_rec["attributes"]["entity"]
    lei = gleif_rec["attributes"]["lei"]
    gains: list[tuple[str, str]] = []

    legal_name = (ent.get("legalName") or {}).get("name")
    if not rec.get("legal_name") and legal_name:
        gains.append(("legal_name", legal_name))

    city = (ent.get("legalAddress") or {}).get("city")
    if not rec.get("city") and city:
        gains.append(("city", city))

    legal_form_text = _legal_form_text(ent)

    parent_name = None
    parent = _relationship_record(gleif_rec, "direct-parent")
    if parent:
        parent_name = (parent.get("attributes", {}).get("entity", {}).get("legalName", {}) or {}).get("name")

    return gains, lei, legal_form_text, parent_name


def load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


#: A long unattended run writes this file once per record checked. On Windows, a cloud-synced
#: (OneDrive) or antivirus-scanned working copy can hold a transient exclusive lock on a file that
#: is being rewritten this often, which surfaces to Python as `OSError: [Errno 22] Invalid
#: argument` — not a corruption, not a disk problem, just bad timing. Observed live during this
#: tool's own first real overnight-style run (crashed at record 1,038 of ~1,610, cache intact,
#: no data lost — see `memory/changelog.md`). Retried with backoff rather than left to crash a
#: multi-hour run over what is, in practice, always a one-shot hiccup.
_CACHE_WRITE_RETRIES = 5
_CACHE_WRITE_BACKOFF = 0.5


def save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    tmp = CACHE_PATH.with_suffix(".json.tmp")
    delay = _CACHE_WRITE_BACKOFF
    last_err: Optional[OSError] = None
    for attempt in range(_CACHE_WRITE_RETRIES):
        try:
            tmp.write_text(body, encoding="utf-8")
            tmp.replace(CACHE_PATH)  # atomic on both POSIX and Windows (NTFS)
            return
        except OSError as e:
            last_err = e
            if attempt < _CACHE_WRITE_RETRIES - 1:
                time.sleep(delay)
                delay *= 2
    raise ConnectorError(
        f"could not write {CACHE_PATH} after {_CACHE_WRITE_RETRIES} attempts: {last_err}. "
        f"This is the enrichment cache, not the CRM itself — CRM records already written are safe "
        f"— but progress bookkeeping could not be saved, so stopping rather than risking a silent "
        f"re-check storm on the next run."
    ) from last_err


def _apply_enrichment(
    slug: str, gains: list[tuple[str, str]], lei: str, note: str,
    legal_form_text: Optional[str], parent_name: Optional[str], *, dry_run: bool,
) -> list[str]:
    """Write the gains onto the CRM record, reloading fresh from disk first.

    Reloading (rather than trusting the in-memory copy from ``crm.load_all_companies()``, which
    carries a ``_path`` key and could be stale) is the same defence ``enrich_from_registers.py``
    uses, and the null-check is repeated here rather than trusted from the caller — "never
    overwrite" is cheap to verify twice and expensive to get wrong once.
    """
    path = crm.company_path(slug)
    fresh = crm.load_yaml(path)
    applied: list[str] = []
    for field, value in gains:
        if not fresh.get(field):
            fresh[field] = value
            applied.append(f"{field} {value!r}")

    summary = (
        f"GLEIF enrichment: LEI {lei} found for this firm ({note}). "
        + (f"Filled {', '.join(applied)}. " if applied else "No blank schema field to fill. ")
        + (f"Legal form per GLEIF: {legal_form_text}. " if legal_form_text else "")
        + (f"Direct parent per GLEIF: {parent_name}. " if parent_name else "")
        + "crm/SCHEMA.md has no `lei` field, so the LEI itself lives only in this note, not a "
          "structured field. Match was made on normalized name + country only, not a second "
          "identifier — treat as provisional and challenge if it looks wrong. Record: "
          f"https://search.gleif.org/#/record/{lei}"
    )
    fresh.setdefault("activities", []).append(
        {"date": crm.today(), "type": "research", "summary": summary, "link": None}
    )
    fresh["updated"] = crm.today()
    if not dry_run:
        crm.save_yaml(path, fresh)
    return applied


def run_enrichment(*, dry_run: bool = False, recheck: bool = False, limit: Optional[int] = None) -> dict:
    """Try to enrich every CRM record in our four markets from GLEIF. Cached, so re-runs are cheap.

    Raises :class:`ConnectorError` the moment GLEIF itself is unreachable or malformed — it never
    turns that into "0 enriched today", which would read exactly like a quiet, uneventful run.
    """
    cache = load_cache()
    companies = sorted(crm.load_all_companies(), key=lambda r: r.get("slug") or "")
    out_of_territory = 0
    skipped_cached = 0
    checked = 0
    matched = 0
    enriched = 0
    ambiguous = 0
    no_match = 0
    details: list[dict] = []

    for rec in companies:
        slug = rec.get("slug")
        if not slug or "EXAMPLE" in slug:
            continue
        iso = COUNTRY_ISO.get(rec.get("country") or "")
        if not iso:
            out_of_territory += 1
            continue
        if not recheck and slug in cache:
            skipped_cached += 1
            continue
        if limit is not None and checked >= limit:
            break

        checked += 1
        gleif_rec, note = find_match(rec.get("name") or "", rec.get("legal_name"), iso)

        if gleif_rec is None:
            result = "ambiguous" if note.startswith("ambiguous") else "no_match"
            ambiguous += result == "ambiguous"
            no_match += result == "no_match"
            cache[slug] = {"date": crm.today(), "result": result, "lei": None, "note": note}
            if not dry_run:
                save_cache(cache)
            continue

        matched += 1
        lei = gleif_rec["attributes"]["lei"]
        gains, lei, legal_form_text, parent_name = enrich_one(rec, gleif_rec)
        applied = _apply_enrichment(
            slug, gains, lei, note, legal_form_text, parent_name, dry_run=dry_run
        )
        if applied:
            enriched += 1
            print(f"  {slug}: LEI {lei} — + " + ", ".join(applied))
        else:
            print(f"  {slug}: LEI {lei} — matched, nothing left to fill")

        cache[slug] = {"date": crm.today(), "result": "matched", "lei": lei, "note": note}
        if not dry_run:
            save_cache(cache)
        details.append({"slug": slug, "lei": lei, "gains": applied})

    return {
        "checked": checked,
        "matched": matched,
        "enriched": enriched,
        "ambiguous": ambiguous,
        "no_match": no_match,
        "skipped_cached": skipped_cached,
        "out_of_territory": out_of_territory,
        "details": details,
        "dry_run": dry_run,
    }


def format_enrich_report(rep: dict) -> str:
    lines = [
        f"[gleif] enrichment: {rep['checked']} record(s) checked "
        f"({rep['skipped_cached']} already cached, {rep['out_of_territory']} outside our four markets)",
        f"  {rep['matched']} matched on GLEIF ({rep['enriched']} gained a field) · "
        f"{rep['no_match']} no GLEIF record · {rep['ambiguous']} ambiguous (skipped, not guessed)",
    ]
    if rep["dry_run"]:
        lines.append("  DRY RUN — nothing written")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Part 2 — fund -> manager discovery
# ---------------------------------------------------------------------------

def probe_fund_total(country_iso: str) -> int:
    url = (
        f"{GLEIF_API}/lei-records?filter[entity.legalAddress.country]={country_iso}"
        f"&filter[entity.category]=FUND&page[size]=1"
    )
    data = _get_json(url)
    return int(data.get("meta", {}).get("pagination", {}).get("total") or 0)


def list_funds(country_iso: str, *, max_funds: Optional[int] = None) -> Iterator[dict]:
    """Every GLEIF entity marked ``category=FUND`` for one country, paged at GLEIF's own maximum."""
    page = 1
    seen = 0
    while True:
        url = (
            f"{GLEIF_API}/lei-records?filter[entity.legalAddress.country]={country_iso}"
            f"&filter[entity.category]=FUND&page[size]={PAGE_SIZE}&page[number]={page}"
        )
        data = _get_json(url)
        rows = data["data"]
        if not rows:
            return
        for r in rows:
            yield r
            seen += 1
            if max_funds is not None and seen >= max_funds:
                return
        last_page = data.get("meta", {}).get("pagination", {}).get("lastPage", page)
        if page >= last_page:
            return
        page += 1


def _crm_name_country_index() -> dict[str, set[str]]:
    idx: dict[str, set[str]] = {c: set() for c in COUNTRY_ISO}
    for rec in crm.load_all_companies():
        country = rec.get("country")
        if country not in idx:
            continue
        for name in (rec.get("name"), rec.get("legal_name")):
            if name:
                idx[country].add(normalize_name(name))
    return idx


def discover_fund_managers(
    *, dry_run: bool = False, max_funds_per_country: Optional[int] = None,
    countries: Optional[list[str]] = None,
) -> dict:
    """Follow every fund's ``fund-manager`` relationship; propose managers we do not already hold.

    ``fund-manager`` is a real GLEIF relationship type (confirmed live on French, UAE and Saudi fund
    records) whose ``lei-record`` link returns the manager's own full lei-record directly — not a
    list, not a search result. A fund with no ``fund-manager`` key in its relationships has simply
    never had one reported and is skipped, not guessed at.
    """
    countries = countries or list(COUNTRY_ISO)
    known = _crm_name_country_index()
    managers: dict[str, dict] = {}
    fund_totals: dict[str, int] = {}
    funds_considered = 0
    funds_with_manager_link = 0

    for country in countries:
        iso = COUNTRY_ISO[country]
        total = probe_fund_total(iso)
        fund_totals[country] = total
        cap_note = ""
        if max_funds_per_country is not None and total > max_funds_per_country:
            cap_note = f" — capped at {max_funds_per_country} this run (--max-funds-per-country)"
        print(f"  {country}: {total} fund(s) on GLEIF{cap_note}")

        for fund in list_funds(iso, max_funds=max_funds_per_country):
            funds_considered += 1
            rel = (fund.get("relationships") or {}).get("fund-manager")
            if not rel:
                continue
            link = (rel.get("links") or {}).get("lei-record")
            if not link:
                continue
            funds_with_manager_link += 1
            manager_wrapped = _get_json(link, allow_404=True)
            if manager_wrapped is None:
                continue
            manager = manager_wrapped["data"]
            m_ent = manager["attributes"]["entity"]
            m_country = ISO_COUNTRY.get((m_ent.get("legalAddress") or {}).get("country") or "")
            if not m_country:
                continue  # managed from outside our territory — not our prospect

            m_name = (m_ent.get("legalName") or {}).get("name")
            if not m_name:
                continue
            if normalize_name(m_name) in known.get(m_country, set()):
                continue  # already in the CRM under this name + country — not a miss

            m_lei = manager["attributes"]["lei"]
            fund_name = (fund["attributes"]["entity"]["legalName"] or {}).get("name") or fund["attributes"]["lei"]
            acc = managers.setdefault(m_lei, {
                "name": m_name,
                "country": m_country,
                "city": (m_ent.get("legalAddress") or {}).get("city"),
                "created": ((m_ent.get("creationDate") or "") or "")[:10] or None,
                "funds": set(),
            })
            acc["funds"].add(fund_name)

    proposed: list[cq.Candidate] = []
    for lei, acc in managers.items():
        funds_sorted = sorted(acc["funds"])
        shown = ", ".join(funds_sorted[:5])
        more = "" if len(funds_sorted) <= 5 else f", and {len(funds_sorted) - 5} more"
        why = (
            f"Managing entity of {len(funds_sorted)} GLEIF-registered fund(s) domiciled in our "
            f"territory ({shown}{more}), per GLEIF's fund-manager relationship. Not found in the "
            f"CRM under this name and country — may be a firm we have missed, or the same group as "
            f"an existing record under a different legal entity (check before treating as new)."
        )
        proposed.append(cq.Candidate(
            source=SOURCE,
            source_id=lei,
            name=acc["name"],
            country=acc["country"],
            city=acc["city"],
            segment_guess="fund_manager",
            created=acc["created"],
            why=why,
            evidence_url=f"https://search.gleif.org/#/record/{lei}",
            matched_slug=None,
            extra={"lei": lei, "fund_count": len(funds_sorted), "funds": funds_sorted},
        ))

    rep = cq.write(SOURCE, proposed, dry_run=dry_run)
    rep["fund_totals"] = fund_totals
    rep["funds_considered"] = funds_considered
    rep["funds_with_manager_link"] = funds_with_manager_link
    rep["managers_considered"] = len(managers)
    return rep


def format_fund_report(rep: dict) -> str:
    lines = [cq.format_report(rep)]
    lines.append(
        f"  {rep['funds_considered']} fund(s) walked, {rep['funds_with_manager_link']} had a "
        f"fund-manager relationship, {rep['managers_considered']} distinct in-territory manager(s) "
        f"not already in the CRM"
    )
    for country, total in sorted(rep["fund_totals"].items()):
        lines.append(f"    {country}: {total} fund(s) on GLEIF")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252; names are not.

    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--dry-run", action="store_true", help="report what would change/be proposed, write nothing")
    ap.add_argument("--skip-enrich", action="store_true", help="skip Part 1 (enrich existing CRM records)")
    ap.add_argument("--skip-funds", action="store_true", help="skip Part 2 (fund -> manager candidates)")
    ap.add_argument("--recheck", action="store_true", help="re-query CRM records already in crm/gleif/checked.json")
    ap.add_argument("--limit", type=int, default=None, help="max CRM records to check for enrichment this run")
    ap.add_argument(
        "--countries", default=",".join(COUNTRY_ISO),
        help=f"comma-separated markets for fund->manager discovery (default: all four — {', '.join(COUNTRY_ISO)})",
    )
    ap.add_argument(
        "--max-funds-per-country", type=int, default=None,
        help="cap on how many funds to page through per country during discovery "
             "(France alone has ~19,500 — unbounded is a multi-hour run)",
    )
    args = ap.parse_args(argv)

    countries = [c.strip() for c in args.countries.split(",") if c.strip()]
    for c in countries:
        if c not in COUNTRY_ISO:
            ap.error(f"unknown market {c!r} — choose from {sorted(COUNTRY_ISO)}")

    if not args.skip_enrich:
        try:
            rep = run_enrichment(dry_run=args.dry_run, recheck=args.recheck, limit=args.limit)
        except ConnectorError as e:
            sys.stderr.write(f"GLEIF enrichment FAILED: {e}\n")
            return 1
        print(format_enrich_report(rep))

    if not args.skip_funds:
        try:
            rep = discover_fund_managers(
                dry_run=args.dry_run, max_funds_per_country=args.max_funds_per_country, countries=countries
            )
        except ConnectorError as e:
            sys.stderr.write(f"GLEIF fund->manager discovery FAILED: {e}\n")
            return 1
        print(format_fund_report(rep))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
