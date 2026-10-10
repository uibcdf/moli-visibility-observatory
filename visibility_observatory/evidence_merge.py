"""Offline, content-free reconciliation of compatible local capture files."""

import argparse
import hashlib
import json
from pathlib import Path

from visibility_observatory.__main__ import ROOT
from visibility_observatory.evidence_manifest import build_manifest


def _compatibility(manifest):
    provenance = manifest["provenance"]
    schema = provenance["capture_schema_version"]
    required = ({"provider", "settings"} if schema == "1" else
                {"provider", "model", "mode", "protocol_version", "output_token_limit"}
                if schema == "agent-observation-v1" else
                {"retrieval_provider", "model", "mode", "protocol_version", "output_token_limit", "top_k"})
    if any(field not in provenance for field in required):
        raise ValueError("Capture lacks required comparison metadata")
    settings = dict(provenance.get("settings", {}))
    # A query cap selects a segment; it does not change the search protocol.
    settings.pop("max_queries", None)
    return {
        "capture_schema_version": provenance["capture_schema_version"],
        "track": provenance["track"],
        "provider": provenance.get("provider"),
        "retrieval_provider": provenance.get("retrieval_provider"),
        "model": provenance.get("model"),
        "mode": provenance.get("mode"),
        "protocol_version": provenance.get("protocol_version"),
        "output_token_limit": provenance.get("output_token_limit"),
        "top_k": provenance.get("top_k"),
        "settings": settings,
        "synthetic": manifest["synthetic"],
    }


def merge_captures(capture_bytes_list, benchmark_bytes):
    """Reconcile attempts; never copy answers, URLs or other provider content."""
    if len(capture_bytes_list) < 2:
        raise ValueError("At least two captures are required")
    benchmark = json.loads(benchmark_bytes)
    manifests = [build_manifest(data, benchmark_bytes) for data in capture_bytes_list]
    benchmark_hashes = {item["benchmark_sha256"] for item in manifests}
    if len(benchmark_hashes) != 1:
        raise ValueError("Benchmark bytes differ")
    compatibility = _compatibility(manifests[0])
    if any(_compatibility(item) != compatibility for item in manifests[1:]):
        raise ValueError("Incompatible provider, model, protocol or settings")
    run_ids = [item["run_id"] for item in manifests]
    if len(set(run_ids)) != len(run_ids):
        raise ValueError("Duplicate capture")
    manifests.sort(key=lambda item: (item["provenance"]["collected_at_utc"], item["run_id"]))

    requested = {}
    for manifest in manifests:
        for query in manifest["queries"]:
            entry = requested.setdefault(query["query_id"], {"attempts": [], "unattempted_run_ids": []})
            if query["status"] == "unattempted":
                entry["unattempted_run_ids"].append(manifest["run_id"])
            else:
                entry["attempts"].append({"run_id": manifest["run_id"], **query})

    queries = []
    for query in benchmark["queries"]:
        query_id = query["id"]
        if query_id not in requested:
            continue
        entry = requested[query_id]
        complete = [attempt for attempt in entry["attempts"] if attempt["status"] == "complete"]
        if len(complete) > 1:
            raise ValueError("Conflicting complete captures for " + query_id)
        if complete:
            status = "complete"
        elif any(attempt["status"] == "partial" for attempt in entry["attempts"]):
            status = "partial"
        elif entry["attempts"]:
            status = "error"
        else:
            status = "unattempted"
        queries.append({
            "query_id": query_id,
            "status": status,
            "selected_run_id": complete[0]["run_id"] if complete else None,
            "attempts": entry["attempts"],
            "unattempted_run_ids": entry["unattempted_run_ids"],
        })

    identity = "moli-evidence-merge-v1:" + manifests[0]["benchmark_sha256"] + ":" + ":".join(sorted(run_ids))
    return {
        "schema_version": "evidence-merge-v1",
        "publication_status": "internal_unreviewed",
        "selection_rule": "exactly_one_complete_attempt_v1",
        "merge_id": hashlib.sha256(identity.encode()).hexdigest(),
        "benchmark_sha256": manifests[0]["benchmark_sha256"],
        "compatibility": compatibility,
        "runs": [{
            "run_id": item["run_id"],
            "source_sha256": item["source_sha256"],
            "collected_at_utc": item["provenance"]["collected_at_utc"],
        } for item in manifests],
        "queries": queries,
        "status_counts": {status: sum(item["status"] == status for item in queries)
                          for status in ("complete", "partial", "error", "unattempted")},
    }


def main():
    parser = argparse.ArgumentParser(description="Reconcile compatible local captures into an internal manifest")
    parser.add_argument("--run", type=Path, action="append", required=True)
    parser.add_argument("--benchmark", type=Path, default=ROOT / "queries/v1.json")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--check", type=Path)
    args = parser.parse_args()
    merged = merge_captures([path.read_bytes() for path in args.run], args.benchmark.read_bytes())
    if args.check:
        if json.loads(args.check.read_text(encoding="utf-8")) != merged:
            raise ValueError("Merge manifest does not match the exact captures and benchmark bytes")
        print("Merge verified")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
        print("Internal merge written:", merged["merge_id"])


if __name__ == "__main__":
    main()
