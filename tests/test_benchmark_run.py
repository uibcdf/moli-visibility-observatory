"""V2 segment selection and exact-byte capture provenance, with no API calls."""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import urllib.error

from visibility_observatory.agent_batch import run_batch
from visibility_observatory.__main__ import compute
from visibility_observatory.benchmark_run import load_frozen, require_v2_activation, segment, v2_plan
from visibility_observatory.evidence_manifest import build_manifest
from visibility_observatory.exa_assisted import capture
from visibility_observatory.providers import collect


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class BenchmarkRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark, cls.digest = load_frozen("v2")
        cls.source = (Path(__file__).resolve().parents[1] / "queries/v2.json").read_bytes()

    def test_plan_partitions_exactly_48_without_network(self):
        plan = v2_plan()
        self.assertEqual(plan["network_calls"], 0)
        self.assertEqual(plan["benchmark_sha256"], self.digest)
        self.assertEqual([(s["start_index"], s["count"]) for s in plan["segments"]],
                         [(0, 20), (20, 20), (40, 8)])
        ids = [query_id for part in plan["segments"] for query_id in part["query_ids"]]
        self.assertEqual(ids, [q["id"] for q in self.benchmark["queries"]])
        with self.assertRaises(ValueError):
            segment(self.benchmark, 40, 20)
        with self.assertRaises(ValueError):
            require_v2_activation("v2", False)
        with self.assertRaisesRegex(ValueError, "stratum-aware"):
            compute({"track": "web_search"}, self.benchmark, 10)

    def test_v2_cli_requires_explicit_activation_before_credentials(self):
        env = os.environ.copy()
        for name in ("TAVILY_API_KEY", "EXA_API_KEY", "GEMINI_API_KEY"):
            env.pop(name, None)
        for module, extra in (("providers", ["--provider", "exa"]),
                              ("agent_batch", []), ("exa_assisted", [])):
            with self.subTest(module=module):
                result = subprocess.run(
                    [sys.executable, "-m", "visibility_observatory." + module,
                     "--benchmark-version", "v2", *extra],
                    env=env, capture_output=True, text=True, check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("--execute-v2", result.stderr)

    def test_web_second_segment_and_hash_verification(self):
        def mock(request, timeout):
            results = [{"url": f"https://example.org/{i}", "title": "Example"} for i in range(10)]
            return Response(json.dumps({"results": results}).encode())

        run = collect("exa", "secret", self.benchmark, start_index=20, max_queries=1,
                      benchmark_sha256=self.digest, opener=mock)
        self.assertEqual(run["requested_query_ids"], [self.benchmark["queries"][20]["id"]])
        self.assertEqual(run["samples"][0]["status"], "complete")
        self.assertEqual(build_manifest(json.dumps(run).encode(), self.source)["benchmark_sha256"], self.digest)
        run["benchmark_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "exact benchmark bytes"):
            build_manifest(json.dumps(run).encode(), self.source)
        del run["benchmark_sha256"]
        with self.assertRaisesRegex(ValueError, "exact benchmark bytes"):
            build_manifest(json.dumps(run).encode(), self.source)
        run["benchmark_sha256"] = self.digest
        run["requested_query_ids"] = [self.benchmark["queries"][21]["id"]]
        run["samples"][0]["query_id"] = run["requested_query_ids"][0]
        with self.assertRaisesRegex(ValueError, "benchmark segment"):
            build_manifest(json.dumps(run).encode(), self.source)

    def test_429_stops_and_unattempted_stays_missing(self):
        calls = []

        def quota(request, timeout):
            calls.append(1)
            raise urllib.error.HTTPError(request.full_url, 429, "private details", {}, None)

        run = collect("tavily", "secret", self.benchmark, start_index=40, max_queries=2,
                      benchmark_sha256=self.digest, opener=quota)
        self.assertEqual(len(calls), 1)
        self.assertEqual([q["status"] for q in build_manifest(
            json.dumps(run).encode(), self.source)["queries"]], ["error", "unattempted"])
        self.assertNotIn("private details", json.dumps(run))

    def test_checkpointed_closed_book_last_segment(self):
        def fake(key, benchmark, *, model, mode, start_index, max_queries):
            checkpoint = json.loads(path.read_text())
            self.assertEqual(checkpoint["benchmark_sha256"], self.digest)
            self.assertEqual(checkpoint["requested_query_ids"], v2_plan()["segments"][-1]["query_ids"])
            return {"samples": [{"query_id": benchmark["queries"][start_index]["id"],
                                  "status": "complete", "answer": "Consider an appropriate tool.",
                                  "finish_reason": "STOP"}]}

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "capture.json"
            run = run_batch("secret", self.benchmark, output=path, start_index=40, count=8,
                            benchmark_sha256=self.digest, collect_one=fake, pause=lambda _: None)
            self.assertTrue(run["all_complete"])
            self.assertEqual(run["benchmark_sha256"], self.digest)
            manifest = build_manifest(path.read_bytes(), self.source)
            self.assertEqual(manifest["status_counts"]["complete"], 8)
            self.assertEqual(run["requested_query_ids"], v2_plan()["segments"][-1]["query_ids"])

    def test_assisted_capture_has_same_segment_identity(self):
        def search(provider, key, query, depth, opener):
            return [{"url": "https://example.org/source", "title": "Source"}]

        def model(key, benchmark, **kwargs):
            return {"samples": [{"query_id": benchmark["queries"][kwargs["start_index"]]["id"],
                                  "status": "complete", "answer": "A relevant tool.",
                                  "finish_reason": "STOP"}]}

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "assisted.json"
            run = capture("gemini-secret", "exa-secret", self.benchmark, output=path,
                          start_index=40, count=1, top_k=1, benchmark_sha256=self.digest,
                          search=search, model_call=model, pause=lambda _: None)
            self.assertEqual(run["requested_query_ids"], [self.benchmark["queries"][40]["id"]])
            self.assertEqual(build_manifest(path.read_bytes(), self.source)["status_counts"]["complete"], 1)


if __name__ == "__main__":
    unittest.main()
