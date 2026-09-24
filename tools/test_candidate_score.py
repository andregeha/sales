#!/usr/bin/env python
"""Tests for candidate scoring — specifically, that the queue actually sorts.

A review queue whose rows all score the same is not a queue, it is a pile with a number on it. That
is what happened when 715 DIFC candidates arrived from one register with identical fields: they
landed in a 16-point band with 342 tied at exactly 20, and nothing was above anything else.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import candidates as cq  # noqa: E402


def _c(**kw):
    base = dict(source="dfsa-difc-broad", name="Example Advisers Limited", country="UAE",
                why="x")
    base.update(kw)
    return cq.Candidate(**base)


def test_a_weak_signal_sinks_a_candidate_below_its_peers():
    """A DIFC representative office and a DIFC advisory firm arrive identically shaped.

    They are worth wildly different amounts — a representative office cannot conduct financial
    business at all — and the score has to say so, or the register's own judgement is lost.
    """
    plain = _c().score()[0]
    weak = _c(extra={"weak_signal": "a representative office cannot conduct financial business"}).score()[0]
    assert weak < plain
    assert "cannot conduct financial business" in _c(
        extra={"weak_signal": "a representative office cannot conduct financial business"}
    ).score()[1]


def test_a_strong_signal_lifts_one():
    plain = _c().score()[0]
    strong = _c(extra={"strong_signal": "named on a fund's manager record"}).score()[0]
    assert strong > plain


def test_the_reasoning_names_every_signal_that_moved_the_score():
    """A human must be able to disagree in ten seconds without re-researching the firm."""
    _, why = _c(extra={"weak_signal": "only a representative office"}).score()
    assert "proposed by dfsa-difc-broad" in why
    assert "only a representative office" in why
    assert "not the ICP score" in why


def test_a_licensed_source_outranks_a_self_declared_one():
    """A DFSA-authorised firm is regulated; a French NAF code is a claim the company made itself."""
    licensed = _c(source="dfsa-difc-broad").score()[0]
    declared = _c(source="sirene-france").score()[0]
    assert licensed > declared


def test_score_stays_within_bounds():
    assert _c(extra={"weak_signal": "x"}, source="unknown-source").score()[0] >= 0
    assert _c(extra={"fund_count": 99, "officers": ["a"], "naf": "66.30Z"},
              segment_guess="family_office", source="gleif").score()[0] <= 100


def test_the_decision_log_is_not_read_as_a_candidate(tmp_path, monkeypatch):
    """`decisions.jsonl` shares the candidates directory and is not a candidate file.

    Globbing `*.jsonl` blindly fed decision rows into the candidate list, where they carry no
    `source` and broke every reader with a KeyError. Caught in live use, not in review.
    """
    import json

    monkeypatch.setattr(cq, "CANDIDATES_DIR", tmp_path)
    monkeypatch.setattr(cq, "DECISIONS_PATH", tmp_path / "decisions.jsonl")
    (tmp_path / "some-source-2026-09-24.jsonl").write_text(
        json.dumps({"source": "some-source", "name": "A Firm", "country": "UAE", "why": "x"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "decisions.jsonl").write_text(
        json.dumps({"key": "some-source:a firm", "decision": "reject", "reason": "no"}) + "\n",
        encoding="utf-8",
    )
    loaded = list(cq.load_all())
    assert len(loaded) == 1
    assert loaded[0]["source"] == "some-source"
