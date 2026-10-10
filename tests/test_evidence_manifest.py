import json
import unittest

from visibility_observatory.evidence_manifest import build_manifest, verify_manifest


BENCHMARK = json.dumps({"version": "1.0", "queries": [
    {"id": "G01"}, {"id": "G02"}, {"id": "G03"}
]}).encode()
BASE = {"benchmark_version": "1.0", "collected_at_utc": "2026-10-10T00:00:00Z"}


class EvidenceManifestTests(unittest.TestCase):
    def test_partial_web_manifest_is_internal_and_contains_no_results(self):
        run = {**BASE, "schema_version": "1", "track": "web_search", "provider": "synthetic-test",
               "synthetic": True, "settings": {"depth": 10, "search_mode": "basic"},
               "samples": [{"query_id": "G01", "status": "partial",
               "results": [{"url": "https://private.example/sentinel", "title": "SENTINEL"}]}]}
        source = json.dumps(run).encode()
        manifest = build_manifest(source, BENCHMARK)
        self.assertEqual(manifest["publication_status"], "internal_unreviewed")
        self.assertEqual(manifest["queries"], [{"query_id": "G01", "status": "partial"}])
        self.assertEqual(manifest["status_counts"]["complete"], 0)
        self.assertEqual(manifest["provenance"]["settings"], {"depth": 10, "search_mode": "basic"})
        self.assertNotIn("SENTINEL", json.dumps(manifest))
        self.assertNotIn("private.example", json.dumps(manifest))
        verify_manifest(manifest, source, BENCHMARK)
        with self.assertRaises(ValueError):
            verify_manifest(manifest, source + b" ", BENCHMARK)
        run["settings"]["api_key"] = "never-copy-secrets"
        with self.assertRaises(ValueError):
            build_manifest(json.dumps(run).encode(), BENCHMARK)

    def test_agent_error_and_unattempted_remain_missing(self):
        run = {**BASE, "schema_version": "agent-observation-v1",
               "track": "agent_recommendation", "provider": "google-gemini-api",
               "model": "gemini-3.8-flash", "mode": "closed_book",
               "protocol_version": "concise-v2", "output_token_limit": 4096,
               "requested_query_ids": ["G01", "G02", "G03"],
               "samples": [{"query_id": "G01", "status": "complete", "answer": "Answer", "finish_reason": "STOP"},
                           {"query_id": "G02", "status": "error", "http_status": 429}]}
        manifest = build_manifest(json.dumps(run).encode(), BENCHMARK)
        self.assertEqual(manifest["status_counts"],
                         {"complete": 1, "partial": 0, "error": 1, "unattempted": 1})
        self.assertEqual(manifest["queries"][-1], {"query_id": "G03", "status": "unattempted"})
        self.assertEqual(manifest["queries"][1],
                         {"query_id": "G02", "status": "error", "http_status": 429})
        self.assertEqual(manifest["provenance"]["output_token_limit"], 4096)

    def test_rejects_duplicate_or_reordered_samples(self):
        run = {**BASE, "schema_version": "agent-observation-v1",
               "track": "agent_recommendation", "requested_query_ids": ["G01", "G02"],
               "samples": [{"query_id": "G02", "status": "error"}]}
        with self.assertRaises(ValueError):
            build_manifest(json.dumps(run).encode(), BENCHMARK)
        run["requested_query_ids"] = ["G01", "G01"]
        with self.assertRaises(ValueError):
            build_manifest(json.dumps(run).encode(), BENCHMARK)

    def test_truncation_remains_partial(self):
        run = {**BASE, "schema_version": "agent-observation-v1",
               "track": "agent_recommendation", "requested_query_ids": ["G01"],
               "samples": [{"query_id": "G01", "status": "partial",
                            "answer": "Incomplete", "finish_reason": "MAX_TOKENS"}]}
        manifest = build_manifest(json.dumps(run).encode(), BENCHMARK)
        self.assertEqual(manifest["queries"],
                         [{"query_id": "G01", "status": "partial", "finish_reason": "MAX_TOKENS"}])
        self.assertEqual(manifest["status_counts"]["complete"], 0)

    def test_assisted_complete_needs_full_retrieval(self):
        run = {**BASE, "schema_version": "agent-assisted-observation-v1",
               "track": "agent_recommendation", "mode": "exa_assisted", "top_k": 5,
               "requested_query_ids": ["G01"],
               "samples": [{"query_id": "G01", "status": "complete", "answer": "Answer",
                            "finish_reason": "STOP", "retrieval_status": "complete", "sources": [{}]}]}
        with self.assertRaises(ValueError):
            build_manifest(json.dumps(run).encode(), BENCHMARK)


if __name__ == "__main__":
    unittest.main()
