#!/usr/bin/env python3
"""Export production by allowlist; keep every evaluation input separate."""
import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 dist=ROOT/'dist';subject=dist/'analysis-subject';oracle=dist/'evaluation-oracle'
 dist.mkdir(exist_ok=True)
 for p in (subject,oracle):
  if p.exists():shutil.rmtree(p)
  p.mkdir()
 paths=sorted((ROOT/'subject/src').glob('*.c'))+sorted((ROOT/'subject/include').glob('*.h'))
 for path in paths:
  dest=subject/path.relative_to(ROOT/'subject');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
 make='''CC ?= cc
CFLAGS ?= -std=c17 -O2 -Wall -Wextra -Wpedantic -Werror
SOURCES := $(wildcard src/*.c)
all: aurum
aurum: $(SOURCES) include/aurum.h
\t$(CC) $(CFLAGS) -Iinclude $(SOURCES) -o $@
clean:
\trm -f aurum
'''
 (subject/'Makefile').write_text(make)
 for directory in ('docs','evaluation','harness'):
  shutil.copytree(ROOT/directory,oracle/directory,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for filename in ('AGENTS.md','START_HERE.md','README.md','PROGRESS.md'):
  shutil.copyfile(ROOT/filename,oracle/filename)
 shutil.copyfile(ROOT/'evaluation/criteria-public.json',dist/'criteria-public.json')
 forbidden=('BR-','FR-','SC-','.feature','oracle','expected','scenario')
 for path in subject.rglob('*'):
  if not path.is_file():continue
  content=path.read_text()
  for needle in forbidden:
   if needle in content:raise AssertionError(f'Forbidden oracle marker {needle} in {path}')
 manifest={}
 for name,path in [('analysis-subject',subject),('evaluation-oracle',oracle)]:
  manifest[name]=[{'path':str(p.relative_to(path)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(path.rglob('*')) if p.is_file()]
 with tempfile.TemporaryDirectory(prefix='aurum-isolated-') as temp:
  dest=Path(temp)/'subject';shutil.copytree(subject,dest)
  result=subprocess.run(['make','all'],cwd=dest,capture_output=True,text=True)
  if result.returncode:raise AssertionError(result.stdout+result.stderr)
  (ROOT/'artifacts').mkdir(exist_ok=True)
  (ROOT/'artifacts/export-build.txt').write_text(result.stdout+result.stderr)
  seed=Path(temp)/'seed';seed.write_text('CLOCK now=144600\nACCOUNT id=A1\nCARD id=C1 account_id=A1\nMERCHANT id=M1\n')
  run=subprocess.run([str(dest/'aurum'),'--seed',str(seed),'--commands','-'],input='QUOTE amount=123 currency=USD\n',capture_output=True,text=True)
  assert run.returncode==0
  row=json.loads(run.stdout);assert row['principal']==615 and row['fee']==12,row
 (dist/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'export':'PASS','production_files':len(manifest['analysis-subject']),'isolated_build':'PASS','isolated_quote':'PASS','leak_scan':'PASS'}))
if __name__=='__main__': main()
