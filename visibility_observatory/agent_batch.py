"""Checkpointed Gemini benchmark runner; bounded and fail-safe.

Independent provider runs; never combine model recommendations with search ranks.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import time

from visibility_observatory.__main__ import ROOT, load
from visibility_observatory.gemini import DEFAULT_MODEL, collect

def write_atomic(path, value):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    temporary.replace(path)

def run_batch(key, benchmark, *, output, model=DEFAULT_MODEL, start_index=0,
              count=20, delay=8, collect_one=collect, pause=time.sleep):
    if not key: raise ValueError("GEMINI_API_KEY is required")
    queries=benchmark["queries"]
    if not 0 <= start_index < len(queries) or not 1 <= count <= 20:
        raise ValueError("Invalid query range")
    chosen=queries[start_index:start_index+count]
    data={"schema_version":"agent-observation-v1","track":"agent_recommendation",
          "benchmark_version":benchmark["version"],"provider":"google-gemini-api",
          "model":model,"mode":"closed_book","collected_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
          "start_index":start_index,"requested_query_ids":[q["id"] for q in chosen],
          "evaluation_status":"unadjudicated","synthetic":False,"samples":[]}
    write_atomic(output,data)
    for ix,q in enumerate(chosen):
        if ix: pause(delay)
        result=collect_one(key,benchmark,model=model,mode="closed_book",
                           start_index=start_index+ix,max_queries=1)
        sample=result["samples"][0]
        data["samples"].append(sample)
        write_atomic(output,data)
        # Quota, auth and model access errors are not transient: stop to avoid
        # repeated billable or rejected requests.
        if sample["status"]=="error" and sample.get("http_status") in (400,401,403,404,429):
            data["stop_reason"]="provider_nonretryable_error"
            write_atomic(output,data)
            break
        # Other persistent 5xx / transport errors are preserved; continue to
        # next prompt to prevent one transient failure aborting all observations.
    data["completed_at_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
    data["complete_count"]=sum(x["status"]=="complete" for x in data["samples"])
    data["failed_count"]=sum(x["status"]!="complete" for x in data["samples"])
    data["unattempted_count"]=len(chosen)-len(data["samples"])
    data["all_complete"]=len(data["samples"])==len(chosen) and data["failed_count"]==0
    write_atomic(output,data)
    return data

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start-index",type=int,default=0)
    p.add_argument("--count",type=int,default=20)
    p.add_argument("--delay-seconds",type=int,default=8)
    p.add_argument("--output",default="build/observations/gemini-batch.json")
    args=p.parse_args()
    if not 0 <= args.delay_seconds <= 120: p.error("Invalid delay")
    result=run_batch(os.environ.get("GEMINI_API_KEY"),load(ROOT/"queries/v1.json"),
                     output=args.output,start_index=args.start_index,
                     count=args.count,delay=args.delay_seconds)
    print(json.dumps({k:result[k] for k in ("complete_count","failed_count","unattempted_count","all_complete")}))
    # Nonzero exit for incomplete benchmark, but artifacts remain available.
    if not result["all_complete"]: raise SystemExit(2)

if __name__=="__main__":main()
