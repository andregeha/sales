#!/usr/bin/env python
"""Tests for the register connectors — run with `python tools/connectors/test_connectors.py`.

These exist for one reason above all others: to prove that **a connector which cannot read its
source fails loudly and writes nothing**. A radar that fails silently is worse than no radar,
because it is trusted. Everything else here is secondary.

No network access is used. Sources are stubbed.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import base  # noqa: E402
from base import Connector, ConnectorError, Entry, normalize_name  # noqa: E402


def mk_entry(key: str, name: str, **kw) -> Entry:
    kw.setdefault("country", "France")
    kw.setdefault("segment", "asset_manager")
    kw.setdefault("licence_date", "2026-09-01")
    return Entry(key=key, name=name, **kw)


class StubConnector(Connector):
    register = "test-register"
    regulator = "TESTREG"
    country = "France"
    source_name = "Test register"
    source_url = "https://example.invalid/register"

    def __init__(self, entries=None, error=None):
        self._entries = entries or []
        self._error = error

    def fetch(self):
        if self._error:
            raise self._error
        return self._entries


class ConnectorHarness(unittest.TestCase):
    """Redirects the CRM and snapshot directories into a temp tree so tests never touch real data."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._orig = (base.REGISTERS_DIR, base.EVENTS_DIR, base.crm.COMPANIES_DIR, base.crm.RFPS_DIR)
        base.REGISTERS_DIR = self.tmp / "registers"
        base.EVENTS_DIR = self.tmp / "events"
        base.crm.COMPANIES_DIR = self.tmp / "companies"
        base.crm.RFPS_DIR = self.tmp / "rfps"
        for d in (base.REGISTERS_DIR, base.EVENTS_DIR, base.crm.COMPANIES_DIR, base.crm.RFPS_DIR):
            d.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        base.REGISTERS_DIR, base.EVENTS_DIR, base.crm.COMPANIES_DIR, base.crm.RFPS_DIR = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def snapshots(self, register="test-register"):
        d = base.REGISTERS_DIR / register
        return sorted(d.glob("*.json")) if d.exists() else []

    def companies(self):
        return sorted(base.crm.COMPANIES_DIR.glob("*.yaml"))

    def events(self):
        return sorted(base.EVENTS_DIR.glob("*.jsonl")) if base.EVENTS_DIR.exists() else []

    def event_lines(self):
        lines = []
        for p in self.events():
            for raw in p.read_text(encoding="utf-8").splitlines():
                if raw.strip():
                    lines.append(json.loads(raw))
        return lines


class TestFailsLoudly(ConnectorHarness):
    """The non-negotiable: failure is never mistaken for a quiet day."""

    def test_unreachable_source_raises(self):
        c = StubConnector(error=ConnectorError("register unreachable: connection refused"))
        with self.assertRaises(ConnectorError):
            c.run()

    def test_unreachable_source_writes_nothing(self):
        c = StubConnector(error=ConnectorError("boom"))
        with self.assertRaises(ConnectorError):
            c.run()
        self.assertEqual(self.snapshots(), [], "a failed run must not leave a snapshot behind")
        self.assertEqual(self.companies(), [], "a failed run must not create CRM records")

    def test_empty_result_is_treated_as_failure_not_a_quiet_day(self):
        """The heart of it: zero entries from a live register is a bug, not news."""
        c = StubConnector(entries=[])
        with self.assertRaises(ConnectorError) as ctx:
            c.run()
        self.assertIn("zero entries", str(ctx.exception))
        self.assertEqual(self.snapshots(), [])

    def test_truncated_download_refuses_to_diff(self):
        """A collapsed row count is a truncated fetch, not 90% of an industry being delisted."""
        full = [mk_entry(f"K{i}", f"Firm {i}") for i in range(100)]
        c = StubConnector(entries=full)
        c.run(baseline_window_days=0)
        self.assertEqual(len(self.snapshots()), 1)

        # Next day: the source returns a fraction of the rows.
        snap = self.snapshots()[0]
        snap.rename(snap.parent / "2026-01-01.json")
        c2 = StubConnector(entries=full[:10])
        with self.assertRaises(ConnectorError) as ctx:
            c2.run()
        self.assertIn("truncated", str(ctx.exception).lower())
        self.assertEqual(len(self.snapshots()), 1, "must not overwrite a good snapshot with a bad one")


