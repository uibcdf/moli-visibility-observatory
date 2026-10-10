"""Optional Brave Search API collector. No calls without explicit API credentials."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from visibility_observatory.__main__ import ROOT, load

ENDPOINT = "https://api.search.brave.com/res/v1/web/search"

def collect(api_key, benchmark, *, count=10, country="us", language="en", opener=None):
    if not api_key:
        raise ValueError("BRAVE_SEARCH_API_KEY must be explicitly configured")
    if count < 10 or count > 20:
        raise ValueError("count must be 10..20 for complete top-10 measurement")
    opener = opener or urllib.request.urlopen
    samples = []
    for item in benchmark["queries"]:
        params = urllib.parse.urlencode({"q": item["query"], "count": count, "country": country, "search_lang": language})
        req = urllib.request.Request(ENDPOINT + "?" + params, headers={
            "Accept":"application/json",
            "X-Subscription-Token":api_key,
            "User-Agent":"MOLI-Visibility-Observatory/0.1"
        })
        try:
            with opener(req, timeout=30) as response:
                payload = json.load(response)
            results = payload.get("web", {}).get("results", [])
            if not isinstance(results, list):
                raise ValueError("Unexpected provider response shape")
            normalized=[{"url":r["url"], "title":r.get("title","")} for r in results if isinstance(r,dict) and isinstance(r.get("url"),str)]
            # A short result list is unknown: the provider may have omitted items.
            status="complete" if len(normalized)>=10 else "partial"
            samples.append({"query_id":item["id"],"status":status,"results":normalized,"provider_result_count":len(results)})
        except (urllib.error.URLError,TimeoutError,ValueError,KeyError,TypeError) as error:
            # Do not include response body or credentials in public errors.
            samples.append({"query_id":item["id"],"status":"error","results":[],"error_type":type(error).__name__})
    return {"schema_version":"1","benchmark_version":benchmark["version"],"track":"web_search",
            "provider":"brave-web-search-api","collected_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "settings":{"count":count,"country":country,"search_lang":language},
            "samples":samples}

def main():
    parser=argparse.ArgumentParser(description="Opt-in Brave web results collector")
    parser.add_argument("--output",default="build/observations/brave.json")
    parser.add_argument("--country",default="us")
    parser.add_argument("--language",default="en")
    args=parser.parse_args()
    data=collect(os.environ.get("BRAVE_SEARCH_API_KEY"),load(ROOT/"queries/v1.json"),
                 country=args.country,language=args.language)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print("Collected",len(data["samples"]),"queries; complete:",sum(s["status"]=="complete" for s in data["samples"]))
if __name__=="__main__": main()
