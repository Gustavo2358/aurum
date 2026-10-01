#!/usr/bin/env python3
"""Run the same acceptance oracle with instrumented production builds."""
import argparse,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts'
def run(cmd,env=None,cwd=ROOT):
 r=subprocess.run([str(x) for x in cmd],cwd=cwd,env=env,capture_output=True,text=True)
 return {'command':[str(x) for x in cmd],'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['sanitize','coverage'],required=True);args=parser.parse_args()
 folder=ROOT/'build'/args.mode;folder.mkdir(parents=True,exist_ok=True);ART.mkdir(exist_ok=True)
 for pattern in ('*.gcda','*.gcno','*.gcov.json.gz'):
  for old in folder.glob(pattern):old.unlink()
 sources=sorted((ROOT/'subject/src').glob('*.c'));core=[x for x in sources if x.name!='main.c']
 base=['cc','-std=c17','-O1','-g','-Wall','-Wextra','-Wpedantic','-Werror','-I'+str(ROOT/'subject/include')]
 flags=['-fsanitize=address,undefined','-fno-omit-frame-pointer'] if args.mode=='sanitize' else ['--coverage','-O0']
 results=[]
 def checked(cmd,env=None,cwd=ROOT):
  r=run(cmd,env,cwd);results.append(r)
  if r['exit']:
   (ART/(args.mode+'.json')).write_text(json.dumps({'status':'FAIL','runs':results},indent=2)+'\n')
   print(r['stdout'][-5000:]+r['stderr'][-5000:]);raise SystemExit(1)
  print(r['stdout'].strip(),flush=True)
 checked(base+flags+list(map(str,sources))+['-o',str(folder/'aurum')],cwd=folder)
 checked(base+flags+['-fPIC','-shared']+list(map(str,core))+['-o',str(folder/'libaurum.so')],cwd=folder)
 env=dict(os.environ,AURUM_BIN=str(folder/'aurum'),AURUM_LIB=str(folder/'libaurum.so'),AURUM_BINARY=str(folder/'aurum'))
 if args.mode=='sanitize':
  asan=subprocess.check_output(['cc','-print-file-name=libasan.so'],text=True).strip()
  env.update(LD_PRELOAD=asan,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
 checked([sys.executable,ROOT/'harness/run.py','--self-test','--report','artifacts/'+args.mode+'-gherkin.json'],env)
 cli_env=env.copy()
 if args.mode=='sanitize':
  cli_env.pop('LD_PRELOAD',None);cli_env['ASAN_OPTIONS']='detect_leaks=1:halt_on_error=1'
 checked([sys.executable,ROOT/'harness/protocol_adversarial.py'],cli_env)
 checked([sys.executable,ROOT/'harness/adversarial.py','--binary',folder/'aurum','--report','artifacts/'+args.mode+'-adversarial.json'],cli_env)
 if (ROOT/'harness/numeric_properties.py').exists():checked([sys.executable,ROOT/'harness/numeric_properties.py'],env)
 if (ROOT/'harness/invariants.py').exists():checked([sys.executable,ROOT/'harness/invariants.py'],env)
 if (ROOT/'harness/regression_audit.py').exists():checked([sys.executable,ROOT/'harness/regression_audit.py'],env)
 coverage={}
 if args.mode=='coverage':
  checked(['gcov','--json-format','--branch-probabilities']+list(map(str,folder.glob('*.gcda'))),cwd=folder)
  import gzip
  merged={}
  for p in folder.glob('*.gcov.json.gz'):
   data=json.loads(gzip.decompress(p.read_bytes()))
   for f in data['files']:
    name=f['file']
    if '/subject/src/' not in name:continue
    target=merged.setdefault(name,{})
    for row in f['lines']:
     record=target.setdefault(row['line_number'],{'count':0,'branches':{}});record['count']+=row['count']
     for i,branch in enumerate(row.get('branches',[])):record['branches'][i]=record['branches'].get(i,0)+branch['count']
  for name,lines in merged.items():
   coverage[str(Path(name).relative_to(ROOT))]={'lines':len(lines),'lines_hit':sum(x['count']>0 for x in lines.values()),'branches':sum(len(x['branches']) for x in lines.values()),'branches_hit':sum(sum(n>0 for n in x['branches'].values()) for x in lines.values())}
 status={'status':'PASS','mode':args.mode,'runs':results,'coverage':coverage,'scope':'ASan+UBSan execute full Gherkin via shared C; CLI leak detection enabled separately. Coverage is execution evidence, not semantic correctness.'}
 (ART/(args.mode+'.json')).write_text(json.dumps(status,indent=2)+'\n')
 print(json.dumps({'status':'PASS','mode':args.mode,'coverage':coverage}))
if __name__=='__main__':main()
