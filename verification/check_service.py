#!/usr/bin/env python3
"""Independent black-box service checks, always against a disposable local database.

Usage: python verification/check_service.py -- /path/to/node /path/to/main.js
The command is launched with --litai-serve, --host and --port appended.
Use --diagnostic-continue before -- to collect later phase failures; any failure
still exits nonzero. Reporter commands use the framework's JSON-array entrypoint.
"""
from __future__ import annotations

import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import urllib.error
import urllib.request


def check(command: list[str], *, diagnostic_continue: bool = False) -> None:
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
        diagnostic_failures = []

        def run_phase(name, operation):
            try:
                operation()
            except Exception as error:
                if not diagnostic_continue:
                    raise
                diagnostic_failures.append({'phase': name, 'error': str(error)[:2000]})
                print(f'Diagnostic phase failed: {name}: {error}', file=sys.stderr)


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
                allowed = expected if isinstance(expected, tuple) else (expected,)
                assert response.status in allowed, (method, path, response.status, text)
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
            workflow = request('GET', f'/api/repos/{repo_id}/states')['items']
            in_progress = next(state['id'] for state in workflow
                               if state.get('name') == 'in_progress')
            task = request('POST', f'/api/repos/{repo_id}/tasks', {
                'title': 'Persist and edit', 'description': 'Initial description'}, 201)
            task_id = task['id']
            changed = request('PATCH', f'/api/tasks/{task_id}', {
                'revision': task['revision'], 'title': 'Edited title',
                'state': in_progress, 'labels': ['integration'],
                'checklist': [{'text': 'Restart proof', 'done': True}]})
            assert changed['title'] == 'Edited title', changed
            assert changed['state'] == in_progress, changed
            assert changed['revision'] > task['revision'], changed
            request('PATCH', f'/api/tasks/{task_id}', {
                'revision': task['revision'], 'title': 'Stale writer'}, 409)
            stop()
            start()
            restored = request('GET', f'/api/tasks/{task_id}')
            assert restored == changed, (restored, changed)
            session_id = str(uuid.uuid4())
            heartbeat = {'session_id': session_id, 'repo_id': repo_id,
                         'hostname': 'fixture-host', 'host_id': 'host-fixture',
                         'cli': 'codex', 'pid': 12345, 'branch': 'main',
                         'task_id': task_id, 'model': None, 'status': 'running'}
            request('POST', '/api/sessions/heartbeat', heartbeat)
            sessions = request('GET', '/api/sessions')['items']
            reported = next(item for item in sessions if item['session_id'] == session_id)
            assert reported['hostname'] == 'fixture-host' and reported['cli'] == 'codex', reported
            assert reported['last_seen_at'], reported
            heartbeat['status'] = 'stopped'
            request('POST', '/api/sessions/heartbeat', heartbeat)
            stopped = next(item for item in request('GET', '/api/sessions')['items']
                           if item['session_id'] == session_id)
            assert stopped['status'] == 'stopped', stopped

            def first_event(after=None):
                headers = {'Accept': 'text/event-stream'}
                if after is not None:
                    headers['Last-Event-ID'] = after
                req = urllib.request.Request(base + '/api/events', headers=headers)
                with urllib.request.urlopen(req, timeout=5) as response:
                    fields = {}
                    for raw_line in response:
                        line = raw_line.decode().rstrip('\r\n')
                        if not line and 'data' in fields and 'id' in fields:
                            return fields
                        key, separator, value = line.partition(':')
                        if separator and key:
                            fields[key] = value.lstrip()
                raise AssertionError('SSE stream ended without a replayable event')
            first = first_event()
            stop()
            start()
            following = first_event(first['id'])
            assert int(following['id']) > int(first['id']), (first, following)
            message = {'kind': 'message', 'role': 'user', 'messageId': str(uuid.uuid4()),
                       'parts': [{'kind': 'data', 'data': {
                           'operation': 'create_task', 'repo_id': repo_id,
                           'task': {'title': 'Peer idempotency'}}}]}
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
                    get_tool = next(tool for tool in tools.tools if tool.name == 'get_task')
                    properties = get_tool.input_schema.get('properties', {})
                    id_key = 'task_id' if 'task_id' in properties else 'id'
                    assert id_key in properties, get_tool
                    result = await client.call_tool('get_task', {id_key: task_id})
                    assert not result.is_error, result
                    assert task_id in result.model_dump_json(), result
                    resources = await client.list_resources()
                    assert any(str(item.uri) == 'tracker://repositories'
                               for item in resources.resources), resources
                    result = await client.read_resource('tracker://repositories')
                    assert repo_id in result.model_dump_json(), result
            asyncio.run(asyncio.wait_for(mcp_roundtrip(), timeout=30))

            def llm_gateway():
                llm_calls = []
                fixture_key = 'disposable-llm-secret-' + str(uuid.uuid4())

                class Gateway(BaseHTTPRequestHandler):
                    def log_message(self, *_):
                        pass

                    def do_POST(self):
                        payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                        llm_calls.append((self.path, self.headers.get('Authorization'), payload))
                        encoded = json.dumps({'choices': [{'message': {
                            'role': 'assistant', 'content': 'Fixture summary of tracker work'}}]}).encode()
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Content-Length', str(len(encoded)))
                        self.end_headers()
                        self.wfile.write(encoded)

                gateway = ThreadingHTTPServer(('127.0.0.1', 0), Gateway)
                gateway_thread = threading.Thread(target=gateway.serve_forever, daemon=True)
                gateway_thread.start()
                try:
                    stop()
                    environment.update(TRACKER_LLM_URL=f'http://127.0.0.1:{gateway.server_port}/v1',
                                       TRACKER_LLM_KEY=fixture_key, TRACKER_LLM_MODEL='fixture-model')
                    start()
                    settings = request('GET', '/api/settings')
                    assert fixture_key not in json.dumps(settings), settings
                    answer = request('POST', '/api/assistant', {
                        'question': 'Summarize current work', 'repo_id': repo_id})
                    assert 'Fixture summary' in json.dumps(answer), answer
                    assert fixture_key not in json.dumps(answer), answer
                    assert len(llm_calls) == 1, llm_calls
                    path, authorization, payload = llm_calls[0]
                    assert path == '/v1/chat/completions', path
                    assert authorization == 'Bearer ' + fixture_key
                    assert payload['model'] == 'fixture-model', payload
                    assert 'Edited title' in json.dumps(payload), payload
                    assert fixture_key not in json.dumps(payload), payload
                finally:
                    gateway.shutdown()
                    gateway.server_close()
                    gateway_thread.join(timeout=2)

            run_phase('llm_gateway', llm_gateway)

            def git_and_reporter():
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

                child_pid_file = root / 'reported-child.pid'
                child_release_file = root / 'release-reported-child'
                child_code = (
                    'import os, pathlib, time; '
                    f'pathlib.Path({str(child_pid_file)!r}).write_text(str(os.getpid())); '
                    f'path = pathlib.Path({str(child_release_file)!r}); '
                    'deadline = time.monotonic() + 20\n'
                    'while not path.exists() and time.monotonic() < deadline: time.sleep(0.1)\n'
                )
                reporter_env = dict(environment, TRACKER_URL=base,
                                    TRACKER_ACCESS_TOKEN='disposable-reporter-token')
                reporter_arguments = ['service', 'session', '--repo', str(git_root),
                                      '--cli', 'other', '--', sys.executable, '-c', child_code]
                reporter = subprocess.Popen(command + [json.dumps(reporter_arguments)],
                                            env=reporter_env, stdout=log, stderr=log)
                try:
                    deadline = time.monotonic() + 12
                    observed = None
                    while time.monotonic() < deadline:
                        if child_pid_file.exists():
                            child_pid = int(child_pid_file.read_text())
                            observed = next((item for item in request('GET', '/api/sessions')['items']
                                             if item.get('pid') == child_pid
                                             and item.get('status') == 'running'), None)
                            if observed:
                                break
                        if reporter.poll() is not None:
                            raise AssertionError('Host reporter exited before reporting its child')
                        time.sleep(0.1)
                    assert observed, 'Host reporter did not publish the running child PID'
                    assert observed['hostname'] == socket.gethostname(), observed
                    assert observed['repo_id'] == git_repo['id'], observed
                    assert observed['branch'] == 'main', observed
                    child_release_file.touch()
                    assert reporter.wait(timeout=8) == 0
                    ended = next(item for item in request('GET', '/api/sessions')['items']
                                 if item['session_id'] == observed['session_id'])
                    assert ended['status'] == 'stopped', ended
                finally:
                    child_release_file.touch()
                    if reporter.poll() is None:
                        reporter.terminate()
                        try:
                            reporter.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            reporter.kill()
                            reporter.wait(timeout=5)
            run_phase('git_and_reporter', git_and_reporter)

            def mac_authority():
                from mac_fixture import MacFixture
                stop()
                with MacFixture() as fleet:
                    environment.update(TRACKER_DATA_DIR=str(root / 'fleet-data'),
                                       TRACKER_MAC_URL=fleet.url, TRACKER_MAC_TOKEN=fleet.token)
                    start()
                    deadline = time.monotonic() + 15
                    fleet_repo = None
                    while time.monotonic() < deadline:
                        page = request('GET', '/api/repos')
                        fleet_repo = next((item for item in page['items']
                                           if item.get('authority') == 'mac'), None)
                        if fleet_repo:
                            break
                        time.sleep(0.2)
                    assert fleet_repo, ('MAC project summaries were not imported', page)
                    assert not fleet.writes, ('Read-only startup mutated the fleet', fleet.writes)
                    unmatched = request('POST', '/api/repos', {
                        'name': 'Confirmed absent from MAC',
                        'remote_url': 'https://example.test/unrelated/local-only.git'}, 201)
                    assert unmatched['authority'] == 'local', unmatched
                    local_task = request('POST', f"/api/repos/{unmatched['id']}/tasks", {
                        'title': 'Local work with fleet configured'}, 201)
                    assert local_task['authority'] == 'local', local_task
                    assert not fleet.writes, ('Unmatched local work mutated the fleet', fleet.writes)
                    fleet_id = fleet_repo['id']
                    page = request('GET', f'/api/repos/{fleet_id}/tasks')
                    existing = next((item for item in page['items']
                                     if item['title'] == 'Existing fleet task'), None)
                    assert existing, page
                    created = request('POST', f'/api/repos/{fleet_id}/tasks', {
                        'title': 'Route to fleet', 'description': 'Must be MAC owned'}, 201)
                    assert any(method == 'POST' and path == '/tasks'
                               and body.get('project') == fleet.project
                               for method, path, body in fleet.writes), fleet.writes
                    request('PATCH', f"/api/tasks/{existing['id']}", {
                        'revision': existing['revision'], 'labels': ['updated']})
                    preserved = next(item for item in fleet.tasks if item['id'] == 'task_fixture_1')
                    assert preserved['metadata']['foreign_key'] == 'preserve', preserved
                    assert preserved['metadata']['project_tracker']['labels'] == ['updated'], preserved
                    refreshed = request('GET', f"/api/tasks/{created['id']}")
                    request('PATCH', f"/api/tasks/{created['id']}", {
                        'revision': refreshed['revision'], 'state': 'completed'},
                        (400, 403, 409, 422))
                    unchanged = request('GET', f"/api/tasks/{created['id']}")
                    assert unchanged['state'] != 'completed', unchanged
                    fleet.unavailable = True
                    time.sleep(6)
                    unknown = request('POST', '/api/repos', {
                        'name': 'Unknown during outage',
                        'remote_url': 'https://example.test/unknown/during-outage.git'}, 201)
                    assert unknown['authority'] == 'unresolved', unknown
                    request('POST', f"/api/repos/{unknown['id']}/tasks", {
                        'title': 'Must wait for authority resolution'}, 503)
                    request('POST', f'/api/repos/{fleet_id}/tasks', {
                        'title': 'Must not become a local shadow'}, 503)
                    cached = request('GET', f'/api/repos/{fleet_id}/tasks')
                    assert all(item['title'] != 'Must not become a local shadow'
                               for item in cached['items']), cached
                    stop()
            run_phase('mac_authority', mac_authority)

            if diagnostic_failures:
                print(json.dumps({'ok': False, 'diagnostic_failures': diagnostic_failures}))
                raise AssertionError('Independent diagnostic phases failed')
            print(json.dumps({'ok': True, 'checks': [
                'local authority', 'task attributes and state', 'revision conflict',
                'database restart', 'session heartbeat and stop', 'SSE replay after restart',
                'A2A durable tasks', 'A2A idempotent creation',
                'A2A terminal cancellation rejection', 'official MCP client roundtrip',
                'backend LLM gateway and secret redaction',
                'real Git fork and merge parent edges', 'MAC discovery and task routing',
                'physical-host reporter child PID and stopped lifecycle',
                'MAC metadata preservation', 'MAC lifecycle rejection',
                'confirmed MAC absence permits local work',
                'MAC outage without local fallback']}))
        except BaseException:
            stop()
            log.flush()
            log.seek(0)
            print('Disposable service log (last 12000 characters):', file=sys.stderr)
            print(log.read()[-12000:], file=sys.stderr)
            raise
        finally:
            stop()
            log.close()


if __name__ == '__main__':
    argv = sys.argv[1:]
    diagnostic_continue = argv[:1] == ['--diagnostic-continue']
    if diagnostic_continue:
        argv = argv[1:]
    if argv[:1] == ['--']:
        argv = argv[1:]
    check(argv, diagnostic_continue=diagnostic_continue)
