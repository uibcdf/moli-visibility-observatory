"""Generate public static Pages using reviewed, versioned summary records only.

Never ingest API credentials, raw search responses, private artifacts or synthetic runs.
"""
import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINES = ROOT / "data" / "baselines"

def validated_records(directory=BASELINES):
    records = []
    for source in sorted(Path(directory).glob("*.summary.json")):
        d = json.loads(source.read_text(encoding="utf-8"))
        required = ("date","provider","run_url","benchmark_version","queries_requested","complete","partial","errors","k","presence_at_10","mrr_at_10","hits","limitations")
        if d.get("schema_version") != "baseline-summary-v1" or d.get("track") != "web_search":
            raise ValueError(f"Unsupported baseline schema: {source}")
        if any(key not in d for key in required):
            raise ValueError(f"Missing fields in {source}")
        n = d["complete"] + d["partial"] + d["errors"]
        if d["complete"] < 0 or n != d["queries_requested"]:
            raise ValueError(f"Invalid sample counts in {source}")
        hits = d["hits"]
        if len(hits) > d["complete"] or any(not 1 <= hit["rank"] <= d["k"] for hit in hits):
            raise ValueError(f"Invalid rank information in {source}")
        if d["k"] != 10 or d["complete"] == 0:
            raise ValueError("Only complete-query denominator and k=10 currently supported")
        if abs(d["presence_at_10"] - len(hits)/d["complete"]) > 1e-10:
            raise ValueError("Presence does not reconcile with rank data")
        if abs(d["mrr_at_10"] - sum(1/h["rank"] for h in hits)/d["complete"]) > 1e-10:
            raise ValueError("MRR does not reconcile with rank data")
        if d.get("synthetic"):
            raise ValueError("Synthetic data may not be published as a real baseline")
        records.append(d)
    return records

def render(records, output):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "baselines.json").write_text(json.dumps(records, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
    e = html.escape
    blocks = []
    for d in reversed(records):
        run = e(d["run_url"], quote=True)
        stats = f'<div class="stats"><div><b>{d["complete"]}/{d["queries_requested"]}</b><span>evaluable queries</span></div><div><b>{d["presence_at_10"]:.0%}</b><span>Presence@10</span></div><div><b>{d["mrr_at_10"]:.3f}</b><span>MRR@10</span></div></div>'
        hits = "".join(f'<li><code>{e(h["query_id"])}</code> · rank {h["rank"]} · <a href="{e(h["url"],quote=True)}">{e(h["title"])}</a></li>' for h in d["hits"])
        warnings = "".join(f"<li>{e(str(x))}</li>" for x in d["limitations"])
        blocks.append(f'<section><div class="eyebrow">{e(d["date"])} · {e(d["provider"])} · {e(d.get("mode",""))}</div><h2>MolSysMT web discoverability</h2>{stats}<h3>Detected results</h3><ul>{hits or "<li>No canonical hits</li>"}</ul><details><summary>Scope and limitations</summary><ul>{warnings}</ul></details><p><a href="{run}">Original GitHub Actions run ↗</a></p></section>')
    display = "".join(blocks) if blocks else "<section><h2>No reviewed baseline yet</h2><p>Only reviewed baseline summaries are published. Synthetic fixtures are excluded.</p></section>"
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Reproducible observations of scientific-software web discoverability."><title>MOLI Visibility Observatory</title><style>:root{{color-scheme:light dark}}body{{font:16px/1.55 system-ui,sans-serif;max-width:940px;margin:auto;padding:2rem 1.2rem}}header{{margin-bottom:2rem}}h1{{font-size:2.2rem;letter-spacing:-.035em;margin-bottom:0}}h2{{margin-top:.5rem}}section{{padding:1.5rem;border:1px solid #8886;border-radius:12px;margin:1.4rem 0}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem}}.stats div{{padding:1rem;background:color-mix(in srgb,CanvasText 5%,Canvas);border-radius:9px}}.stats b{{display:block;font-size:1.7rem}}.stats span{{font-size:.85rem;opacity:.75}}.eyebrow,small{{opacity:.7}}.notice{{padding:1rem 1.3rem;border-left:4px solid currentColor;background:color-mix(in srgb,CanvasText 5%,Canvas)}}a{{color:inherit;text-decoration-thickness:1px;text-underline-offset:3px}}li{{margin:.4rem 0}}footer{{margin:2rem 0}}</style></head><body><header><small>UIBCDF · Open scientific software observability</small><h1>MOLI Visibility Observatory</h1><p>Evidence-backed monitoring of how scientific software is found in web search.</p></header><aside class="notice"><strong>Web discovery ≠ AI-agent recommendation.</strong> Scores are specific to the search provider, query set and capture date. They do not measure scientific merit. AI-model results are reported independently, with no composite consensus score.</aside>{display}<footer><a href="agents.html">AI-model results</a> · <a href="baselines.json">Reviewed baseline dataset (JSON)</a> · <a href="https://github.com/uibcdf/moli-visibility-observatory/blob/main/docs/methodology.md">Methodology</a> · <a href="https://github.com/uibcdf/moli-visibility-observatory">Source code</a></footer></body></html>"""
    (out / "index.html").write_text(page, encoding="utf-8")
    (out / ".nojekyll").write_text("",encoding="utf-8")
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="build/public-site")
    args=parser.parse_args()
    records=validated_records()
    render(records,args.output)
    from visibility_observatory.agent_publish import read_agent_summaries, render_agents
    render_agents(read_agent_summaries(),args.output)
    print(f"Published {len(records)} reviewed baseline summaries")
if __name__=="__main__":
    main()
