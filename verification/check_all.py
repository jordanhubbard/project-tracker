#!/usr/bin/env python3
"""Run independent runtime/browser checks; this does not create a LitAI receipt."""
from test_tools import NODE, CHROME
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entrypoint', type=Path)
    parser.add_argument('--node', default=NODE)
    parser.add_argument('--output', type=Path, default=Path('_build/independent-checks'))
    args = parser.parse_args()
    entrypoint = args.entrypoint.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    scripts = Path(__file__).resolve().parent
    phases = [
        ('service', [str(scripts / 'check_service.py'), '--', args.node, str(entrypoint)]),
        ('multi-fleet', [str(scripts / 'check_multi_fleet.py'), str(entrypoint),
                         '--node', args.node, '--output', str(output / 'multi-fleet')]),
        ('mac-project-details', [str(scripts / 'check_project_details.py'), str(entrypoint.parent),
                                 '--output', str(output / 'mac-project-details')]),
        ('mac-project-details-ui', [str(scripts / 'check_project_details_browser.py'), str(entrypoint),
                                    '--node', args.node,
                                    '--output', str(output / 'mac-project-details-ui')]),
        ('live-operations', [str(scripts / 'check_live_operations.py'), str(entrypoint),
                             '--node', args.node,
                             '--output', str(output / 'live-operations')]),
        ('browser-login', [str(scripts / 'check_login_browser.py'), str(entrypoint),
                           '--node', args.node, '--output', str(output / 'browser-login')]),
        ('mac-status-ui', [str(scripts / 'check_mac_status_browser.py'), str(entrypoint),
                           str(output / 'mac-status-ui')]),
        ('board', [str(scripts / 'check_browser.py'), str(entrypoint), '--node', args.node,
                   '--output', str(output / 'board')]),
        ('peer-ui', [str(scripts / 'check_peer_browser.py'), str(entrypoint), '--node', args.node,
                     '--output', str(output / 'peer-ui')]),
        ('session-expiry', [str(scripts / 'check_expiry_browser.py'), str(entrypoint), '--node', args.node,
                            '--output', str(output / 'session-expiry')]),
        ('git-states', [str(scripts / 'check_git_states_browser.py'), str(entrypoint),
                        '--node', args.node, '--output', str(output / 'git-states')]),
        ('equal-time-graph', [str(scripts / 'check_graph_browser.py'), str(entrypoint),
                              '--node', args.node, '--output', str(output / 'equal-time-graph')]),
        ('irregular-time-graph', [str(scripts / 'check_graph_browser.py'), str(entrypoint),
                                  '--node', args.node, '--irregular-times',
                                  '--output', str(output / 'irregular-time-graph')]),
    ]
    results = []
    def write_report():
        report = {'kind': 'independent-product-checks', 'entrypoint': str(entrypoint),
                  'complete': len(results) == len(phases),
                  'ok': len(results) == len(phases) and all(r['exit_code'] == 0 for r in results),
                  'phases': results}
        pending = output / 'summary.pending.json'
        pending.write_text(json.dumps(report, indent=2) + '\n')
        pending.replace(output / 'summary.json')
        return report
    write_report()
    for name, arguments in phases:
        command = [sys.executable, *arguments]
        print(f'Running {name}', flush=True)
        start = time.monotonic()
        log_path = output / f'{name}.log'
        with log_path.open('w') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        results.append({'phase': name, 'command': command, 'exit_code': result.returncode,
                        'elapsed_seconds': round(time.monotonic() - start, 2), 'log': str(log_path)})
        print(f'{name}: {"passed" if result.returncode == 0 else "failed"}; {log_path}', flush=True)
        report = write_report()
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
