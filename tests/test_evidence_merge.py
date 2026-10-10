import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout

from visibility_observatory.evidence_merge import main, merge_captures


BENCHMARK = json.dumps({"version": "1.0", "queries": [
    {"id": "G01"}, {"id": "G02"}, {"id": "G03"}
]}).encode()


def capture(when, requested, samples, **changes):
    run = {"schema_version": "agent-observation-v1", "track": "agent_recommendation",
           "benchmark_version": "1.0", "provider": "google-gemini-api",
           "model": "gemini-test", "mode": "closed_book", "protocol_version": "concise-v2",
           "output_token_limit": 4096, "synthetic": True, "collected_at_utc": when,
           "requested_query_ids": requested, "samples": samples}
    run.update(changes)
    return json.dumps(run).encode()


class EvidenceMergeTests(unittest.TestCase):
    def test_retry_selects_one_complete_and_retains_missing_attempts(self):
        first = capture("2026-10-10T00:00:00Z", ["G01", "G02", "G03"], [
            {"query_id": "G01", "status": "error", "http_status": 429},
            {"query_id": "G02", "status": "partial", "finish_reason": "MAX_TOKENS", "answer": "PRIVATE"}])
        second = capture("2026-10-11T00:00:00Z", ["G01", "G03"], [
            {"query_id": "G01", "status": "complete", "finish_reason": "STOP", "answer": "SECRET"},
            {"query_id": "G03", "status": "error", "http_status": 503}])
        merged = merge_captures([second, first], BENCHMARK)
        self.assertEqual(merged["selection_rule"], "exactly_one_complete_attempt_v1")
        self.assertEqual(merged["status_counts"],
                         {"complete": 1, "partial": 1, "error": 1, "unattempted": 0})
        self.assertEqual([item["query_id"] for item in merged["queries"]], ["G01", "G02", "G03"])
        self.assertEqual([item["status"] for item in merged["queries"][0]["attempts"]],
                         ["error", "complete"])
        self.assertEqual(len(merged["queries"][2]["unattempted_run_ids"]), 1)
        self.assertEqual(merged["queries"][0]["selected_run_id"], merged["runs"][1]["run_id"])
        self.assertNotIn("PRIVATE", json.dumps(merged))
        self.assertNotIn("SECRET", json.dumps(merged))
        self.assertEqual(merged, merge_captures([first, second], BENCHMARK))
        self.assertNotEqual(merged["benchmark_sha256"],
                            merge_captures([first, second], BENCHMARK + b" ")["benchmark_sha256"])

    def test_multiple_complete_attempts_are_conflict(self):
        first = capture("2026-10-10T00:00:00Z", ["G01"], [
            {"query_id": "G01", "status": "complete", "finish_reason": "STOP", "answer": "A"}])
        second = capture("2026-10-11T00:00:00Z", ["G01"], [
            {"query_id": "G01", "status": "complete", "finish_reason": "STOP", "answer": "B"}])
        with self.assertRaisesRegex(ValueError, "Conflicting complete"):
            merge_captures([first, second], BENCHMARK)
        with self.assertRaisesRegex(ValueError, "Duplicate capture"):
            merge_captures([first, first], BENCHMARK)

    def test_incompatible_model_or_protocol_rejected(self):
        first = capture("2026-10-10T00:00:00Z", ["G01"], [])
        changed_model = capture("2026-10-11T00:00:00Z", ["G02"], [], model="another-model")
        changed_protocol = capture("2026-10-11T00:00:00Z", ["G02"], [], protocol_version="other-v1")
        for changed in (changed_model, changed_protocol):
            with self.subTest(changed=changed):
                with self.assertRaisesRegex(ValueError, "Incompatible"):
                    merge_captures([first, changed], BENCHMARK)

    def test_missing_generation_profile_rejected(self):
        first = capture("2026-10-10T00:00:00Z", ["G01"], [])
        second = capture("2026-10-11T00:00:00Z", ["G02"], [])
        legacy = json.loads(first)
        legacy.pop("protocol_version")
        with self.assertRaisesRegex(ValueError, "lacks required comparison metadata"):
            merge_captures([json.dumps(legacy).encode(), second], BENCHMARK)

    def test_web_segments_may_have_different_query_caps(self):
        common = {"schema_version": "1", "track": "web_search", "benchmark_version": "1.0",
                  "provider": "tavily-search-api", "synthetic": True}
        first = json.dumps({**common, "collected_at_utc": "2026-10-10T00:00:00Z",
                            "settings": {"depth": 10, "search_mode": "basic", "max_queries": 1},
                            "samples": [{"query_id": "G01", "status": "partial", "results": []}]}).encode()
        second = json.dumps({**common, "collected_at_utc": "2026-10-11T00:00:00Z",
                             "settings": {"depth": 10, "search_mode": "basic", "max_queries": 2},
                             "samples": [{"query_id": "G02", "status": "error", "results": []}]}).encode()
        merged = merge_captures([first, second], BENCHMARK)
        self.assertEqual(merged["status_counts"],
                         {"complete": 0, "partial": 1, "error": 1, "unattempted": 0})
        self.assertNotIn("max_queries", merged["compatibility"]["settings"])

    def test_cli_verification_requires_original_capture_bytes(self):
        first = capture("2026-10-10T00:00:00Z", ["G01"], [])
        second = capture("2026-10-11T00:00:00Z", ["G02"], [])
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("first.json", "second.json", "benchmark.json", "merge.json")]
            for path, contents in zip(paths, (first, second, BENCHMARK)):
                path.write_bytes(contents)
            common = ["evidence_merge", "--run", str(paths[0]), "--run", str(paths[1]),
                      "--benchmark", str(paths[2])]
            with patch("sys.argv", common + ["--output", str(paths[3])]), redirect_stdout(io.StringIO()):
                main()
            with patch("sys.argv", common + ["--check", str(paths[3])]), redirect_stdout(io.StringIO()):
                main()
            paths[0].write_bytes(first + b" ")
            with patch("sys.argv", common + ["--check", str(paths[3])]), self.assertRaisesRegex(
                    ValueError, "exact captures"):
                main()


if __name__ == "__main__":
    unittest.main()
