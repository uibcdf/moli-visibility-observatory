"""Bounded Exa-assisted Gemini evaluation; independent of closed-book and web ranks."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import time
import urllib.error

from visibility_observatory.__main__ import ROOT, load
from visibility_observatory.agent_batch import write_atomic
from visibility_observatory.gemini import collect, PROTOCOL_VERSION
from visibility_observatory.providers import _fetch

def capture(gemini_key, exa_key, benchmark, *, output, model="gemini-3.8-flash",
            start_index=0, count=1, top_k=5, delay=8,
            search=_fetch, model_call=collect, pause=time.sleep):
    if not gemini_key or not exa_key:
        raise ValueError("Gemini and Exa keys are required")
    if not 0 <= start_index < len(benchmark["queries"]) or not 1 <= count <= 20 or not 1 <= top_k <= 10:
        raise ValueError("Invalid bounded evaluation parameters")
    selected=benchmark["queries"][start_index:start_index+count]
    data={"schema_version":"agent-assisted-observation-v1",
          "benchmark_version":benchmark["version"],"track":"agent_recommendation",
          "mode":"exa_assisted","model":model,"retrieval_provider":"exa-search-api",
          "top_k":top_k,"protocol_version":PROTOCOL_VERSION,
          "collected_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
          "requested_query_ids":[q["id"] for q in selected],
          "evaluation_status":"unadjudicated","samples":[]}
    write_atomic(output,data)
    for offset,q in enumerate(selected):
        if offset: pause(delay)
        try:
            found=search("exa",exa_key,q["query"],top_k,None)
            # A short retrieval may still provide useful context, but log it explicitly.
            sources=[{"rank":i,"url":s["url"],"title":s["title"]}
                     for i,s in enumerate(found[:top_k],1)]
            context="\n".join(f"[{s['rank']}] {s['title']} | {s['url']}" for s in sources)
            result=model_call(gemini_key,benchmark,model=model,mode="closed_book",
                              max_queries=1,start_index=start_index+offset,context=context)
            answer=result["samples"][0]
            data["samples"].append({"query_id":q["id"],"retrieval_status":"complete" if len(sources)==top_k else "partial",
                                    "sources":sources,**answer})
        except urllib.error.HTTPError as e:
            data["samples"].append({"query_id":q["id"],"status":"error","error_type":"ExaHTTPError","http_status":e.code})
        except (urllib.error.URLError,ValueError,TimeoutError,KeyError,TypeError) as e:
            data["samples"].append({"query_id":q["id"],"status":"error","error_type":"Retrieval"+type(e).__name__})
        write_atomic(output,data)
        last=data["samples"][-1]
        if last.get("http_status") in (400,401,403,404,429) or (
           last.get("status")=="error" and last.get("error_type") not in ("ExaHTTPError",)):
            data["stop_reason"]="provider_error_or_quota"
            break
    data["complete_count"]=sum(s.get("status")=="complete" for s in data["samples"])
    data["incomplete_count"]=sum(s.get("status")!="complete" for s in data["samples"])
    data["unattempted_count"]=len(selected)-len(data["samples"])
    data["all_complete"]=data["complete_count"]==len(selected)
    data["completed_at_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
    write_atomic(output,data)
    return data

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--model",default="gemini-3.8-flash",choices=("gemini-3.8-flash","gemini-3.1-flash-lite"))
    p.add_argument("--count",type=int,default=1)
    p.add_argument("--start-index",type=int,default=0)
    p.add_argument("--output",default="build/observations/exa-assisted.json")
    args=p.parse_args()
    data=capture(os.environ.get("GEMINI_API_KEY"),os.environ.get("EXA_API_KEY"),
        load(ROOT/"queries/v1.json"),model=args.model,count=args.count,
        start_index=args.start_index,output=args.output)
    print(json.dumps({k:data[k] for k in ("complete_count","incomplete_count","unattempted_count","all_complete")}))
    if not data["all_complete"]:raise SystemExit(2)
if __name__=="__main__":main()
