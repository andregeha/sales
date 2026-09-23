#!/usr/bin/env python
"""site_data.py — emits the read-only JSON data contract that powers the sales website.

Who this is for: nobody edits this by hand. `tools/connectors/run_all.py` calls it after every
scheduled run, and it can be re-run any time with `python tools/site_data.py`. It is the ONLY place
Python and the eventual React front-end meet (`plan/website.md` §2) — this script owns the data,
the site owns presentation, and they agree on nothing but the JSON under `site/public/data/`.

**The CRM (`crm/*.yaml`) stays the system of record and is never written here** — this script only
reads `crm/`, `crm/runs/`, `crm/events/`, `crm/registers/` and `memory/open-questions.md`, and it
never invents a fact: a value the source does not state is `null`, not a guess.

**Determinism is the whole point (`plan/website.md` §7).** Every file is written with sorted keys
and a stable row order, so `python tools/site_data.py` run twice in a row produces byte-identical
output, and a `git diff` on `site/public/data/` is a meaningful record of what a run actually
changed. The single permitted exception is the git commit sha, and it appears in exactly one place:
`build.json`.

Usage:
    python tools/site_data.py                  # write site/public/data/
    python tools/site_data.py --out DIR         # write elsewhere (tests use this)
    python tools/site_data.py --quiet           # suppress the per-file size report
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

sys.path.insert(0, str(HERE))
import crm  # noqa: E402  (path set above so this reuses the CRM's own code path)
import candidates  # noqa: E402
import crm_report  # noqa: E402  (has_contact_route / trigger_line — one definition, not two)

sys.path.insert(0, str(HERE / "connectors"))
import base as connectors_base  # noqa: E402  (REGISTERS_DIR / EVENTS_DIR — one definition, not two)

RUNS_DIR = REPO_ROOT / "crm" / "runs"
EVENTS_DIR = connectors_base.EVENTS_DIR
REGISTERS_DIR = connectors_base.REGISTERS_DIR
QUESTIONS_FILE = REPO_ROOT / "memory" / "open-questions.md"

SCHEMA_VERSION = 1
DEFAULT_OUT = REPO_ROOT / "site" / "public" / "data"

#: A register counts as "failing" once it has missed this many runs in a row. Chosen to match the
#: rule of thumb in `plan/website.md` §3.2 — a connector dead for days must be impossible to miss,
#: but one bad run in isolation is not yet a pattern worth alarming Andre over.
FAILING_THRESHOLD = 3

#: How many recent runs feed the `/sources` sparkline.
SOURCE_HISTORY_LIMIT = 30


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def git_commit_sha() -> Optional[str]:
    """The commit this build's output belongs to, or `None`. Never guessed."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def write_json(path: Path, data: Any) -> int:
    """Write one file, sorted keys, LF, trailing newline. Returns the byte size written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    payload = text.encode("utf-8")
    path.write_bytes(payload)
    return len(payload)


def _is_example(rec: dict) -> bool:
    """Schema-example records never reach the website.

    ⚠ This matters more than it looks. `EXAMPLE-mfo-portfolio-system-rfp` is a FICTIONAL tender
    that exists only to validate the record structure — and it carries a deadline, so on the
    Today page it rendered as a real thing closing on 2026-10-15. A workspace whose first rule is
    "never invent a tender" cannot show an invented one as fact, however it got there.
    """
    return str(rec.get("slug", "")).startswith("EXAMPLE-")


def _strip_path(rec: dict) -> dict:
    """Drop crm.py's `_path` bookkeeping key — an artefact of the loader, not part of the record."""
    return {k: v for k, v in rec.items() if k != "_path"}


