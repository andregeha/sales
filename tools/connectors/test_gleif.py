#!/usr/bin/env python
"""Tests for `gleif_enrich.py` — run with `python tools/connectors/test_gleif.py`.

No network access is used: every test stubs `gleif_enrich._get_json`, the single seam all GLEIF
calls pass through. What matters most, in order:

1. A match requires name AND country to agree — a name hit in the wrong country is not a match.
2. An existing non-null field is never overwritten, no matter what GLEIF says.
3. A fund-manager candidate never becomes a CRM record, and is skipped when already known.
4. GLEIF being unreachable raises — it is never mistaken for "nothing to enrich".
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

import candidates as cq  # noqa: E402
import crm  # noqa: E402
import gleif_enrich as g  # noqa: E402
from base import ConnectorError  # noqa: E402


def lei_record(lei: str, name: str, country: str, city: str = "Paris",
                other_names: list[str] | None = None, relationships: dict | None = None) -> dict:
    return {
        "attributes": {
            "lei": lei,
            "entity": {
                "legalName": {"name": name},
                "otherNames": [{"name": n} for n in (other_names or [])],
                "legalAddress": {"country": country, "city": city},
                "legalForm": {"id": "K65D", "other": None},
                "creationDate": "2010-01-01T00:00:00Z",
            },
        },
        "relationships": relationships or {},
    }


def search_response(records: list[dict]) -> dict:
    return {"data": records, "meta": {"pagination": {"total": len(records), "lastPage": 1}}}


class GleifHarness(unittest.TestCase):
    """Redirects the CRM, candidate queue and GLEIF cache into a temp tree."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._orig = (crm.COMPANIES_DIR, cq.CANDIDATES_DIR, cq.REPO_ROOT, g.CACHE_PATH)
        crm.COMPANIES_DIR = self.tmp / "companies"
        cq.CANDIDATES_DIR = self.tmp / "candidates"
        # tools/candidates.py's write() computes its report path relative to its own module-level
        # REPO_ROOT (not derived from CANDIDATES_DIR), so it has to move too for the redirect to work.
        cq.REPO_ROOT = self.tmp
        g.CACHE_PATH = self.tmp / "gleif" / "checked.json"
        crm.COMPANIES_DIR.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        crm.COMPANIES_DIR, cq.CANDIDATES_DIR, cq.REPO_ROOT, g.CACHE_PATH = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_company(self, slug: str, **overrides) -> dict:
        rec = {
            "slug": slug,
            "name": overrides.pop("name", "Test Firm SA"),
            "legal_name": overrides.pop("legal_name", None),
            "country": overrides.pop("country", "France"),
            "city": overrides.pop("city", None),
            "segment": "asset_manager",
            "regulator": "AMF",
            "website": None,
            "linkedin": None,
            "size": {"aum": None, "employees": None, "portfolios": None},
            "description": None,
            "source": {"channel": "register", "detail": "test", "date": "2026-09-22"},
            "status": "nurture",
            "stage": "identified",
            "owner": crm.DEFAULT_OWNER,
            "tags": [],
            "created": "2026-09-22",
            "updated": "2026-09-22",
            "contacts": [],
            "fit": {"score": 50, "reasoning": "test", "disqualified_reason": None},
            "activities": [],
            "next_action": None,
        }
        rec.update(overrides)
        crm.save_yaml(crm.company_path(slug), rec)
        return rec


class TestNameCountryMatching(GleifHarness):
    def test_match_requires_name_and_country(self):
        # Same normalized name, but GLEIF's own record says a different country: must NOT match.
        wrong_country = lei_record("LEI000000000000000A", "TEST FIRM", "AE")
        with self._stub(lambda url: search_response([wrong_country])):
            rec, note = g.find_match("Test Firm SA", None, "FR")
        self.assertIsNone(rec)
        self.assertEqual(note, "no GLEIF record found")

    def test_match_on_name_and_country(self):
        hit = lei_record("LEI000000000000000B", "TEST FIRM", "FR")
        with self._stub(lambda url: search_response([hit])):
            rec, note = g.find_match("Test Firm SA", None, "FR")
        self.assertIsNotNone(rec)
        self.assertEqual(rec["attributes"]["lei"], "LEI000000000000000B")
        self.assertIn("name + country", note)

    def test_ambiguous_match_is_not_guessed(self):
        a = lei_record("LEI000000000000000C", "TEST FIRM", "FR")
        b = lei_record("LEI000000000000000D", "TEST FIRM", "FR")
        with self._stub(lambda url: search_response([a, b])):
            rec, note = g.find_match("Test Firm SA", None, "FR")
        self.assertIsNone(rec)
        self.assertIn("ambiguous", note)

    def test_other_names_count_as_a_match(self):
        hit = lei_record("LEI000000000000000E", "NEW LEGAL NAME SA", "FR",
                          other_names=["TEST FIRM"])
        with self._stub(lambda url: search_response([hit])):
            rec, note = g.find_match("Test Firm SA", None, "FR")
        self.assertIsNotNone(rec)

    def _stub(self, fn):
        return _patch(g, "_get_json", lambda url, allow_404=False: fn(url))


