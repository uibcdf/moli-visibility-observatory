from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from visibility_observatory.evidence_recompute import main, verify_web_summary


BENCHMARK = json.dumps({"version": "1.0", "queries": [
    {"id": "G01", "family": "general"},
    {"id": "G02", "family": "general"},
    {"id": "G03", "family": "general"},
]}).encode()
RESULTS = [{"url": "https://example.org/" + str(i), "title": "PRIVATE TITLE"} for i in range(10)]
RESULTS[1] = {"url": "https://github.com/uibcdf/molsysmt", "title": "PRIVATE TITLE"}
CAPTURE = {"schema_version": "1", "benchmark_version": "1.0", "track": "web_search",
           "provider": "synthetic-search-api", "collected_at_utc": "2026-10-10T00:00:00Z",
           "synthetic": True, "settings": {"depth": 10, "search_mode": "basic", "max_queries": 3},
           "samples": [
               {"query_id": "G01", "status": "complete", "results": RESULTS},
               {"query_id": "G02", "status": "partial", "results": [{"url": "https://example.org/one"}]},
               {"query_id": "G03", "status": "error", "results": []},
           ]}
SUMMARY = {"schema_version": "baseline-summary-v1", "date": "2026-10-10", "track": "web_search",
           "provider": "synthetic-search-api", "mode": "basic", "benchmark_version": "1.0",
           "synthetic": True, "queries_requested": 3, "complete": 1, "partial": 1, "errors": 1,
           "k": 10, "presence_at_10": 1.0, "mrr_at_10": 0.5,
           "hits": [{"query_id": "G01", "rank": 2, "url": "https://github.com/uibcdf/molsysmt",
                     "title": "Reviewed editorial label"}],
           "run_url": "https://example.org/actions/runs/1", "limitations": ["Synthetic fixture"]}


def encoded(value):
    return json.dumps(value).encode()


class EvidenceRecomputeTests(unittest.TestCase):
    def test_complete_partial_and_error_reconcile_without_copying_results(self):
        report = verify_web_summary(encoded(CAPTURE), BENCHMARK, encoded(SUMMARY))
        self.assertEqual(report["publication_status"], "internal_unreviewed")
        self.assertIn("actions_run_identity", report["not_verified"])
        self.assertNotIn("PRIVATE TITLE", json.dumps(report))
        self.assertNotIn("github.com/uibcdf/molsysmt", json.dumps(report))

    def test_rate_counts_and_hit_provenance_are_checked(self):
        variants = [("presence_at_10", 0.0, "presence_at_10"),
                    ("errors", 0, "errors"),
                    ("queries_requested", 2, "queries_requested"),
                    ("hits", [{**SUMMARY["hits"][0], "rank": 3}], "hit query/rank/URL"),
                    ("mode", "auto", "mode")]
        for key, value, message in variants:
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, message):
                    verify_web_summary(encoded(CAPTURE), BENCHMARK,
                                       encoded({**SUMMARY, key: value}))

    def test_incomplete_result_cannot_be_declared_complete(self):
        malformed = {**CAPTURE, "samples": [{"query_id": "G01", "status": "complete", "results": []}]}
        with self.assertRaisesRegex(ValueError, "Invalid web result count"):
            verify_web_summary(encoded(malformed), BENCHMARK, encoded(SUMMARY))

    def test_cli_check_binds_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("run.json", "benchmark.json", "summary.json", "report.json")]
            for path, contents in zip(paths, (encoded(CAPTURE), BENCHMARK, encoded(SUMMARY))):
                path.write_bytes(contents)
            common = ["evidence_recompute", "--run", str(paths[0]), "--benchmark", str(paths[1]),
                      "--summary", str(paths[2])]
            with patch("sys.argv", common + ["--output", str(paths[3])]), redirect_stdout(io.StringIO()):
                main()
            with patch("sys.argv", common + ["--check", str(paths[3])]), redirect_stdout(io.StringIO()):
                main()
            paths[2].write_bytes(encoded(SUMMARY) + b" ")
            with patch("sys.argv", common + ["--check", str(paths[3])]), self.assertRaisesRegex(
                    ValueError, "exact input bytes"):
                main()


if __name__ == "__main__":
    unittest.main()