def _read_json_files(directory: Path, pattern: str = "*.json") -> list[tuple[Path, dict]]:
    """(path, parsed) for every file matching, sorted by filename, skipping unparsable ones."""
    if not directory.exists():
        return []
    out = []
    for p in sorted(directory.glob(pattern)):
        try:
            out.append((p, json.loads(p.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError) as e:
            sys.stderr.write(f"warning: could not parse {p}: {e}\n")
    return out


def _read_jsonl_files(directory: Path) -> list[dict]:
    """Every event across every `<YYYY-MM>.jsonl` file, in file-then-line order (both stable)."""
    if not directory.exists():
        return []
    out = []
    for p in sorted(directory.glob("*.jsonl")):
        for lineno, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                out.append(json.loads(raw))
            except json.JSONDecodeError as e:
                sys.stderr.write(f"warning: could not parse {p}:{lineno}: {e}\n")
    return out


# ---------------------------------------------------------------------------
# Companies — index.json (slim) + companies/<slug>.json (full)
# ---------------------------------------------------------------------------

def build_company_index_row(rec: dict) -> dict:
    fit = rec.get("fit") or {}
    return {
        "slug": rec.get("slug"),
        "name": rec.get("name"),
        "country": rec.get("country"),
        "city": rec.get("city"),
        "segment": rec.get("segment"),
        "status": rec.get("status"),
        "stage": rec.get("stage"),
        "regulator": rec.get("regulator"),
        "website": rec.get("website"),
        "score": fit.get("score"),
        "has_contact_route": crm_report.has_contact_route(rec),
        "has_email": any(c.get("email") for c in (rec.get("contacts") or [])),
        "has_phone": any(c.get("phone") for c in (rec.get("contacts") or [])),
        "has_linkedin": any(c.get("linkedin") for c in (rec.get("contacts") or [])),
        "trigger": crm_report.trigger_line(rec),
        "created": rec.get("created"),
        "updated": rec.get("updated"),
        "tags": rec.get("tags") or [],
    }


def build_companies(companies: list[dict], out: Path) -> dict:
    """Writes both `index.json` (the slim list) and one `companies/<slug>.json` per firm.

    The full record is the raw CRM record **plus** the same derived fields as the index row (score,
    has_contact_route, has_email, has_phone, has_linkedin, trigger) merged on top — the detail view
    is a superset of the index row, not a different shape, so a score or a contact route renders
    identically wherever it appears (`plan/website.md` §6c: "a domain component means a score looks
    identical everywhere").
    """
    index_rows = []
    for rec in sorted(companies, key=lambda r: r.get("slug") or ""):
        clean = _strip_path(rec)
        derived = build_company_index_row(clean)
        full = {**clean, **derived}
        write_json(out / "companies" / f"{full['slug']}.json", full)
        index_rows.append(derived)
    size = write_json(out / "index.json", index_rows)
    return {"rows": len(index_rows), "bytes": size}


# ---------------------------------------------------------------------------
# RFPs
# ---------------------------------------------------------------------------

def build_rfps(rfps: list[dict], out: Path) -> int:
    rows = sorted((_strip_path(r) for r in rfps), key=lambda r: r.get("slug") or "")
    return write_json(out / "rfps.json", rows)


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------

def load_runs() -> list[dict]:
    """Every `Run` record, oldest first (filenames sort chronologically by construction).

    Each record is stamped with an ``id`` (its filename, minus the extension) — the record itself
    does not carry one on disk, since the filename already is the identity, but the site needs a
    stable react ``key`` and a way to link `/runs` to a specific file.
    """
    out = []
    for path, rec in _read_json_files(RUNS_DIR):
        out.append({"id": path.stem, **rec})
    return out


def build_runs(runs: list[dict], out: Path) -> int:
    return write_json(out / "runs.json", runs)


# ---------------------------------------------------------------------------
# Events — the structured trigger feed
# ---------------------------------------------------------------------------

def load_events() -> list[dict]:
    return _read_jsonl_files(EVENTS_DIR)


def build_events(events: list[dict], out: Path) -> int:
    return write_json(out / "events.json", events)


# ---------------------------------------------------------------------------
# SourceHealth — DERIVED, not stored (plan §3.2 / §6a)
# ---------------------------------------------------------------------------

def _register_regulator(register: str) -> Optional[str]:
    """The regulator name a register publishes about itself, read off its own snapshots.

    `Connector.run()` writes ``regulator`` into every snapshot (`base.py`'s ``snap`` dict) — reusing
    it here means this never has to duplicate the register→regulator mapping that already lives
    in each connector.
    """
    snaps = _read_json_files(REGISTERS_DIR / register)
    return snaps[-1][1].get("regulator") if snaps else None


def compute_source_health(runs: list[dict]) -> list[dict]:
    """Per register: last success, consecutive failures, latest count, a short run history.

    Entirely a function of `runs` (plus, as a fallback, the register snapshots on disk) — nothing
    here reads the wall clock, so it stays deterministic for a fixed set of inputs.
    """
    registers: set[str] = set()
    for r in runs:
        for c in r.get("connectors", []):
            registers.add(c["register"])
    if REGISTERS_DIR.exists():
        for d in REGISTERS_DIR.iterdir():
            if d.is_dir():
                registers.add(d.name)

    out = []
    for reg in sorted(registers):
        # Most-recent-first participation: (started_at, connector-summary) for every run this
        # register actually appeared in. A run made with `--only another-register` simply did not
        # touch this one and must not count as either a success or a failure.
        dated: list[tuple[Optional[str], dict]] = []
        for r in reversed(runs):
            for c in r.get("connectors", []):
                if c["register"] == reg:
                    dated.append((r.get("started_at"), c))
                    break

        consecutive_failures = 0
        for _, c in dated:
            if c["ok"]:
                break
            consecutive_failures += 1

        last_success_date = next(
            (started[:10] for started, c in dated if c["ok"] and started), None
        )
        latest_entry_count = next((c.get("total") for _, c in dated if c["ok"] and c.get("total") is not None), None)
        if latest_entry_count is None:
            snaps = _read_json_files(REGISTERS_DIR / reg)
            if snaps:
                latest_entry_count = snaps[-1][1].get("count")

        latest_partial = next((c.get("partial") for _, c in dated if c.get("partial") is not None), False)

        if not dated:
            status = "stale"          # never run
        elif consecutive_failures >= FAILING_THRESHOLD:
            status = "failing"
        elif consecutive_failures >= 1:
            status = "stale"
        else:
            status = "ok"

        note = None
        if latest_partial:
            note = ("Partial source — reads a slice of the register, not all of it. New names are "
                    "caught; disappearances are not detected.")
        elif dated and not dated[0][1]["ok"]:
            note = dated[0][1].get("error")

        history = [
            {"date": started[:10] if started else None, "count": c.get("total")}
            for started, c in reversed(dated[:SOURCE_HISTORY_LIMIT])
        ]

        out.append({
            "register": reg,
            "regulator": _register_regulator(reg),
            "status": status,
            "last_success_date": last_success_date,
            "consecutive_failures": consecutive_failures,
            "latest_count": latest_entry_count,
            "partial": bool(latest_partial),
            "note": note,
            "runs_seen": len(dated),
            "history": history,
        })
    return out


def build_candidates(out: Path) -> int:
    """The review queue: what noisy sources PROPOSED but were not allowed to create.

    ⚠ These are deliberately not records and are never counted as pipeline. A candidate is a
    question ("is this one of ours?"), and the website's job is to make answering it cheap.
    """
    rows = sorted(
        candidates.load_all(),
        key=lambda r: ((r.get("name") or "").lower(), r.get("source") or ""),
    )
    return write_json(out / "candidates.json", rows)


def build_sources(runs: list[dict], out: Path) -> int:
    return write_json(out / "sources.json", compute_source_health(runs))


# ---------------------------------------------------------------------------
# Stats — counts, coverage matrix, score distribution, contact-route coverage
# ---------------------------------------------------------------------------

#: A deal that has closed one way or the other is not part of the "is this pipeline alive" question
#: `active_total` answers. Everything else — including `nurture`, which is most of the register-
#: sourced volume — is still something we might act on.
TERMINAL_STATUSES = {"won", "lost", "disqualified"}

#: Buckets in display order — numeric bands ascending, `unscored` always last.
_SCORE_BANDS = [f"{lo}-{lo + 9}" for lo in range(0, 90, 10)] + ["90-100", "unscored"]


def _score_bucket(score: Optional[int]) -> str:
    if score is None:
        return "unscored"
    score = max(0, min(100, int(score)))
    if score == 100:
        return "90-100"
    lo = (score // 10) * 10
    return f"{lo}-{lo + 9}"


def compute_stats(companies: list[dict], rfps: list[dict]) -> dict:
    base_stats = crm.compute_stats(companies=companies, rfps=rfps)
    base_stats["active_total"] = sum(
        1 for c in companies if (c.get("status") or "") not in TERMINAL_STATUSES
    )

    countries = sorted({c.get("country") or "unknown" for c in companies})
    segments = sorted(set(crm.SEGMENTS) | {c.get("segment") or "unknown" for c in companies})

    coverage: dict[str, dict[str, int]] = {ctry: {seg: 0 for seg in segments} for ctry in countries}
    for c in companies:
        ctry = c.get("country") or "unknown"
        seg = c.get("segment") or "unknown"
        coverage.setdefault(ctry, {seg2: 0 for seg2 in segments})
        coverage[ctry][seg] = coverage[ctry].get(seg, 0) + 1

    counts: dict[str, int] = {band: 0 for band in _SCORE_BANDS}
    for c in companies:
        bucket = _score_bucket((c.get("fit") or {}).get("score"))
        counts[bucket] = counts.get(bucket, 0) + 1
    score_distribution = [{"band": band, "count": counts[band]} for band in _SCORE_BANDS]

    contact_route_by_market = []
    for ctry in countries:
        in_market = [c for c in companies if (c.get("country") or "unknown") == ctry]
        with_route = sum(1 for c in in_market if crm_report.has_contact_route(c))
        contact_route_by_market.append(
            {"country": ctry, "total": len(in_market), "with_route": with_route}
        )

    base_stats.update({
        "coverage": coverage,
        "score_distribution": score_distribution,
        "contact_route_by_market": contact_route_by_market,
    })
    return base_stats


def build_stats(companies: list[dict], rfps: list[dict], out: Path) -> int:
    return write_json(out / "stats.json", compute_stats(companies, rfps))


# ---------------------------------------------------------------------------
# Open questions — memory/open-questions.md parsed into rows
# ---------------------------------------------------------------------------

_ROW_RE = re.compile(r"^\|.+\|\s*$")
_SEP_RE = re.compile(r"^\|[\s:|\-]+\|\s*$")


def _split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _clean_md(s: str) -> str:
    return s.replace("**", "").strip()


def _id_sort_key(rid: str) -> tuple[int, str]:
    m = re.match(r"(\d+)([a-z]*)", rid)
    if m:
        return (int(m.group(1)), m.group(2))
    return (10 ** 9, rid)


#: `memory/open-questions.md`'s own legend: "🔴 blocking · 🟠 needed soon · ⚪ nice to have."
#: Anything else (a row with no recognised emoji) defaults to "soon" rather than silently vanishing.
_PRIORITY_BY_EMOJI = {"🔴": "blocking", "🟠": "soon", "⚪": "nice"}


def _priority_from_status(status: Optional[str]) -> str:
    if not status:
        return "soon"
    for emoji, priority in _PRIORITY_BY_EMOJI.items():
        if emoji in status:
            return priority
    return "soon"


def parse_open_questions(text: str) -> tuple[list[dict], list[str]]:
    """Structured rows out of every markdown table with a "Question" and "Status" column.

    The narrative "Answered by Andre" / "Resolved" sections are numbered prose, not tables — they
    are already resolved, so they are deliberately not turned into open-question rows. Anything
    that looks like a table row but does not parse cleanly is reported in ``warnings`` rather than
    silently dropped or guessed at.
    """
    rows: list[dict] = []
    warnings: list[str] = []
    lines = text.splitlines()
    section: Optional[str] = None
    i, n = 0, len(lines)

    while i < n:
        line = lines[i]
        if line.startswith("## "):
            section = line[3:].strip()
            i += 1
            continue

        looks_like_header = (
            _ROW_RE.match(line) and "question" in line.lower() and "status" in line.lower()
        )
        if looks_like_header and i + 1 < n and _SEP_RE.match(lines[i + 1]):
            header_cells = [c.lower() for c in _split_row(line)]
            col = {h: idx for idx, h in enumerate(header_cells)}
            id_idx = col.get("#")
            status_idx = col.get("status")
            q_idx = next((idx for h, idx in col.items() if h.startswith("question")), None)
            detail_idx = next(
                (idx for h, idx in col.items()
                 if idx not in (id_idx, status_idx, q_idx)),
                None,
            )
            i += 2
            while i < n and lines[i].strip().startswith("|"):
                cells = _split_row(lines[i])
                ok = (
                    id_idx is not None and q_idx is not None
                    and id_idx < len(cells) and q_idx < len(cells)
                )
                rid = _clean_md(cells[id_idx]) if ok else ""
                question = _clean_md(cells[q_idx]) if ok else ""
                if ok and rid and question:
                    status = (_clean_md(cells[status_idx])
                             if status_idx is not None and status_idx < len(cells) else None)
                    # The "why it matters" column, when a table has one, IS what the question
                    # unblocks — that is what the source file uses that column for in every table.
                    unblocks = (_clean_md(cells[detail_idx])
                               if detail_idx is not None and detail_idx < len(cells) else None)
                    rows.append({
                        "id": rid,
                        "question": question,
                        "status": status,
                        "priority": _priority_from_status(status),
                        "unblocks": unblocks,
                        "section": section,
                    })
                else:
                    warnings.append(f"unparsed row in section {section!r}: {lines[i]!r}")
                i += 1
            continue
        i += 1

    rows.sort(key=lambda r: (_id_sort_key(r["id"]), r["section"] or ""))
    return rows, warnings


def build_questions(out: Path) -> tuple[int, list[str]]:
    if not QUESTIONS_FILE.exists():
        return write_json(out / "questions.json", []), ["memory/open-questions.md not found"]
    rows, warnings = parse_open_questions(QUESTIONS_FILE.read_text(encoding="utf-8"))
    size = write_json(out / "questions.json", rows)
    return size, warnings


# ---------------------------------------------------------------------------
# build.json — the one place a commit sha or build-specific fact appears
# ---------------------------------------------------------------------------

def build_manifest(company_count: int, out: Path) -> int:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "commit": git_commit_sha(),
        "company_count": company_count,
    }
    return write_json(out / "build.json", manifest)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def build(out: Path) -> dict:
    """Build the whole contract into ``out``. Returns a summary dict (sizes, counts, warnings) —
    used by the CLI report and by the test suite. Never touches `crm/companies` or `crm/rfps`."""
    companies = [_strip_path(c) for c in crm.load_all_companies() if not _is_example(c)]
    rfps = [_strip_path(r) for r in crm.load_all_rfps() if not _is_example(r)]
    runs = load_runs()
    events = load_events()

    sizes: dict[str, int] = {}
    company_info = build_companies(companies, out)
    sizes["index.json"] = company_info["bytes"]
    sizes["rfps.json"] = build_rfps(rfps, out)
    sizes["runs.json"] = build_runs(runs, out)
    sizes["events.json"] = build_events(events, out)
    sizes["sources.json"] = build_sources(runs, out)
    sizes["candidates.json"] = build_candidates(out)
    sizes["stats.json"] = build_stats(companies, rfps, out)
    q_size, q_warnings = build_questions(out)
    sizes["questions.json"] = q_size
    sizes["build.json"] = build_manifest(len(companies), out)

    return {
        "out": str(out),
        "companies": len(companies),
        "rfps": len(rfps),
        "runs": len(runs),
        "events": len(events),
        "sizes": sizes,
        "questions_warnings": q_warnings,
    }


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help=f"output directory (default: {DEFAULT_OUT.relative_to(REPO_ROOT)})")
    ap.add_argument("--quiet", action="store_true", help="suppress the per-file size report")
    args = ap.parse_args(argv)

    summary = build(args.out)

    if not args.quiet:
        print(f"wrote site data to {summary['out']}")
        print(f"  companies: {summary['companies']}   rfps: {summary['rfps']}   "
              f"runs: {summary['runs']}   events: {summary['events']}")
        for name, size in sorted(summary["sizes"].items()):
            print(f"  {name:16s} {size:>10,d} bytes")
        for w in summary["questions_warnings"]:
            print(f"  warning: {w}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