class TestDiffing(ConnectorHarness):
    def test_baseline_run_does_not_dump_the_back_catalogue(self):
        entries = [
            mk_entry("OLD", "Ancient Gestion", licence_date="2004-01-01"),
            mk_entry("NEW", "Brand New Gestion", licence_date="2026-09-01"),
        ]
        res = StubConnector(entries=entries).run(baseline_window_days=180)
        self.assertTrue(res["baseline"])
        created = [c["name"] for c in res["created"]]
        self.assertEqual(created, ["Brand New Gestion"])
        # ...but the old firm is still in the snapshot, so tomorrow's diff is correct.
        snap = json.loads(self.snapshots()[0].read_text(encoding="utf-8"))
        self.assertEqual(snap["count"], 2)

    def test_second_run_creates_only_genuinely_new_entries(self):
        day1 = [mk_entry("A", "Alpha Gestion"), mk_entry("B", "Beta Gestion")]
        StubConnector(entries=day1).run(baseline_window_days=0)
        self.snapshots()[0].rename(self.snapshots()[0].parent / "2026-01-01.json")

        day2 = day1 + [mk_entry("C", "Gamma Gestion")]
        res = StubConnector(entries=day2).run()
        self.assertFalse(res["baseline"])
        self.assertEqual([c["name"] for c in res["created"]], ["Gamma Gestion"])

    def test_disappearance_is_reported(self):
        day1 = [mk_entry("A", "Alpha Gestion"), mk_entry("B", "Beta Gestion")]
        StubConnector(entries=day1).run(baseline_window_days=0)
        self.snapshots()[0].rename(self.snapshots()[0].parent / "2026-01-01.json")

        res = StubConnector(entries=[mk_entry("A", "Alpha Gestion")]).run()
        self.assertEqual([g["name"] for g in res["disappeared"]], ["Beta Gestion"])

    def test_dry_run_writes_nothing(self):
        res = StubConnector(entries=[mk_entry("A", "Alpha Gestion")]).run(dry_run=True)
        self.assertTrue(res["created"])
        self.assertEqual(self.snapshots(), [])
        self.assertEqual(self.companies(), [])


class TestPartialSources(ConnectorHarness):
    """A source that returns only a slice of a register must not report the rest as delisted."""

    def test_partial_source_does_not_report_disappearances(self):
        class Partial(StubConnector):
            partial_source = True

        day1 = [mk_entry("A", "Alpha"), mk_entry("B", "Beta"), mk_entry("C", "Gamma")]
        Partial(entries=day1).run(baseline_window_days=0)
        self.snapshots()[0].rename(self.snapshots()[0].parent / "2026-01-01.json")

        # Day 2 the slice only contains one of them — that is not evidence anything was delisted.
        res = Partial(entries=[mk_entry("A", "Alpha")]).run()
        self.assertEqual(res["disappeared"], [])
        self.assertTrue(res["partial"])

    def test_partial_source_skips_the_truncation_guard(self):
        """The slice size is not the register size, so a shrinking slice is not a broken download."""
        class Partial(StubConnector):
            partial_source = True

        day1 = [mk_entry(f"K{i}", f"Firm {i}") for i in range(50)]
        Partial(entries=day1).run(baseline_window_days=0)
        self.snapshots()[0].rename(self.snapshots()[0].parent / "2026-01-01.json")
        # Would raise for a complete source; must not here.
        res = Partial(entries=day1[:5]).run()
        self.assertTrue(res["ok"])

    def test_complete_source_still_guards(self):
        day1 = [mk_entry(f"K{i}", f"Firm {i}") for i in range(50)]
        StubConnector(entries=day1).run(baseline_window_days=0)
        self.snapshots()[0].rename(self.snapshots()[0].parent / "2026-01-01.json")
        with self.assertRaises(ConnectorError):
            StubConnector(entries=day1[:5]).run()


class TestUnsegmentableEntries(ConnectorHarness):
    def test_entry_with_no_segment_is_skipped_with_a_reason(self):
        """The CRM requires a segment; a firm whose licensed activities are not ours is not a lead."""
        e = mk_entry("A", "Advisory Only Ltd", licence_type="Advising")
        e.segment = None
        res = StubConnector(entries=[e]).run(baseline_window_days=9999)
        self.assertEqual(res["created"], [])
        self.assertEqual(len(res["skipped"]), 1)
        self.assertIn("no segment", res["skipped"][0]["reason"])
        self.assertIn("Advising", res["skipped"][0]["reason"])
        self.assertEqual(self.companies(), [])


