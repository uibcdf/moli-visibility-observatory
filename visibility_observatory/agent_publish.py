"""Publish reviewed agent summaries independently of web-search ranks."""
import html
import json
from pathlib import Path

from visibility_observatory.publish import ROOT

AGENT_DIR = ROOT / "data" / "agent-baselines"

def read_agent_summaries(directory=AGENT_DIR):
    records=[]
    for path in sorted(Path(directory).glob("*.summary.json")):
        d=json.loads(path.read_text(encoding="utf-8"))
        required=("date","model","mode","run_url","queries_requested","complete",
                  "partial","errors","queries_with_explicit_name_mentions","query_ids_with_mentions")
        if d.get("schema_version") != "agent-baseline-summary-v1" or d.get("track")!="agent_recommendation":
            raise ValueError(f"Invalid agent schema: {path}")
        if any(key not in d for key in required) or d.get("synthetic"):
            raise ValueError(f"Invalid agent summary: {path}")
        total=d["complete"]+d["partial"]+d["errors"]+d.get("unattempted",0)
        if total!=d["queries_requested"] or d["complete"]<1:
            raise ValueError(f"Agent denominators inconsistent: {path}")
        hits=d["queries_with_explicit_name_mentions"]
        if hits!=len(d["query_ids_with_mentions"]) or hits>d["complete"]:
            raise ValueError(f"Agent mentions inconsistent: {path}")
        if abs(d.get("explicit_name_mention_rate",-1)-hits/d["complete"])>1e-9:
            raise ValueError(f"Agent mention rate inconsistent: {path}")
        records.append(d)
    return records

def render_agents(records,out):
    destination=Path(out)
    destination.mkdir(parents=True,exist_ok=True)
    (destination/"agent-baselines.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    escape=html.escape
    sections=[]
    for d in reversed(records):
        model=escape(d["model"])
        mode=escape(d["mode"])
        url=escape(d["run_url"],quote=True)
        summary=f'{d["queries_with_explicit_name_mentions"]}/{d["complete"]} ({d["explicit_name_mention_rate"]:.0%})'
        sections.append(f'<section><h2>{model} · {mode}</h2><p>{escape(d["date"])}</p><p><strong>Explicit MolSysMT mentions: {summary}</strong></p><p>Complete: {d["complete"]} / requested: {d["queries_requested"]}; partial: {d["partial"]}; errors: {d["errors"]}</p><p><a href="{url}">Original Actions run</a></p><p>This is a mention-rate observation, not a validated tool recommendation rate.</p></section>')
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Agent recommendations · MOLI Observatory</title><style>body{font:16px/1.55 system-ui;max-width:900px;margin:auto;padding:2rem}section{border:1px solid #8886;border-radius:12px;padding:1.3rem;margin:1rem 0}</style></head><body><p><a href="./">← Web discoverability</a></p><h1>AI-model responses</h1><p>Separate from web-search visibility. Only reviewed, non-synthetic summaries are included. Missing or truncated responses are not considered negative recommendations.</p>'+''.join(sections)+'<p><a href="agent-baselines.json">Agent summaries (JSON)</a></p></body></html>'
    (destination/"agents.html").write_text(page,encoding="utf-8")
