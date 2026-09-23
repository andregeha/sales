#!/usr/bin/env python
"""Run every register connector and report per-source success or failure.

Usage:
    python tools/connectors/run_all.py                 # run them all
    python tools/connectors/run_all.py --only amf-france
    python tools/connectors/run_all.py --dry-run       # fetch, diff and report; write nothing
    python tools/connectors/run_all.py --json          # machine-readable, for the daily brief

Exit codes:
    0  every connector ran
    1  at least one connector failed — the brief must say so by name

A failed connector is **loud**. It never degrades into an empty diff, because an empty diff reads as
"nothing happened today" and would be believed.
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from base import REPO_ROOT, ConnectorError, format_report  # noqa: E402

# Add a module here as each connector is built. Order is the build order in README.md.
CONNECTOR_MODULES = [
    "amf_france",
    "cma_saudi",
    "dfsa_difc",
    "fsra_adgm",
    "regafi_france",
]

#: The engine's memory of itself — one file per invocation, never overwritten. See `plan/website.md`
#: §3.1: "was the radar actually looking last Tuesday?" must always be answerable, including on a
#: run that failed outright.
RUNS_DIR = REPO_ROOT / "crm" / "runs"


def git_commit_sha() -> Optional[str]:
    """The commit this run's output belongs to, or `None` if it cannot be determined.

    Never guessed — an unreadable git state is recorded as `null`, not a stale or invented sha.
    """
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            sha = out.stdout.strip()
            return sha or None
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def _connector_run_summary(res: dict) -> dict:
    return {
        "register": res["register"],
        "source": res["source"],
        "ok": True,
        "error": None,
        "total": res["total"],
        "new_on_register": res["new_on_register"],
        "created": len(res["created"]),
        "skipped": len(res["skipped"]),
        "changes": len(res["changes"]),
        "baseline": res["baseline"],
        "backfill": res["backfill"],
        "partial": res["partial"],
    }


def _connector_failure_summary(fail: dict) -> dict:
    # `total`/`baseline`/`backfill`/`partial` are genuinely unknown — the source was never read, so
    # `null` is the honest value. `created`/`skipped`/`changes`/`new_on_register` are true zeros: a
    # connector that never ran created, skipped and changed exactly nothing.
    return {
        "register": fail["register"],
        "source": fail["source"],
        "ok": False,
        "error": fail["error"],
        "total": None,
        "new_on_register": 0,
        "created": 0,
        "skipped": 0,
        "changes": 0,
        "baseline": None,
        "backfill": None,
        "partial": None,
    }


def build_run_record(started_at: datetime, finished_at: datetime,
                     results: list[dict], failures: list[dict]) -> dict:
    """Assemble the structured `Run` record. Pure function — no filesystem access — so it is testable
    without a real connector or a real clock."""
    connectors = [_connector_run_summary(r) for r in results] + \
                 [_connector_failure_summary(f) for f in failures]
    connectors.sort(key=lambda c: c["register"])
    return {
        "started_at": started_at.isoformat(timespec="seconds"),
        "finished_at": finished_at.isoformat(timespec="seconds"),
        "duration_s": round((finished_at - started_at).total_seconds(), 3),
        "commit": git_commit_sha(),
        "ok": not failures,
        "connectors": connectors,
    }


def write_run_record(record: dict, runs_dir: Optional[Path] = None) -> Path:
    """Write the record under `crm/runs/<YYYY-MM-DD-HHMMSS>.json`. Never overwrites an existing
    file — on the rare collision (two runs in the same second, e.g. in tests) a numeric suffix is
    added instead.

    ``runs_dir`` defaults to the *current* value of the module-level ``RUNS_DIR`` (looked up at call
    time, not import time) so tests can redirect it by monkeypatching ``run_all.RUNS_DIR``.
    """
    if runs_dir is None:
        runs_dir = RUNS_DIR
    runs_dir.mkdir(parents=True, exist_ok=True)
    stamp = record["started_at"][:19].replace(":", "").replace("T", "-")
    path = runs_dir / f"{stamp}.json"
    n = 2
    while path.exists():
        path = runs_dir / f"{stamp}-{n}.json"
        n += 1
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


def load_connectors(only: str | None) -> list:
    out = []
    for mod_name in CONNECTOR_MODULES:
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, "CONNECTOR")
        if only and cls.register != only:
            continue
        out.append(cls())
    if only and not out:
        raise SystemExit(f"error: no connector named {only!r}. Known: "
                         f"{[importlib.import_module(m).CONNECTOR.register for m in CONNECTOR_MODULES]}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="run a single connector by its register name")
    ap.add_argument("--dry-run", action="store_true", help="fetch and diff, but write nothing")
    ap.add_argument("--baseline-window-days", type=int, default=None,
                    help="on a first run, create records for firms licensed within this many days")
    ap.add_argument("--backfill", action="store_true",
                    help="record EVERY firm on the register not already in the CRM, regardless of "
                         "licence date — run once per register to establish market coverage")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args(argv)

    started_at = datetime.now(timezone.utc)
    results, failures = [], []
    for c in load_connectors(args.only):
        try:
            res = c.run(dry_run=args.dry_run, baseline_window_days=args.baseline_window_days,
                        backfill=args.backfill)
            results.append(res)
        except ConnectorError as e:
            failures.append({"register": c.register, "source": c.source_name, "ok": False,
                             "error": str(e)})
        except Exception as e:  # noqa: BLE001 - an unexpected bug must still be loud, not silent
            failures.append({"register": c.register, "source": c.source_name, "ok": False,
                             "error": f"unexpected {type(e).__name__}: {e}",
                             "traceback": traceback.format_exc()})
    finished_at = datetime.now(timezone.utc)

    # Every run leaves a record, success or failure — a dry run is a preview and leaves none,
    # matching the rule that a dry run writes nothing else either (no snapshot, no CRM record).
    run_path = None
    if not args.dry_run:
        record = build_run_record(started_at, finished_at, results, failures)
        run_path = write_run_record(record)

    if args.json:
        print(json.dumps({"results": results, "failures": failures,
                          "run_record": str(run_path) if run_path else None},
                         ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(format_report(r))
            print()
        for f in failures:
            print(f"[{f['register']}] FAILED — {f['source']}")
            print(f"  ⚠ {f['error']}")
            print(f"  No snapshot written and no records created. This is NOT a quiet day —")
            print(f"    the source could not be read. Do not report zero new leads from it.")
            print()
        if run_path:
            print(f"run record: {run_path.relative_to(REPO_ROOT)}".replace("\\", "/"))

    if failures:
        print(f"{len(failures)} of {len(results) + len(failures)} connectors FAILED.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
