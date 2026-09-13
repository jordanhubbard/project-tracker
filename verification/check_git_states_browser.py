#!/usr/bin/env python3
"""Check visible empty and truncated real Git histories in isolated Chrome sessions."""
import argparse
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time
import urllib.request
from playwright.sync_api import sync_playwright, expect
from service_response import entity_response

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('entrypoint', type=Path)
parser.add_argument('--node', default='/opt/homebrew/opt/node@22/bin/node')
parser.add_argument('--output', type=Path, default=Path('_build/git-states-browser'))
args = parser.parse_args()
entry = args.entrypoint.resolve(strict=True)
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='tracker-git-states-') as temporary:
    root = Path(temporary).resolve()
    checkout = root / 'checkout'
    checkout.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TRACKER_', 'MAC_', 'OPENAI_'))}
    env.update(TRACKER_DATA_DIR=str(root / 'data'), TRACKER_MAC_URL='',
               TRACKER_ACCESS_TOKEN='', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    subprocess.run(['git', '-C', str(checkout), 'init', '-b', 'main'],
                   env=env, check=True, capture_output=True)
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    def request(method, path, body=None):
        req = urllib.request.Request(base + path, method=method,
              headers={'Content-Type': 'application/json'},
              data=None if body is None else json.dumps(body).encode())
        with urllib.request.urlopen(req, timeout=10) as response:
            return entity_response(json.load(response))
    with (out / 'server.log').open('w') as log:
        process = subprocess.Popen([args.node, str(entry), '--litai-serve', '--host', '127.0.0.1',
                                    '--port', str(port)], env=env, stdout=log, stderr=log)
        results = []
        errors = []
        try:
            for _ in range(100):
                try:
                    request('GET', '/health')
                    break
                except OSError:
                    if process.poll() is not None:
                        raise AssertionError('Service exited during startup')
                    time.sleep(.1)
            repo = request('POST', '/api/repos', {'name': 'History fixture', 'local_path': str(checkout)})
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
                def open_graph(page):
                    page.goto(base)
                    page.get_by_role('button', name=re.compile(r'^Open board(?: for .+)?$')).click()
                    with page.expect_response(lambda response: '/graph' in response.url and response.status == 200) as fetched:
                        page.get_by_role('button', name='Graph', exact=True).or_(
                            page.get_by_role('link', name='Graph', exact=True)).or_(
                            page.get_by_role('tab', name='Graph', exact=True)).click()
                    return entity_response(fetched.value.json())
                for width in (1440, 390):
                    page = browser.new_page(viewport={'width': width, 'height': 1000 if width > 390 else 844})
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    open_graph(page)
                    expect(page.get_by_text(re.compile(r'(no commits|no history|unborn)', re.I)).first).to_be_visible()
                    assert page.locator('svg [role=button]').count() == 0
                    page.screenshot(path=str(out / f'{width}-empty.png'), full_page=True)
                    results.append({'width': width, 'state': 'empty', 'ok': True})
                    page.close()
                stream = []
                for index in range(1, 1006):
                    message = f'History commit {index}\n'
                    stream.append(f'commit refs/heads/main\nmark :{index}\n'
                                  f'committer Fixture <fixture@example.test> {1700000000 + index} +0000\n'
                                  f'data {len(message)}\n{message}')
                    if index > 1:
                        stream.append(f'from :{index - 1}\n')
                    stream.append('\n')
                subprocess.run(['git', '-C', str(checkout), 'fast-import', '--quiet'],
                               input=''.join(stream), text=True, env=env, check=True,
                               capture_output=True, timeout=20)
                graph = request('GET', f"/api/repos/{repo['id']}/graph")
                assert 0 < len(graph['commits']) < 1005
                if 'truncated' in graph:
                    assert graph['truncated']
                known = {c['hash'] for c in graph['commits'] if not c.get('boundary', False)}
                boundary = {parent for c in graph['commits'] if not c.get('boundary', False) for parent in c['parents'] if parent not in known}
                assert boundary
                for width in (1440, 390):
                    page = browser.new_page(viewport={'width': width, 'height': 1000 if width > 390 else 844})
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    rendered_graph = open_graph(page)
                    known = {c['hash'] for c in rendered_graph['commits'] if not c.get('boundary', False)}
                    boundary = {parent for c in rendered_graph['commits'] if not c.get('boundary', False) for parent in c['parents'] if parent not in known}
                    assert boundary and 0 < len(known) < 1005
                    marker = page.locator('svg').get_by_role('button', name=re.compile(next(iter(boundary))[:7])).or_(
                        page.locator('svg').locator('text').filter(has_text=re.compile(next(iter(boundary))[:7])))
                    marker.first.scroll_into_view_if_needed()
                    expect(marker.first).to_be_visible()
                    page.screenshot(path=str(out / f'{width}-boundary.png'), full_page=True)
                    page.get_by_role('button', name='Timeline', exact=True).or_(page.get_by_role('tab', name='Timeline', exact=True)).or_(page.get_by_role('link', name='Timeline', exact=True)).click()
                    page.wait_for_timeout(400)
                    page.screenshot(path=str(out / f'{width}-bounded-timeline.png'), full_page=True)
                    (out / f'{width}-bounded-timeline.aria.txt').write_text(page.locator('body').aria_snapshot())
                    expect(page.locator('svg [role=button]')).to_have_count(len(known), timeout=2000)

                    results.append({'width': width, 'state': 'truncated', 'commits': len(known),
                                    'boundary': sorted(boundary), 'ok': True})
                    page.close()
                browser.close()
            assert not errors, errors
        finally:
            (out / 'result.json').write_text(json.dumps({'checks': results, 'page_errors': errors,
                                                        'ok': len(results) == 4 and not errors}, indent=2) + '\n')
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
