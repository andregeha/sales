#!/usr/bin/env python
"""Build the website end to end: data contract, then the app.

    python tools/build_site.py            # data + production build
    python tools/build_site.py --data     # data only (fast; what `dev` needs)
    python tools/build_site.py --check    # build twice and prove the output is identical

This is the step the daily run calls. It is deliberately one command, because a build Andre has to
remember to run is a build that silently goes stale (plan §1, R3).
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
NPM = "npm.cmd" if sys.platform == "win32" else "npm"


def run(cmd: list[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=cwd, shell=False)
    if proc.returncode != 0:
        raise SystemExit(f"error: {' '.join(cmd)} failed with exit {proc.returncode}")


def build_data() -> None:
    run([sys.executable, str(ROOT / "tools" / "site_data.py")], cwd=ROOT)


def build_app() -> None:
    if not (SITE / "node_modules").exists():
        print("installing site dependencies (first run only)…")
        run([NPM, "install", "--no-fund", "--no-audit"], cwd=SITE)
    run([NPM, "run", "build"], cwd=SITE)


def hash_tree(root: Path) -> str:
    """Stable hash of a built tree — the determinism check (plan §7)."""
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(root)).replace("\\", "/").encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", action="store_true", help="regenerate the JSON contract only")
    ap.add_argument("--check", action="store_true",
                    help="build twice and assert the output is byte-identical")
    args = ap.parse_args(argv)

    build_data()
    if args.data:
        print("data contract regenerated.")
        return 0

    build_app()
    dist = SITE / "dist"
    first = hash_tree(dist)
    print(f"built {dist.relative_to(ROOT)}  sha256={first[:16]}")

    if args.check:
        # ⚠ Do NOT stash a copy of the output anywhere under site/. Tailwind 4 auto-detects its
        # content sources by scanning the project, so a copy of the built CSS/JS inside the source
        # tree gets scanned for class names and changes the CSS the next build emits. An earlier
        # version of this checker copied dist to site/.dist-first and was itself the only source of
        # nondeterminism it ever found. Comparing hashes needs no copy at all.
        build_data()
        build_app()
        second = hash_tree(dist)
        if first != second:
            print(f"NOT DETERMINISTIC: {first[:16]} != {second[:16]}", file=sys.stderr)
            return 1
        print(f"deterministic: two builds agree ({second[:16]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
