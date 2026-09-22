#!/usr/bin/env python
"""Fill gaps in existing CRM records from the latest register snapshots.

The binding constraint on this whole engine is not lead volume — it is that we hold names with no
way to reach them. Regulators publish some of what we are missing: the AMF's dataset carries a
website and a switchboard number for many licensed firms.

**These are contact details published by the regulator, not guessed patterns.** That distinction is
the entire reason this script is allowed to exist. It writes a value only where the register states
one and our record is empty; it never overwrites, never infers, and never constructs an address.

Usage:
    python tools/connectors/enrich_from_registers.py --dry-run
    python tools/connectors/enrich_from_registers.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import crm  # noqa: E402
from base import REGISTERS_DIR, normalize_name  # noqa: E402

# Which register covers which country, so we only match within the right population.
REGISTER_COUNTRY = {
    "amf-france": "France",
    "cma-saudi": "Saudi Arabia",
}


def latest_snapshot(register: str) -> Path | None:
    d = REGISTERS_DIR / register
    if not d.exists():
        return None
    files = sorted(d.glob("*.json"))
    return files[-1] if files else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report what would change, write nothing")
    args = ap.parse_args(argv)

    if not REGISTERS_DIR.exists():
        print("No register snapshots yet — run tools/connectors/run_all.py first.")
        return 0

    # Build one lookup per country from the newest snapshot of each register.
    by_country: dict[str, dict[str, dict]] = {}
    sources: dict[str, str] = {}
    for register, country in REGISTER_COUNTRY.items():
        snap_path = latest_snapshot(register)
        if not snap_path:
            continue
        snap = json.loads(snap_path.read_text(encoding="utf-8"))
        by_country.setdefault(country, {}).update(
            {normalize_name(e["name"]): e for e in snap["entries"]}
        )
        sources[country] = f"{register} register snapshot {snap_path.stem}"

    if not by_country:
        print("No usable snapshots found.")
        return 0

    changed = 0
    for rec in crm.load_all_companies():
        lookup = by_country.get(rec.get("country") or "")
        if not lookup:
            continue
        entry = lookup.get(normalize_name(rec.get("name") or ""))
        if not entry:
            continue

        slug = rec["slug"]
        gains: list[str] = []
        path = crm.company_path(slug)
        # Reload from disk so we write the file as it is, not the index copy with its _path key.
        fresh = crm.load_yaml(path)

        # 1. Website — only if we have none.
        if not fresh.get("website") and entry.get("website"):
            fresh["website"] = entry["website"]
            gains.append(f"website {entry['website']}")

        # 2. Switchboard number — as a clearly-labelled generic contact, never attached to a person.
        if entry.get("phone"):
            contacts = fresh.get("contacts") or []
            already = any((c.get("phone") or "").replace(" ", "") ==
                          entry["phone"].replace(" ", "") for c in contacts)
            if not already:
                contacts.append({
                    "name": f"{fresh['name']} — switchboard (register-published)",
                    "title": "General enquiries",
                    "role": "unknown",
                    "email": None,
                    "phone": entry["phone"],
                    "linkedin": None,
                    "language": "fr" if fresh.get("country") == "France" else None,
                    "notes": (
                        "Switchboard number as published by the regulator on its own register — "
                        "not a guessed or inferred number, and not an individual's line. A generic "
                        "number is a weak route: use it to reach a named person, not as the first "
                        "touch itself."
                    ),
                    "source": sources.get(fresh.get("country"), "register snapshot"),
                })
                fresh["contacts"] = contacts
                gains.append(f"switchboard {entry['phone']}")

        if not gains:
            continue

        changed += 1
        print(f"  {slug}: + " + ", ".join(gains))
        if args.dry_run:
            continue

        fresh["updated"] = crm.today()
        fresh.setdefault("activities", []).append({
            "date": crm.today(),
            "type": "research",
            "summary": (
                "Enriched from the " + sources.get(fresh.get("country"), "register") + ": "
                + ", ".join(gains) + ". These are details the regulator publishes on its own "
                "register, not guessed or pattern-inferred. Existing values were left untouched."
            ),
            "link": None,
        })
        crm.save_yaml(path, fresh)

    print(f"\n{changed} record(s) {'would be' if args.dry_run else ''} enriched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
