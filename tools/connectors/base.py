#!/usr/bin/env python
"""Shared pipeline for regulator register connectors.

The idea in one line: **pull each regulator's list of licensed firms, diff it against the last
snapshot, and create a CRM record for every new name.** A firm that has just been licensed needs a
portfolio system and has no incumbent to displace.

A connector subclasses :class:`Connector` and implements exactly two things: how to fetch its own
source, and how to map one raw row onto our fields. Everything else — snapshotting, diffing,
deduplication, record creation, scoring and reporting — lives here.

The rule that matters most is in :meth:`Connector.run`: **a connector that cannot reach its source
raises and exits non-zero.** It never returns an empty diff. An empty diff and a dead source look
identical in a morning brief, and the second one is a lie that gets trusted.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import crm  # noqa: E402  (path set above so the connector reuses the CRM's own code path)

REGISTERS_DIR = REPO_ROOT / "crm" / "registers"
EVENTS_DIR = REPO_ROOT / "crm" / "events"

# We identify ourselves honestly. These are public registers being read once a day.
USER_AGENT = (
    "OFS-Sales-RegisterConnector/1.0 "
    "(Omega Financial Solutions; business development; contact: andre.geha@omega-financial-solutions.com)"
)

DEFAULT_TIMEOUT = 60


class ConnectorError(RuntimeError):
    """The source could not be reached or did not look like itself.

    Raised rather than returning an empty result, so a failure can never be mistaken for a quiet day.
    """


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def http_get(url: str, timeout: int = DEFAULT_TIMEOUT, accept: Optional[str] = None) -> bytes:
    """GET a URL, or raise :class:`ConnectorError` with a message worth putting in Andre's brief."""
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                raise ConnectorError(f"{url} returned HTTP {resp.status}")
            return resp.read()
    except HTTPError as e:
        raise ConnectorError(f"{url} returned HTTP {e.code} ({e.reason})") from e
    except URLError as e:
        raise ConnectorError(f"{url} unreachable: {e.reason}") from e
    except TimeoutError as e:
        raise ConnectorError(f"{url} timed out after {timeout}s") from e


# ---------------------------------------------------------------------------
# Entries
# ---------------------------------------------------------------------------

@dataclass
class Entry:
    """One firm as the register states it. Anything the register does not say stays ``None``."""

    key: str                      # stable identifier within this register (licence number)
    name: str
    country: str
    segment: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    licence_date: Optional[str] = None
    licence_type: Optional[str] = None
    legal_name: Optional[str] = None

    # Set these ONLY when the register itself proves them. They award ICP fit points, so a guess
    # here would inflate a score with an invented fact. `None` means "the register does not say".
    multi_asset: Optional[bool] = None
    third_party: Optional[bool] = None
    evidence: dict = field(default_factory=dict)   # what proved the flags, quoted from the register

    raw: dict = field(default_factory=dict)

    def to_snapshot(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "country": self.country,
            "segment": self.segment,
            "city": self.city,
            "website": self.website,
            "phone": self.phone,
            "licence_date": self.licence_date,
            "licence_type": self.licence_type,
            "legal_name": self.legal_name,
            "multi_asset": self.multi_asset,
            "third_party": self.third_party,
            "evidence": self.evidence or None,
        }


# ---------------------------------------------------------------------------
# Name matching (for deduplication against the existing CRM)
# ---------------------------------------------------------------------------

# Legal forms and filler words that differ between a register and how a firm writes its own name.
_NOISE = {
    "sa", "sas", "sasu", "sarl", "sca", "snc", "scs", "se", "eurl", "gmbh", "ltd", "limited",
    "llc", "plc", "inc", "co", "company", "group", "groupe", "holding", "holdings", "the",
    "de", "du", "des", "la", "le", "les", "et", "and",
}


def normalize_name(name: str) -> str:
    """Fold a firm name to a comparable key: no accents, no case, no legal form, no punctuation."""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    tokens = [t for t in s.split() if t and t not in _NOISE]
    return " ".join(tokens)


# ---------------------------------------------------------------------------
# Snapshots
# ---------------------------------------------------------------------------

def snapshot_dir(register: str) -> Path:
    return REGISTERS_DIR / register


