#!/usr/bin/env python
"""Tests for `multilateral_rfp.py` — run with `python tools/connectors/test_multilateral.py`.

No network access. `SOURCES` is stubbed for every orchestration test; `classify()` is exercised
directly for the false-positive classes, using the real example titles that were found (and
rejected) while building the connector — see its module docstring for the provenance of each.

What matters most, in order:
1. A source that raises is reported BY NAME and never folded into "zero found".
2. Zero genuine matches produces zero CRM records — a quiet run is not a bug.
3. Each documented false-positive class is actually rejected, not just described in a comment.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import multilateral_rfp as mr  # noqa: E402
from base import ConnectorError  # noqa: E402


def mk_notice(**kw) -> mr.Notice:
    kw.setdefault("source", "test_source")
    kw.setdefault("source_id", "1")
    kw.setdefault("country", "Lebanon")
    kw.setdefault("raw_country", "Lebanon")
    kw.setdefault("source_url", "https://example.invalid/notice/1")
    kw.setdefault("issuer", "Test Issuer")
    kw.setdefault("title", "Portfolio Management System")
    kw.setdefault("published_date", None)
    kw.setdefault("deadline", None)
    kw.setdefault("description", "")
    kw.setdefault("require_system_indicator", True)
    return mr.Notice(**kw)


# ---------------------------------------------------------------------------
# classify() — genuine hits
# ---------------------------------------------------------------------------

class TestClassifyAccepts(unittest.TestCase):
    def test_genuine_portfolio_management_system(self):
        ok, reason = mr.classify("Portfolio Management System for XYZ Bank", "", "XYZ Bank")
        self.assertTrue(ok, reason)

    def test_french_gestion_de_portefeuille_software(self):
        ok, reason = mr.classify("Logiciel de gestion de portefeuille", "", "Banque X")
        self.assertTrue(ok, reason)

    def test_core_banking_system(self):
        ok, reason = mr.classify("Core Banking System Replacement", "", "Some Bank")
        self.assertTrue(ok, reason)

    def test_relaxed_mode_accepts_a_title_with_no_system_word(self):
        # UNGM: the positive match already came from the source's own full-text search over the
        # notice description, which we cannot see client-side — only the title. Demanding a
        # system/software word IN THE TITLE would create false negatives for genuine hits whose
        # short title just doesn't happen to repeat it.
        ok, reason = mr.classify("Investment Management Advisory Services", "", "UNDP",
                                  require_system_indicator=False)
        self.assertTrue(ok, reason)


# ---------------------------------------------------------------------------
# classify() — the documented false-positive classes, one real example each
# ---------------------------------------------------------------------------

class TestFalsePositiveClasses(unittest.TestCase):
    def test_project_portfolio_management_rejected(self):
        ok, reason = mr.classify(
            "Establishing a Project Portfolio Management Office", "", "Ministry of Planning")
        self.assertFalse(ok)
        self.assertIn("project-portfolio-management", reason)

    def test_french_portefeuille_de_projets_rejected(self):
        ok, reason = mr.classify("Gestion du portefeuille de projets", "", "Ministère")
        self.assertFalse(ok)

    def test_road_asset_management_system_rejected(self):
        # Real IsDB/World Bank hit found while building this connector.
        ok, reason = mr.classify(
            "Establishment of Road Asset Management System (RAMS) For Planning & Prioritizing "
            "Roads Maintenance Needs in Lebanon",
            "", "Council for Development and Reconstruction")
        self.assertFalse(ok)
        self.assertIn("IT-asset, real-estate or physical-asset", reason)

    def test_it_asset_management_rejected(self):
        ok, reason = mr.classify("IT Asset Management System Upgrade", "", "Ministry")
        self.assertFalse(ok)
        self.assertIn("IT-asset", reason)

    def test_select_an_asset_manager_rejected(self):
        ok, reason = mr.classify("Selection of an external asset manager for the Fund", "", "Fund")
        self.assertFalse(ok)
        self.assertIn("SELECT an asset or fund manager", reason)

    def test_investment_policy_development_rejected(self):
        # Real IsDB hit: BCC2025-056.
        ok, reason = mr.classify(
            "BCC2025-056 The Development of an Investment Policy for an endowment out of a "
            "Charity Program (the Fund)", "", "Islamic Development Bank (IsDB)")
        self.assertFalse(ok)
        self.assertIn("advisory mandate", reason)

    def test_individual_consultant_rejected(self):
        # Real IsDB hit: the "platform" here is a programme M&E dashboard, not an investment system.
        ok, reason = mr.classify(
            "INDIVIDUAL CONSULTANT SERVICES: Tadamon Data Monitoring and Platform Developer",
            "", "Islamic Development Bank (IsDB)")
        self.assertFalse(ok)
        self.assertIn("a person", reason)

    def test_loan_management_system_rejected(self):
        # Real World Bank hit: KAFALAT / Lebanon Green Agrifood Transformation (GATE).
        ok, reason = mr.classify("Loan Management system", "", "KAFALAT")
        self.assertFalse(ok)
        self.assertIn("lending programme", reason)

    def test_grant_for_development_rejected(self):
        # Real IsDB hit.
        ok, reason = mr.classify(
            "Islamic Finance Grant for the Development of Islamic Capital Market Products - GPN",
            "", "Islamic Development Bank (IsDB)")
        self.assertFalse(ok)
        self.assertIn("grant", reason)

    def test_french_pension_fund_issuer_rejected_regardless_of_title(self):
        ok, reason = mr.classify(
            "Mandat de gestion d'actifs pour le compte du fonds de réserve", "", "FRR")
        self.assertFalse(ok)
        self.assertIn("asset-manager mandates", reason)

    def test_category_word_without_system_indicator_rejected(self):
        ok, reason = mr.classify("Asset Management Office Review", "", "Some Project")
        self.assertFalse(ok)
        self.assertIn("no system/software/platform indicator", reason)

    def test_unrelated_notice_rejected(self):
        ok, reason = mr.classify("Procurement of IT Hardware and Software", "", "Ministry")
        self.assertFalse(ok)
        self.assertEqual(
            reason,
            "no portfolio/investment/fund/core-banking/treasury/capital-markets term matched",
        )

    def test_data_monitoring_platform_rejected(self):
        ok, reason = mr.classify(
            "Data Monitoring and Platform Development for a Health Programme", "", "Ministry")
        self.assertFalse(ok)
        self.assertIn("M&E", reason)


# ---------------------------------------------------------------------------
# Orchestration — stubbed sources, temp CRM directory
# ---------------------------------------------------------------------------

class RunHarness(unittest.TestCase):
    """Redirects the CRM's RFP directory into a temp tree, and restores `SOURCES`, so no test
    touches the real CRM or the real network."""

    def setUp(self):
        # Inside REPO_ROOT, not the system temp dir: `crm.cmd_rfp_add` prints a path relative to
        # `crm.REPO_ROOT` (a module-level constant this test does not — and should not — override),
        # and `Path.relative_to` raises if the CRM dirs it redirects live outside that tree.
        self.tmp = Path(tempfile.mkdtemp(dir=mr.REPO_ROOT))
        self._orig_rfps_dir = mr.crm.RFPS_DIR
        self._orig_companies_dir = mr.crm.COMPANIES_DIR
        self._orig_sources = mr.SOURCES
        mr.crm.RFPS_DIR = self.tmp / "rfps"
        mr.crm.COMPANIES_DIR = self.tmp / "companies"
        mr.crm.RFPS_DIR.mkdir(parents=True, exist_ok=True)
        mr.crm.COMPANIES_DIR.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        mr.crm.RFPS_DIR = self._orig_rfps_dir
        mr.crm.COMPANIES_DIR = self._orig_companies_dir
        mr.SOURCES = self._orig_sources
        shutil.rmtree(self.tmp, ignore_errors=True)

    def rfp_files(self):
        return sorted(mr.crm.RFPS_DIR.glob("*.yaml"))


class TestFailsLoudly(RunHarness):
    """The one rule this whole file exists to protect: an unreadable source is reported BY NAME,
    never silently folded into 'zero found'."""

    def test_source_failure_is_named_not_zeroed(self):
        def boom():
            raise ConnectorError("simulated outage")

        mr.SOURCES = [("Stub Source", "stub", boom)]
        result = mr.run(dry_run=True)

        self.assertEqual(len(result["sources_failed"]), 1)
        self.assertEqual(result["sources_failed"][0]["source"], "Stub Source")
        self.assertIn("simulated outage", result["sources_failed"][0]["error"])
        self.assertEqual(result["sources_ok"], [])
        self.assertEqual(result["created"], [])
        self.assertEqual(self.rfp_files(), [])

    def test_one_failing_source_does_not_silence_the_others(self):
        def boom():
            raise ConnectorError("down")

        def ok_but_empty():
            return []

        mr.SOURCES = [("Down Source", "down", boom), ("Fine Source", "fine", ok_but_empty)]
        result = mr.run(dry_run=True)

        self.assertEqual([f["source"] for f in result["sources_failed"]], ["Down Source"])
        self.assertEqual([s["source"] for s in result["sources_ok"]], ["Fine Source"])

    def test_unexpected_exception_is_still_isolated_and_reported(self):
        def buggy():
            raise ValueError("a real bug, not a ConnectorError")

        def ok_but_empty():
            return []

        mr.SOURCES = [("Buggy Source", "buggy", buggy), ("Fine Source", "fine", ok_but_empty)]
        result = mr.run(dry_run=True)

        self.assertEqual(len(result["sources_failed"]), 1)
        self.assertIn("unexpected ValueError", result["sources_failed"][0]["error"])
        self.assertEqual([s["source"] for s in result["sources_ok"]], ["Fine Source"])

    def test_main_exits_nonzero_when_a_source_fails(self):
        mr.SOURCES = [("Down Source", "down", lambda: (_ for _ in ()).throw(ConnectorError("x")))]
        rc = mr.main(["--dry-run", "--json"])
        self.assertEqual(rc, 1)

    def test_main_exits_zero_when_every_source_is_fine(self):
        mr.SOURCES = [("Fine Source", "fine", lambda: [])]
        rc = mr.main(["--dry-run", "--json"])
        self.assertEqual(rc, 0)


class TestZeroGenuineMatches(RunHarness):
    def test_zero_matches_creates_nothing(self):
        def only_noise():
            return [mk_notice(title="Procurement of IT Hardware and Software")]

        mr.SOURCES = [("Noise Source", "noise", only_noise)]
        result = mr.run(dry_run=True)

        self.assertEqual(result["created"], [])
        self.assertEqual(len(result["rejected"]), 1)
        self.assertEqual(self.rfp_files(), [])

    def test_notice_outside_our_four_markets_is_ignored(self):
        def foreign():
            return [mk_notice(country="Egypt", raw_country="Egypt",
                              title="Portfolio Management System")]

        mr.SOURCES = [("Foreign Source", "foreign", foreign)]
        result = mr.run(dry_run=True)

        self.assertEqual(result["created"], [])
        self.assertEqual(result["rejected"], [])
        self.assertEqual(self.rfp_files(), [])


class TestGenuineHitCreatesARecord(RunHarness):
    def test_hit_creates_a_valid_record_with_a_null_deadline(self):
        def one_hit():
            return [mk_notice(
                title="Portfolio Management System for XYZ Bank", issuer="XYZ Bank",
                country="Lebanon", source_url="https://example.invalid/n/42",
                deadline=None, published_date=None,
            )]

        mr.SOURCES = [("Hit Source", "hit", one_hit)]
        result = mr.run(dry_run=False)

        self.assertEqual(len(result["created"]), 1)
        files = self.rfp_files()
        self.assertEqual(len(files), 1)
        rec = mr.crm.load_yaml(files[0])
        self.assertIsNone(rec["deadline"])
        self.assertEqual(rec["status"], "spotted")
        self.assertEqual(rec["country"], "Lebanon")
        self.assertEqual(rec["source_url"], "https://example.invalid/n/42")

        # The whole point of making `deadline` nullable in crm.py: a null deadline must still pass
        # the CRM's own schema validation.
        errors: list = []
        mr.crm.validate_rfp(files[0], rec, errors, set())
        self.assertEqual(errors, [])

    def test_dry_run_writes_nothing(self):
        def one_hit():
            return [mk_notice(title="Portfolio Management System for XYZ Bank", issuer="XYZ Bank")]

        mr.SOURCES = [("Hit Source", "hit", one_hit)]
        result = mr.run(dry_run=True)

        self.assertEqual(len(result["created"]), 1)
        self.assertTrue(result["created"][0]["dry_run"])
        self.assertEqual(self.rfp_files(), [])

    def test_rerun_does_not_duplicate_by_source_url(self):
        def one_hit():
            return [mk_notice(title="Portfolio Management System for XYZ Bank", issuer="XYZ Bank",
                              source_url="https://example.invalid/n/99")]

        mr.SOURCES = [("Hit Source", "hit", one_hit)]
        mr.run(dry_run=False)
        result2 = mr.run(dry_run=False)

        self.assertEqual(result2["created"], [])
        self.assertEqual(len(result2["skipped"]), 1)
        self.assertEqual(len(self.rfp_files()), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
