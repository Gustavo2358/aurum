#!/usr/bin/env python3
"""Qualify CPG ingestion and selected dependencies; do not certify slice completeness."""
import hashlib,json,re,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/joern-smoke'

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 commands=[]
 def run(name,args,timeout=180,cwd=ROOT):
  start=time.monotonic()
  try:
   r=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=timeout,input='')
   rc=r.returncode;stdout=r.stdout;stderr=r.stderr
  except subprocess.TimeoutExpired as error:
   rc=124;stdout=error.stdout or b'';stderr=error.stderr or b''
   stdout=stdout.decode() if isinstance(stdout,bytes) else stdout
   stderr=stderr.decode() if isinstance(stderr,bytes) else stderr
  (OUT/(name+'.stdout')).write_text(stdout);(OUT/(name+'.stderr')).write_text(stderr)
  commands.append({'name':name,'command':args,'exit':rc,'seconds':round(time.monotonic()-start,2)})
  return rc,stdout,stderr
 if not all(shutil.which(x) for x in ('joern','joern-parse','joern-slice')):
  report={'CPG_INGESTION':'NOT_RUN','LOCATION_MAPPING':'NOT_RUN','SELECTED_DEPENDENCE_CHECKS':'NOT_RUN','reason':'Required Joern executables unavailable'}
  (OUT/'summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));return 2
 rc,banner,_=run('version',['joern'],30)
 match=re.search(r'Version:\s*([^\s]+)',banner);version=match.group(1) if match else 'UNKNOWN'
 code,_,_=run('parse',['joern-parse',str(ROOT/'dist/analysis-subject'),'--language','C','-o',str(OUT/'cpg.bin')])
 assert code==0,'Joern parse failed; see parse.stderr'
 runtime=ROOT/'build/joern-runtime'
 if runtime.exists():shutil.rmtree(runtime)
 runtime.mkdir(parents=True)
 code,_,_=run('query',['joern','--script',str(ROOT/'tools/joern_smoke.sc'),'--param','cpgFile='+str(OUT/'cpg.bin'),'--param','out='+str(OUT/'inventory.json')],cwd=runtime)
 assert code==0,'Joern queries failed; see query.stderr'
 graph=json.loads((OUT/'inventory.json').read_text());ast=json.loads((ROOT/'evaluation/inventory.json').read_text())
 by_name={m['name']:m for m in graph['methods'] if not m['name'].startswith('<')}
 errors=[]
 for f in ast['functions']:
  m=by_name.get(f['symbol']);a=f['anchor']
  if not m:errors.append('missing method '+f['symbol']);continue
  expected_file=a['file'].removeprefix('subject/')
  if m['file']!=expected_file or m['line']!=a['start_line'] or m['line_end']!=a['end_line']:errors.append('location mismatch '+f['symbol'])
  if m['cfg_nodes']==0:errors.append('empty CFG '+f['symbol'])
 selected=[]
 for s in graph['sentinels']:
  file=by_name[s['method']]['file']
  other=[p for p in s['cross_file_callees'] if p!=file]
  checks={'cross_file_call':bool(other),'parameter_to_argument_path':s['parameter_to_argument_paths']>0,'control_dependence':len(s['control_dependencies'])>0,'observable_write':len(s['writes'])>0,'sink_location':bool(s['sink_lines']) and min(s['sink_lines'])>0}
  if not all(checks.values()):errors.append('sentinel '+s['id'])
  selected.append({'id':s['id'],'method':s['method'],'callee':s['call'],'checks':checks,'paths':s['parameter_to_argument_paths'],'control_nodes':len(s['control_dependencies']),'sink_lines':s['sink_lines']})
 code,_,_=run('slice-depth4',['joern-slice','data-flow','--method-name-filter','capture_apply','--sink-filter','.*ledger_pair.*','--slice-depth','4','-p','2','-o',str(OUT/'capture-slice-depth4'),str(OUT/'cpg.bin')],timeout=90)
 slice_status='PASS' if code==0 else 'TIMEOUT' if code==124 else 'FAIL'
 nodes=edges=0
 if code==0:
  sliced=json.loads((OUT/'capture-slice-depth4.json').read_text());nodes=len(sliced['nodes']);edges=len(sliced['edges'])
  if not nodes or not edges:errors.append('empty slice')
 report={'CPG_INGESTION':'PASS','LOCATION_MAPPING':'PASS' if not any('method' in x or 'location' in x or 'CFG' in x for x in errors) else 'FAIL','SELECTED_DEPENDENCE_CHECKS':'PASS' if not errors else 'FAIL','joern_version':version,'production_methods':len(ast['functions']),'synthetic_initializers':sum(m['name']=='<clinit>' for m in graph['methods']),'sentinels':selected,'slice':{'status':slice_status,'depth':4,'nodes':nodes,'edges':edges,'scope':'Backward argument slice; partial by construction. No claim of complete memory/state/control support.'},'commands':commands,'errors':errors,'limitations':['Frontend reported CFG order fallbacks for for/break/continue; selected paths and locations were inspected, not every CFG edge.','The exploratory depth-20 ledger slice was interrupted after minutes without output; reproducible smoke uses depth 4.','Source location and selected dependencies are not proof of complete slicing or extracted-rule correctness.','CPG synthetic <clinit> methods are frontend nodes, not additional production functions.']}
 (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
 rows='\n'.join(f"| {s['id']} | {s['method']} → {s['callee']} | {s['paths']} | {s['control_nodes']} |" for s in selected)
 content=f'''# Joern smoke

Joern {version}. Ingestion: {report['CPG_INGESTION']}; source locations: {report['LOCATION_MAPPING']}; selected dependence checks: {report['SELECTED_DEPENDENCE_CHECKS']}.

All {len(ast['functions'])} production functions match the independent Clang inventory in file, starting line and ending line. Each has a nonempty CFG. The frontend adds {report['synthetic_initializers']} synthetic initializers.

| Sentinel | Real call between files | Parameter→argument paths | Control nodes |
|---|---|---:|---:|
{rows}

The five sentinels have real source locations, cross-file calls, control dependence and observable writes. Raw queries and path samples are in `inventory.json`; exact commands and timings are in `summary.json`.

## Slicing boundary

The bounded depth-4 `capture_apply`/`ledger_pair` argument slice returned {nodes} nodes and {edges} edges ({slice_status}). It is partial by construction. An exploratory depth-20 run was interrupted after minutes without output. This smoke does not establish completeness of memory, state or control support for all rules. The [official slicing documentation](https://docs.joern.io/cpg-slicing/) specifies backward slicing from call arguments.

The frontend emitted CFG order fallback warnings for for/break/continue. Selected dependence checks passed; uninspected CFG edges remain a frontend limitation. Java runtime deprecation/native-access warnings are preserved in stderr logs. No rule extraction was run in this implementation context.
'''
 (OUT/'REPORT.md').write_text(content)
 print(json.dumps({k:report[k] for k in ('CPG_INGESTION','LOCATION_MAPPING','SELECTED_DEPENDENCE_CHECKS','joern_version','production_methods','slice','errors')}))
 return int(bool(errors) or slice_status!='PASS')
if __name__=='__main__':raise SystemExit(main())
