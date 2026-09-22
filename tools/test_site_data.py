#!/usr/bin/env python
"""Tests for `site_data.py` — run with `python tools/test_site_data.py`.

Two things matter more than any other: (1) the JSON contract has the shape the website plan
promises (`plan/website.md` §6b/§7), and (2) it is byte-for-byte deterministic, because a
non-deterministic build is a broken promise (R2) that would only be discovered by someone staring
at an unexplained `git diff`. No network access is used; the real CRM is read but never written.
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
sys.path.insert(0, str(HERE / "connectors"))

import site_data  # noqa: E402
import base as connectors_base  # noqa: E402


def _tree_bytes(root: Path) -> dict[str, bytes]:
    """Every file under root, keyed by its path relative to root, for a byte-exact comparison."""
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root)).replace("\\", "/")] = p.read_bytes()
    return out


class SiteDataHarness(unittest.TestCase):
    """Points site_data at a throwaway CRM/runs/events tree so tests never touch real data,
    and never depend on however large the real CRM happens to be that day."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._orig = (
            site_data.crm.COMPANIES_DIR, site_data.crm.RFPS_DIR,
            site_data.RUNS_DIR, site_data.EVENTS_DIR, site_data.REGISTERS_DIR,
            site_data.QUESTIONS_FILE,
        )
        site_data.crm.COMPANIES_DIR = self.tmp / "companies"
        site_data.crm.RFPS_DIR = self.tmp / "rfps"
        site_data.RUNS_DIR = self.tmp / "runs"
        site_data.EVENTS_DIR = self.tmp / "events"
        site_data.REGISTERS_DIR = self.tmp / "registers"
        site_data.QUESTIONS_FILE = self.tmp / "open-questions.md"
        for d in (site_data.crm.COMPANIES_DIR, site_data.crm.RFPS_DIR, site_data.RUNS_DIR,
                 site_data.EVENTS_DIR, site_data.REGISTERS_DIR):
            d.mkdir(parents=True, exist_ok=True)
        self.out = self.tmp / "out"

    def tearDown(self):
        (site_data.crm.COMPANIES_DIR, site_data.crm.RFPS_DIR,
         site_data.RUNS_DIR, site_data.EVENTS_DIR, site_data.REGISTERS_DIR,
         site_data.QUESTIONS_FILE) = self._orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def seed_company(self, slug: str, **overrides) -> dict:
        rec = {
            "slug": slug, "name": overrides.pop("name", slug.replace("-", " ").title()),
            "legal_name": None, "country": "France", "city": None, "segment": "asset_manager",
            "regulator": "AMF", "website": None, "linkedin": None,
            "size": {"aum": None, "employees": None, "portfolios": None}, "description": None,
            "source": {"channel": "register", "detail": "test", "date": "2026-09-22"},
            "status": "nurture", "stage": "identified", "owner": "Andre Geha", "tags": [],
            "created": "2026-09-22", "updated": "2026-09-22", "contacts": [],
            "fit": {"score": 50, "reasoning": "test", "disqualified_reason": None},
            "activities": [], "next_action": None,
        }
        rec.update(overrides)
        site_data.crm.save_yaml(site_data.crm.COMPANIES_DIR / f"{slug}.yaml", rec)
        return rec


