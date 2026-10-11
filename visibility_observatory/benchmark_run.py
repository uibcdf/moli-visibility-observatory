"""Offline selection and byte identity for the two frozen query corpora."""

import argparse
import hashlib
import json

from visibility_observatory.__main__ import ROOT
from visibility_observatory.benchmark_v2 import validate_v2


FROZEN = {
    "v1": ("queries/v1.json", "733c7280bee7e06f08091c77b542e80b43a77d2a41f9f455d31599194fc36071"),
    "v2": ("queries/v2.json", "fab3c490c1ff158f0ae4528bf147c8aea216da527c2d65e5e4f4330315ee6335"),
}
MAX_SEGMENT = 20


def load_frozen(version):
    """Read exact checked-in bytes; return benchmark and its SHA-256."""
    if version not in FROZEN:
        raise ValueError("Unknown benchmark version")
    relative, expected = FROZEN[version]
    source = (ROOT / relative).read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    if digest != expected:
        raise ValueError("Frozen benchmark bytes changed; version the protocol before collecting")
    benchmark = json.loads(source)
    if version == "v2":
        validate_v2(benchmark)
    elif benchmark.get("version") != "1.0" or len(benchmark.get("queries", [])) != 20:
        raise ValueError("Unexpected V1 benchmark")
    return benchmark, digest


def segment(benchmark, start_index, count):
    """Select an exact bounded contiguous range, without silently clipping it."""
    queries = benchmark.get("queries") if isinstance(benchmark, dict) else None
    if (not isinstance(queries, list) or type(start_index) is not int or
            type(count) is not int or start_index < 0 or
            not 1 <= count <= MAX_SEGMENT or start_index + count > len(queries)):
        raise ValueError("Invalid or overflowing query segment")
    return queries[start_index:start_index + count]


def require_v2_activation(version, execute_v2):
    """A local explicit switch; account approval remains an external requirement."""
    if version == "v2" and not execute_v2:
        raise ValueError("V2 live capture requires --execute-v2 after terms, quota and owner review")
    if version != "v2" and execute_v2:
        raise ValueError("--execute-v2 applies only to V2")


def v2_plan():
    benchmark, digest = load_frozen("v2")
    queries = benchmark["queries"]
    segments = []
    for start in range(0, len(queries), MAX_SEGMENT):
        chosen = segment(benchmark, start, min(MAX_SEGMENT, len(queries) - start))
        segments.append({"start_index": start, "count": len(chosen),
                         "query_ids": [item["id"] for item in chosen]})
    return {"schema_version": "benchmark-collection-plan-v1", "benchmark_version": "2.0",
            "benchmark_sha256": digest, "network_calls": 0, "segments": segments}


def main():
    argparse.ArgumentParser(description="Print the offline V2 segment plan; no API access").parse_args()
    print(json.dumps(v2_plan(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
