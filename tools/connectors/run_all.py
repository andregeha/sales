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
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from base import ConnectorError, format_report  # noqa: E402

# Add a module here as each connector is built. Order is the build order in README.md.
CONNECTOR_MODULES = [
    "amf_france",
    "cma_saudi",
    "dfsa_difc",
    "fsra_adgm",
]


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

    if args.json:
        print(json.dumps({"results": results, "failures": failures}, ensure_ascii=False, indent=2))
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

    if failures:
        print(f"{len(failures)} of {len(results) + len(failures)} connectors FAILED.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
