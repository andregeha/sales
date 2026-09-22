#!/usr/bin/env python
"""Tests for `run_all.py`'s `Run` record — run with `python tools/connectors/test_run_all.py`.

The point of the `Run` record is the one in `plan/website.md` §3.1: after the ADGM bug, where a run
reported a confident "0 created, 412 skipped" while never having looked, "was the radar actually
looking last Tuesday?" must always be answerable — for a run that succeeded AND for one that did not.
No network access is used.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_all  # noqa: E402
from base import ConnectorError  # noqa: E402
from test_connectors import StubConnector, mk_entry, ConnectorHarness  # noqa: E402


class TestBuildRunRecord(unittest.TestCase):
    """Pure function — no filesystem, no clock — so the shape is easy to pin down exactly."""

    def setUp(self):
        self.started = datetime(2026, 9, 22, 6, 0, 0, tzinfo=timezone.utc)
        self.finished = self.started + timedelta(seconds=12.5)

    def test_success_only(self):
        res = {"register": "amf-france", "source": "AMF France", "total": 666,
               "new_on_register": 10, "created": [{"slug": "a"}], "skipped": [],
               "changes": [{"x": 1}], "baseline": False, "backfill": False, "partial": False}
        record = run_all.build_run_record(self.started, self.finished, [res], [])
        self.assertTrue(record["ok"])
        self.assertEqual(record["duration_s"], 12.5)
        self.assertEqual(record["started_at"], "2026-09-22T06:00:00+00:00")
        self.assertEqual(len(record["connectors"]), 1)
        c = record["connectors"][0]
        self.assertEqual(c["register"], "amf-france")
        self.assertTrue(c["ok"])
        self.assertIsNone(c["error"])
        self.assertEqual(c["total"], 666)
        self.assertEqual(c["created"], 1)
        self.assertEqual(c["changes"], 1)

    def test_a_failure_is_recorded_not_dropped(self):
        """The whole point: a failed connector must leave a record saying so."""
        fail = {"register": "cma-saudi", "source": "CMA Saudi",
                "error": "cma.org.sa unreachable: timed out"}
        record = run_all.build_run_record(self.started, self.finished, [], [fail])
        self.assertFalse(record["ok"])
        c = record["connectors"][0]
        self.assertEqual(c["register"], "cma-saudi")
        self.assertFalse(c["ok"])
        self.assertEqual(c["error"], "cma.org.sa unreachable: timed out")
        self.assertIsNone(c["total"], "total is genuinely unknown for a source never read")
        self.assertEqual(c["created"], 0, "a connector that never ran created exactly nothing")

    def test_mixed_success_and_failure_sorted_by_register(self):
        ok = {"register": "dfsa-difc", "source": "DFSA", "total": 5, "new_on_register": 0,
              "created": [], "skipped": [], "changes": [], "baseline": False,
              "backfill": False, "partial": False}
        fail = {"register": "amf-france", "source": "AMF", "error": "boom"}
        record = run_all.build_run_record(self.started, self.finished, [ok], [fail])
        self.assertFalse(record["ok"])
        self.assertEqual([c["register"] for c in record["connectors"]],
                         ["amf-france", "dfsa-difc"], "connectors must be in a stable, sorted order")

    def test_git_commit_sha_is_a_string_or_none_never_invented(self):
        sha = run_all.git_commit_sha()
        self.assertTrue(sha is None or (isinstance(sha, str) and len(sha) == 40))


class TestWriteRunRecord(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_expected_filename_shape(self):
        record = {"started_at": "2026-09-22T06:00:00+00:00", "finished_at": "x",
                  "duration_s": 1.0, "commit": None, "ok": True, "connectors": []}
        path = run_all.write_run_record(record, runs_dir=self.tmp)
        self.assertEqual(path.name, "2026-09-22-060000.json")
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), record)

    def test_never_overwrites_an_existing_run_file(self):
        record = {"started_at": "2026-09-22T06:00:00+00:00", "finished_at": "x",
                  "duration_s": 1.0, "commit": None, "ok": True, "connectors": []}
        p1 = run_all.write_run_record(record, runs_dir=self.tmp)
        record2 = dict(record, ok=False)
        p2 = run_all.write_run_record(record2, runs_dir=self.tmp)
        self.assertNotEqual(p1, p2)
        self.assertTrue(p2.name.endswith("-2.json"))
        # The first file must be untouched.
        self.assertTrue(json.loads(p1.read_text(encoding="utf-8"))["ok"])


class TestMainWritesARunRecordEndToEnd(ConnectorHarness):
    """Exercises `main()` itself, with the real connector modules swapped for a stub."""

    def setUp(self):
        super().setUp()
        self.runs_dir = self.tmp / "runs"
        self._orig_runs_dir = run_all.RUNS_DIR
        run_all.RUNS_DIR = self.runs_dir
        self._orig_load = run_all.load_connectors

    def tearDown(self):
        run_all.RUNS_DIR = self._orig_runs_dir
        run_all.load_connectors = self._orig_load
        super().tearDown()

    def _stub_loader_ok(self, only=None):
        return [StubConnector(entries=[mk_entry("A", "Alpha Gestion")])]

    def _stub_loader_failing(self, only=None):
        return [StubConnector(error=ConnectorError("register unreachable"))]

    def runs(self):
        return sorted(self.runs_dir.glob("*.json")) if self.runs_dir.exists() else []

    def test_successful_run_writes_a_run_record(self):
        run_all.load_connectors = self._stub_loader_ok
        rc = run_all.main(["--json"])
        self.assertEqual(rc, 0)
        files = self.runs()
        self.assertEqual(len(files), 1)
        record = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertTrue(record["ok"])
        self.assertEqual(record["connectors"][0]["created"], 1)

    def test_failing_run_still_writes_a_run_record(self):
        """The non-negotiable: a run that fails must leave a record saying so."""
        run_all.load_connectors = self._stub_loader_failing
        rc = run_all.main(["--json"])
        self.assertEqual(rc, 1)
        files = self.runs()
        self.assertEqual(len(files), 1)
        record = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertFalse(record["ok"])
        self.assertEqual(record["connectors"][0]["error"], "register unreachable")

    def test_dry_run_writes_no_run_record(self):
        run_all.load_connectors = self._stub_loader_ok
        rc = run_all.main(["--dry-run", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(self.runs(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
