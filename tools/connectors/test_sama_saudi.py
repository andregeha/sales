#!/usr/bin/env python
"""Tests for `sama_saudi.py` — run with `python tools/connectors/test_sama_saudi.py`.

No network access is used: `sama_saudi.http_get` is monkeypatched to return a canned JSON payload
shaped exactly like the live API's response (field names and the `Created` date format were read
from a live call on 2026-09-24 — see the module docstring). What matters most, in order:

1. The banks list is parsed correctly: name, key, website, category all land where they should.
2. Every entry maps to `segment: bank` — this register has no other population.
3. `Created` (a CMS record-creation date) is NEVER used as `licence_date`, even though it is present
   on every row and looks superficially date-shaped.
4. The finance/finance-support companies list (91 firms) is never fetched at all — only one HTTP call
   is made, and it is for the banks list.
5. Zero rows from a live call is a bug, not a quiet day, and raises.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import base  # noqa: E402
from base import ConnectorError  # noqa: E402
from sama_saudi import BANKS_LIST_URL, SAMASaudiConnector  # noqa: E402


def row(item_id, name_en, name_ar="اسم عربي", category_en="Local Banks",
       activity_en="Banking Business", url_en="https://example.sa/", url_ar="https://example.sa/ar",
       licensing_number="1010000000", unified_number="7000000000", created="24/02/2022"):
    """One row exactly shaped like the live SAMA `LoadItems` API response."""
    return {
        "ID": item_id,
        "Title": name_ar,
        "TitleEn": name_en,
        "UrlLinkAr": url_ar,
        "UrlLinkEn": url_en,
        "ActivityType": "مزاولة أعمال مصرفية",
        "ActivityType_x003a_TitleEn": activity_en,
        "Categories": "الفئة",
        "Categories_x003a_TitleEn": category_en,
        "LicensingNumber": licensing_number,
        "UnifiedNumber": unified_number,
        "Created": created,
    }


def fake_http_get(payload):
    """A drop-in for `base.http_get` that ignores its arguments and returns `payload` as JSON bytes."""
    def _get(url, timeout=60, accept=None):
        return json.dumps(payload).encode("utf-8")
    return _get


# ---------------------------------------------------------------------------
# Parsing and mapping
# ---------------------------------------------------------------------------

class TestParsing(unittest.TestCase):
    def test_fields_land_where_they_should(self):
        rows = [row(37, "Saudi National Bank (SNB)", name_ar="البنك الأهلي السعودي",
                    category_en="Local Banks", url_en="https://www.alahli.com/en",
                    licensing_number="4030001588", unified_number="7000025887")]
        with patch("sama_saudi.http_get", fake_http_get(rows)):
            entries = SAMASaudiConnector().fetch()
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e.key, "37")
        self.assertEqual(e.name, "Saudi National Bank (SNB)")
        self.assertEqual(e.legal_name, "البنك الأهلي السعودي")
        self.assertEqual(e.website, "https://www.alahli.com/en")
        self.assertEqual(e.licence_type, "Local Banks")
        self.assertEqual(e.raw["licensing_number"], "4030001588")
        self.assertEqual(e.raw["unified_number"], "7000025887")

    def test_website_without_a_scheme_gets_one(self):
        rows = [row(1, "Bank Without Scheme", url_en="www.example.sa")]
        with patch("sama_saudi.http_get", fake_http_get(rows)):
            entries = SAMASaudiConnector().fetch()
        self.assertEqual(entries[0].website, "https://www.example.sa")

    def test_missing_website_is_none_not_guessed(self):
        rows = [row(1, "Bank Without A Website", url_en="")]
        with patch("sama_saudi.http_get", fake_http_get(rows)):
            entries = SAMASaudiConnector().fetch()
        self.assertIsNone(entries[0].website)

    def test_row_with_no_english_name_is_skipped_not_crashed_on(self):
        rows = [row(1, ""), row(2, "Real Bank")]
        with patch("sama_saudi.http_get", fake_http_get(rows)):
            entries = SAMASaudiConnector().fetch()
        self.assertEqual([e.name for e in entries], ["Real Bank"])


# ---------------------------------------------------------------------------
# Segment mapping
# ---------------------------------------------------------------------------

class TestSegmentMapping(unittest.TestCase):
    def test_every_row_maps_to_bank(self):
        rows = [
            row(1, "A Local Bank", category_en="Local Banks"),
            row(2, "A Foreign Branch", category_en="Foreign Bank Branches"),
            row(3, "A Digital Bank", category_en="Digital Banks"),
        ]
        with patch("sama_saudi.http_get", fake_http_get(rows)):
            entries = SAMASaudiConnector().fetch()
        self.assertTrue(all(e.segment == "bank" for e in entries))
        self.assertEqual(len(entries), 3)


# ---------------------------------------------------------------------------
# `Created` is never a licence date
# ---------------------------------------------------------------------------

class TestCreatedIsNeverALicenceDate(unittest.TestCase):
    def test_created_date_is_not_mapped_to_licence_date(self):
        rows = [row(1, "A Bank", created="24/02/2022")]
        with patch("sama_saudi.http_get", fake_http_get(rows)):
            entries = SAMASaudiConnector().fetch()
        self.assertIsNone(entries[0].licence_date)
        # It is still kept, but clearly labelled as a CMS date, not lost.
        self.assertEqual(entries[0].raw["created_cms_date_ddmmyyyy"], "24/02/2022")

    def test_a_bank_never_scores_a_licence_trigger_from_created(self):
        rows = [row(1, "A Very Recently Created Row", created="24/02/2022")]
        with patch("sama_saudi.http_get", fake_http_get(rows)):
            entries = SAMASaudiConnector().fetch()
        c = SAMASaudiConnector()
        points, why = c._trigger_points(entries[0])
        self.assertEqual(points, 0)
        self.assertIn("no licence date published", why)


# ---------------------------------------------------------------------------
# Finance companies are never fetched
# ---------------------------------------------------------------------------

class TestFinanceCompaniesExcluded(unittest.TestCase):
    def test_only_one_http_call_is_made_and_it_is_the_banks_list(self):
        calls = []

        def spy(url, timeout=60, accept=None):
            calls.append(url)
            return json.dumps([row(1, "A Bank")]).encode("utf-8")

        with patch("sama_saudi.http_get", spy):
            SAMASaudiConnector().fetch()
        self.assertEqual(len(calls), 1, "the finance/finance-support list must never be fetched")
        self.assertIn(BANKS_LIST_URL, calls[0])
        self.assertNotIn("LicensedFinance", calls[0])


# ---------------------------------------------------------------------------
# Failure contract
# ---------------------------------------------------------------------------

class TestFailsLoudly(unittest.TestCase):
    def test_empty_list_raises(self):
        with patch("sama_saudi.http_get", fake_http_get([])):
            with self.assertRaises(ConnectorError) as ctx:
                SAMASaudiConnector().fetch()
        self.assertIn("no bank entries", str(ctx.exception))

    def test_non_list_json_raises(self):
        def bad_get(url, timeout=60, accept=None):
            return json.dumps({"not": "a list"}).encode("utf-8")

        with patch("sama_saudi.http_get", bad_get):
            with self.assertRaises(ConnectorError):
                SAMASaudiConnector().fetch()

    def test_unparseable_json_raises(self):
        def bad_get(url, timeout=60, accept=None):
            return b"not json at all"

        with patch("sama_saudi.http_get", bad_get):
            with self.assertRaises(ConnectorError) as ctx:
                SAMASaudiConnector().fetch()
        self.assertIn("did not return parseable JSON", str(ctx.exception))

    def test_rows_with_no_usable_name_at_all_raises(self):
        rows = [row(1, ""), row(2, "  ")]
        with patch("sama_saudi.http_get", fake_http_get(rows)):
            with self.assertRaises(ConnectorError) as ctx:
                SAMASaudiConnector().fetch()
        self.assertIn("none carried a usable name", str(ctx.exception))


# ---------------------------------------------------------------------------
# End to end against the CRM's own schema
# ---------------------------------------------------------------------------

class TestEndToEnd(unittest.TestCase):
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

    def test_backfill_creates_valid_records_for_every_bank(self):
        rows = [row(1, "Bank One"), row(2, "Bank Two"), row(3, "Bank Three")]
        with patch("sama_saudi.http_get", fake_http_get(rows)):
            res = SAMASaudiConnector().run(dry_run=False, backfill=True)
        self.assertEqual(res["total"], 3)
        files = sorted(base.crm.COMPANIES_DIR.glob("*.yaml"))
        self.assertEqual(len(files), 3)
        errors: list[str] = []
        for f in files:
            rec = base.crm.load_yaml(f)
            base.crm.validate_company(f, rec, errors, set())
            self.assertEqual(rec["segment"], "bank")
            self.assertEqual(rec["regulator"], "SAMA (Saudi Central Bank)")
            # No licence date is published, so no baseline/backfill run should ever be a "trigger".
            self.assertEqual(rec["status"], "nurture")
        self.assertEqual(errors, [])

    def test_a_registered_bank_never_needs_a_second_record(self):
        rows = [row(1, "Bank One")]
        with patch("sama_saudi.http_get", fake_http_get(rows)):
            SAMASaudiConnector().run(dry_run=False, backfill=True)
            res2 = SAMASaudiConnector().run(dry_run=False, backfill=True)
        self.assertIn("Bank One", [s["name"] for s in res2["skipped"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