class TestChangeDetection(ConnectorHarness):
    """Field-level diffing: the firms that were already there and changed.

    This is where most real triggers live — a register's population turns over slowly, but its
    entries are amended constantly. It also WRITES to CRM records, so the guardrails matter.
    """

    def _seed(self, rec_overrides=None):
        rec = {"slug": "alpha-gestion", "name": "Alpha Gestion", "country": "France",
               "segment": "asset_manager", "status": "nurture", "stage": "identified",
               "owner": "Andre Geha", "activities": []}
        rec.update(rec_overrides or {})
        base.crm.save_yaml(base.crm.COMPANIES_DIR / f"{rec['slug']}.yaml", rec)
        return rec

    def _two_days(self, day1, day2, **kw):
        StubConnector(entries=day1).run(baseline_window_days=0)
        self.snapshots()[0].rename(self.snapshots()[0].parent / "2026-01-01.json")
        return StubConnector(entries=day2).run(**kw)

    def test_new_authorised_activity_wakes_a_nurture_record(self):
        self._seed()
        d1 = [mk_entry("A", "Alpha Gestion", licence_type="Advising")]
        d2 = [mk_entry("A", "Alpha Gestion", licence_type="Advising; Managing Assets")]
        res = self._two_days(d1, d2)
        self.assertEqual(len(res["changes_applied"]), 1)
        self.assertTrue(res["changes_applied"][0]["woke"])
        rec = base.crm.load_yaml(base.crm.COMPANIES_DIR / "alpha-gestion.yaml")
        self.assertEqual(rec["status"], "qualified")
        self.assertIn("Register change detected", rec["activities"][-1]["summary"])

    def test_a_live_deal_is_never_overwritten(self):
        """A human moved this record down the pipeline. A register amendment is not grounds to undo that."""
        for status in ("contacted", "engaged", "opportunity", "won", "lost", "disqualified"):
            with self.subTest(status=status):
                extra = {"fit": {"score": None, "reasoning": None,
                                 "disqualified_reason": "x" if status == "disqualified" else None}}
                self._seed({"status": status, **extra})
                d1 = [mk_entry("A", "Alpha Gestion", licence_type="Advising")]
                d2 = [mk_entry("A", "Alpha Gestion", licence_type="Advising; Managing Assets")]
                res = self._two_days(d1, d2)
                self.assertFalse(res["changes_applied"][0]["woke"])
                rec = base.crm.load_yaml(base.crm.COMPANIES_DIR / "alpha-gestion.yaml")
                self.assertEqual(rec["status"], status, "status must not move")
                # ...but the change is still recorded, because it is still information.
                self.assertIn("Register change detected", rec["activities"][-1]["summary"])
                shutil.rmtree(self.tmp, ignore_errors=True)
                self.setUp()

    def test_housekeeping_is_logged_but_does_not_wake(self):
        """A published phone number is information, not a reason to write."""
        self._seed()
        d1 = [mk_entry("A", "Alpha Gestion", licence_type="Managing Assets")]
        d2 = [mk_entry("A", "Alpha Gestion", licence_type="Managing Assets", phone="+33 1 23")]
        res = self._two_days(d1, d2)
        self.assertEqual(len(res["changes_applied"]), 1)
        self.assertFalse(res["changes_applied"][0]["woke"])
        rec = base.crm.load_yaml(base.crm.COMPANIES_DIR / "alpha-gestion.yaml")
        self.assertEqual(rec["status"], "nurture")

    def test_a_value_the_register_drops_is_not_reported(self):
        """Registers blank fields routinely; that is noise, not an event."""
        self._seed()
        d1 = [mk_entry("A", "Alpha Gestion", licence_type="Managing Assets", phone="+33 1 23")]
        d2 = [mk_entry("A", "Alpha Gestion", licence_type="Managing Assets")]
        res = self._two_days(d1, d2)
        self.assertEqual(res["changes_applied"], [])

    def test_unchanged_entries_produce_nothing(self):
        self._seed()
        d1 = [mk_entry("A", "Alpha Gestion", licence_type="Managing Assets")]
        res = self._two_days(d1, list(d1))
        self.assertEqual(res["changes"], [])
        self.assertEqual(res["changes_applied"], [])

    def test_dry_run_detects_but_does_not_write(self):
        self._seed()
        d1 = [mk_entry("A", "Alpha Gestion", licence_type="Advising")]
        d2 = [mk_entry("A", "Alpha Gestion", licence_type="Advising; Managing Assets")]
        res = self._two_days(d1, d2, dry_run=True)
        self.assertTrue(res["changes_applied"][0]["woke"])
        rec = base.crm.load_yaml(base.crm.COMPANIES_DIR / "alpha-gestion.yaml")
        self.assertEqual(rec["status"], "nurture", "dry run must not write")

    def test_change_on_a_firm_not_in_the_crm_is_counted_not_dropped(self):
        d1 = [mk_entry("A", "Unknown Ltd", licence_type="Advising")]
        d2 = [mk_entry("A", "Unknown Ltd", licence_type="Advising; Managing Assets")]
        res = self._two_days(d1, d2)
        self.assertEqual(res["changes_applied"], [])
        self.assertEqual(len(res["changes"]), 1)

    def test_baseline_run_detects_no_changes(self):
        res = StubConnector(entries=[mk_entry("A", "Alpha Gestion")]).run(baseline_window_days=0)
        self.assertEqual(res["changes"], [])