class TestNeverOverwrites(GleifHarness):
    def test_null_field_is_filled(self):
        rec = self.make_company("test-firm", name="Test Firm SA", city=None, legal_name=None)
        hit = lei_record("LEI000000000000000F", "TEST FIRM", "FR", city="Paris")
        gains, lei, form, parent = g.enrich_one(rec, hit)
        fields = dict(gains)
        self.assertEqual(fields.get("city"), "Paris")
        self.assertEqual(fields.get("legal_name"), "TEST FIRM")

    def test_existing_value_is_never_overwritten(self):
        rec = self.make_company("test-firm", name="Test Firm SA", city="Lyon",
                                 legal_name="Test Firm Legal Name SARL")
        hit = lei_record("LEI0000000000000010", "TEST FIRM", "FR", city="Paris")
        gains, lei, form, parent = g.enrich_one(rec, hit)
        self.assertEqual(gains, [])  # nothing offered, since both fields are already non-null

    def test_apply_enrichment_rechecks_disk_before_writing(self):
        """Belt-and-braces: even if the in-memory record looked null, the file on disk wins."""
        self.make_company("test-firm", name="Test Firm SA", city=None)
        # Simulate a concurrent edit that filled `city` after enrich_one() computed its gains.
        path = crm.company_path("test-firm")
        fresh = crm.load_yaml(path)
        fresh["city"] = "Marseille"
        crm.save_yaml(path, fresh)

        g._apply_enrichment(
            "test-firm", [("city", "Paris")], "LEI0000000000000011", "matched on name + country",
            None, None, dry_run=False,
        )
        saved = crm.load_yaml(path)
        self.assertEqual(saved["city"], "Marseille", "an existing value must never be overwritten")

    def test_dry_run_writes_nothing(self):
        self.make_company("test-firm", name="Test Firm SA", city=None)
        g._apply_enrichment(
            "test-firm", [("city", "Paris")], "LEI0000000000000012", "matched on name + country",
            None, None, dry_run=True,
        )
        saved = crm.load_yaml(crm.company_path("test-firm"))
        self.assertIsNone(saved["city"])
        self.assertEqual(saved["activities"], [])


class TestCandidatesNeverBecomeRecords(GleifHarness):
    def test_discovery_writes_only_to_candidate_queue(self):
        self.make_company("known-manager", name="Known Manager SA", country="France")

        fund = lei_record(
            "FUNDLEI0000000000001", "SOME FUND", "FR",
            relationships={"fund-manager": {"links": {"lei-record": "https://x/fund-manager"}}},
        )
        new_manager = lei_record("MGRLEI00000000000001", "Unknown Manager SA", "FR")

        def stub(url, allow_404=False):
            if url.endswith("fund-manager"):
                return {"data": new_manager}
            if "filter[entity.category]=FUND" in url:
                return search_response([fund])
            raise AssertionError(f"unexpected URL: {url}")

        with _patch(g, "_get_json", stub):
            rep = g.discover_fund_managers(dry_run=False, countries=["France"])

        self.assertEqual(rep["new"], 1)
        # No CRM record was created for the new manager — only a candidate line.
        self.assertFalse(crm.company_path("unknown-manager-sa").exists())
        self.assertEqual(len(crm.load_all_companies()), 1)  # still just "known-manager"

        candidates = list(cq.load_all())
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["name"], "Unknown Manager SA")
        self.assertIsNone(candidates[0]["matched_slug"])

    def test_manager_already_in_crm_is_not_proposed(self):
        self.make_company("known-manager", name="Known Manager SA", country="France")

        fund = lei_record(
            "FUNDLEI0000000000002", "SOME FUND", "FR",
            relationships={"fund-manager": {"links": {"lei-record": "https://x/fund-manager"}}},
        )
        existing_manager = lei_record("MGRLEI00000000000002", "KNOWN MANAGER SA", "FR")

        def stub(url, allow_404=False):
            if url.endswith("fund-manager"):
                return {"data": existing_manager}
            if "filter[entity.category]=FUND" in url:
                return search_response([fund])
            raise AssertionError(f"unexpected URL: {url}")

        with _patch(g, "_get_json", stub):
            rep = g.discover_fund_managers(dry_run=False, countries=["France"])

        self.assertEqual(rep["new"], 0)
        self.assertEqual(list(cq.load_all()), [])


class TestFailsLoudly(GleifHarness):
    def test_unreachable_api_raises_during_enrichment(self):
        self.make_company("test-firm", name="Test Firm SA")

        def stub(url, allow_404=False):
            raise ConnectorError("GLEIF unreachable: [Errno -2] Name or service not known (url)")

        with _patch(g, "_get_json", stub):
            with self.assertRaises(ConnectorError):
                g.run_enrichment()

    def test_unreachable_api_raises_during_discovery(self):
        def stub(url, allow_404=False):
            raise ConnectorError("GLEIF unreachable")

        with _patch(g, "_get_json", stub):
            with self.assertRaises(ConnectorError):
                g.discover_fund_managers(countries=["France"])

    def test_unexpected_shape_raises_not_silently_ignored(self):
        """A 200 with no 'data' key (a changed API contract) must not look like zero results."""
        import json as _json

        class FakeResp:
            status = 200

            def read(self):
                return _json.dumps({"unexpected": True}).encode()

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        with _patch(g, "urlopen", lambda *a, **k: FakeResp()):
            with _patch(g.time, "sleep", lambda *_: None):
                with self.assertRaises(ConnectorError) as ctx:
                    g._get_json("https://api.gleif.org/api/v1/lei-records")
        self.assertIn("unexpected shape", str(ctx.exception))


class _patch:
    """Minimal context-manager monkeypatch, so this file has no dependency beyond stdlib unittest."""

    def __init__(self, obj, attr, value):
        self.obj, self.attr, self.value = obj, attr, value

    def __enter__(self):
        self.old = getattr(self.obj, self.attr)
        setattr(self.obj, self.attr, self.value)
        return self.value

    def __exit__(self, *exc):
        setattr(self.obj, self.attr, self.old)
        return False


if __name__ == "__main__":
    unittest.main()
