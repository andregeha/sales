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

#: Sources that are NOT register connectors but must still report their health into the same run
#: record. A register connector produces company records; these produce RFPs or candidates. They
#: share nothing but the contract that matters: **a source that could not be read says so, by name,
#: somewhere Andre will see it.**
#:
#: ⚠ Without this, a dead source is visible only in whoever's terminal happened to run it. EBRD is
#: currently unreadable by design (a stateful JSF portal we refuse to guess at), and that fact
#: belongs on the website's Sources view alongside the registers, not in scrollback.
#:
#: Deliberately excluded: `sirene_france` and `gleif_enrich`. Those are periodic sweeps over tens of
#: thousands of rows, not daily passes, and running them here would make the daily run take hours.
AUX_MODULES = ["multilateral_rfp"]


def _aux_summaries(mod_name: str, *, dry_run: bool) -> list[dict]:
    """Run one auxiliary source and flatten it into per-source rows shaped like a connector run.

    The RFP radar reads four organisations and any of them can fail independently, so it emits four
    rows rather than one — a run where EBRD is dead and the World Bank is fine is not "the radar
    failed", and must not read as either "fine" or "all broken".
    """
    mod = importlib.import_module(mod_name)
    res = mod.run(dry_run=dry_run)
    rows = []

    def key_for(entry: dict) -> str:
        # The register key is shown to a human on the Sources view, so it must read as a name and
        # not as an internal module path. `multilateral_rfp:EBRD procurement` was the module's
        # identifier leaking into the UI.
        short = entry.get("key") or entry["source"].lower().split("(")[0].strip().replace(" ", "-")
        return f"rfp:{short.replace('_', '-')}"

    for r in res.get("sources_ok", []):
        rows.append({
            "register": key_for(r), "source": r["source"], "ok": True, "error": None,
            # The organisation's own name, so the card reads "rfp:ebrd · EBRD procurement".
            "regulator": r["source"],
            # `total` is notices READ in our markets; `created` is genuine hits. A source can read
            # 69 notices and correctly create nothing — that is a working radar, not a quiet one.
            "total": r.get("found"), "new_on_register": r.get("found") or 0,
            # Join on the SHORT key each notice carries, not the display name — they differ, and
            # matching on the display name silently tallied zero for every source.
            "created": sum(1 for c in res.get("created", []) if c.get("source") == r.get("key")),
            "skipped": sum(1 for c in res.get("rejected", []) if c.get("source") == r.get("key")),
            "changes": 0, "baseline": None, "backfill": None, "partial": None,
        })
    for f in res.get("sources_failed", []):
        rows.append({
            "register": key_for(f), "source": f["source"], "ok": False,
            "regulator": f["source"],
            "error": f["error"], "total": None, "new_on_register": 0,
            "created": 0, "skipped": 0, "changes": 0,
            "baseline": None, "backfill": None, "partial": None,
        })
    return rows


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
                     results: list[dict], failures: list[dict],
                     aux: Optional[list[dict]] = None) -> dict:
    """Assemble the structured `Run` record. Pure function — no filesystem access — so it is testable
    without a real connector or a real clock."""
    connectors = (
        [_connector_run_summary(r) for r in results]
        + [_connector_failure_summary(f) for f in failures]
        # Auxiliary sources arrive already in this shape — they are reported beside the registers
        # because a dead RFP source and a dead register are the same kind of bad news.
        + list(aux or [])
    )
    connectors.sort(key=lambda c: c["register"])
    return {
        "started_at": started_at.isoformat(timespec="seconds"),
        "finished_at": finished_at.isoformat(timespec="seconds"),
        "duration_s": round((finished_at - started_at).total_seconds(), 3),
        "commit": git_commit_sha(),
        "ok": not failures and all(c["ok"] for c in (aux or [])),
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
    # Auxiliary sources run only in a full pass: `--only <register>` means "just that register".
    aux_rows: list[dict] = []
    if not args.only:
        for mod_name in AUX_MODULES:
            try:
                aux_rows.extend(_aux_summaries(mod_name, dry_run=args.dry_run))
            except Exception as e:  # noqa: BLE001 - the whole module dying is itself a finding
                aux_rows.append({
                    "register": mod_name, "source": mod_name, "ok": False,
                    "error": f"unexpected {type(e).__name__}: {e}",
                    "total": None, "new_on_register": 0, "created": 0, "skipped": 0,
                    "changes": 0, "baseline": None, "backfill": None, "partial": None,
                })
    finished_at = datetime.now(timezone.utc)

    # Every run leaves a record, success or failure — a dry run is a preview and leaves none,
    # matching the rule that a dry run writes nothing else either (no snapshot, no CRM record).
    run_path = None
    if not args.dry_run:
        record = build_run_record(started_at, finished_at, results, failures, aux_rows)
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
        for a in aux_rows:
            if a["ok"]:
                print(f"[{a['source']}] read {a['total']} notice(s) in our markets · "
                      f"{a['created']} created · {a['skipped']} rejected after filtering")
            else:
                print(f"[{a['source']}] FAILED")
                print(f"  ⚠ {a['error']}")
                print("  This is NOT a quiet day for this source — it could not be read.")
            print()
        if run_path:
            print(f"run record: {run_path.relative_to(REPO_ROOT)}".replace("\\", "/"))

    dead_aux = [a for a in aux_rows if not a["ok"]]
    if failures or dead_aux:
        total = len(results) + len(failures) + len(aux_rows)
        print(f"{len(failures) + len(dead_aux)} of {total} sources FAILED.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