class TestChangeEvents(ConnectorHarness):
    """The structured event feed emitted by `_apply_changes` — `crm/events/<YYYY-MM>.jsonl`."""

    def _seed(self, rec_overrides=None):
        rec = {"slug": "alpha-gestion", "name": "Alpha Gestion", "country": "France",
               "segment": "asset_manager", "status": "nurture", "stage": "identified",
               "owner": "Andre Geha", "activities": []}
        rec.update(rec_overrides or {})
        base.crm.save_yaml(base.crm.COMPANIES_DIR / f"{rec['slug']}.yaml", rec)
        return rec

    def _two_days(self, day1, day2, **kw):
        StubConnector(entries=day1).run(baseline_window_days=0)
        self.snapshots()[0].rename(self.snapshots()[0].parent / "2026-01-01.json")
        return StubConnector(entries=day2).run(**kw)

    def test_event_written_for_a_matched_crm_record(self):
        self._seed()
        d1 = [mk_entry("A", "Alpha Gestion", licence_type="Advising")]
        d2 = [mk_entry("A", "Alpha Gestion", licence_type="Advising; Managing Assets")]
        self._two_days(d1, d2)
        lines = self.event_lines()
        self.assertEqual(len(lines), 1)
        ev = lines[0]
        self.assertEqual(ev["company_slug"], "alpha-gestion")
        self.assertEqual(ev["company_name"], "Alpha Gestion")
        self.assertEqual(ev["field"], "licence_type")
        self.assertTrue(ev["is_trigger"])
        self.assertTrue(ev["woke"])
        self.assertEqual(ev["register"], "test-register")

    def test_event_written_with_null_slug_for_a_firm_not_in_the_crm(self):
        d1 = [mk_entry("A", "Unknown Ltd", licence_type="Advising")]
        d2 = [mk_entry("A", "Unknown Ltd", licence_type="Advising; Managing Assets")]
        self._two_days(d1, d2)
        lines = self.event_lines()
        self.assertEqual(len(lines), 1)
        self.assertIsNone(lines[0]["company_slug"])
        self.assertEqual(lines[0]["company_name"], "Unknown Ltd")
        self.assertFalse(lines[0]["woke"], "no CRM record to wake")

    def test_dry_run_does_not_write_events(self):
        self._seed()
        d1 = [mk_entry("A", "Alpha Gestion", licence_type="Advising")]
        d2 = [mk_entry("A", "Alpha Gestion", licence_type="Advising; Managing Assets")]
        self._two_days(d1, d2, dry_run=True)
        self.assertEqual(self.events(), [], "a dry run must leave no event trail")

    def test_events_append_across_runs_rather_than_overwrite(self):
        self._seed()
        d1 = [mk_entry("A", "Alpha Gestion", licence_type="Advising")]
        d2 = [mk_entry("A", "Alpha Gestion", licence_type="Advising; Managing Assets")]
        d3 = [mk_entry("A", "Alpha Gestion", licence_type="Advising; Managing Assets; Custody")]
        self._two_days(d1, d2)
        self.assertEqual(len(self.event_lines()), 1)
        self.snapshots()[0].rename(self.snapshots()[0].parent / "2026-01-02.json")
        StubConnector(entries=d3).run()
        lines = self.event_lines()
        self.assertEqual(len(lines), 2, "the second run's event must be appended, not replace the first")

    def test_housekeeping_change_is_still_logged_as_a_non_trigger_event(self):
        self._seed()
        d1 = [mk_entry("A", "Alpha Gestion", licence_type="Managing Assets")]
        d2 = [mk_entry("A", "Alpha Gestion", licence_type="Managing Assets", phone="+33 1 23")]
        self._two_days(d1, d2)
        lines = self.event_lines()
        self.assertEqual(len(lines), 1)
        self.assertFalse(lines[0]["is_trigger"])
        self.assertFalse(lines[0]["woke"])


