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


#: Words in a firm's own name that suggest it does what we sell to. Weak evidence on its own — a
#: name is not a business model — but across a queue of 300 it sorts the plausible to the top.
NAME_SIGNALS = {
    "asset management": 12, "asset manager": 12, "gestion privee": 12, "gestion de fortune": 12,
    "wealth": 10, "family office": 16, "multi family": 16, "patrimoine": 10, "patrimonial": 10,
    "capital": 6, "investment": 6, "investissement": 6, "invest": 5, "gestion": 6,
    "partners": 4, "advisors": 4, "conseil": 3, "fund": 8, "fonds": 8, "sicav": 10, "am": 0,
}

#: How much a source's proposal is worth before anything else is known about the firm.
SOURCE_WEIGHT = {
    "gleif": 30,           # it actually manages a registered fund — the strongest signal we have
    "sirene-france": 10,   # it declared an industry code, which is a claim, not a fact
}

#: A NAF code's own signal strength, since they differ enormously.
NAF_WEIGHT = {
    "66.30Z": 18,   # fund management as the principal declared activity
    "64.30Z": 12,   # a collective investment vehicle
    "66.12Z": 10,   # securities brokerage
    "64.20Z": 2,    # every holding company in France
    "70.10Z": 2,    # every head office
}


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

    def score(self) -> tuple[int, str]:
        """How likely this is to be one of ours, 0-100, with the reasoning that produced it.

        ⚠ Deliberately NOT the ICP score in `knowledge/market/icp.md`. That model scores a firm we
        have researched; this scores a *proposal* about a firm we have not. Conflating them would
        let an unreviewed guess inherit the authority of a researched record.

        The reasoning matters more than the number, exactly as it does for a real record — it is
        what lets a human disagree in ten seconds instead of re-researching from scratch.
        """
        pts = 0
        why: list[str] = []

        w = SOURCE_WEIGHT.get(self.source, 5)
        pts += w
        why.append(f"proposed by {self.source} ({w})")

        naf = str((self.extra or {}).get("naf") or "")
        if naf:
            nw = NAF_WEIGHT.get(naf, 4)
            pts += nw
            why.append(f"NAF {naf} ({nw})")

        funds = (self.extra or {}).get("fund_count")
        if isinstance(funds, int) and funds > 0:
            fw = min(24, 8 + 4 * funds)
            pts += fw
            why.append(f"manages {funds} registered fund(s) ({fw})")

        low = self.name.lower()
        hits = [(k, v) for k, v in NAME_SIGNALS.items() if v and k in low]
        if hits:
            best = max(hits, key=lambda x: x[1])
            pts += best[1]
            why.append(f'name contains "{best[0]}" ({best[1]})')

        officers = (self.extra or {}).get("officers") or []
        if officers:
            pts += 8
            why.append(f"{len(officers)} named officer(s) on the public record (8)")

        if self.segment_guess in {"family_office", "mfo", "asset_manager", "fund_manager", "bank"}:
            pts += 8
            why.append(f"guessed segment {self.segment_guess} is one we sell to (8)")

        if self.matched_slug:
            pts -= 20
            why.append(f"already in the CRM as {self.matched_slug} (-20, not a new lead)")

        pts = max(0, min(100, pts))
        return pts, (
            "; ".join(why)
            + ". ⚠ This ranks a PROPOSAL, not a researched firm — it is not the ICP score and "
            "carries none of its authority."
        )


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
        lines = []
        for c in sorted(fresh, key=lambda x: (x.name.lower(), x.key())):
            row = asdict(c)
            row["score"], row["score_reasoning"] = c.score()
            lines.append(json.dumps(row, ensure_ascii=False, sort_keys=True))
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
