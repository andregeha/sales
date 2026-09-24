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

import pytest  # noqa: E402

import crm  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_resolver_cache():
    """The resolver caches records for the life of the process.

    ⚠ That cache leaks between tests: one test's fixture would still be in memory for the next,
    which is exactly how a stale index causes a duplicate in real use. Clearing it around every
    test keeps each one honest, and mirrors the rule that a write invalidates the cache.
    """
    crm.invalidate_match_index()
    yield
    crm.invalidate_match_index()


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


def test_one_shared_common_word_is_not_identity(monkeypatch):
    """"Finance House Securities" reduces to the single word "house" once industry words are
    stripped — and "house" is contained in "small house single family office fze", which scored a
    confident 0.90 and hid a real Dubai family office behind an unrelated broker.

    One word may stand in for a name of at most two words; beyond that the distance is too great.
    """
    fixture = [_rec("finance-house-securities", "Finance House Securities", country="UAE")]
    monkeypatch.setattr(crm, "load_all_companies", lambda: list(fixture))
    ranked = crm.find_companies("Small House Capital (Single Family Office FZE)", country="UAE")
    assert all(s < 0.90 for s, _ in ranked), "an unrelated firm sharing one word must not read as a duplicate"


def test_a_short_form_still_matches_its_longer_legal_name(monkeypatch):
    """The case single-token containment exists for, and which must keep working."""
    fixture = [_rec("jadwa-investment-difc-limited", "Jadwa Investment (DIFC) Limited", country="UAE")]
    monkeypatch.setattr(crm, "load_all_companies", lambda: list(fixture))
    top = crm.find_companies("Jadwa", country="UAE")[0]
    assert top[0] >= 0.90 and top[1]["slug"] == "jadwa-investment-difc-limited"


def test_the_resolver_caches_records_but_a_write_invalidates_it(tmp_path, monkeypatch):
    """Resolution reads every company record; re-reading them per call made bulk promotion time out.

    ⚠ The dangerous half is the invalidation. A promotion pass creates a record and then resolves
    the NEXT candidate against the CRM — if the cache were stale it would not see what it had just
    written, and would create the same firm twice. That is the precise failure the resolver exists
    to prevent, reintroduced by the optimisation meant to make it usable.
    """
    calls = {"n": 0}
    records = [_rec("first-firm", "First Firm", country="UAE")]

    def counted():
        calls["n"] += 1
        return list(records)

    monkeypatch.setattr(crm, "load_all_companies", counted)
    crm.invalidate_match_index()

    crm.find_companies("First Firm", country="UAE")
    crm.find_companies("Something Else", country="UAE")
    assert calls["n"] == 1, "records should be parsed once, not once per call"

    # A write must make the next resolution see the new record.
    records.append(_rec("second-firm", "Second Firm", country="UAE"))
    crm.invalidate_match_index()
    hit = crm.find_companies("Second Firm", country="UAE")
    assert hit and hit[0][1]["slug"] == "second-firm"
    assert calls["n"] == 2

    crm.invalidate_match_index()


def test_same_firm_refuses_to_decide_on_a_merely_close_match(monkeypatch):
    """The failure this exists to stop, which happened twice in one run.

    Auto-merging the resolver's top hit at 0.90 folded "Alajlan Family Office" into "The Family
    Office International Investment Company" — two unrelated firms sharing the words "family
    office" — and "AlRajhi Partners" into "Sulaiman Alrajhi Holding", two different branches of a
    family whose name covers at least four organisations, a collision our own research had flagged
    in advance.

    `find_companies` ranks and says so. `same_firm` is the decision, and it declines unless the
    names are near-identical, returning the close match so a human sees what it nearly matched.
    """
    fixture = [
        _rec("the-family-office-ksa", "The Family Office International Investment Company (Saudi Arabia)",
             country="Saudi Arabia"),
        _rec("sulaiman-alrajhi-holding", "Sulaiman Alrajhi Holding - Financial Investments",
             country="Saudi Arabia"),
    ]
    monkeypatch.setattr(crm, "load_all_companies", lambda: list(fixture))

    for name in ("Alajlan Family Office", "AlRajhi Partners"):
        slug, _close = crm.same_firm(name, country="Saudi Arabia")
        assert slug is None, f"{name} must not be auto-merged into a different firm"


def test_a_near_miss_is_surfaced_rather_than_hidden(monkeypatch):
    """Declining to merge is only half of it — the caller must SEE what it nearly matched.

    A silent `None` would send a near-duplicate straight into record creation with nobody aware
    there was a candidate to compare it against.
    """
    fixture = [_rec("zenith-orion-capital", "Zenith Orion Capital", country="UAE")]
    monkeypatch.setattr(crm, "load_all_companies", lambda: list(fixture))
    slug, close = crm.same_firm("Zenith Capital", country="UAE")
    assert slug is None, "a shared first word is not identity — Zenith Capital may be a different firm"
    assert close and close[0][1]["slug"] == "zenith-orion-capital"
    assert crm.SUGGEST_THRESHOLD <= close[0][0] < crm.IDENTITY_THRESHOLD


def test_same_firm_does_resolve_a_genuine_identity(monkeypatch):
    """It must still decide when the answer is obvious, or every promotion becomes manual."""
    fixture = [_rec("jadwa-investment-company", "Jadwa Investment Company", country="Saudi Arabia")]
    monkeypatch.setattr(crm, "load_all_companies", lambda: list(fixture))
    slug, _ = crm.same_firm("Jadwa Investment Company", country="Saudi Arabia")
    assert slug == "jadwa-investment-company"
