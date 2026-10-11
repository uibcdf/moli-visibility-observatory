"""Offline structural validation for the frozen V2 question corpus."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {
    "P": "preparation",
    "C": "conversion",
    "A": "selection_analysis",
    "I": "simulation_interop",
    "S": "storage_reproducibility",
}
PAIR_IDS = ("P01A", "C01A", "A01A", "I01A", "S01A", "C02A")
COUNTS = {"primary_unbranded": 30, "negative_control": 6,
          "named_alternative": 6, "spanish_unbranded": 6}
BRAND = re.compile(r"\bmol\s*[- ]?\s*sys\s*[- ]?\s*mt\b", re.IGNORECASE)
ALTERNATIVE = re.compile(r"\b(?:PDBFixer|Biotite|MDAnalysis|MDTraj|OpenMM)\b", re.IGNORECASE)


def validate_v2(benchmark):
    """Raise ValueError if the frozen design or a query's analysis metadata is invalid."""
    if not isinstance(benchmark, dict) or benchmark.get("schema_version") != "benchmark-v2" or benchmark.get("version") != "2.0" or benchmark.get("status") != "frozen":
        raise ValueError("Expected frozen benchmark-v2 version 2.0")
    design = benchmark.get("design")
    if not isinstance(design, dict) or any(design.get(k) != v for k, v in {
            "primary_intents": 15, "primary_prompts_per_intent": 2,
            "negative_controls": 6, "named_alternative_pairs": 6,
            "spanish_pairs": 6}.items()):
        raise ValueError("V2 design counts changed")
    queries = benchmark.get("queries")
    if not isinstance(queries, list) or len(queries) != 48 or any(not isinstance(q, dict) for q in queries):
        raise ValueError("V2 requires 48 query objects")
    ids = [q.get("id") for q in queries]
    if len(set(ids)) != 48 or any(not isinstance(i, str) for i in ids):
        raise ValueError("V2 query IDs must be unique strings")
    by_id = {q["id"]: q for q in queries}
    expected = {f"{prefix}{number:02d}{variant}"
                for prefix in FAMILIES for number in range(1, 4) for variant in "AB"}
    expected |= {f"N{number:02d}" for number in range(1, 7)}
    expected |= {f"{prefix}{number:02d}" for prefix in "HE" for number in range(1, 7)}
    if set(ids) != expected or Counter(q.get("stratum") for q in queries) != COUNTS:
        raise ValueError("V2 IDs or stratum sizes changed")

    normalized = []
    for q in queries:
        prompt = q.get("query")
        if not isinstance(prompt, str) or not prompt.strip() or BRAND.search(prompt):
            raise ValueError(f"Invalid or branded prompt: {q['id']}")
        normalized.append(" ".join(prompt.casefold().split()))
    if len(set(normalized)) != len(normalized):
        raise ValueError("Duplicate V2 prompt")

    for prefix, family in FAMILIES.items():
        for number in range(1, 4):
            intent = f"{prefix}{number:02d}"
            for suffix, variant in (("A", "researcher_request"), ("B", "concrete_io")):
                q = by_id[intent + suffix]
                if any((q.get("family") != family,
                        q.get("stratum") != "primary_unbranded",
                        q.get("intent_id") != intent,
                        q.get("variant") != variant,
                        q.get("language") != "en",
                        q.get("expected_scope") != "in_scope",
                        "paired_with" in q,
                        bool(ALTERNATIVE.search(q["query"])))):
                    raise ValueError(f"Invalid primary metadata or alternative name: {q['id']}")

    for number in range(1, 7):
        q = by_id[f"N{number:02d}"]
        if any((q.get("family") != "negative_control",
                q.get("stratum") != "negative_control",
                q.get("intent_id") != q["id"],
                q.get("variant") != "control",
                q.get("language") != "en",
                q.get("expected_scope") != "out_of_scope",
                "paired_with" in q)):
            raise ValueError(f"Invalid negative control: {q['id']}")
        for prefix, stratum, variant, language in (
                ("H", "named_alternative", "named_alternative", "en"),
                ("E", "spanish_unbranded", "spanish_translation", "es")):
            item = by_id[f"{prefix}{number:02d}"]
            parent = by_id[PAIR_IDS[number - 1]]
            if any((item.get("family") != parent["family"],
                    item.get("stratum") != stratum,
                    item.get("intent_id") != parent["intent_id"],
                    item.get("variant") != variant,
                    item.get("language") != language,
                    item.get("expected_scope") != "in_scope",
                    item.get("paired_with") != parent["id"],
                    bool(ALTERNATIVE.search(item["query"])) != (prefix == "H"))):
                raise ValueError(f"Invalid paired variant: {item['id']}")
    return dict(COUNTS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=ROOT / "queries/v2.json")
    args = parser.parse_args()
    source = args.benchmark.read_bytes()
    counts = validate_v2(json.loads(source))
    print(json.dumps({"version": "2.0", "counts": counts,
                      "sha256": hashlib.sha256(source).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
