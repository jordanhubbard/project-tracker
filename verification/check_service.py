#!/usr/bin/env python3
"""Independent black-box service checks, always against a disposable local database.

Usage: python verification/check_service.py -- /path/to/python /path/to/main.py
The command is launched with --litai-serve, --host and --port appended.
"""
from __future__ import annotations

import asyncio
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
            async def mcp_roundtrip():
                from mcp import Client
                async with Client(base + '/mcp', read_timeout_seconds=8) as client:
                    tools = await client.list_tools()
                    names = {tool.name for tool in tools.tools}
                    assert {'list_repositories', 'get_task', 'create_task',
                            'update_task', 'list_sessions', 'get_branch_graph'} <= names, names
                    result = await client.call_tool('get_task', {'task_id': task_id})
                    assert not result.isError, result
                    assert task_id in result.model_dump_json(), result
                    resources = await client.list_resources()
                    assert any(str(item.uri) == 'tracker://repositories'
                               for item in resources.resources), resources
                    result = await client.read_resource('tracker://repositories')
                    assert repo_id in result.model_dump_json(), result
            asyncio.run(asyncio.wait_for(mcp_roundtrip(), timeout=30))

            git_root = root / 'git-fixture'
            git_root.mkdir()
            git_env = dict(environment, GIT_AUTHOR_NAME='Tracker acceptance',
                           GIT_AUTHOR_EMAIL='tracker@example.test',
                           GIT_COMMITTER_NAME='Tracker acceptance',
                           GIT_COMMITTER_EMAIL='tracker@example.test',
                           GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
            def git(*args):
                return subprocess.check_output(['git', '-C', str(git_root), *args],
                                               env=git_env, stderr=subprocess.PIPE,
                                               text=True, timeout=8).strip()
            git('init', '-b', 'main')
            (git_root / 'base.txt').write_text('base')
            git('add', '.')
            git('commit', '-m', 'Base commit')
            base_hash = git('rev-parse', 'HEAD')
            git('checkout', '-b', 'feature')
            (git_root / 'feature.txt').write_text('feature')
            git('add', '.')
            git('commit', '-m', 'Feature commit')
            feature_hash = git('rev-parse', 'HEAD')
            git('checkout', 'main')
            (git_root / 'main.txt').write_text('main')
            git('add', '.')
            git('commit', '-m', 'Main commit')
            main_hash = git('rev-parse', 'HEAD')
            git('merge', '--no-ff', 'feature', '-m', 'Merge feature')
            merge_hash = git('rev-parse', 'HEAD')
            git_repo = request('POST', '/api/repos', {
                'name': 'Git DAG fixture', 'local_path': str(git_root)}, 201)
            graph = request('GET', f"/api/repos/{git_repo['id']}/graph")
            commits = {commit['hash']: commit for commit in graph['commits']}
            assert set(commits[merge_hash]['parents']) == {feature_hash, main_hash}, graph
            assert commits[feature_hash]['parents'] == [base_hash], graph
            assert commits[main_hash]['parents'] == [base_hash], graph
            print(json.dumps({'ok': True, 'checks': [
                'local authority', 'task attributes and state', 'revision conflict',
                'database restart', 'A2A durable tasks', 'A2A idempotent creation',
                'A2A terminal cancellation rejection', 'official MCP client roundtrip',
                'real Git fork and merge parent edges']}))
        finally:
            stop()
            log.close()


if __name__ == '__main__':
    argv = sys.argv[1:]
    if argv[:1] == ['--']:
        argv = argv[1:]
    check(argv)
