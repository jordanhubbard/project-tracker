#!/usr/bin/env python3
"""Independent black-box service checks, always against a disposable local database.

Usage: python verification/check_service.py -- /path/to/python /path/to/main.py
The command is launched with --litai-serve, --host and --port appended.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import uuid
import urllib.error
import urllib.request


def check(command: list[str]) -> None:
    if not command:
        raise SystemExit('Pass a runnable artifact command after --')
    with tempfile.TemporaryDirectory(prefix='tracker-independent-') as temporary:
        root = Path(temporary)
        environment = {k: v for k, v in os.environ.items()
                       if not k.startswith(('TRACKER_', 'MAC_', 'OPENAI_'))}
        environment.update(TRACKER_DATA_DIR=str(root / 'data'),
                           TRACKER_MAC_URL='', TRACKER_LLM_KEY='',
                           PYTHONDONTWRITEBYTECODE='1')
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        base = f'http://127.0.0.1:{port}'
        process = None
        log = (root / 'server.log').open('w+')

        def request(method, path, body=None, expected=200):
            data = None if body is None else json.dumps(body).encode()
            req = urllib.request.Request(base + path, data=data, method=method,
                                         headers={'Content-Type': 'application/json'})
            try:
                response = urllib.request.urlopen(req, timeout=8)
            except urllib.error.HTTPError as error:
                response = error
            with response:
                text = response.read().decode()
                assert response.status == expected, (method, path, response.status, text)
            return json.loads(text) if text else None

        def start():
            nonlocal process
            process = subprocess.Popen(command + ['--litai-serve', '--host', '127.0.0.1',
                                                  '--port', str(port)],
                                       env=environment, stdout=log, stderr=log)
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise AssertionError('Service exited before readiness')
                try:
                    request('GET', '/health')
                    return
                except (OSError, AssertionError):
                    time.sleep(0.1)
            raise AssertionError('Service did not become ready')

        def stop():
            nonlocal process
            if process is not None:
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                process = None

        def rpc(method, params):
            return request('POST', '/a2a', {'jsonrpc': '2.0', 'id': str(uuid.uuid4()),
                                           'method': method, 'params': params})

        try:
            start()
            repo = request('POST', '/api/repos', {
                'name': 'Independent acceptance',
                'remote_url': 'https://example.test/team/acceptance.git'}, 201)
            assert repo['authority'] == 'local', repo
            repo_id = repo['id']
            task = request('POST', f'/api/repos/{repo_id}/tasks', {
                'title': 'Persist and edit', 'description': 'Initial description'}, 201)
            task_id = task['id']
            changed = request('PATCH', f'/api/tasks/{task_id}', {
                'revision': task['revision'], 'title': 'Edited title',
                'state': 'in_progress', 'labels': ['integration'],
                'checklist': [{'text': 'Restart proof', 'done': True}]})
            assert changed['title'] == 'Edited title', changed
            assert changed['state'] == 'in_progress', changed
            assert changed['revision'] > task['revision'], changed
            request('PATCH', f'/api/tasks/{task_id}', {
                'revision': task['revision'], 'title': 'Stale writer'}, 409)
            stop()
            start()
            restored = request('GET', f'/api/tasks/{task_id}')
            assert restored == changed, (restored, changed)
            message = {'kind': 'message', 'role': 'user', 'messageId': str(uuid.uuid4()),
                       'parts': [{'kind': 'data', 'data': {
                           'operation': 'create_task', 'arguments': {
                               'repo_id': repo_id, 'title': 'Peer idempotency'}}}]}
            result = rpc('message/send', {'message': message})
            assert 'result' in result, result
            peer_task = result['result']
            assert peer_task['kind'] == 'task', peer_task
            assert peer_task['status']['state'] == 'completed', peer_task
            repeated = rpc('message/send', {'message': message})
            assert repeated['result']['id'] == peer_task['id'], repeated
            fetched = rpc('tasks/get', {'id': peer_task['id']})
            assert fetched['result']['id'] == peer_task['id'], fetched
            cancelled = rpc('tasks/cancel', {'id': peer_task['id']})
            assert cancelled['error']['code'] == -32002, cancelled
            rows = request('GET', f'/api/repos/{repo_id}/tasks')
            assert sum(row['title'] == 'Peer idempotency' for row in rows['items']) == 1, rows
            stop()
            start()
            persisted = rpc('tasks/get', {'id': peer_task['id']})
            assert persisted['result']['id'] == peer_task['id'], persisted
            print(json.dumps({'ok': True, 'checks': [
                'local authority', 'task attributes and state', 'revision conflict',
                'database restart', 'A2A durable tasks', 'A2A idempotent creation',
                'A2A terminal cancellation rejection']}))
        finally:
            stop()
            log.close()


if __name__ == '__main__':
    argv = sys.argv[1:]
    if argv[:1] == ['--']:
        argv = argv[1:]
    check(argv)