class TestCompanyIndexShape(SiteDataHarness):
    def test_index_row_has_the_documented_fields(self):
        self.seed_company("alpha-gestion", website="https://alpha.example",
                          contacts=[{"name": "A B", "role": "champion", "email": "a@example.com",
                                     "phone": "+33 1 23", "linkedin": "https://linkedin.example/a",
                                     "language": "en",
                                     "title": None, "notes": None, "source": None}],
                          status="qualified",
                          fit={"score": 74, "reasoning": "Trigger 20/25: new licence granted. more.",
                               "disqualified_reason": None})
        summary = site_data.build(self.out)
        self.assertEqual(summary["companies"], 1)
        index = json.loads((self.out / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(len(index), 1)
        row = index[0]
        expected_keys = {
            "slug", "name", "country", "city", "segment", "status", "stage", "regulator",
            "website", "score", "has_contact_route", "has_email", "has_phone", "has_linkedin",
            "trigger", "created", "updated", "tags",
        }
        self.assertEqual(set(row.keys()), expected_keys)
        self.assertEqual(row["slug"], "alpha-gestion")
        self.assertEqual(row["score"], 74)
        self.assertTrue(row["has_contact_route"])
        self.assertTrue(row["has_email"])
        self.assertTrue(row["has_phone"])
        self.assertTrue(row["has_linkedin"])
        self.assertEqual(row["trigger"], "new licence granted")

    def test_company_with_no_contacts_has_no_route_and_no_trigger(self):
        self.seed_company("bare-gestion", status="nurture")
        site_data.build(self.out)
        index = json.loads((self.out / "index.json").read_text(encoding="utf-8"))
        self.assertFalse(index[0]["has_contact_route"])
        self.assertFalse(index[0]["has_email"])
        self.assertFalse(index[0]["has_phone"])
        self.assertFalse(index[0]["has_linkedin"])
        self.assertIsNone(index[0]["trigger"])

    def test_full_record_is_written_per_slug_and_matches_the_yaml(self):
        self.seed_company("gamma-gestion", city="Paris")
        site_data.build(self.out)
        full = json.loads((self.out / "companies" / "gamma-gestion.json").read_text(encoding="utf-8"))
        self.assertEqual(full["slug"], "gamma-gestion")
        self.assertEqual(full["city"], "Paris")
        self.assertNotIn("_path", full, "the loader's bookkeeping key must never leak into the contract")

    def test_full_record_carries_the_same_derived_fields_as_the_index_row(self):
        """The site's `Company` type extends `CompanyIndexRow` — the detail page must not lose the
        route/score/trigger fields it inherited, or it renders them as false/null by default."""
        self.seed_company("delta-gestion",
                          contacts=[{"name": "A", "role": "champion", "email": "a@example.com",
                                     "phone": None, "linkedin": None, "language": "en",
                                     "title": None, "notes": None, "source": None}])
        site_data.build(self.out)
        full = json.loads((self.out / "companies" / "delta-gestion.json").read_text(encoding="utf-8"))
        self.assertTrue(full["has_contact_route"])
        self.assertTrue(full["has_email"])
        self.assertIn("score", full)
        self.assertIn("fit", full, "the raw fit object must still be present alongside the top-level score")

    def test_index_sorted_by_slug_regardless_of_filesystem_order(self):
        for slug in ("zeta", "alpha", "mu"):
            self.seed_company(slug)
        site_data.build(self.out)
        index = json.loads((self.out / "index.json").read_text(encoding="utf-8"))
        self.assertEqual([r["slug"] for r in index], ["alpha", "mu", "zeta"])


class TestExampleRecordsExcluded(SiteDataHarness):
    """`EXAMPLE-*` records (`crm/SCHEMA.md`'s worked examples) are fictional and must never render
    on the site as if they were real pipeline — the point that motivated `_is_example`."""

    def test_example_company_and_rfp_are_excluded_from_every_output(self):
        self.seed_company("EXAMPLE-oasis-family-office", status="disqualified",
                          fit={"score": 0, "reasoning": "x", "disqualified_reason": "schema example"})
        self.seed_company("real-gestion")
        site_data.crm.save_yaml(site_data.crm.RFPS_DIR / "EXAMPLE-some-rfp.yaml", {
            "slug": "EXAMPLE-some-rfp", "title": "Example RFP", "issuer": "x", "country": "France",
            "segment": "asset_manager", "source_url": None, "published_date": "2026-09-01",
            "deadline": "2026-10-15", "status": "skipped", "fit_assessment": "x",
            "decision": {"outcome": "no_bid", "reason": "example"}, "documents": [],
            "owner": "Andre Geha", "created": "2026-09-22", "updated": "2026-09-22",
        })
        summary = site_data.build(self.out)
        self.assertEqual(summary["companies"], 1)
        self.assertEqual(summary["rfps"], 0)
        index = json.loads((self.out / "index.json").read_text(encoding="utf-8"))
        self.assertEqual([r["slug"] for r in index], ["real-gestion"])
        self.assertFalse((self.out / "companies" / "EXAMPLE-oasis-family-office.json").exists())
        self.assertEqual(json.loads((self.out / "rfps.json").read_text(encoding="utf-8")), [])


class TestBuildManifest(SiteDataHarness):
    def test_build_json_is_the_only_place_with_build_specific_facts(self):
        self.seed_company("alpha")
        site_data.build(self.out)
        manifest = json.loads((self.out / "build.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest.keys()), {"schema_version", "commit", "company_count"})
        self.assertEqual(manifest["company_count"], 1)
        self.assertTrue(manifest["commit"] is None or len(manifest["commit"]) == 40)


class TestDeterminism(SiteDataHarness):
    """R2 (`plan/website.md` §2, enforced in §7): same data in, same site out, byte for byte."""

    def test_double_build_is_byte_identical(self):
        for i in range(5):
            self.seed_company(f"firm-{i}", segment="fund_manager" if i % 2 else "asset_manager",
                              fit={"score": 40 + i, "reasoning": "x", "disqualified_reason": None})
        site_data.crm.save_yaml(site_data.crm.RFPS_DIR / "some-rfp.yaml", {
            "slug": "some-rfp", "title": "Test RFP", "issuer": "Firm 0", "country": "France",
            "segment": "asset_manager", "source_url": "https://example.invalid",
            "published_date": "2026-09-01", "deadline": "2026-12-01", "status": "spotted",
            "fit_assessment": "x", "decision": {"outcome": "pending", "reason": None},
            "documents": [], "owner": "Andre Geha", "created": "2026-09-22", "updated": "2026-09-22",
        })
        run_record = {
            "started_at": "2026-09-22T06:00:00+00:00", "finished_at": "2026-09-22T06:00:12+00:00",
            "duration_s": 12.0, "commit": "a" * 40, "ok": True,
            "connectors": [{"register": "amf-france", "source": "AMF", "ok": True, "error": None,
                            "total": 5, "new_on_register": 1, "created": 1, "skipped": 0,
                            "changes": 0, "baseline": False, "backfill": False, "partial": False}],
        }
        (site_data.RUNS_DIR / "2026-09-22-060000.json").write_text(
            json.dumps(run_record, sort_keys=True), encoding="utf-8")
        (site_data.EVENTS_DIR / "2026-09.jsonl").write_text(
            json.dumps({"date": "2026-09-22", "register": "amf-france", "company_slug": "firm-0",
                       "company_name": "Firm 0", "field": "licence_type", "label": "x",
                       "before": "a", "after": "b", "is_trigger": True, "woke": True},
                      sort_keys=True) + "\n",
            encoding="utf-8")

        out1, out2 = self.tmp / "out1", self.tmp / "out2"
        site_data.build(out1)
        site_data.build(out2)

        tree1, tree2 = _tree_bytes(out1), _tree_bytes(out2)
        self.assertEqual(set(tree1.keys()), set(tree2.keys()))
        for name in tree1:
            self.assertEqual(tree1[name], tree2[name], f"{name} differs between two identical builds")

    def test_all_json_files_have_sorted_keys(self):
        self.seed_company("alpha")
        site_data.build(self.out)
        for p in self.out.rglob("*.json"):
            raw = p.read_text(encoding="utf-8")
            data = json.loads(raw)
            resorted = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
            self.assertEqual(raw, resorted, f"{p} is not written with sort_keys=True")


class TestQuestionsParsing(SiteDataHarness):
    SAMPLE = """# Open questions

## \U0001F51D The four to answer first (2026-09-22)
| # | Question | Why it matters | Status |
|---|---|---|---|
| 1 | **First question?** With detail. | Because reasons. | \U0001F7E0 |
| 2 | Second question, no bold. | Other reason. | ⚪ |

## For Andre — still open
| # | Question | Status |
|---|---|---|
| 5 | Simple question | \U0001F7E0 |
| 5a | Lettered id question | \U0001F7E0 |

## ✅ Answered by Andre 2026-09-22
1. **Scope** → resolved, not a table row.
"""

    def test_parses_rows_from_every_table(self):
        rows, warnings = site_data.parse_open_questions(self.SAMPLE)
        self.assertEqual(warnings, [])
        self.assertEqual(len(rows), 4)
        ids = [r["id"] for r in rows]
        self.assertEqual(ids, ["1", "2", "5", "5a"], "rows must sort numerically, not lexically")

    def test_bold_markers_are_stripped_and_unblocks_column_is_captured(self):
        rows, _ = site_data.parse_open_questions(self.SAMPLE)
        first = rows[0]
        self.assertEqual(first["question"], "First question? With detail.")
        self.assertNotIn("**", first["question"])
        self.assertEqual(first["unblocks"], "Because reasons.")
        self.assertEqual(first["status"], "\U0001F7E0")
        self.assertEqual(first["priority"], "soon")
        self.assertEqual(first["section"], "\U0001F51D The four to answer first (2026-09-22)")

    def test_table_without_a_why_column_leaves_unblocks_null(self):
        rows, _ = site_data.parse_open_questions(self.SAMPLE)
        simple = next(r for r in rows if r["id"] == "5")
        self.assertIsNone(simple["unblocks"])

    def test_priority_derives_from_the_files_own_emoji_legend(self):
        rows, _ = site_data.parse_open_questions(
            "## S\n| # | Question | Status |\n|---|---|---|\n"
            "| 1 | Blocking one | \U0001F534 |\n"
            "| 2 | Soon one | \U0001F7E0 |\n"
            "| 3 | Nice one | ⚪ |\n"
        )
        by_id = {r["id"]: r["priority"] for r in rows}
        self.assertEqual(by_id, {"1": "blocking", "2": "soon", "3": "nice"})

    def test_narrative_sections_produce_no_rows_and_no_warnings(self):
        """'Answered'/'Resolved' prose is not a table — it must be skipped cleanly, not guessed at."""
        rows, warnings = site_data.parse_open_questions(self.SAMPLE)
        self.assertTrue(all(r["section"] != "✅ Answered by Andre 2026-09-22" for r in rows))

    def test_build_writes_questions_json_from_the_real_file_shape(self):
        site_data.QUESTIONS_FILE.write_text(self.SAMPLE, encoding="utf-8")
        self.seed_company("alpha")
        site_data.build(self.out)
        rows = json.loads((self.out / "questions.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 4)

    def test_missing_questions_file_reports_a_warning_rather_than_crashing(self):
        site_data.QUESTIONS_FILE.unlink(missing_ok=True)
        self.seed_company("alpha")
        summary = site_data.build(self.out)
        self.assertTrue(summary["questions_warnings"])
        self.assertEqual(json.loads((self.out / "questions.json").read_text(encoding="utf-8")), [])


class TestSourceHealth(SiteDataHarness):
    def _run(self, day: str, register: str, ok: bool, total: int = 10):
        c = {"register": register, "source": register, "ok": ok, "error": None if ok else "boom",
             "total": total if ok else None, "new_on_register": 0 if ok else None,
             "created": 0, "skipped": 0, "changes": 0, "baseline": False, "backfill": False,
             "partial": False}
        if not ok:
            for k in ("total", "new_on_register", "created", "skipped", "changes",
                     "baseline", "backfill", "partial"):
                c[k] = None
        record = {"started_at": f"{day}T06:00:00+00:00", "finished_at": f"{day}T06:00:10+00:00",
                 "duration_s": 10.0, "commit": None, "ok": ok, "connectors": [c]}
        (site_data.RUNS_DIR / f"{day}-060000.json").write_text(
            json.dumps(record, sort_keys=True), encoding="utf-8")

    def test_register_marked_ok_after_a_clean_run(self):
        self._run("2026-09-20", "amf-france", ok=True)
        health = site_data.compute_source_health(site_data.load_runs())
        row = next(r for r in health if r["register"] == "amf-france")
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["consecutive_failures"], 0)
        self.assertEqual(row["latest_count"], 10)
        self.assertEqual(row["last_success_date"], "2026-09-20")

    def test_register_marked_failing_after_three_consecutive_failures(self):
        self._run("2026-09-18", "cma-saudi", ok=True, total=36)
        self._run("2026-09-19", "cma-saudi", ok=False)
        self._run("2026-09-20", "cma-saudi", ok=False)
        self._run("2026-09-21", "cma-saudi", ok=False)
        health = site_data.compute_source_health(site_data.load_runs())
        row = next(r for r in health if r["register"] == "cma-saudi")
        self.assertEqual(row["consecutive_failures"], 3)
        self.assertEqual(row["status"], "failing")
        self.assertEqual(row["last_success_date"], "2026-09-18",
                         "the last real success must still be remembered through the failures")
        self.assertEqual(row["latest_count"], 36,
                         "count should hold at the last known-good figure, not vanish")
        self.assertEqual(row["note"], "boom", "the most recent error should surface as the note")

    def test_one_failure_alone_is_stale_not_failing(self):
        self._run("2026-09-20", "dfsa-difc", ok=True)
        self._run("2026-09-21", "dfsa-difc", ok=False)
        health = site_data.compute_source_health(site_data.load_runs())
        row = next(r for r in health if r["register"] == "dfsa-difc")
        self.assertEqual(row["status"], "stale")

    def test_a_run_with_only_flag_does_not_count_as_success_or_failure_for_other_registers(self):
        self._run("2026-09-18", "fsra-adgm", ok=False)
        self._run("2026-09-19", "fsra-adgm", ok=False)
        self._run("2026-09-20", "fsra-adgm", ok=False)
        # A later run that only touched a DIFFERENT register must not reset or hide the streak.
        self._run("2026-09-21", "amf-france", ok=True)
        health = site_data.compute_source_health(site_data.load_runs())
        row = next(r for r in health if r["register"] == "fsra-adgm")
        self.assertEqual(row["consecutive_failures"], 3)
        self.assertEqual(row["status"], "failing")


class TestRunsAndEvents(SiteDataHarness):
    def test_runs_json_carries_every_run_record(self):
        (site_data.RUNS_DIR / "2026-09-20-060000.json").write_text(
            json.dumps({"started_at": "2026-09-20T06:00:00+00:00", "ok": True, "connectors": []}),
            encoding="utf-8")
        self.seed_company("alpha")
        site_data.build(self.out)
        runs = json.loads((self.out / "runs.json").read_text(encoding="utf-8"))
        self.assertEqual(len(runs), 1)
        self.assertTrue(runs[0]["ok"])

    def test_events_json_carries_every_line_from_every_month(self):
        (site_data.EVENTS_DIR / "2026-08.jsonl").write_text(
            json.dumps({"date": "2026-08-15", "register": "r", "company_slug": None,
                       "company_name": "X", "field": "f", "label": "l", "before": None,
                       "after": "v", "is_trigger": False, "woke": False}) + "\n",
            encoding="utf-8")
        (site_data.EVENTS_DIR / "2026-09.jsonl").write_text(
            json.dumps({"date": "2026-09-01", "register": "r", "company_slug": "alpha",
                       "company_name": "Alpha", "field": "f", "label": "l", "before": "a",
                       "after": "b", "is_trigger": True, "woke": True}) + "\n",
            encoding="utf-8")
        self.seed_company("alpha")
        site_data.build(self.out)
        events = json.loads((self.out / "events.json").read_text(encoding="utf-8"))
        self.assertEqual(len(events), 2)
        self.assertEqual({e["company_name"] for e in events}, {"X", "Alpha"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
