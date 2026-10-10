"""Opt-in, bounded web-search collectors. No credentials or network calls on import.

All providers return the same versioned web_search observation shape. Search
provider rank is not an AI-agent recommendation and is not cross-provider comparable.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

from visibility_observatory.__main__ import ROOT, load

PROVIDERS = {
    "tavily": ("https://api.tavily.com/search", "TAVILY_API_KEY"),
    "exa": ("https://api.exa.ai/search", "EXA_API_KEY"),
}

def _fetch(provider, key, query, depth, opener):
    url, _ = PROVIDERS[provider]
    if provider == "tavily":
        payload = {"query": query, "search_depth": "basic", "max_results": depth,
                   "include_answer": False, "include_raw_content": False}
        headers = {"Authorization": "Bearer " + key}
    else:
        payload = {"query": query, "numResults": depth, "type": "auto"}
        headers = {"x-api-key": key}
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, method="POST",
        headers={**headers, "Content-Type": "application/json",
                 "Accept": "application/json", "User-Agent": "MOLI-Visibility-Observatory/0.1"},
    )
    with opener(request, timeout=30) as response:
        result = json.load(response)
    items = result.get("results")
    if not isinstance(items, list):
        raise ValueError("Unexpected provider response: results must be a list")
    if any(not isinstance(item, dict) or not isinstance(item.get("url"), str) for item in items):
        raise ValueError("Unexpected provider response: result missing URL")
    return [{"url": item["url"], "title": str(item.get("title") or "")} for item in items]

def collect(provider, key, benchmark, *, depth=10, max_queries=20, opener=None):
    if provider not in PROVIDERS:
        raise ValueError("Unknown provider")
    if not key:
        raise ValueError("Missing provider API key; refusing to query")
    if not (10 <= depth <= 20) or not (1 <= max_queries <= 20):
        raise ValueError("depth must be 10..20 and max_queries 1..20")
    opener = opener or urllib.request.urlopen
    samples = []
    for item in benchmark["queries"][:max_queries]:
        try:
            results = _fetch(provider, key, item["query"], depth, opener)
            samples.append({"query_id": item["id"], "status": "complete" if len(results) >= 10 else "partial",
                            "results": results, "provider_result_count": len(results)})
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            # Deliberately omit raw provider response and exception string (can include private data).
            samples.append({"query_id": item["id"], "status": "error", "results": [],
                            "error_type": type(error).__name__})
    return {"schema_version": "1", "benchmark_version": benchmark["version"],
            "track": "web_search", "provider": provider + "-search-api",
            "collected_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "settings": {"depth": depth, "max_queries": max_queries,
                         "search_mode": "basic" if provider == "tavily" else "auto"},
            "samples": samples}

def main():
    parser = argparse.ArgumentParser(description="Opt-in bounded Tavily / Exa web-search collector")
    parser.add_argument("--provider", choices=sorted(PROVIDERS), required=True)
    parser.add_argument("--output", default=None)
    parser.add_argument("--max-queries", type=int, default=20)
    args = parser.parse_args()
    key = os.environ.get(PROVIDERS[args.provider][1])
    result = collect(args.provider, key, load(ROOT / "queries/v1.json"), max_queries=args.max_queries)
    output = Path(args.output or ("build/observations/" + args.provider + ".json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"provider": result["provider"], "queries": len(result["samples"]),
                      "complete": sum(x["status"] == "complete" for x in result["samples"]),
                      "partial": sum(x["status"] == "partial" for x in result["samples"]),
                      "errors": sum(x["status"] == "error" for x in result["samples"])}))
if __name__ == "__main__":
    main()
