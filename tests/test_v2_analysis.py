"""Descriptive V2 analysis keeps strata, tracks and missingness separate."""

import json
from pathlib import Path
import unittest

from visibility_observatory.benchmark_run import load_frozen, v2_plan
from visibility_observatory.v2_analysis import analyze


BENCHMARK, DIGEST = load_frozen("v2")
SOURCE = (Path(__file__).resolve().parents[1] / "queries/v2.json").read_bytes()
TIMESTAMP = "2026-10-11T00:00:00Z"


def web_capture(start, count, hits=()):
    selected = BENCHMARK["queries"][start:start + count]
    samples = []
    for item in selected:
        urls = (["https://www.uibcdf.org/molsysmt/"] if item["id"] in hits
                else ["https://example.org/other"])
        urls += [f"https://example.org/{i}" for i in range(9)]
        samples.append({"query_id": item["id"], "status": "complete",
                        "results": [{"url": url} for url in urls]})
    return json.dumps({
        "schema_version": "1", "benchmark_version": "2.0", "benchmark_sha256": DIGEST,
        "track": "web_search", "provider": "exa-search-api", "synthetic": True,
        "collected_at_utc": TIMESTAMP, "start_index": start,
        "requested_query_ids": [item["id"] for item in selected],
        "settings": {"depth": 10, "search_mode": "auto", "max_queries": count},
        "samples": samples,
    }).encode()


class V2AnalysisTests(unittest.TestCase):
    def test_web_panel_has_separate_strata_and_paired_intents(self):
        hits = {"P01A", "N01", "H01", "E01"}
        sources = [web_capture(part["start_index"], part["count"], hits)
                   for part in v2_plan()["segments"]]
        result = analyze(sources, SOURCE)
        self.assertEqual(result["capture_count"], 3)
        self.assertTrue(result["synthetic"])
        self.assertEqual(result["signal"], "canonical_url_presence_at_10")
        self.assertEqual(result["strata"]["primary_unbranded"]["positive"], 1)
        self.assertEqual(result["strata"]["primary_unbranded"]["eligible"], 30)
        for group in ("negative_control", "named_alternative", "spanish_unbranded"):
            self.assertEqual(result["strata"][group]["positive"], 1)
            self.assertEqual(result["strata"][group]["eligible"], 6)
        self.assertEqual(result["primary_intents"]["eligible_pairs"], 15)
        self.assertEqual(result["primary_intents"]["either_positive"], 1)
        self.assertEqual(result["primary_intents"]["both_positive"], 0)
        self.assertEqual(result["paired_variants"]["named_alternative"]["both_positive"], 1)
        self.assertEqual(result["paired_variants"]["spanish_unbranded"]["both_positive"], 1)
        self.assertNotIn("https://", json.dumps(result))
        self.assertNotIn("overall_rate", result)

    def test_missing_and_unattempted_have_no_negative_outcome(self):
        capture = json.loads(web_capture(0, 2))
        capture["samples"] = [{"query_id": capture["requested_query_ids"][0],
                               "status": "error", "http_status": 429, "results": []}]
        result = analyze([json.dumps(capture).encode()], SOURCE)
        statuses = [item["status"] for item in result["query_states"]]
        self.assertEqual(statuses.count("error"), 1)
        self.assertEqual(statuses.count("unattempted"), 47)
        self.assertTrue(all(item["positive"] is None for item in result["query_states"]))
        self.assertIsNone(result["strata"]["primary_unbranded"]["rate"])

    def test_agent_mentions_are_separate_from_assisted_mode(self):
        index = next(i for i, item in enumerate(BENCHMARK["queries"]) if item["id"] == "P01A")
        base = {"benchmark_version": "2.0", "benchmark_sha256": DIGEST,
                "track": "agent_recommendation", "synthetic": True,
                "collected_at_utc": TIMESTAMP, "start_index": index,
                "requested_query_ids": ["P01A"], "model": "test-model",
                "protocol_version": "concise-v2", "output_token_limit": 4096}
        sample = {"query_id": "P01A", "status": "complete",
                  "answer": "MolSysMT may help here.", "finish_reason": "STOP"}
        closed = json.dumps({**base, "schema_version": "agent-observation-v1",
                             "provider": "google-gemini-api", "mode": "closed_book",
                             "samples": [sample]}).encode()
        assisted = json.dumps({**base, "schema_version": "agent-assisted-observation-v1",
                               "retrieval_provider": "exa-search-api", "mode": "exa_assisted", "top_k": 1,
                               "samples": [{**sample, "retrieval_status": "complete",
                                            "sources": [{"url": "https://example.org/source"}]}]}).encode()
        for source in (closed, assisted):
            result = analyze([source], SOURCE)
            self.assertEqual(result["strata"]["primary_unbranded"]["positive"], 1)
            self.assertEqual(result["strata"]["primary_unbranded"]["eligible"], 1)
            self.assertEqual(result["primary_intents"]["eligible_pairs"], 0)
            self.assertEqual(result["signal"], "molsysmt-text-mention-v1")
        with self.assertRaisesRegex(ValueError, "Incompatible"):
            analyze([closed, assisted], SOURCE)


if __name__ == "__main__":
    unittest.main()
