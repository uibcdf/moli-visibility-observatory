"""Offline reconciliation of one web capture with one reviewed-style summary."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from visibility_observatory.__main__ import ROOT, compute, target
from visibility_observatory.evidence_manifest import build_manifest


def _sha256(value):
    return hashlib.sha256(value).hexdigest()


def _require_equal(label, actual, expected):
    if actual != expected:
        raise ValueError("Summary mismatch: " + label)


def _rate(summary, key, expected):
    value = summary.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Invalid summary rate: " + key)
    if not math.isclose(value, expected, rel_tol=0, abs_tol=1e-10):
        raise ValueError("Summary mismatch: " + key)


def verify_web_summary(capture_bytes, benchmark_bytes, summary_bytes):
    """Check reconstructible fields; return only internal hashes and check names."""
    manifest = build_manifest(capture_bytes, benchmark_bytes)
    if manifest["provenance"]["track"] != "web_search":
        raise ValueError("Only web-search captures can be reconciled")
    capture = json.loads(capture_bytes)
    benchmark = json.loads(benchmark_bytes)
    summary = json.loads(summary_bytes)
    if not isinstance(summary, dict) or summary.get("schema_version") != "baseline-summary-v1":
        raise ValueError("Unsupported summary schema")
    if (not isinstance(summary.get("run_url"), str) or not summary["run_url"] or
            not isinstance(summary.get("limitations"), list) or
            any(not isinstance(item, str) for item in summary["limitations"])):
        raise ValueError("Invalid summary review metadata")
    _require_equal("track", summary.get("track"), "web_search")
    _require_equal("benchmark_version", summary.get("benchmark_version"), benchmark["version"])
    provider = manifest["provenance"].get("provider")
    if not provider:
        raise ValueError("Capture lacks provider identity")
    _require_equal("provider", summary.get("provider"), provider)
    _require_equal("date", summary.get("date"),
                   manifest["provenance"]["collected_at_utc"][:10])
    _require_equal("mode", summary.get("mode"), capture.get("settings", {}).get("search_mode"))
    if type(summary.get("synthetic", False)) is not bool:
        raise ValueError("Invalid synthetic flag")
    _require_equal("synthetic", summary.get("synthetic", False), manifest["synthetic"])
    if type(summary.get("k")) is not int or summary["k"] != 10:
        raise ValueError("Summary mismatch: k")
    if type(summary.get("queries_requested")) is not int:
        raise ValueError("Invalid summary count: queries_requested")
    _require_equal("queries_requested", summary["queries_requested"], len(manifest["queries"]))
    for source_key, summary_key in (("complete", "complete"), ("partial", "partial"), ("error", "errors")):
        if type(summary.get(summary_key)) is not int:
            raise ValueError("Invalid summary count: " + summary_key)
        _require_equal(summary_key, summary[summary_key], manifest["status_counts"][source_key])
    _require_equal("unattempted", manifest["status_counts"]["unattempted"], 0)

    metrics = compute(capture, benchmark, 10)
    _require_equal("complete denominator", metrics["evaluable"], manifest["status_counts"]["complete"])
    if not metrics["evaluable"]:
        raise ValueError("No complete web queries to reconcile")
    _rate(summary, "presence_at_10", metrics["presence"])
    _rate(summary, "mrr_at_10", metrics["mrr"])

    expected_hits = []
    for sample in capture["samples"]:
        if sample["status"] != "complete":
            continue
        for rank, result in enumerate(sample["results"][:10], 1):
            if target(result["url"]):
                expected_hits.append((sample["query_id"], rank, result["url"]))
                break
    hits = summary.get("hits")
    if not isinstance(hits, list) or any(
            not isinstance(hit, dict) or not isinstance(hit.get("query_id"), str) or
            type(hit.get("rank")) is not int or not isinstance(hit.get("url"), str) or
            not isinstance(hit.get("title"), str)
            for hit in hits):
        raise ValueError("Invalid summary hits")
    actual_hits = [(hit["query_id"], hit["rank"], hit["url"]) for hit in hits]
    _require_equal("hit query/rank/URL", sorted(actual_hits), sorted(expected_hits))

    return {
        "schema_version": "web-summary-reconciliation-v1",
        "publication_status": "internal_unreviewed",
        "source_run_id": manifest["run_id"],
        "source_sha256": manifest["source_sha256"],
        "benchmark_sha256": manifest["benchmark_sha256"],
        "summary_sha256": _sha256(summary_bytes),
        "checks": ["track", "provider", "mode", "date", "benchmark_version", "synthetic",
                   "requested_and_status_counts", "presence_at_10", "mrr_at_10", "hit_query_rank_url"],
        "not_verified": ["actions_run_identity", "artifact_identity", "hit_titles", "limitations",
                         "search_depth_and_locale", "scientific_relevance", "canonical_matcher_validity"],
    }


def main():
    parser = argparse.ArgumentParser(description="Verify a web summary against an already-local capture")
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, default=ROOT / "queries/v1.json")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--output", type=Path)
    action.add_argument("--check", type=Path)
    args = parser.parse_args()
    report = verify_web_summary(args.run.read_bytes(), args.benchmark.read_bytes(), args.summary.read_bytes())
    if args.check:
        if json.loads(args.check.read_text(encoding="utf-8")) != report:
            raise ValueError("Reconciliation report does not match exact input bytes")
    elif args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Web summary reconciled:", report["source_run_id"])


if __name__ == "__main__":
    main()
