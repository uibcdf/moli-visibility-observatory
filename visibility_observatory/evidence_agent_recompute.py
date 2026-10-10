"""Offline verification of explicit-name mentions in a closed-book agent summary."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from visibility_observatory.__main__ import ROOT
from visibility_observatory.evidence_manifest import build_manifest


MATCH_DEFINITION = ("Case-insensitive explicit textual occurrence of MolSysMT "
                    "(including spaced or hyphenated form); no implication of tool "
                    "endorsement or latent model knowledge.")
MATCH_RULE = "molsysmt-text-mention-v1"
NAME_PATTERN = re.compile(r"(?<![A-Za-z0-9])mol[ \t\r\n-]*sys[ \t\r\n-]*mt(?![A-Za-z0-9])", re.I)


def has_explicit_name(answer):
    return bool(NAME_PATTERN.search(answer))


def _equal(label, actual, expected):
    if actual != expected:
        raise ValueError("Agent summary mismatch: " + label)


def _count(summary, key, expected):
    value = summary.get(key)
    if type(value) is not int or value < 0:
        raise ValueError("Invalid agent summary count: " + key)
    _equal(key, value, expected)


def verify_agent_summary(capture_bytes, benchmark_bytes, summary_bytes):
    """Check reproducible mention counts without returning answer text."""
    manifest = build_manifest(capture_bytes, benchmark_bytes)
    provenance = manifest["provenance"]
    if provenance["capture_schema_version"] != "agent-observation-v1" or provenance.get("mode") != "closed_book":
        raise ValueError("Only closed-book agent captures can be reconciled")
    capture = json.loads(capture_bytes)
    summary = json.loads(summary_bytes)
    if not isinstance(summary, dict) or summary.get("schema_version") != "agent-baseline-summary-v1":
        raise ValueError("Unsupported agent summary schema")
    if (not isinstance(summary.get("run_url"), str) or not summary["run_url"] or
            not isinstance(summary.get("limitations"), list) or
            any(not isinstance(item, str) for item in summary["limitations"])):
        raise ValueError("Invalid agent summary review metadata")
    _equal("track", summary.get("track"), "agent_recommendation")
    _equal("benchmark_version", summary.get("benchmark_version"), provenance["benchmark_version"])
    for key in ("provider", "model", "mode"):
        if not provenance.get(key):
            raise ValueError("Capture lacks agent identity: " + key)
        _equal(key, summary.get(key), provenance[key])
    _equal("date", summary.get("date"), provenance["collected_at_utc"][:10])
    if type(summary.get("synthetic", False)) is not bool:
        raise ValueError("Invalid agent synthetic flag")
    _equal("synthetic", summary.get("synthetic", False), manifest["synthetic"])
    _equal("match_definition", summary.get("match_definition"), MATCH_DEFINITION)
    _count(summary, "queries_requested", len(manifest["queries"]))
    for source_key, summary_key in (("complete", "complete"), ("partial", "partial"),
                                    ("error", "errors"), ("unattempted", "unattempted")):
        _count(summary, summary_key, manifest["status_counts"][source_key])
    complete = manifest["status_counts"]["complete"]
    if complete < 1:
        raise ValueError("No complete agent responses to reconcile")

    mentions = [sample["query_id"] for sample in capture["samples"]
                if sample["status"] == "complete" and has_explicit_name(sample["answer"])]
    ids = summary.get("query_ids_with_mentions")
    if not isinstance(ids, list) or any(not isinstance(item, str) for item in ids):
        raise ValueError("Invalid agent mention IDs")
    _equal("query_ids_with_mentions", ids, mentions)
    _count(summary, "queries_with_explicit_name_mentions", len(mentions))
    rate = summary.get("explicit_name_mention_rate")
    if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not math.isfinite(rate):
        raise ValueError("Invalid agent mention rate")
    if not math.isclose(rate, len(mentions) / complete, rel_tol=0, abs_tol=1e-10):
        raise ValueError("Agent summary mismatch: explicit_name_mention_rate")

    return {
        "schema_version": "agent-summary-reconciliation-v1",
        "publication_status": "internal_unreviewed",
        "match_rule": MATCH_RULE,
        "source_run_id": manifest["run_id"],
        "source_sha256": manifest["source_sha256"],
        "benchmark_sha256": manifest["benchmark_sha256"],
        "summary_sha256": hashlib.sha256(summary_bytes).hexdigest(),
        "checks": ["track", "provider", "model", "mode", "date", "benchmark_version",
                   "synthetic", "requested_and_status_counts", "explicit_mention_ids_and_rate"],
        "not_verified": ["actions_run_identity", "artifact_identity", "prompt_protocol_if_absent",
                         "response_adjudication", "recommendation_quality", "scientific_accuracy"],
    }


def main():
    parser = argparse.ArgumentParser(description="Verify closed-book mention counts against a local capture")
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, default=ROOT / "queries/v1.json")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--output", type=Path)
    action.add_argument("--check", type=Path)
    args = parser.parse_args()
    report = verify_agent_summary(args.run.read_bytes(), args.benchmark.read_bytes(), args.summary.read_bytes())
    if args.check:
        if json.loads(args.check.read_text(encoding="utf-8")) != report:
            raise ValueError("Agent reconciliation report does not match exact input bytes")
    elif args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Closed-book summary reconciled:", report["source_run_id"])


if __name__ == "__main__":
    main()
