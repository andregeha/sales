#!/usr/bin/env python
"""Tests for `crm.py find` — the resolver that intake leans on.

**Why this is tested harder than its size suggests.** Intake's real risk is not missing a firm; it
is creating a *second* record for a firm we already hold. A duplicate splits a firm's history in
two, and from then on the activities, the contacts and the trigger live on whichever copy the last
writer happened to reach. Nobody notices, because both records look fine.

So the resolver has two failure modes and both matter:

- **Too strict** → a duplicate gets created.
- **Too loose** → a confident-looking wrong match invites a wrong merge, which is worse, because a
  duplicate can be merged later while a wrong merge destroys information.

The cases below are the real ones that were wrong during development, kept as tests so they cannot
come back quietly.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import crm  # noqa: E402


def _rec(slug: str, name: str, **kw) -> dict:
    return {"slug": slug, "name": name, "country": kw.get("country", "France"),
            "segment": kw.get("segment", "asset_manager"),
            "legal_name": kw.get("legal_name")}


FIXTURE = [
    _rec("snb-capital-difc-limited", "SNB Capital (DIFC) Limited", country="UAE"),
    _rec("asb-capital-limited", "ASB Capital Limited", country="UAE"),
    _rec("g-capital-ltd", "G CAPITAL Ltd", country="UAE"),
    _rec("one-investment-management-ltd", "One Investment Management Ltd", country="UAE"),
    _rec("bank-audi-france", "Bank Audi France", segment="bank"),
    _rec("banque-sba", "Banque SBA", segment="bank"),
    _rec("carmignac-gestion", "CARMIGNAC GESTION"),
    _rec("societe-generale-gestion", "Société Générale Gestion", legal_name="SOCIETE GENERALE GESTION S.A."),
]


def _find(monkeypatch, text, limit=8):
    monkeypatch.setattr(crm, "load_all_companies", lambda: list(FIXTURE))
    return crm.find_companies(text, limit=limit)


def test_exact_name_resolves_to_its_own_record(monkeypatch):
    top = _find(monkeypatch, "Carmignac Gestion")[0]
    assert top[1]["slug"] == "carmignac-gestion"


def test_short_form_resolves_to_the_full_legal_name(monkeypatch):
    """Andre writes "SNB Capital", never "SNB Capital (DIFC) Limited"."""
    top = _find(monkeypatch, "SNB Capital")[0]
    assert top[1]["slug"] == "snb-capital-difc-limited"


def test_a_near_neighbour_does_not_outrank_the_real_firm(monkeypatch):
    """ASB Capital and SNB Capital differ by one letter and are different firms.

    Folded whole-string, they are 91% similar — which once put ASB above SNB.
    """
    ranked = _find(monkeypatch, "SNB Capital")
    assert ranked[0][1]["slug"] == "snb-capital-difc-limited"
    asb = next((s for s, r in ranked if r["slug"] == "asb-capital-limited"), 0)
    assert asb < ranked[0][0], "a one-letter-different firm must not tie with the real one"


def test_language_and_legal_form_do_not_prevent_a_match(monkeypatch):
    """"banque audi" must find "Bank Audi France" — different language, different legal suffix."""
    top = _find(monkeypatch, "banque audi")[0]
    assert top[1]["slug"] == "bank-audi-france"


def test_accents_and_legal_suffixes_fold_away(monkeypatch):
    top = _find(monkeypatch, "societe generale gestion")[0]
    assert top[1]["slug"] == "societe-generale-gestion"


def test_an_unknown_firm_returns_nothing_rather_than_plausible_noise(monkeypatch):
    """The one that matters most.

    Sharing the word "capital" with two hundred records is not evidence. When this returned eight
    confident-looking matches for a firm that does not exist, the next step would have been a merge
    into the wrong record.
    """
    assert _find(monkeypatch, "Zzz Nonexistent Capital") == []


def test_a_single_letter_core_does_not_match_everything(monkeypatch):
    """"G Capital" reduces to the distinctive core "g", which is a substring of almost every name.

    Raw substring containment scored it 0.90 against unrelated firms.
    """
    ranked = _find(monkeypatch, "Zzz Qqq Holdings")
    assert all(r["slug"] != "g-capital-ltd" for _, r in ranked)


def test_word_containment_is_not_raw_substring(monkeypatch):
    """"one" is a substring of "nonexistent" but is not a word in it."""
    ranked = _find(monkeypatch, "Zzz Nonexistent Capital")
    assert all(r["slug"] != "one-investment-management-ltd" for _, r in ranked)


def test_results_are_ranked_best_first_and_capped(monkeypatch):
    ranked = _find(monkeypatch, "capital", limit=3)
    assert len(ranked) <= 3
    assert ranked == sorted(ranked, key=lambda x: (-x[0], (x[1].get("name") or "").lower()))


def test_a_name_match_in_another_country_is_not_a_duplicate(monkeypatch):
    """The error this prevents actually happened, and cost us two real firms.

    "SNB Capital" (Riyadh) was dismissed as a duplicate of "SNB Capital (DIFC) Limited" (Dubai).
    They share a name, a brand and an owner — and are different legal entities under different
    regulators, in different markets. Saudi is our thinnest market and both were among its largest
    managers. A cross-country match is capped below the certainty threshold so it can be surfaced
    as a relative but never actioned as identity.
    """
    fixture = [_rec("snb-capital-difc-limited", "SNB Capital (DIFC) Limited", country="UAE")]
    monkeypatch.setattr(crm, "load_all_companies", lambda: list(fixture))

    same = crm.find_companies("SNB Capital", country="UAE")
    assert same and same[0][0] >= 0.90, "same-country match must still read as a duplicate"

    cross = crm.find_companies("SNB Capital", country="Saudi Arabia")
    assert cross, "the foreign relative should still be surfaced, not hidden"
    assert cross[0][0] < 0.90, "a cross-country namesake must never reach duplicate certainty"
