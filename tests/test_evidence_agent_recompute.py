from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from visibility_observatory.evidence_agent_recompute import (
    MATCH_DEFINITION, has_explicit_name, main, verify_agent_summary)


BENCHMARK = json.dumps({"version": "1.0", "queries": [
    {"id": "G01"}, {"id": "G02"}, {"id": "G03"}, {"id": "G04"}
]}).encode()
CAPTURE = {"schema_version": "agent-observation-v1", "benchmark_version": "1.0",
           "track": "agent_recommendation", "provider": "google-gemini-api", "model": "gemini-test",
           "mode": "closed_book", "collected_at_utc": "2026-10-10T00:00:00Z",
           "synthetic": True, "requested_query_ids": ["G01", "G02", "G03", "G04"],
           "samples": [
               {"query_id": "G01", "status": "complete", "answer": "Try Mol-Sys-MT.",
                "finish_reason": "STOP"},
               {"query_id": "G02", "status": "complete", "answer": "Try another library.",
                "finish_reason": "STOP"},
               {"query_id": "G03", "status": "partial", "answer": "MolSysMT appears...",
                "finish_reason": "MAX_TOKENS"},
           ]}
SUMMARY = {"schema_version": "agent-baseline-summary-v1", "date": "2026-10-10",
           "track": "agent_recommendation", "provider": "google-gemini-api",
           "model": "gemini-test", "mode": "closed_book", "benchmark_version": "1.0",
           "synthetic": True, "run_url": "https://example.org/actions/runs/1",
           "queries_requested": 4, "complete": 2, "partial": 1, "errors": 0,
           "unattempted": 1, "queries_with_explicit_name_mentions": 1,
           "query_ids_with_mentions": ["G01"], "explicit_name_mention_rate": 0.5,
           "match_definition": MATCH_DEFINITION, "response_adjudication": "pending",
           "limitations": ["Synthetic test"]}


def encoded(value):
    return json.dumps(value).encode()


class AgentRecomputeTests(unittest.TestCase):
    def test_name_rule_and_boundaries(self):
        for answer in ("MolSysMT", "mol sys mt", "MOL-SYS-MT"):
            with self.subTest(answer=answer):
                self.assertTrue(has_explicit_name(answer))
        for answer in ("MolSysMTExtra", "No tool named here", "OtherMolSysMT"):
            with self.subTest(answer=answer):
                self.assertFalse(has_explicit_name(answer))

    def test_partial_mention_is_missing_and_report_omits_answers(self):
        report = verify_agent_summary(encoded(CAPTURE), BENCHMARK, encoded(SUMMARY))
        self.assertEqual(report["publication_status"], "internal_unreviewed")
        self.assertIn("recommendation_quality", report["not_verified"])
        self.assertNotIn("Try Mol", json.dumps(report))

    def test_counts_mentions_and_scope_are_checked(self):
        cases = [("complete", 3, "complete"),
                 ("unattempted", 0, "unattempted"),
                 ("query_ids_with_mentions", ["G01", "G03"], "query_ids_with_mentions"),
                 ("explicit_name_mention_rate", 1.0, "explicit_name_mention_rate"),
                 ("match_definition", "any substring", "match_definition")]
        for key, value, message in cases:
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, message):
                    verify_agent_summary(encoded(CAPTURE), BENCHMARK,
                                         encoded({**SUMMARY, key: value}))
        with self.assertRaisesRegex(ValueError, "Only closed-book"):
            verify_agent_summary(encoded({**CAPTURE, "mode": "google_search"}),
                                 BENCHMARK, encoded(SUMMARY))

    def test_cli_report_check_uses_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("run.json", "benchmark.json", "summary.json", "report.json")]
            for path, value in zip(paths, (encoded(CAPTURE), BENCHMARK, encoded(SUMMARY))):
                path.write_bytes(value)
            common = ["evidence_agent_recompute", "--run", str(paths[0]),
                      "--benchmark", str(paths[1]), "--summary", str(paths[2])]
            with patch("sys.argv", common + ["--output", str(paths[3])]), redirect_stdout(io.StringIO()):
                main()
            with patch("sys.argv", common + ["--check", str(paths[3])]), redirect_stdout(io.StringIO()):
                main()
            paths[0].write_bytes(encoded(CAPTURE) + b" ")
            with patch("sys.argv", common + ["--check", str(paths[3])]), self.assertRaisesRegex(
                    ValueError, "exact input bytes"):
                main()


if __name__ == "__main__":
    unittest.main()
