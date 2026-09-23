#!/usr/bin/env python
"""The candidate queue — where a noisy source lands before it is allowed to be a record.

Licence registers are clean: a firm on the AMF list *is* an authorised société de gestion, so a
connector can create a record from it directly. The sources that close our remaining gaps are not
clean:

- French NAF code ``64.20Z`` is *every holding company in France*. A handful are family offices.
- ``70.10Z`` is every head office.
- GLEIF has no industry classification at all.

Creating records from those would refill the CRM with the 22,280 *Agent PSP* problem in a different
costume, and it would destroy the thing that makes this CRM worth trusting — that a record in it
means something.

So: **noisy sources propose, they never create.** A candidate carries its evidence and its reason,
and something with judgement decides. That is the whole of this module.

    crm/candidates/<source>-<YYYY-MM-DD>.jsonl   append-only, one JSON object per line

⚠ Candidates are NOT records. They are not counted in the CRM, they never appear as pipeline, and
`crm.py validate` does not see them. A candidate that is never promoted has cost us nothing.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import crm  # noqa: E402

CANDIDATES_DIR = REPO_ROOT / "crm" / "candidates"


@dataclass
class Candidate:
    """A firm a source thinks we might want, with the evidence for that belief."""

    source: str
    name: str
    country: str
    #: Why this is worth a human's attention. Specific, not "matched a filter".
    why: str
    #: A URL a human can open to check. A candidate without evidence is a rumour.
    evidence_url: Optional[str] = None
    #: The source's own stable id, so re-running does not duplicate.
    source_id: Optional[str] = None
    city: Optional[str] = None
    segment_guess: Optional[str] = None
    created: Optional[str] = None
    #: Set when this candidate appears to already be in the CRM — then it is not a new lead,
    #: it is a reconciliation hit and may still carry new information.
    matched_slug: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)

    def key(self) -> str:
        return f"{self.source}:{self.source_id or self.name.strip().lower()}"


def _path(source: str, date: str) -> Path:
    return CANDIDATES_DIR / f"{source}-{date}.jsonl"


def existing_keys(source: str) -> set[str]:
    """Every candidate key this source has ever emitted.

    Re-running a source must not re-propose what a human has already seen and left alone.
    """
    keys: set[str] = set()
    if not CANDIDATES_DIR.exists():
        return keys
    for p in sorted(CANDIDATES_DIR.glob(f"{source}-*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = row.get("source_id") or (row.get("name") or "").strip().lower()
            keys.add(f"{row.get('source')}:{sid}")
    return keys


def write(source: str, candidates: list[Candidate], *, dry_run: bool = False) -> dict:
    """Append new candidates, skipping any this source has proposed before.

    Returns a report rather than printing one, so a caller can put it in a run record.
    """
    seen = existing_keys(source)
    fresh = [c for c in candidates if c.key() not in seen]
    already = len(candidates) - len(fresh)

    if fresh and not dry_run:
        CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
        path = _path(source, crm.today())
        # Sorted for determinism: the same input always produces the same file.
        lines = [
            json.dumps(asdict(c), ensure_ascii=False, sort_keys=True)
            for c in sorted(fresh, key=lambda x: (x.name.lower(), x.key()))
        ]
        with path.open("a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    return {
        "source": source,
        "proposed": len(candidates),
        "new": len(fresh),
        "already_seen": already,
        "file": str(_path(source, crm.today()).relative_to(REPO_ROOT)).replace("\\", "/"),
        "dry_run": dry_run,
    }


def load_all() -> Iterator[dict]:
    """Every candidate ever written, for the website and for reconciliation reporting."""
    if not CANDIDATES_DIR.exists():
        return
    for p in sorted(CANDIDATES_DIR.glob("*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def format_report(rep: dict) -> str:
    bits = [
        f"[{rep['source']}] {rep['new']} new candidate(s)",
        f"{rep['already_seen']} already proposed before" if rep["already_seen"] else "",
        "(DRY RUN — nothing written)" if rep["dry_run"] else rep["file"],
    ]
    return "  " + " · ".join(b for b in bits if b)
