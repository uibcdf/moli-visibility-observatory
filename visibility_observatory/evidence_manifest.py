"""Offline manifest for an existing capture; never stores provider answers or URLs."""

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from visibility_observatory.__main__ import ROOT

SCHEMAS = {
    "1": "web_search",
    "agent-observation-v1": "agent_recommendation",
    "agent-assisted-observation-v1": "agent_recommendation",
}
STATUSES = ("complete", "partial", "error")
WEB_SETTINGS = {"depth", "max_queries", "search_mode", "count", "country", "search_lang"}


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _utc(value):
    if not isinstance(value, str):
        raise ValueError("Capture timestamp must be UTC text")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Invalid capture timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise ValueError("Capture timestamp must be UTC")
    return value


def _query_ids(benchmark):
    if not isinstance(benchmark, dict) or not isinstance(benchmark.get("queries"), list):
        raise ValueError("Invalid benchmark")
    ids = [item.get("id") for item in benchmark["queries"] if isinstance(item, dict)]
    if len(ids) != len(benchmark["queries"]) or any(not isinstance(x, str) or not x for x in ids):
        raise ValueError("Invalid benchmark query IDs")
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate benchmark query IDs")
    return ids


def _requested_ids(capture, benchmark_ids, samples):
    if "requested_query_ids" in capture:
        requested = capture["requested_query_ids"]
    elif "start_index" in capture and "max_queries" in capture:
        start, count = capture["start_index"], capture["max_queries"]
        if type(start) is not int or type(count) is not int or start < 0 or count < 1:
            raise ValueError("Invalid requested query range")
        requested = benchmark_ids[start:start + count]
    else:
        requested = [sample.get("query_id") for sample in samples]
    if (not isinstance(requested, list) or not requested or
            any(not isinstance(x, str) or x not in benchmark_ids for x in requested) or
            len(requested) != len(set(requested))):
        raise ValueError("Invalid requested query IDs")
    return requested


