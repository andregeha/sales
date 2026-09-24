#!/usr/bin/env python
"""Tests for `cma_uae.py` — run with `python tools/connectors/test_cma_uae.py`.

No network access is used: every test stubs `CMAUAEConnector._call`, the single seam every API call
(both the listing, integrationId 2045, and the per-company detail, integrationId 2055) passes
through. What matters most, in order:

1. The payload sent is the nested `urlParameters` shape the live API actually requires — a flat
   payload is rejected by the real API with `code:400`, so the shape is asserted directly.
2. The seven mapped categories -> our segments, exactly as measured live on 2026-09-23.
3. A firm holding more than one mapped category is ONE record, not several, with every category it
   holds kept in `licence_type` — and its segment follows the documented priority order.
4. A category returning zero firms is a broken query, not a quiet day, and raises.
5. A withdrawn/cancelled firm is excluded, the same contract `dfsa_difc.py` and `fsra_adgm.py` keep.
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

import base  # noqa: E402
from base import ConnectorError  # noqa: E402
from cma_uae import CATEGORIES, CMAUAEConnector  # noqa: E402


def row(code, name, status="Active", website="", year="2026"):
    return {"code": code, "name": name, "status": status, "website": website, "year": year}


class StubbedConnector(CMAUAEConnector):
    """A CMAUAEConnector whose `_call` is driven entirely from an in-memory script.

    `listing` maps a `type` id to the list of rows the live 2045 call would return for it.
    `details` maps a company code to the `CompanyDetails` dict the live 2055 call would return.
    Every call is recorded in `self.calls` so tests can assert on exactly what was sent.
    """

    def __init__(self, listing: dict[str, list[dict]], details: dict[str, dict] | None = None):
        super().__init__()
        self._listing = listing
        self._detail_script = details or {}
        self.calls: list[tuple[int, dict]] = []

    def _call(self, integration_id: int, params: dict) -> dict:
        self.calls.append((integration_id, dict(params)))
        if integration_id == 2045:
            items = self._listing.get(params.get("type"), [])
            return {"items": items}
        if integration_id == 2055:
            code = params.get("companyId")
            company = {"CompanyDetails": self._detail_script.get(code, {})}
            return {"company": company}
        raise AssertionError(f"unexpected integrationId in test: {integration_id}")


def full_listing(overrides: dict[str, list[dict]] | None = None) -> dict[str, list[dict]]:
    """One firm per mapped category by default — enough for the connector to run end to end."""
    listing = {cat_id: [row(f"CP-{cat_id}", f"Firm {cat_id}")] for cat_id in CATEGORIES}
    listing.update(overrides or {})
    return listing


# ---------------------------------------------------------------------------
# The request shape
# ---------------------------------------------------------------------------

class TestRequestShape(unittest.TestCase):
    def test_listing_payload_is_nested_under_urlparameters(self):
        c = StubbedConnector(full_listing())
        c.fetch()
        listing_calls = [p for iid, p in c.calls if iid == 2045]
        self.assertTrue(listing_calls)
        for params in listing_calls:
            # The real API returns `code:400 "Invalid Integration Parameters"` for anything else —
            # this is the one shape that is actually accepted, verified live on 2026-09-23.
            self.assertEqual(
                set(params.keys()),
                {"pageIndex", "pageSize", "type", "keyword", "languageId", "languageCode"},
            )
            self.assertEqual(params["languageCode"], "en")
            self.assertEqual(params["languageId"], 1)

    def test_every_mapped_category_is_queried(self):
        c = StubbedConnector(full_listing())
        c.fetch()
        queried_types = {p["type"] for iid, p in c.calls if iid == 2045}
        self.assertEqual(queried_types, set(CATEGORIES.keys()))

    def test_detail_lookup_sends_company_id(self):
        c = StubbedConnector(
            full_listing({"6": [row("CP-FUNDCO", "Fund Co")]}),
            details={"CP-FUNDCO": {"EstablishedDate": "13-Sep-2024"}},
        )
        entries = {e.key: e for e in c.fetch()}
        c.build_record(entries["CP-FUNDCO"], "snap.json")
        detail_calls = [p for iid, p in c.calls if iid == 2055]
        self.assertEqual(detail_calls, [{"companyId": "CP-FUNDCO", "languageId": 1, "languageCode": "en"}])


# ---------------------------------------------------------------------------
# Segment mapping
# ---------------------------------------------------------------------------

class TestSegmentMapping(unittest.TestCase):
    def test_each_category_maps_to_the_documented_segment(self):
        expected = {
            "6": "fund_manager", "7": "asset_manager", "45": "asset_manager",
            "21": "custodian", "1": "broker", "4": "broker", "2": "broker",
        }
        for cat_id, seg in expected.items():
            listing = {other: [] if other != cat_id else [row(f"CP-{cat_id}", "Solo Firm")]
                       for other in CATEGORIES}
            # every OTHER category must still return something, or fetch() raises
            for other in CATEGORIES:
                if other != cat_id:
                    listing[other] = [row(f"CP-{other}-filler", f"Filler {other}")]
            c = StubbedConnector(listing)
            entries = {e.key: e for e in c.fetch()}
            self.assertEqual(entries[f"CP-{cat_id}"].segment, seg, cat_id)

    def test_a_disqualified_category_is_never_queried(self):
        """Listing advisor, Promotion, virtual-asset categories etc. are excluded on purpose."""
        self.assertNotIn("18", CATEGORIES)   # Listing advisor
        self.assertNotIn("20", CATEGORIES)   # Promotion
        self.assertNotIn("19", CATEGORIES)   # Introduction
        self.assertNotIn("59", CATEGORIES)   # Dealing in Virtual Assets
        # ⚠ Commodity brokerage, all three variants. A DECISION, not an omission: our other brokers
        # trade securities and currencies — instruments a multi-asset portfolio holds — while a
        # commodity broker clearing physical trades is an execution business. Mapping it would widen
        # `broker` until the segment stopped meaning anything.
        for cid in ("22", "23", "24"):
            self.assertNotIn(cid, CATEGORIES)

    def test_custody_and_otc_broking_are_mapped(self):
        """⚠ This REVERSES the connector's original decision, and the reversal is the point.

        Custody (9) and OTC-derivatives/spot broking (3) were first left unmapped. An audit of all 52
        unmapped categories showed that was not a scope judgement but an inconsistency: we map
        custody in DIFC, and three other broker categories in this very register. Excluding these
        made our coverage depend on which category a regulator happened to file a firm under.
        """
        self.assertEqual(CATEGORIES["9"][1], "custodian")
        self.assertEqual(CATEGORIES["3"][1], "broker")


# ---------------------------------------------------------------------------
# Dedupe across categories
# ---------------------------------------------------------------------------

class TestDedupe(unittest.TestCase):
    def test_a_firm_in_two_categories_is_one_entry_with_both_kept(self):
        listing = full_listing({
            "6": [row("CP-DUAL", "Dual Licensed Co")],
            "7": [row("CP-DUAL", "Dual Licensed Co")],
        })
        c = StubbedConnector(listing)
        entries = {e.key: e for e in c.fetch()}
        # 7 categories, 2 of them collapsed onto the same firm -> 6 unique entries.
        self.assertEqual(len(entries), len(CATEGORIES) - 1)
        dual = entries["CP-DUAL"]
        self.assertIn("Investment Fund Management", dual.licence_type)
        self.assertIn("Portfolios management", dual.licence_type)

    def test_segment_follows_the_documented_priority_order(self):
        """Fund management (type 6) outranks portfolio management (type 7) when a firm holds both."""
        listing = full_listing({
            "6": [row("CP-DUAL", "Dual Licensed Co")],
            "7": [row("CP-DUAL", "Dual Licensed Co")],
        })
        c = StubbedConnector(listing)
        entries = {e.key: e for e in c.fetch()}
        self.assertEqual(entries["CP-DUAL"].segment, "fund_manager")

    def test_third_party_flag_only_for_managing_segments(self):
        listing = full_listing({"1": [row("CP-BROKER", "Broker Co")]})
        c = StubbedConnector(listing)
        entries = {e.key: e for e in c.fetch()}
        self.assertIsNone(entries["CP-BROKER"].third_party)
        self.assertTrue(entries["CP-6"].third_party)  # type 6, fund_manager


# ---------------------------------------------------------------------------
# Failure contract
# ---------------------------------------------------------------------------

class TestFailsLoudly(unittest.TestCase):
    def test_a_mapped_category_returning_zero_firms_raises(self):
        listing = full_listing({"7": []})
        c = StubbedConnector(listing)
        with self.assertRaises(ConnectorError) as ctx:
            c.fetch()
        self.assertIn("Portfolios management", str(ctx.exception))

    def test_every_category_empty_still_raises_and_names_the_first(self):
        listing = {cat_id: [] for cat_id in CATEGORIES}
        c = StubbedConnector(listing)
        with self.assertRaises(ConnectorError):
            c.fetch()

    def test_withdrawn_firm_is_excluded(self):
        listing = full_listing({"6": [row("CP-GONE", "Former Licensee", status="Withdrawn")]})
        c = StubbedConnector(listing)
        entries = {e.key: e for e in c.fetch()}
        self.assertNotIn("CP-GONE", entries)

    def test_a_failed_detail_lookup_does_not_raise_and_leaves_fields_unset(self):
        class Boom(StubbedConnector):
            def _call(self, integration_id, params):
                if integration_id == 2055:
                    raise ConnectorError("simulated detail outage")
                return super()._call(integration_id, params)

        c = Boom(full_listing({"6": [row("CP-FUNDCO", "Fund Co")]}))
        entries = {e.key: e for e in c.fetch()}
        rec = c.build_record(entries["CP-FUNDCO"], "snap.json")
        self.assertEqual(rec["contacts"], [])
        self.assertIsNone(entries["CP-FUNDCO"].licence_date)


# ---------------------------------------------------------------------------
# Detail enrichment and the record it produces
# ---------------------------------------------------------------------------

class TestDetailEnrichment(unittest.TestCase):
    def test_established_date_phone_and_email_are_applied(self):
        c = StubbedConnector(
            full_listing({"6": [row("CP-FUNDCO", "Fund Co", website="fundco.ae")]}),
            details={"CP-FUNDCO": {
                "EstablishedDate": "13-Sep-2024",
                "Telephone": "971-48180501",
                "City": "Dubai",
                "Email": "compliance@fundco.ae",
                "CompanyAddress": "Office 1, Business Bay, Dubai, UAE",
            }},
        )
        entries = {e.key: e for e in c.fetch()}
        rec = c.build_record(entries["CP-FUNDCO"], "snap.json")
        self.assertEqual(rec["website"], "https://fundco.ae")
        self.assertEqual(len(rec["contacts"]), 1)
        contact = rec["contacts"][0]
        self.assertEqual(contact["email"], "compliance@fundco.ae")
        self.assertEqual(contact["phone"], "971-48180501")
        self.assertIn("Business Bay", rec["activities"][0]["summary"])
        self.assertIn("Capital Market Authority (UAE)", rec["activities"][0]["summary"])

    def test_established_date_parses_dd_mmm_yyyy(self):
        self.assertEqual(CMAUAEConnector._iso("13-Sep-2024"), "2024-09-13")
        self.assertEqual(CMAUAEConnector._iso("2-Jul-1988"), "1988-07-02")
        self.assertIsNone(CMAUAEConnector._iso("not a date"))

    def test_website_gets_a_scheme_but_not_a_guess(self):
        self.assertEqual(CMAUAEConnector._clean_website("fundco.ae"), "https://fundco.ae")
        self.assertEqual(CMAUAEConnector._clean_website("https://x.ae"), "https://x.ae")
        self.assertIsNone(CMAUAEConnector._clean_website(""))
        self.assertIsNone(CMAUAEConnector._clean_website(None))


# ---------------------------------------------------------------------------
# End to end against the CRM's own schema — the same discipline test_connectors.py holds
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

    def test_backfill_creates_valid_records_for_every_mapped_firm(self):
        c = StubbedConnector(
            full_listing({"6": [row("CP-FUNDCO", "Fund Co", website="fundco.ae")]}),
            details={"CP-FUNDCO": {"EstablishedDate": "13-Sep-2024", "Telephone": "971-1", "City": "Dubai"}},
        )
        res = c.run(dry_run=False, backfill=True)
        self.assertEqual(res["total"], len(CATEGORIES))
        files = sorted(base.crm.COMPANIES_DIR.glob("*.yaml"))
        self.assertEqual(len(files), len(CATEGORIES))
        errors: list[str] = []
        for f in files:
            rec = base.crm.load_yaml(f)
            base.crm.validate_company(f, rec, errors, set())
            self.assertEqual(rec["regulator"], "Capital Market Authority (UAE)")
            self.assertEqual(rec["country"], "UAE")
        self.assertEqual(errors, [])

    def test_a_registered_firm_never_needs_a_second_record(self):
        c = StubbedConnector(full_listing({"6": [row("CP-FUNDCO", "Fund Co")]}))
        c.run(dry_run=False, backfill=True)
        c2 = StubbedConnector(full_listing({"6": [row("CP-FUNDCO", "Fund Co")]}))
        res2 = c2.run(dry_run=False, backfill=True)
        skipped_names = [s["name"] for s in res2["skipped"]]
        self.assertIn("Fund Co", skipped_names)


if __name__ == "__main__":
    unittest.main(verbosity=2)
