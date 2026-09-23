#!/usr/bin/env python
"""SIRENE / recherche-entreprises (France) — every French company, by industry code.

**Why this exists, and why it is not a register connector.**

A licence register answers "who is regulated". That question cannot find a family office, because a
family office is usually not regulated — which is exactly why France × family office sat at zero
while the AMF connector happily returned 666 firms. The instrument was wrong, not the search.

`recherche-entreprises.api.gouv.fr` answers a different question: **who exists, and what do they say
they do**. It covers every French company, regulated or not, keyed by NAF industry code, with no
API key. It also carries two things registers do not:

- ``date_creation`` — when a company was incorporated. ⚠ **Measured limitation:** the API ignores
  date filters (``date_creation_min`` and friends change nothing) and does **not** order by date —
  page 1 of NAF 66.30Z spans 1966 to 2025. So SIRENE cannot be used to *hunt* new incorporations.
  The AMF connector is the better instrument for that anyway, because it sees the licence. Here,
  a recent ``date_creation`` is a bonus on a candidate we found for another reason.
- ``dirigeants`` — **named officers**, with their role. Not contact details, but names, which is the
  step before a contact route.

⚠ **This source proposes candidates. It never creates records.** NAF codes are self-declared and
broad: ``64.20Z`` is *every holding company in France*, of which a handful are family offices.
Creating records from that would refill the CRM with noise and destroy the thing that makes a
record here mean something. See `tools/candidates.py`.

⚠ **The API caps `total_results` at 10,000** — several of our codes return exactly that, so the
number is a ceiling, not a count. Queries are therefore sliced by *département* to get under it, and
a slice that still hits the ceiling is reported rather than silently truncated.

**Reconciliation is the point, and it is the whole point.** A firm in NAF 66.30Z that is *not* in
our CRM is either unregulated (interesting — an unlicensed manager, an advisory arm, a family
office) or licensed and missed (more interesting still). Neither is visible from a register alone,
and that gap is what this source exists to expose.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Iterator, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import candidates as cq  # noqa: E402
import crm  # noqa: E402

try:
    from .base import ConnectorError, http_get, normalize_name
except ImportError:  # run directly, not as a package
    from base import ConnectorError, http_get, normalize_name

API = "https://recherche-entreprises.api.gouv.fr/search"
SOURCE = "sirene-france"
PAGE = 25          # the API's maximum per_page
API_CEILING = 10000
REQUEST_DELAY = 0.6
#: recherche-entreprises is a free public service with a published rate limit. Being rate-limited
#: is our fault, not its failure, so we back off and retry rather than reporting a dead source.
MAX_RETRIES = 4

#: NAF codes worth reading, and what a match there might mean.
#:
#: ⚠ Signal quality varies enormously and the comment is the honest part:
NAF_CODES: dict[str, tuple[str, str]] = {
    # code: (segment guess, why a hit here is interesting)
    "66.30Z": ("asset_manager", "declares fund management as its principal activity"),
    "66.12Z": ("broker", "declares securities brokerage as its principal activity"),
    "64.30Z": ("fund_manager", "declares itself a collective investment vehicle"),
    "64.20Z": ("family_office", "a holding company — MOST ARE NOT family offices, so this needs a human"),
    "70.10Z": ("family_office", "a head-office entity — same caveat, needs a human"),
}

#: Only these are proposed wholesale. The two family-office codes are so broad that we take only
#: recently created companies from them, or the queue becomes unreadable.
BROAD_CODES = {"64.20Z", "70.10Z"}

#: A company created within this many days is a new entity — the trigger worth having.
NEW_ENTITY_DAYS = 540


def _days_ago(iso: Optional[str]) -> Optional[int]:
    if not iso:
        return None
    try:
        from datetime import date

        y, m, d = (int(x) for x in iso[:10].split("-"))
        return (date.today() - date(y, m, d)).days
    except Exception:  # noqa: BLE001 - a malformed date is simply unknown
        return None


class SireneFrance:
    """Not a `Connector` subclass: this writes candidates, not records, and the base pipeline's
    snapshot/diff/create contract does not apply."""

    source = SOURCE

    def _search(self, **params) -> dict:
        qs = urllib.parse.urlencode(params)
        url = f"{API}?{qs}"
        delay = 1.5
        for attempt in range(MAX_RETRIES):
            try:
                raw = http_get(url, accept="application/json", timeout=45)
            except ConnectorError as e:
                # 429 is us asking too fast. Wait and try again; only give up after several.
                if "429" in str(e) and attempt < MAX_RETRIES - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise
            try:
                return json.loads(raw)
            except json.JSONDecodeError as e:
                raise ConnectorError(f"SIRENE returned unparseable JSON: {e}") from e
        raise ConnectorError(f"SIRENE still rate-limiting after {MAX_RETRIES} attempts: {url}")

    def _pages(self, naf: str, departement: Optional[str] = None) -> Iterator[dict]:
        """All results for a code, optionally within one département."""
        base = {"activite_principale": naf, "etat_administratif": "A", "per_page": PAGE}
        if departement:
            base["departement"] = departement
        first = self._search(**base, page=1)
        total = first.get("total_results") or 0
        if total >= API_CEILING and not departement:
            # Slice and retry rather than silently returning the first 10,000.
            raise _NeedsSlicing(naf, total)
        yield from first.get("results") or []
        pages = min((total + PAGE - 1) // PAGE, 400)
        for p in range(2, pages + 1):
            time.sleep(REQUEST_DELAY)
            yield from self._search(**base, page=p).get("results") or []

    def collect(self, *, limit_per_code: int = 400) -> list[cq.Candidate]:
        known = self._crm_index()
        out: list[cq.Candidate] = []

        for naf, (segment, why) in NAF_CODES.items():
            rows: list[dict] = []
            try:
                for r in self._pages(naf):
                    rows.append(r)
                    if len(rows) >= limit_per_code:
                        break
            except _NeedsSlicing as e:
                rows = self._sliced(naf, limit_per_code, e.total)

            for r in rows:
                c = self._to_candidate(r, naf, segment, why, known)
                if c is not None:
                    out.append(c)

        if not out:
            raise ConnectorError(
                "SIRENE returned no usable rows for any NAF code. France has thousands of firms in "
                "these codes, so this is a fetch or schema failure — not an empty result."
            )
        return out

    def _sliced(self, naf: str, limit: int, total: int) -> list[dict]:
        """A code above the API ceiling is queried département by département.

        Only the départements where this industry actually concentrates — Paris and the Hauts-de-
        Seine business districts hold most of it, and walking all 101 to fill a review queue would
        be disproportionate. ⚠ This is a deliberate narrowing, so it is reported, not hidden.
        """
        rows: list[dict] = []
        for dep in ("75", "92", "69", "13", "33", "59", "44", "31", "06", "67"):
            try:
                for r in self._pages(naf, departement=dep):
                    rows.append(r)
                    if len(rows) >= limit:
                        return rows
            except _NeedsSlicing:
                continue
            time.sleep(REQUEST_DELAY)
        print(
            f"  note: NAF {naf} reported {total}+ results (API ceiling); sampled "
            f"{len(rows)} from the ten départements where the industry concentrates"
        )
        return rows

    @staticmethod
    def _crm_index() -> dict[str, str]:
        idx: dict[str, str] = {}
        for rec in crm.load_all_companies():
            for name in (rec.get("name"), rec.get("legal_name")):
                if name:
                    idx.setdefault(normalize_name(name), rec["slug"])
        return idx

    def _to_candidate(
        self, r: dict, naf: str, segment: str, why: str, known: dict[str, str]
    ) -> Optional[cq.Candidate]:
        name = (r.get("nom_complet") or r.get("nom_raison_sociale") or "").strip()
        siren = str(r.get("siren") or "").strip()
        if not name or not siren:
            return None

        created = (r.get("date_creation") or "").strip() or None
        age = _days_ago(created)
        matched = known.get(normalize_name(name))

        # The broad codes only earn a place in the queue when the company is NEW — otherwise
        # 64.20Z alone would bury the queue under every holding company in France.
        is_new = age is not None and age <= NEW_ENTITY_DAYS
        if naf in BROAD_CODES and not is_new:
            return None

        # An already-known firm is not a new lead. It is still worth surfacing when SIRENE knows
        # something we do not — a director name, or that it was created recently.
        officers = [
            f"{(d.get('prenoms') or '').title()} {(d.get('nom') or '').title()}".strip()
            + (f" ({d.get('qualite')})" if d.get("qualite") else "")
            for d in (r.get("dirigeants") or [])
            if d.get("nom")
        ][:4]
        if matched and not officers and not is_new:
            return None

        reason = why
        if is_new:
            reason = f"incorporated {created} ({age} days ago) — a new entity, and {why}"
        if matched:
            reason = f"already in the CRM as {matched}; SIRENE adds: " + (
                ", ".join(officers) if officers else reason
            )

        siege = r.get("siege") or {}
        return cq.Candidate(
            source=SOURCE,
            source_id=siren,
            name=name,
            country="France",
            city=(siege.get("libelle_commune") or "").title() or None,
            segment_guess=segment,
            created=created,
            why=reason,
            evidence_url=f"https://annuaire-entreprises.data.gouv.fr/entreprise/{siren}",
            matched_slug=matched,
            extra={
                "naf": naf,
                "siren": siren,
                "officers": officers,
                "headcount_band": r.get("tranche_effectif_salarie"),
                "establishments": r.get("nombre_etablissements_ouverts"),
            },
        )


class _NeedsSlicing(Exception):
    def __init__(self, naf: str, total: int):
        super().__init__(naf)
        self.naf = naf
        self.total = total


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report what would be proposed, write nothing")
    ap.add_argument("--limit-per-code", type=int, default=400)
    args = ap.parse_args(argv)

    s = SireneFrance()
    found = s.collect(limit_per_code=args.limit_per_code)
    rep = cq.write(SOURCE, found, dry_run=args.dry_run)
    print(cq.format_report(rep))

    unknown = [c for c in found if not c.matched_slug]
    new_entities = [c for c in found if c.created and (_days_ago(c.created) or 9999) <= NEW_ENTITY_DAYS]
    by_naf: dict[str, int] = {}
    for c in unknown:
        naf = str(c.extra.get("naf"))
        by_naf[naf] = by_naf.get(naf, 0) + 1
    print(f"  reconciliation: {len(unknown)} of {len(found)} are NOT in the CRM")
    for naf, n in sorted(by_naf.items()):
        print(f"    {naf}  {n:>4} unknown to us")
    if new_entities:
        print(f"  incidentally recent ({len(new_entities)}):")
        for c in sorted(new_entities, key=lambda x: x.created or "", reverse=True)[:6]:
            print(f"    + {c.created}  {c.name[:42]:44} {c.extra.get('naf')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
