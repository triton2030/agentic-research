import json, subprocess, sys, time
from pathlib import Path
work = Path(__file__).resolve().parent
script = Path(sys.argv[1]).resolve()
results = []
for case in json.loads((work / 'synthetic-cases.json').read_text()):
    started = time.monotonic()
    run = subprocess.run(['uv','run','--offline','--locked','--script',str(script),str(work/'fixture'),'--query',case['query'],'--json','--limit','5'],text=True,capture_output=True)
    if run.returncode:
        raise RuntimeError(run.stderr)
    response = json.loads(run.stdout)
    holders = response.get('holders',[])
    files = [h['file'] for h in holders]
    results.append({**case,'seconds':round(time.monotonic()-started,3),'files':files,'hit_at_5':case['expected_file'] in files if case['expected_file'] else None,'topics':[x['topic'] for x in response.get('topic_candidates',[])],'holder_routes':[h.get('quote_channels',h.get('admitted_by')) for h in holders],'candidate_holders':len(holders),'warnings':response.get('warnings'),'query_domain':response.get('query_domain'),'dense_top1':response.get('dense_top1')})
print(json.dumps(results,ensure_ascii=False,indent=2))
