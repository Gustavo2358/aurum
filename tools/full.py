#!/usr/bin/env python3
"""One reproducible final gate; recorded PASS always comes from process success."""
import importlib.metadata,json,platform,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts'
def main():
 ART.mkdir(exist_ok=True)
 commands=[['make','test-fast'],[sys.executable,'harness/adversarial.py','--report','artifacts/adversarial.json'],[sys.executable,'harness/numeric_properties.py'],[sys.executable,'harness/invariants.py'],[sys.executable,'harness/regression_audit.py'],[sys.executable,'tools/mutations.py'],[sys.executable,'tools/instrument.py','--mode','sanitize'],[sys.executable,'tools/instrument.py','--mode','coverage'],[sys.executable,'tools/export.py'],[sys.executable,'tools/joern_smoke.py']]
 report={'status':'RUNNING','commands':[],'versions':{'python':platform.python_version(),'gherkin-official':importlib.metadata.version('gherkin-official'),'libclang':importlib.metadata.version('libclang'),'cc':subprocess.check_output(['cc','--version'],text=True).splitlines()[0]}}
 path=ART/'full.json'
 for index,cmd in enumerate(commands):
  print('RUN '+' '.join(cmd),flush=True);start=time.monotonic()
  r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
  (ART/f'full-{index:02d}.log').write_text(r.stdout+r.stderr)
  report['commands'].append({'command':cmd,'exit':r.returncode,'status':'PASS' if r.returncode==0 else 'FAIL','seconds':round(time.monotonic()-start,2),'log':f'artifacts/full-{index:02d}.log'})
  print(r.stdout[-2500:],flush=True)
  if r.returncode:
   report['status']='FAIL';path.write_text(json.dumps(report,indent=2)+'\n');print(r.stderr[-4000:],flush=True);return 1
  path.write_text(json.dumps(report,indent=2)+'\n')
 report['status']='PASS';path.write_text(json.dumps(report,indent=2)+'\n');print('FULL PASS');return 0
if __name__=='__main__':raise SystemExit(main())