class TestPrepareCandidateHook(ConnectorHarness):
    """Regression: a connector that learns its segment per-candidate must not be skipped first.

    ADGM only discovers what a firm is authorised to do by reading its detail page. That happens in
    prepare_candidate(), which the pipeline must call BEFORE the missing-segment skip — otherwise
    every such firm is discarded before its detail page is ever fetched. That bug shipped once and
    silently created nothing from a 412-firm register.
    """

    def test_segment_filled_by_hook_is_honoured(self):
        class Deferred(StubConnector):
            def prepare_candidate(self, entry):
                entry.segment = "asset_manager"
                entry.licence_type = "Managing Assets"

        e = mk_entry("A", "Deferred Segment Ltd")
        e.segment = None
        res = Deferred(entries=[e]).run(baseline_window_days=9999)
        self.assertEqual(len(res["created"]), 1, "hook-supplied segment must prevent the skip")
        self.assertEqual(res["skipped"], [])

    def test_hook_that_cannot_resolve_still_skips(self):
        class Unresolved(StubConnector):
            def prepare_candidate(self, entry):
                entry.licence_type = "detail page unreachable"

        e = mk_entry("A", "Unknown Ltd")
        e.segment = None
        res = Unresolved(entries=[e]).run(baseline_window_days=9999)
        self.assertEqual(res["created"], [])
        self.assertIn("unreachable", res["skipped"][0]["reason"])

    def test_default_hook_is_a_noop(self):
        res = StubConnector(entries=[mk_entry("A", "Normal Ltd")]).run(baseline_window_days=9999)
        self.assertEqual(len(res["created"]), 1)


class TestCMASaudiMapping(unittest.TestCase):
    """Pure mapping logic for the Saudi connector — no network."""

    def setUp(self):
        from cma_saudi import CMASaudiConnector
        self.c = CMASaudiConnector()

    def test_activity_codes_and_full_names_both_normalise(self):
        from cma_saudi import _normalise_activity
        self.assertEqual(_normalise_activity("MI"), "MI")
        self.assertEqual(_normalise_activity("Managing Investments"), "MI")
        self.assertEqual(_normalise_activity("Custody"), "C")
        self.assertEqual(_normalise_activity("Dealing"), "D")

    def test_segment_mapping_matches_the_registers_own_legend(self):
        self.assertEqual(self.c._segment(["MI"]), "asset_manager")
        self.assertEqual(self.c._segment(["MIOF", "Arr"]), "asset_manager")
        self.assertEqual(self.c._segment(["C"]), "custodian")
        self.assertEqual(self.c._segment(["D", "Arr"]), "broker")
        # Advisory/arranging only is not a segment we sell to.
        self.assertIsNone(self.c._segment(["Adv", "Arr"]))

    def test_date_is_converted_from_ddmmyyyy(self):
        body = '<span class="date">16/09/2026</span>'
        self.assertEqual(self.c._last_update(body), "2026-09-16")
        self.assertIsNone(self.c._last_update("no date here"))

    def test_trigger_reasoning_says_what_the_date_actually_means(self):
        e = mk_entry("A", "X", licence_date=base.crm.today())
        pts, why = self.c._trigger_points(e)
        self.assertEqual(pts, 20)
        self.assertIn("last updated", why)
        self.assertNotIn("new licence granted", why)


class TestDeduplication(ConnectorHarness):
    def test_existing_crm_record_is_not_duplicated(self):
        rec = {"slug": "alpha-gestion", "name": "Alpha Gestion SAS", "country": "France",
               "segment": "asset_manager", "status": "qualified", "stage": "identified",
               "owner": "Andre Geha"}
        base.crm.save_yaml(base.crm.COMPANIES_DIR / "alpha-gestion.yaml", rec)
        res = StubConnector(entries=[mk_entry("A", "ALPHA GESTION")]).run(baseline_window_days=9999)
        self.assertEqual(res["created"], [])
        self.assertEqual(len(res["skipped"]), 1)
        self.assertIn("alpha-gestion", res["skipped"][0]["reason"])

    def test_name_normalisation(self):
        self.assertEqual(normalize_name("Société Générale SA"), normalize_name("SOCIETE GENERALE"))
        self.assertEqual(normalize_name("Alpha Gestion SAS"), normalize_name("ALPHA GESTION"))
        self.assertNotEqual(normalize_name("Alpha Capital"), normalize_name("Beta Capital"))


