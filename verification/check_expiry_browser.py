#!/usr/bin/env python3
"""Verify live expiry of a disposable heartbeat, without another application request."""
from test_tools import NODE, CHROME
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
import uuid
from playwright.sync_api import sync_playwright
from service_response import entity_response

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('entrypoint', type=Path)
parser.add_argument('--node', default=NODE)
parser.add_argument('--output', type=Path, default=Path('_build/expiry-browser'))
args = parser.parse_args()
out = args.output
out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='tracker-expiry-') as data:
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TRACKER_', 'MAC_', 'OPENAI_'))}
    env.update(TRACKER_DATA_DIR=data, TRACKER_MAC_URL='', TRACKER_ACCESS_TOKEN='')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    log = (out / 'server.log').open('w')
    process = subprocess.Popen([args.node, str(args.entrypoint.resolve()), '--litai-serve',
                                '--host', '127.0.0.1', '--port', str(port)],
                               env=env, stdout=log, stderr=log)

    def api(method, path, body=None):
        request = urllib.request.Request(base + path, method=method,
            data=None if body is None else json.dumps(body).encode(),
            headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=5) as response:
            return entity_response(json.load(response))

    try:
        for _ in range(100):
            try:
                api('GET', '/health')
                break
            except OSError:
                time.sleep(.1)
        repo = api('POST', '/api/repos', {'name': 'Expiry fixture',
                    'remote_url': 'https://example.test/expiry/fixture.git'})
        api('POST', '/api/sessions/heartbeat', {'session_id': str(uuid.uuid4()),
            'repo_id': repo['id'], 'hostname': 'synthetic-expiry-host',
            'host_id': 'synthetic-expiry-host', 'cli': 'other', 'pid': os.getpid(),
            'branch': 'main', 'status': 'running'})
        started = time.monotonic()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=CHROME)
            page = browser.new_page(viewport={'width': 1440, 'height': 1000})
            page.set_default_timeout(5000)
            page.goto(base)
            page.get_by_role('button', name=re.compile(r'^Open board(?: for .+)?$',re.I)).or_(
                page.get_by_role('link', name=re.compile(r'^Open board(?: for .+)?$',re.I))).or_(page.locator('.repo-card[role="button"], button.repo-card')).first.click()
            page.get_by_role('tab', name='Fleet', exact=True).or_(
                page.get_by_role('button', name='Fleet', exact=True)).or_(
                page.get_by_role('link', name='Fleet', exact=True)).click()
            row = page.get_by_role('cell', name='synthetic-expiry-host', exact=True).locator('..')
            row.get_by_text(re.compile(r'^(active|running)$', re.I)).wait_for()
            repo_control = page.get_by_role('navigation').get_by_role('button', name=re.compile('Expiry fixture')).locator('..')
            assert re.search(r'\b1\b', repo_control.locator('.badge').inner_text() if repo_control.locator('.badge').count() else repo_control.inner_text()), repo_control.locator('.badge').inner_text() if repo_control.locator('.badge').count() else repo_control.inner_text()
            page.screenshot(path=str(out / 'active.png'), full_page=True)
            print('Waiting for the specified 90-second heartbeat deadline', flush=True)
            stale = row.get_by_text(re.compile(r'^stale$', re.I))
            while time.monotonic() - started < 110 and not stale.is_visible():
                page.wait_for_timeout(500)
            elapsed = round(time.monotonic() - started, 2)
            result = {'elapsed_seconds': elapsed, 'row': row.inner_text(),
                      'sidebar': repo_control.locator('.badge').inner_text() if repo_control.locator('.badge').count() else repo_control.inner_text(), 'stale_visible': stale.is_visible()}
            result['ok'] = result['stale_visible'] and (bool(re.search(r'\b0\b', result['sidebar'])) or result['sidebar'].strip() == repo['name'])
            (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
            page.screenshot(path=str(out / 'after-deadline.png'), full_page=True)
            browser.close()
            assert result['ok'], result
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        log.close()
