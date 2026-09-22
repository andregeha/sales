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
        self._orig = (base.REGISTERS_DIR, base.crm.COMPANIES_DIR, base.crm.RFPS_DIR)
        base.REGISTERS_DIR = self.tmp / "registers"
        base.crm.COMPANIES_DIR = self.tmp / "companies"
        base.crm.RFPS_DIR = self.tmp / "rfps"
        for d in (base.REGISTERS_DIR, base.crm.COMPANIES_DIR, base.crm.RFPS_DIR):
            d.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        base.REGISTERS_DIR, base.crm.COMPANIES_DIR, base.crm.RFPS_DIR = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def snapshots(self, register="test-register"):
        d = base.REGISTERS_DIR / register
        return sorted(d.glob("*.json")) if d.exists() else []

    def companies(self):
        return sorted(base.crm.COMPANIES_DIR.glob("*.yaml"))


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