class TestScoring(ConnectorHarness):
    def test_register_silence_is_not_rewarded(self):
        """A firm the register says little about must score lower than one it says a lot about."""
        bare = mk_entry("A", "Bare Gestion")
        rich = mk_entry("B", "Rich Gestion", website="https://x.example",
                        multi_asset=True, third_party=True,
                        evidence={"multi_asset": "4 instrument classes",
                                  "third_party": "mandates for third parties"})
        c = StubConnector()
        bare_score, bare_why = c.score(bare)
        rich_score, _ = c.score(rich)
        self.assertLess(bare_score, rich_score)
        self.assertNotIn("multi-asset", bare_why)

    def test_old_licence_earns_no_trigger_points(self):
        c = StubConnector()
        pts, why = c._trigger_points(mk_entry("A", "X", licence_date="2004-01-01"))
        self.assertEqual(pts, 0)
        self.assertIn("too long ago", why)

    def test_new_licence_earns_full_trigger_points(self):
        c = StubConnector()
        pts, _ = c._trigger_points(mk_entry("A", "X", licence_date=base.crm.today()))
        self.assertEqual(pts, 20)

    def test_generated_record_passes_crm_validation(self):
        c = StubConnector()
        e = mk_entry("A", "Validation Gestion", website="https://x.example")
        rec = c.build_record(e, "snap.json")
        errors: list[str] = []
        base.crm.validate_company(
            base.crm.COMPANIES_DIR / f"{rec['slug']}.yaml", rec, errors, set()
        )
        self.assertEqual(errors, [])


class TestAMFMapping(unittest.TestCase):
    """Pure mapping logic for the AMF connector — no network."""

    def setUp(self):
        from amf_france import AMFFranceConnector
        self.c = AMFFranceConnector()

    def test_phone_malformation_is_corrected_not_invented(self):
        self.assertEqual(self.c._phone("+033 1 85 73 62 56"), "+33 1 85 73 62 56")
        self.assertEqual(self.c._phone("01 85 73 62 56"), "01 85 73 62 56")
        self.assertIsNone(self.c._phone(""))
        self.assertIsNone(self.c._phone(None))

    def test_website_gets_a_scheme_but_not_a_guess(self):
        self.assertEqual(self.c._website("jeito.life"), "https://jeito.life")
        self.assertEqual(self.c._website("https://x.fr"), "https://x.fr")
        self.assertIsNone(self.c._website(""))

    def test_segment_mapping(self):
        self.assertEqual(self.c._segment({"1 - Gestion de portefeuille pour le compte de tiers (Gestion des mandats)"}),
                         "asset_manager")
        self.assertEqual(self.c._segment({"2 - Gestion de FIA"}), "fund_manager")
        self.assertEqual(self.c._segment({"1 - OPCVM"}), "fund_manager")
        # Both -> asset_manager, the broader multi-client business.
        self.assertEqual(self.c._segment({"2 - Gestion de FIA", "1 - Gestion de portefeuille pour le compte de tiers (Gestion des mandats)"}),
                         "asset_manager")


if __name__ == "__main__":
    unittest.main(verbosity=2)


def test_dfsa_phone_never_captures_the_next_field_label():
    """The bug that put "Date of Licence" into 185 records as a telephone number.

    A DFSA detail page renders label/value pairs. A firm with NO telephone collapses to
    ``Telephone Number|Date of Licence|26-Jun-2025``, so taking whatever follows the label captured
    the next label. Those records then counted as reachable — inflating the single number this
    workspace uses to decide whether a firm can be contacted at all.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from dfsa_difc import _clean_phone

    assert _clean_phone("Date of Licence") is None
    assert _clean_phone("date of licence") is None
    assert _clean_phone("Fax Number") is None
    assert _clean_phone("") is None
    assert _clean_phone(None) is None
    # Not a label, but not a phone number either.
    assert _clean_phone("Currency House") is None
    # Real numbers survive, in the formats the register actually publishes.
    assert _clean_phone("+971 4 362 1000") == "+971 4 362 1000"
    assert _clean_phone("  971 4 388 0686  Ext 401 ") == "971 4 388 0686 Ext 401"