def build_manifest(capture_bytes, benchmark_bytes):
    """Bind exact input bytes to query states without copying response content."""
    capture = json.loads(capture_bytes)
    benchmark = json.loads(benchmark_bytes)
    if not isinstance(capture, dict) or not isinstance(benchmark, dict):
        raise ValueError("Invalid capture or benchmark")
    schema = capture.get("schema_version")
    if not isinstance(schema, str) or schema not in SCHEMAS or capture.get("track") != SCHEMAS[schema]:
        raise ValueError("Unsupported capture schema or track")
    if capture.get("benchmark_version") != benchmark.get("version"):
        raise ValueError("Benchmark version mismatch")
    benchmark_ids = _query_ids(benchmark)
    samples = capture.get("samples")
    if not isinstance(samples, list) or any(not isinstance(x, dict) for x in samples):
        raise ValueError("Invalid capture samples")
    requested = _requested_ids(capture, benchmark_ids, samples)
    observed = [sample.get("query_id") for sample in samples]
    if observed != requested[:len(observed)]:
        raise ValueError("Samples must be the ordered prefix of requested queries")
    if any(sample.get("status") not in STATUSES for sample in samples):
        raise ValueError("Invalid sample status")
    if type(capture.get("synthetic", False)) is not bool:
        raise ValueError("Synthetic flag must be boolean")

    top_k = capture.get("top_k")
    if top_k is not None and (type(top_k) is not int or top_k < 1):
        raise ValueError("Invalid top_k")

    for sample in samples:
        if schema == "1":
            results = sample.get("results")
            if not isinstance(results, list) or (sample["status"] == "complete" and len(results) < 10):
                raise ValueError("Invalid web result count")
            if any(not isinstance(result, dict) or not isinstance(result.get("url"), str) or
                   urlparse(result["url"]).scheme not in ("http", "https") or
                   not urlparse(result["url"]).hostname for result in results):
                raise ValueError("Invalid web result URL")
        elif sample["status"] == "complete":
            if not isinstance(sample.get("answer"), str) or not sample["answer"].strip():
                raise ValueError("Complete agent response lacks answer")
            if sample.get("finish_reason") != "STOP":
                raise ValueError("Complete agent response did not stop")
            if schema == "agent-assisted-observation-v1":
                sources = sample.get("sources")
                if sample.get("retrieval_status") != "complete" or not isinstance(sources, list):
                    raise ValueError("Complete assisted response lacks retrieval")
                if top_k is None or len(sources) < top_k:
                    raise ValueError("Incomplete assisted source set")

    states = []
    for index, query_id in enumerate(requested):
        if index >= len(samples):
            states.append({"query_id": query_id, "status": "unattempted"})
            continue
        sample = samples[index]
        state = {"query_id": query_id, "status": sample["status"]}
        if "http_status" in sample:
            code = sample["http_status"]
            if type(code) is not int or not 100 <= code <= 599:
                raise ValueError("Invalid HTTP status")
            state["http_status"] = code
        if sample.get("finish_reason") is not None:
            reason = sample["finish_reason"]
            if not isinstance(reason, str) or not re.fullmatch(r"[A-Z_]{1,40}", reason):
                raise ValueError("Invalid finish reason")
            state["finish_reason"] = reason
        if schema == "agent-assisted-observation-v1":
            retrieval = sample.get("retrieval_status")
            if retrieval is not None:
                if retrieval not in STATUSES:
                    raise ValueError("Invalid retrieval status")
                state["retrieval_status"] = retrieval
            sources = sample.get("sources")
            if sources is not None:
                if not isinstance(sources, list):
                    raise ValueError("Invalid source count")
                state["source_count"] = len(sources)
        states.append(state)
    counts = {status: sum(item["status"] == status for item in states)
              for status in (*STATUSES, "unattempted")}
    source_digest = _sha256(capture_bytes)
    benchmark_digest = _sha256(benchmark_bytes)
    identity = _sha256(("moli-evidence-manifest-v1:" + source_digest + ":" + benchmark_digest).encode())
    provenance = {
        "capture_schema_version": schema,
        "track": capture["track"],
        "benchmark_version": benchmark["version"],
        "collected_at_utc": _utc(capture.get("collected_at_utc")),
    }
    for key in ("provider", "retrieval_provider", "model", "mode", "protocol_version"):
        value = capture.get(key)
        if value is not None:
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1,120}", value):
                raise ValueError("Invalid provenance field: " + key)
            provenance[key] = value
    for key in ("output_token_limit", "top_k"):
        value = capture.get(key)
        if value is not None:
            if type(value) is not int or value < 1:
                raise ValueError("Invalid provenance field: " + key)
            provenance[key] = value
    settings = capture.get("settings")
    if settings is not None:
        if schema != "1" or not isinstance(settings, dict) or any(key not in WEB_SETTINGS for key in settings):
            raise ValueError("Unsupported capture settings")
        for key, value in settings.items():
            if key in ("depth", "max_queries", "count"):
                if type(value) is not int or value < 1:
                    raise ValueError("Invalid capture setting: " + key)
            elif not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,40}", value):
                raise ValueError("Invalid capture setting: " + key)
        provenance["settings"] = settings
    return {
        "schema_version": "evidence-manifest-v1",
        "publication_status": "internal_unreviewed",
        "synthetic": bool(capture.get("synthetic")),
        "run_id": identity,
        "source_sha256": source_digest,
        "benchmark_sha256": benchmark_digest,
        "provenance": provenance,
        "queries": states,
        "status_counts": counts,
    }


def verify_manifest(manifest, capture_bytes, benchmark_bytes):
    if manifest != build_manifest(capture_bytes, benchmark_bytes):
        raise ValueError("Manifest does not match the exact capture and benchmark bytes")


def main():
    parser = argparse.ArgumentParser(description="Build or verify an internal manifest for an existing local capture")
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, default=ROOT / "queries/v1.json")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--check", type=Path)
    args = parser.parse_args()
    capture_bytes = args.run.read_bytes()
    benchmark_bytes = args.benchmark.read_bytes()
    if args.check:
        verify_manifest(json.loads(args.check.read_text(encoding="utf-8")), capture_bytes, benchmark_bytes)
        print("Manifest verified")
    else:
        manifest = build_manifest(capture_bytes, benchmark_bytes)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print("Internal manifest written:", manifest["run_id"])


if __name__ == "__main__":
    main()
