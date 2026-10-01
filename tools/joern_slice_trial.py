#!/usr/bin/env python3
"""Run one bounded native Joern slicing experiment, keeping the smoke separate."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--depth', type=int, default=20)
    parser.add_argument('--timeout-seconds', type=int, default=1800)
    args = parser.parse_args()
    if args.depth < 1 or args.timeout_seconds < 1:
        parser.error('depth and timeout must be positive')
    folder = ROOT / 'artifacts' / f'joern-depth{args.depth}'
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / 'capture-slice.json'
    if output.exists():
        parser.error(f'refusing to reuse existing result: {output}')
    cpg = ROOT / 'artifacts/joern-smoke/cpg.bin'
    command = ['joern-slice', 'data-flow', '--method-name-filter', 'capture_apply',
               '--sink-filter', '.*ledger_pair.*', '--slice-depth', str(args.depth),
               '-p', '2', '-o', str(folder / 'capture-slice'), str(cpg)]
    bounded = ['/usr/bin/time', '-v', '-o', str(folder / 'resources.txt'),
               'timeout', '--kill-after=10s', str(args.timeout_seconds) + 's', *command]
    report = {'status': 'RUNNING', 'depth': args.depth,
              'timeout_seconds': args.timeout_seconds, 'termination_grace_seconds': 10,
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'cpg_sha256': hashlib.sha256(cpg.read_bytes()).hexdigest(),
              'command': command, 'bounded_command': bounded,
              'scope': 'Native Joern slicing experiment; no PGC rule extraction or completeness evaluation.'}
    report_path = folder / 'summary.json'
    start = time.monotonic()
    with (folder / 'stdout.log').open('w') as stdout, (folder / 'stderr.log').open('w') as stderr:
        process = subprocess.Popen(bounded, cwd=ROOT, stdout=stdout, stderr=stderr)
        report['supervisor_pid'] = process.pid
        report_path.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': 'RUNNING', 'pid': process.pid, 'limit_seconds': args.timeout_seconds}), flush=True)
        while process.poll() is None:
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                print(json.dumps({'status': 'RUNNING', 'elapsed_seconds': round(time.monotonic()-start, 1)}), flush=True)
    report['elapsed_seconds'] = round(time.monotonic() - start, 3)
    report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report['exit_code'] = process.returncode
    report['status'] = 'COMPLETED' if process.returncode == 0 else 'TIMEOUT' if process.returncode in (124, 137) else 'FAILED'
    if process.returncode == 0:
        try:
            graph = json.loads(output.read_text())
            nodes, edges = graph['nodes'], graph['edges']
            assert isinstance(nodes, list) and isinstance(edges, list) and nodes and edges
            ids = {n['id'] for n in nodes}
            assert len(ids) == len(nodes)
            assert all(e['src'] in ids and e['dst'] in ids for e in edges)
            report['result'] = {'nodes': len(nodes), 'edges': len(edges),
                                'bytes': output.stat().st_size,
                                'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                                'structural_validation': 'PASS'}
            shallow = json.loads((ROOT / 'artifacts/joern-smoke/capture-slice-depth4.json').read_text())
            old_ids = {n['id'] for n in shallow['nodes']}
            report['comparison_depth4'] = {'nodes': len(shallow['nodes']), 'edges': len(shallow['edges']),
                                           'shared_nodes': len(ids & old_ids), 'additional_nodes': len(ids-old_ids),
                                           'depth4_nodes_absent': len(old_ids-ids),
                                           'meaning': 'Structural comparison within this CPG only; no semantic sufficiency claim.'}
        except (OSError, ValueError, KeyError, AssertionError) as error:
            report['status'] = 'INVALID_RESULT'
            report['validation_error'] = str(error)
    elif output.exists():
        report['partial_output_bytes'] = output.stat().st_size
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)
    return 0 if report['status'] == 'COMPLETED' else 2

if __name__ == '__main__':
    raise SystemExit(main())
