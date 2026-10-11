"""Internal V2 stratum analysis of already-local, compatible captures."""

import argparse
import hashlib
import json
from pathlib import Path

from visibility_observatory.__main__ import ROOT, target
from visibility_observatory.benchmark_run import FROZEN
from visibility_observatory.benchmark_v2 import COUNTS, validate_v2
from visibility_observatory.evidence_agent_recompute import MATCH_RULE, has_explicit_name
from visibility_observatory.evidence_manifest import build_manifest
from visibility_observatory.evidence_merge import _compatibility, merge_captures


STATUSES = ("complete", "partial", "error", "unattempted")


def _rate(numerator, denominator):
    return numerator / denominator if denominator else None


def analyze(capture_bytes_list, benchmark_bytes):
    """Compute descriptive signals only; never infer recommendation quality."""
    if not capture_bytes_list:
        raise ValueError("At least one local capture is required")
    if hashlib.sha256(benchmark_bytes).hexdigest() != FROZEN["v2"][1]:
        raise ValueError("Analysis requires exact frozen V2 benchmark bytes")
    benchmark = json.loads(benchmark_bytes)
    validate_v2(benchmark)
    manifests = [build_manifest(source, benchmark_bytes) for source in capture_bytes_list]
    if len(manifests) > 1:
        merged = merge_captures(capture_bytes_list, benchmark_bytes)
        compatibility = merged["compatibility"]
        states = {item["query_id"]: item["status"] for item in merged["queries"]}
    else:
        compatibility = _compatibility(manifests[0])
        states = {item["query_id"]: item["status"] for item in manifests[0]["queries"]}

    schema = compatibility["capture_schema_version"]
    if schema == "1":
        signal = "canonical_url_presence_at_10"
    elif schema in ("agent-observation-v1", "agent-assisted-observation-v1"):
        signal = MATCH_RULE
    else:
        raise ValueError("Unsupported V2 capture schema")
    if schema == "agent-observation-v1" and compatibility["mode"] != "closed_book":
        raise ValueError("Expected closed-book mode")
    if schema == "agent-assisted-observation-v1" and compatibility["mode"] != "exa_assisted":
        raise ValueError("Expected Exa-assisted mode")

    complete = {}
    for source in capture_bytes_list:
        capture = json.loads(source)
        for sample in capture["samples"]:
            if sample["status"] == "complete":
                query_id = sample["query_id"]
                if query_id in complete:
                    raise ValueError("Conflicting complete V2 attempts: " + query_id)
                complete[query_id] = sample

    rows = []
    for query in benchmark["queries"]:
        query_id = query["id"]
        status = states.get(query_id, "unattempted")
        row = {"query_id": query_id, "stratum": query["stratum"],
               "intent_id": query["intent_id"], "status": status,
               "positive": None, "first_rank": None}
        if status == "complete":
            sample = complete[query_id]
            if schema == "1":
                rank = next((index for index, item in enumerate(sample["results"][:10], 1)
                             if target(item["url"])), None)
                row["first_rank"] = rank
                row["positive"] = rank is not None
            else:
                row["positive"] = has_explicit_name(sample["answer"])
        rows.append(row)
    by_id = {row["query_id"]: row for row in rows}

    strata = {}
    for stratum, size in COUNTS.items():
        group = [row for row in rows if row["stratum"] == stratum]
        eligible = [row for row in group if row["status"] == "complete"]
        positives = sum(row["positive"] for row in eligible)
        record = {"planned": size,
                  "status_counts": {status: sum(row["status"] == status for row in group)
                                    for status in STATUSES},
                  "positive": positives, "eligible": len(eligible),
                  "rate": _rate(positives, len(eligible))}
        if schema == "1":
            record["mrr_at_10"] = _rate(
                sum(1 / row["first_rank"] for row in eligible if row["first_rank"]),
                len(eligible))
        strata[stratum] = record

    intents = []
    for query in benchmark["queries"]:
        if query["stratum"] == "primary_unbranded" and query["id"].endswith("A"):
            a, b = by_id[query["id"]], by_id[query["intent_id"] + "B"]
            if a["status"] == b["status"] == "complete":
                intents.append((a["positive"], b["positive"]))
    intent_summary = {"planned": 15, "eligible_pairs": len(intents),
                      "either_positive": sum(a or b for a, b in intents),
                      "both_positive": sum(a and b for a, b in intents)}
    intent_summary["either_rate"] = _rate(intent_summary["either_positive"], len(intents))
    intent_summary["both_rate"] = _rate(intent_summary["both_positive"], len(intents))

    comparisons = {}
    for stratum in ("named_alternative", "spanish_unbranded"):
        pairs = [(by_id[query["paired_with"]], by_id[query["id"]])
                 for query in benchmark["queries"] if query["stratum"] == stratum]
        eligible = [(base, variant) for base, variant in pairs
                    if base["status"] == variant["status"] == "complete"]
        comparisons[stratum] = {
            "planned_pairs": 6, "eligible_pairs": len(eligible),
            "variant_only": sum(not base["positive"] and variant["positive"] for base, variant in eligible),
            "reference_only": sum(base["positive"] and not variant["positive"] for base, variant in eligible),
            "both_positive": sum(base["positive"] and variant["positive"] for base, variant in eligible),
            "neither_positive": sum(not base["positive"] and not variant["positive"] for base, variant in eligible),
        }

    return {
        "schema_version": "v2-internal-analysis-v1", "publication_status": "internal_unreviewed",
        "synthetic": compatibility["synthetic"], "benchmark_sha256": FROZEN["v2"][1],
        "signal": signal, "compatibility": compatibility,
        "source_run_ids": [item["run_id"] for item in manifests],
        "capture_count": len(manifests), "strata": strata,
        "primary_intents": intent_summary, "paired_variants": comparisons,
        "query_states": rows,
        "limitations": ["descriptive fixed prompts, not a representative sample",
                        "multi-capture panels span collection times" if len(manifests) > 1 else "single capture",
                        "name mention or URL presence does not establish recommendation quality",
                        "human adjudication and publication rights remain separate"],
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze existing local V2 captures without network access")
    parser.add_argument("--run", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = analyze([path.read_bytes() for path in args.run],
                     (ROOT / "queries/v2.json").read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Internal V2 analysis written; no public metric or provider request")


if __name__ == "__main__":
    main()