def previous_snapshot(register: str, before: str) -> Optional[Path]:
    """The most recent snapshot strictly older than ``before`` (a YYYY-MM-DD string)."""
    d = snapshot_dir(register)
    if not d.exists():
        return None
    files = sorted(p for p in d.glob("*.json") if p.stem < before)
    return files[-1] if files else None


def load_snapshot(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Change events — the structured trigger feed (`crm/events/<YYYY-MM>.jsonl`)
# ---------------------------------------------------------------------------

def append_events(events: list[dict]) -> Optional[Path]:
    """Append one JSON object per line to this month's event log. Never overwrites; never truncates.

    A change on a firm not yet in the CRM (``company_slug: null``) is still appended — it is real
    information about the market even before we have a record for it.
    """
    if not events:
        return None
    month = events[0]["date"][:7]
    path = EVENTS_DIR / f"{month}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def _display_path(path: Path) -> str:
    """Repo-relative if we can manage it, absolute if we cannot. Never raises — this is a label."""
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


# ---------------------------------------------------------------------------
# The connector
# ---------------------------------------------------------------------------

#: Register fields whose change is worth telling Andre about, and why.
#: The first is the one that matters: a firm that gains an authorised activity has just expanded
#: what it is allowed to do, which is a business change and therefore a reason to write.
WATCHED_FIELDS = {
    "licence_type": "authorised activities changed",
    "segment": "segment reclassified",
    "name": "renamed",
    "website": "website published or changed",
    "phone": "telephone published or changed",
}

#: Changes that count as a buying TRIGGER rather than mere housekeeping. A firm adding an activity
#: is growing; a firm publishing a phone number is not.
TRIGGER_FIELDS = {"licence_type", "segment"}


def detect_changes(prev_entries: list[dict], current: list[Entry]) -> list[dict]:
    """Field-level diff of firms present in BOTH snapshots.

    The key-level diff catches firms arriving and leaving. This catches the ones that were already
    there and *changed* — which is where most real triggers live, because a register's population
    turns over slowly but its entries are amended all the time.
    """
    before = {e["key"]: e for e in prev_entries}
    out = []
    for e in current:
        old = before.get(e.key)
        if not old:
            continue
        now = e.to_snapshot()
        for field, label in WATCHED_FIELDS.items():
            a, b = old.get(field), now.get(field)
            if a == b:
                continue
            # A field going from unknown to known is new information, not a change of fact.
            if a in (None, "") and b not in (None, ""):
                label_used = f"{field} published (was unknown)"
            elif b in (None, ""):
                # The register dropping a value it used to publish is usually noise, not news.
                continue
            else:
                label_used = label
            out.append({
                "key": e.key, "name": e.name, "field": field, "label": label_used,
                "before": a, "after": b, "is_trigger": field in TRIGGER_FIELDS,
            })
    return out


class Connector:
    """Base class. A subclass implements :meth:`fetch` and sets the class attributes."""

    register: str = ""            # directory name under crm/registers/
    regulator: str = ""           # what goes in the CRM's `regulator` field
    country: str = ""
    source_name: str = ""         # human name of the register, for source.detail
    source_url: str = ""

    #: Ignore a run whose row count collapses below this fraction of the previous snapshot.
    #: A truncated download must never read as a mass delisting.
    min_retention: float = 0.80

    #: ...but a proportion alone misjudges a small register, where losing one or two names is
    #: ordinary churn. The guard fires only when the drop is BOTH proportionally large and more
    #: than this many entries.
    normal_churn: int = 5

    #: True when the source hands us only a slice of the register rather than the whole of it —
    #: for example a "most recently updated" feed. A partial source must NOT be diffed for
    #: disappearances (everything outside the slice would look delisted) and must not be
    #: retention-checked (the slice size is not the register size).
    partial_source: bool = False

    #: On the very first run, create records only for firms licensed within this many days.
    #: The rest are recorded in the snapshot so tomorrow's diff works, but not written to the CRM —
    #: a register's full back-catalogue is mostly established firms with incumbents, and dumping
    #: hundreds of them would bury the leads that matter.
    baseline_window_days: int = 180

    def fetch(self) -> list[Entry]:  # pragma: no cover - implemented by subclasses
        raise NotImplementedError

    # -- scoring ----------------------------------------------------------

    def score(self, entry: Entry) -> tuple[int, str]:
        """Score a newly licensed firm against `knowledge/market/icp.md`.

        Deliberately conservative: this scores what the *register* proves, nothing more. Fit points
        that depend on facts a register does not state — multi-asset, third-party money — are not
        awarded here. Enrichment raises the score later; invention never does.
        """
        fit = 0
        bits = []
        if entry.segment in {"family_office", "mfo", "bank", "asset_manager", "fund_manager"}:
            fit += 20
            bits.append(f"priority segment {entry.segment} (20)")
        elif entry.segment:
            fit += 10
            bits.append(f"adjacent segment {entry.segment} (10)")
        if entry.country in {"France", "UAE", "Saudi Arabia", "Lebanon"}:
            fit += 15
            bits.append(f"priority market {entry.country} (15)")
        if entry.multi_asset:
            fit += 10
            bits.append(f"multi-asset — {entry.evidence.get('multi_asset', 'per the register')} (10)")
        if entry.third_party:
            fit += 10
            bits.append(f"manages third-party money — {entry.evidence.get('third_party', 'per the register')} (10)")
        if self.regulator:
            fit += 5
            bits.append(f"regulated by {self.regulator} (5)")

        trigger, tbits = self._trigger_points(entry)
        access = 3 if (entry.website or entry.phone) else 0
        abits = (
            "generic company contact published on the register (3)" if access
            else "no contact route published (0)"
        )

        total = fit + trigger + access
        reasoning = (
            f"Fit {fit}/60: " + " + ".join(bits) + ". "
            f"Trigger {trigger}/25: {tbits}. "
            f"Access {access}/15: {abits}. "
            f"Scored automatically from the {self.source_name} at first sighting. Fit points are "
            f"awarded only where the register itself states the fact; anything it is silent on "
            f"scores zero rather than being assumed. Enrich before outreach."
        )
        return total, reasoning

    def _trigger_points(self, entry: Entry) -> tuple[int, str]:
        if not entry.licence_date:
            return 0, "no licence date published, so no datable trigger"
        try:
            lic = datetime.strptime(entry.licence_date, "%Y-%m-%d").date()
        except ValueError:
            return 0, f"licence date {entry.licence_date!r} not parseable"
        age = (date.today() - lic).days
        if age <= 365:
            return 20, f"new licence granted {entry.licence_date} ({age} days ago), no incumbent to displace (20)"
        if age <= 730:
            return 12, f"licence granted {entry.licence_date}, still early-stage but not brand new (12)"
        return 0, f"licence granted {entry.licence_date}, too long ago to count as a trigger"

    # -- record creation --------------------------------------------------

    def _existing_index(self) -> tuple[set[str], dict[str, str]]:
        """(slugs, normalized-name -> slug) across the whole CRM, for deduplication."""
        slugs: set[str] = set()
        by_name: dict[str, str] = {}
        for rec in crm.load_all_companies():
            slug = rec.get("slug")
            if not slug:
                continue
            slugs.add(slug)
            for candidate in (rec.get("name"), rec.get("legal_name")):
                if candidate:
                    by_name.setdefault(normalize_name(candidate), slug)
        return slugs, by_name

    def prepare_candidate(self, entry: Entry) -> None:
        """Hook: enrich one entry just before it is considered for creation.

        Default does nothing. Override where a segment (or anything else the skip checks depend on)
        can only be established by a further request — and note that it is called *before* the
        segment check, which is the whole point.
        """

    def build_record(self, entry: Entry, snapshot_file: str) -> dict:
        today = crm.today()
        score, reasoning = self.score(entry)
        # ⚠ Status follows the TRIGGER, not the raw score. Reading a register gives a firm full
        # fit marks — segment, market, multi-asset, third-party money, regulated — so essentially
        # every licensed société de gestion scores in the 60s on fit alone. That is a statement
        # about how well it *fits*, not about whether there is any reason to write to it today.
        # Calling 600 firms "qualified" because they exist would make the word meaningless and
        # bury the handful that have actually just done something.
        trigger_points, _ = self._trigger_points(entry)
        status = "qualified" if trigger_points > 0 else "nurture"
        detail = (
            f"{self.source_name} ({self.source_url}); licence {entry.key}"
            + (f" dated {entry.licence_date}" if entry.licence_date else "")
            + f". Snapshot: {snapshot_file}."
        )
        summary = (
            f"Appeared as a new entry in the {self.source_name}. Licence {entry.key}"
            + (f", authorised {entry.licence_date}" if entry.licence_date else "")
            + (f", {entry.licence_type}" if entry.licence_type else "")
            + ". Detected by the automated register diff; every field here is as the register "
              "publishes it and nothing has been inferred. Not yet researched or enriched."
        )
        return {
            "slug": self._unique_slug(entry),
            "name": entry.name,
            "legal_name": entry.legal_name,
            "country": entry.country,
            "city": entry.city,
            "segment": entry.segment,
            "regulator": self.regulator,
            "website": entry.website,
            "linkedin": None,
            "size": {"aum": None, "employees": None, "portfolios": None},
            "description": None,
            "source": {"channel": "register", "detail": detail, "date": today},
            "status": status,
            "stage": "identified",
            "owner": crm.DEFAULT_OWNER,
            "tags": self.tags_for(entry),
            "created": today,
            "updated": today,
            "contacts": [],
            "fit": {"score": score, "reasoning": reasoning, "disqualified_reason": None},
            "activities": [{
                "date": today,
                "type": "research",
                "summary": summary,
                "link": self.source_url or None,
            }],
            "next_action": None,
        }

    def tags_for(self, entry: Entry) -> list[str]:
        tags = [self.register, "register-sourced", "new-licence"]
        if entry.segment:
            tags.append(entry.segment.replace("_", "-"))
        return tags

    def _unique_slug(self, entry: Entry) -> str:
        base = crm.slugify(entry.name)
        slug = base
        n = 2
        while crm.company_path(slug).exists():
            slug = f"{base}-{n}"
            n += 1
        return slug

    # -- the pipeline -----------------------------------------------------

    #: Statuses we will wake on a new trigger. Anything further along the pipeline is a human's
    #: judgement about a live deal, and a register amendment is not grounds to overwrite it.
    WAKEABLE = {"nurture", "new"}

    def _apply_changes(self, changes: list[dict], *, dry_run: bool) -> list[dict]:
        """Log each register change on the matching CRM record, and wake the dormant ones.

        This is the payoff for holding a register's whole population. Most of those records sit at
        `nurture` because nothing was happening at the firm. When the register says something HAS
        happened, the record stops being background and becomes a lead — automatically, with the
        regulator as the source.

        Two things it deliberately does not do: it never advances a record a human has already
        moved down the pipeline, and it never touches `disqualified` (we decided that, with a
        reason). A register amendment is evidence, not a verdict.
        """
        if not changes:
            return []
        by_name: dict[str, str] = {}
        for rec in crm.load_all_companies():
            for candidate in (rec.get("name"), rec.get("legal_name")):
                if candidate:
                    by_name.setdefault(normalize_name(candidate), rec["slug"])

        applied = []
        events = []
        grouped: dict[str, list[dict]] = {}
        for ch in changes:
            grouped.setdefault(ch["name"], []).append(ch)

        # Sorted rather than insertion order, so the event log and report are stable run to run.
        for name, items in sorted(grouped.items()):
            slug = by_name.get(normalize_name(name))
            woke = False

            if slug and crm.company_path(slug).exists():
                path = crm.company_path(slug)
                rec = crm.load_yaml(path)
                triggers = [c for c in items if c["is_trigger"]]

                detail = "; ".join(
                    f"{c['label']}: {c['before']!r} -> {c['after']!r}" for c in items
                )
                summary = (
                    f"Register change detected by the automated {self.source_name} diff. {detail}. "
                    f"Every value here is as the regulator publishes it."
                )
                if triggers and rec.get("status") in self.WAKEABLE:
                    rec["status"] = "qualified"
                    woke = True
                    summary += (
                        " ⚠ Status raised from nurture to qualified on the strength of this change — "
                        "an authorisation or segment change means the firm's business has moved, which "
                        "is a reason to write. NOT yet researched; confirm before any outreach."
                    )

                rec.setdefault("activities", []).append({
                    "date": crm.today(), "type": "research",
                    "summary": summary, "link": self.source_url or None,
                })
                rec["updated"] = crm.today()
                if not dry_run:
                    crm.save_yaml(path, rec)
                applied.append({"slug": slug, "name": name, "woke": woke,
                                "fields": [c["field"] for c in items]})
            else:
                # Not (yet) a CRM record. Still a real market event — recorded with a null slug
                # rather than dropped, so "everything that changed this week" is a complete feed.
                slug = None

            for c in items:
                events.append({
                    "date": crm.today(),
                    "register": self.register,
                    "company_slug": slug,
                    "company_name": name,
                    "field": c["field"],
                    "label": c["label"],
                    "before": c["before"],
                    "after": c["after"],
                    "is_trigger": c["is_trigger"],
                    "woke": woke,
                })

        if not dry_run:
            append_events(events)
        return applied

    def run(self, *, dry_run: bool = False, baseline_window_days: Optional[int] = None,
            backfill: bool = False) -> dict:
        """Fetch, diff, create, snapshot, report.

        ``backfill=True`` records **every** firm currently on the register that is not already in
        the CRM, regardless of licence date or of whether it is new since the last snapshot. Use it
        once per register, to establish market coverage: knowing a firm exists is not the same as
        deciding to work it, and the ``status``/``fit.score`` fields are what separate those.
        """
        window = self.baseline_window_days if baseline_window_days is None else baseline_window_days
        run_date = crm.today()

        entries = self.fetch()            # raises ConnectorError — never returns empty on failure
        if not entries:
            raise ConnectorError(
                f"{self.source_name} returned zero entries. A live register is never empty, so this "
                f"is a fetch or parse failure, not a quiet day."
            )

        prev_path = previous_snapshot(self.register, run_date)
        prev = load_snapshot(prev_path) if prev_path else None

        if prev and not self.partial_source:
            prev_count = len(prev["entries"])
            kept = len(entries) / max(prev_count, 1)
            lost = prev_count - len(entries)
            if kept < self.min_retention and lost > self.normal_churn:
                raise ConnectorError(
                    f"{self.source_name} returned {len(entries)} entries against {prev_count} in "
                    f"{prev_path.name} — {lost} gone ({kept:.0%} retained). That is below the "
                    f"{self.min_retention:.0%} floor and looks like a truncated download rather "
                    f"than a mass delisting. Refusing to diff. Check the source by hand."
                )

        prev_keys = {e["key"] for e in prev["entries"]} if prev else set()
        new_entries = [e for e in entries if e.key not in prev_keys]
        # A partial source cannot tell us that anything has gone — only that it is not in the slice.
        gone = sorted(prev_keys - {e.key for e in entries}) if (prev and not self.partial_source) else []
        gone_named = []
        if prev and not self.partial_source:
            by_key = {e["key"]: e for e in prev["entries"]}
            gone_named = [{"key": k, "name": by_key[k]["name"]} for k in gone]

        # --- firms that were already here and changed ---
        changes = detect_changes(prev["entries"], entries) if prev else []

        # --- what actually becomes a CRM record ---
        if backfill:
            candidates = entries
            baseline = False
        elif prev is None:
            cutoff = (date.today() - timedelta(days=window)).isoformat()
            candidates = [
                e for e in entries
                if e.licence_date and e.licence_date >= cutoff
            ]
            baseline = True
        else:
            candidates = new_entries
            baseline = False

        slugs, by_name = self._existing_index()
        created, skipped = [], []
        for e in candidates:
            hit = by_name.get(normalize_name(e.name))
            if hit:
                skipped.append({"name": e.name, "key": e.key, "reason": f"already in CRM as {hit}"})
                continue
            # Give the connector a chance to fill in fields it can only learn per-candidate —
            # ADGM, for instance, has to read a detail page to find out what a firm is authorised
            # to do. This runs ONLY for candidates (new firms), never for the whole register, which
            # is what keeps the two-stage design cheap.
            self.prepare_candidate(e)
            if not e.segment:
                # The register states this firm's authorised activities and none of them map onto a
                # segment we sell to. Recording it would create an unsegmented record (which the CRM
                # schema rejects) and would bury the real leads. Skipping with the reason is the
                # honest outcome — and the reason is what stops us re-finding it next month.
                skipped.append({
                    "name": e.name, "key": e.key,
                    "reason": f"no segment — authorised activities ({e.licence_type or 'none stated'}) "
                              f"do not map to a segment we sell to",
                })
                continue
            rec = self.build_record(e, f"crm/registers/{self.register}/{run_date}.json")
            if not dry_run:
                crm.COMPANIES_DIR.mkdir(parents=True, exist_ok=True)
                crm.save_yaml(crm.company_path(rec["slug"]), rec)
            by_name[normalize_name(e.name)] = rec["slug"]
            created.append({"slug": rec["slug"], "name": e.name, "score": rec["fit"]["score"],
                            "licence_date": e.licence_date})

        # --- write the changes onto the matching CRM records ---
        applied_changes = self._apply_changes(changes, dry_run=dry_run)

        # --- snapshot last, and only on success ---
        snap = {
            "register": self.register,
            "regulator": self.regulator,
            "source_url": self.source_url,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_date": run_date,
            "count": len(entries),
            "entries": [e.to_snapshot() for e in sorted(entries, key=lambda x: x.key)],
        }
        snap_path = snapshot_dir(self.register) / f"{run_date}.json"
        if not dry_run:
            snap_path.parent.mkdir(parents=True, exist_ok=True)
            snap_path.write_text(
                json.dumps(snap, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
                encoding="utf-8",
            )

        return {
            "register": self.register,
            "source": self.source_name,
            "ok": True,
            "baseline": baseline,
            "backfill": backfill,
            "partial": self.partial_source,
            "total": len(entries),
            "previous": len(prev["entries"]) if prev else None,
            "previous_file": prev_path.name if prev_path else None,
            "new_on_register": len(new_entries),
            "created": created,
            "skipped": skipped,
            "disappeared": gone_named,
            "changes": changes,
            "changes_applied": applied_changes,
            "snapshot": _display_path(snap_path),
            "dry_run": dry_run,
        }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def format_report(result: dict) -> str:
    lines = []
    head = f"[{result['register']}] {result['source']}"
    lines.append(head)
    if result.get("partial"):
        lines.append(
            "  ⚠ PARTIAL SOURCE — this reads the most-recently-updated slice of the register, not "
            "all of it. New names are caught; disappearances are NOT detected and are not reported."
        )
    if result.get("backfill"):
        lines.append(
            f"  BACKFILL — recording every firm on the register not already in the CRM, for market "
            f"coverage. Status follows the trigger, so most land in 'nurture'."
        )
    if result.get("baseline"):
        lines.append(
            f"  BASELINE run — {result['total']} entries recorded. Records created only for firms "
            f"licensed recently; the rest are in the snapshot so tomorrow's diff is meaningful."
        )
    else:
        lines.append(
            f"  {result['total']} entries (was {result['previous']} in {result['previous_file']}) "
            f"— {result['new_on_register']} new on the register"
        )
    for c in result["created"]:
        lines.append(f"  + CREATED {c['name']}  [{c['slug']}]  score={c['score']}  licensed={c['licence_date']}")
    for s in result["skipped"]:
        lines.append(f"  = skipped {s['name']} — {s['reason']}")
    for c in result.get("changes_applied", []):
        flag = "WOKE  " if c["woke"] else "change"
        lines.append(f"  ~ {flag}  {c['name']}  [{c['slug']}]  ({', '.join(c['fields'])})")
    unmatched = len(result.get("changes", [])) - sum(
        len(c["fields"]) for c in result.get("changes_applied", []))
    if unmatched > 0:
        lines.append(f"  ~ {unmatched} further register change(s) on firms not in the CRM")
    for g in result["disappeared"]:
        lines.append(f"  - GONE    {g['name']} ({g['key']}) — licence surrendered, renamed or acquired? Worth a look.")
    if not result["created"] and not result["disappeared"] and not result.get("changes_applied"):
        lines.append("  no change")
    lines.append(f"  snapshot: {result['snapshot']}" + ("  (DRY RUN — nothing written)" if result["dry_run"] else ""))
    return "\n".join(lines)
