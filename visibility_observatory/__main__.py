import argparse, json, pathlib, datetime, html
from urllib.parse import urlparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(p): return json.loads(pathlib.Path(p).read_text())
def target(url):
    u=urlparse(url);host=(u.hostname or '').lower();path=u.path.lower()
    return (host=='github.com' and (path.rstrip('/')=='/uibcdf/molsysmt' or path.startswith('/uibcdf/molsysmt/'))) or ((host=='uibcdf.org' or host.endswith('.uibcdf.org')) and 'molsysmt' in path)
def compute(run,bench,k):
    if bench.get('version')=='2.0': raise ValueError('V2 requires separate stratum-aware analysis; pooled web metrics are invalid')
    if run.get('track')!='web_search': raise ValueError('Only web_search is supported; agent scoring is not implemented')
    if run.get('schema_version')!='1' or run.get('benchmark_version')!=bench['version']: raise ValueError('Version mismatch')
    if not run.get('provider') or not run.get('collected_at_utc'): raise ValueError('Missing provenance')
    date=datetime.datetime.fromisoformat(run['collected_at_utc'].replace('Z','+00:00'))
    if date.tzinfo is None or date.utcoffset()!=datetime.timedelta(0): raise ValueError('UTC required')
    ids={q['id']:q for q in bench['queries']};seen=set();rows=[]
    for s in run.get('samples',[]):
        key=s.get('query_id'); status=s.get('status')
        if key not in ids or key in seen or status not in ('complete','partial','error'): raise ValueError('Invalid sample')
        seen.add(key);results=s.get('results',[])
        if not isinstance(results,list): raise ValueError('results must be list')
        if status=='complete' and 'results' not in s: raise ValueError('Missing complete results')
        if any(not isinstance(r,dict) or not isinstance(r.get('url'),str) or urlparse(r['url']).scheme not in ('http','https') for r in results): raise ValueError('Invalid URL')
        eligible=status=='complete' and len(results)>=k
        rank=next((i for i,r in enumerate(results[:k],1) if target(r['url'])),None) if eligible else None
        rows.append(dict(query_id=key,family=ids[key]['family'],status=status,count=len(results),eligible=eligible,rank=rank))
    qualified=[r for r in rows if r['eligible']];n=len(qualified)
    hits=sum(r['rank'] is not None for r in qualified)
    return dict(provider=run['provider'],synthetic=bool(run.get('synthetic')),timestamp=run['collected_at_utc'],track='web_search',benchmark_version=bench['version'],k=k,total=len(ids),evaluable=n,hits=hits,presence=hits/n if n else None,mrr=sum(1/r['rank'] for r in qualified if r['rank'])/n if n else None,rows=rows)
def render(m,out):
    p=pathlib.Path(out);p.mkdir(parents=True,exist_ok=True)
    (p/'metrics.json').write_text(json.dumps(m,indent=2)+'\n')
    warning='SYNTHETIC DEMONSTRATION: NOT REAL OBSERVATIONS' if m['synthetic'] else 'Exploratory web search dataset; NOT agent recommendations'
    values=''.join('<tr>'+''.join('<td>'+html.escape(str(r[x]))+'</td>' for x in ('query_id','family','status','count','eligible','rank'))+'</tr>' for r in m['rows'])
    page=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>MOLI Visibility Observatory</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{{font:16px/1.5 system-ui;max-width:960px;margin:auto;padding:2rem;color:#233}}.note{{background:#eee;padding:1.5rem}}table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #ddd;padding:.7rem;text-align:left}}</style></head><body><h1>MOLI Visibility Observatory</h1><p class="note"><strong>{warning}</strong>. Incomplete samples never count as failures or non-hits. No live agent results have been collected.</p><p>{html.escape(m['provider'])} · {html.escape(m['timestamp'])}</p><h2>Web search metrics (k={m['k']})</h2><p>Eligible: {m['evaluable']}/{m['total']} · Presence@k: {m['presence'] if m['presence'] is not None else 'Not measurable'} · MRR@k: {m['mrr'] if m['mrr'] is not None else 'Not measurable'}</p><h2>Query detail</h2><table><tr><th>ID</th><th>Family</th><th>Status</th><th>Results</th><th>Eligible</th><th>Rank</th></tr>{values}</table><p><a href="metrics.json">JSON metrics</a> | <a href="https://github.com/uibcdf/moli-visibility-observatory/blob/main/docs/methodology.md">Methodology</a></p></body></html>"""
    (p/'index.html').write_text(page)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True);parser.add_argument('--output',default='build/site');parser.add_argument('--k',type=int,default=10);a=parser.parse_args()
    if a.k<1: parser.error('k must be positive')
    m=compute(load(a.run),load(ROOT/'queries/v1.json'),a.k);render(m,a.output);print(json.dumps({'evaluable':m['evaluable'],'presence':m['presence'],'mrr':m['mrr']}))
if __name__=='__main__':main()
