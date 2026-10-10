"""Bounded, opt-in Gemini recommendation capture.

No live calls on import. No secrets in outputs. This track is distinct from
ranked web-search results: do not apply Presence@10 or MRR to generated text.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from visibility_observatory.__main__ import ROOT, load

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-3.1-flash-lite"

def collect(key, benchmark, *, model=DEFAULT_MODEL, mode="closed_book", max_queries=1, opener=None):
    if not key:
        raise ValueError("GEMINI_API_KEY missing: no requests will be made")
    if mode not in ("closed_book", "google_search"):
        raise ValueError("Invalid evaluation mode")
    if mode == "google_search":
        raise ValueError("Google Search grounding is disabled pending explicit paid-tier and billing review")
    if not 1 <= max_queries <= 20:
        raise ValueError("max_queries must be in 1..20")
    if not model or "/" in model or "?" in model or "#" in model:
        raise ValueError("Invalid Gemini model identifier")
    opener = opener or urllib.request.urlopen
    samples=[]
    for item in benchmark["queries"][:max_queries]:
        prompt=("You are recommending scientific Python software to a researcher. "
                "Answer the following request normally, without being told which package to recommend. "
                "Name specific tools when appropriate, explain why, and mention relevant limitations. "
                "Do not fabricate capabilities or citations. Request: " + item["query"])
        payload={"contents":[{"role":"user","parts":[{"text":prompt}]}],
                 "generationConfig":{"temperature":0,"maxOutputTokens":768}}
        if mode=="google_search":
            payload["tools"]=[{"google_search":{}}]
        request=urllib.request.Request(ENDPOINT.format(model=urllib.parse.quote(model,safe="")),
            data=json.dumps(payload).encode(),method="POST",
            headers={"x-goog-api-key":key,"Content-Type":"application/json","Accept":"application/json"})
        try:
            with opener(request,timeout=60) as response:
                result=json.load(response)
            candidates=result.get("candidates",[])
            if not candidates:
                raise ValueError("Missing candidates")
            first=candidates[0]
            parts=first.get("content",{}).get("parts",[])
            answer="\n".join(p["text"] for p in parts if isinstance(p,dict) and isinstance(p.get("text"),str))
            samples.append({"query_id":item["id"],"status":"complete" if answer else "partial",
                "answer":answer,"finish_reason":first.get("finishReason"),
                "grounding_metadata":first.get("groundingMetadata",{}) if mode=="google_search" else None,
                "usage":result.get("usageMetadata",{})})
        except urllib.error.HTTPError as error:
            # Expose only HTTP status, never request headers or provider error body.
            samples.append({"query_id":item["id"],"status":"error",
                            "error_type":"HTTPError","http_status":error.code})
            break
        except (urllib.error.URLError,TimeoutError,ValueError,KeyError,TypeError) as error:
            samples.append({"query_id":item["id"],"status":"error","error_type":type(error).__name__})
            # Fail closed after an API error to avoid repeated charge/rate-limit attempts.
            break
    return {"schema_version":"agent-observation-v1","benchmark_version":benchmark["version"],
            "track":"agent_recommendation","provider":"google-gemini-api","model":model,
            "mode":mode,"collected_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "max_queries":max_queries,"samples":samples,
            "evaluation_status":"unadjudicated","synthetic":False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--model",default=DEFAULT_MODEL)
    parser.add_argument("--mode",choices=("closed_book","google_search"),default="closed_book")
    parser.add_argument("--max-queries",type=int,default=1)
    parser.add_argument("--output",default="build/observations/gemini.json")
    args=parser.parse_args()
    data=collect(os.environ.get("GEMINI_API_KEY"),load(ROOT/"queries/v1.json"),
        model=args.model,mode=args.mode,max_queries=args.max_queries)
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"provider":data["provider"],"model":data["model"],"mode":data["mode"],
         "recorded":len(data["samples"]),"status_counts":{status:sum(s["status"]==status for s in data["samples"]) for status in ("complete","partial","error")},
         "evaluation_status":"unadjudicated"}))
if __name__=="__main__":main()
