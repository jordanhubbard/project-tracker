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
import traceback
import uuid
import urllib.error
import urllib.request
from service_response import entity_response


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
                print(f'Independent phase passed: {name}', file=sys.stderr)
            except Exception as error:
                if not diagnostic_continue:
                    raise
                diagnostic_failures.append({'phase': name, 'error': str(error)[:2000]})
                print(f'Diagnostic phase failed: {name}: {error}', file=sys.stderr)
                traceback.print_exception(error, file=sys.stderr)


        def request(method, path, body=None, expected=200):
            if method == 'PATCH' and path.startswith('/api/tasks/') and isinstance(body, dict) and 'revision' in body:
                body = dict(body)
                body['expected_revision'] = body.pop('revision')
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
            return entity_response(json.loads(text)) if text else None

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
            prerequisite = request('POST', f'/api/repos/{repo_id}/tasks', {
                'title': 'Independent prerequisite'}, 201)
            task = request('POST', f'/api/repos/{repo_id}/tasks', {
                'title': 'Persist and edit', 'description': 'Initial description'}, 201)
            task_id = task['id']
            state_field = next(key for key in ('key', 'name', 'id') if any(state.get(key) == task['state'] for state in workflow))
            in_progress = next(state[state_field] for state in workflow
                               if state.get('name', '').lower().replace(' ', '_') == 'in_progress')
            changed = request('PATCH', f'/api/tasks/{task_id}', {
                'revision': task['revision'], 'title': 'Edited title',
                'state': in_progress, 'labels': ['integration'],
                'assignee': 'fixture-owner', 'branch': 'feature/verification',
                'cover_color': 'purple', 'due_date': '2026-10-01',
                'dependencies': [prerequisite['id']],
                'checklist': [{'text': 'Restart proof', 'done': True}]})
            assert changed['title'] == 'Edited title', changed
            assert changed['state'] == in_progress, changed
            assert changed['revision'] > task['revision'], changed
            for field, expected in {'assignee': 'fixture-owner', 'branch': 'feature/verification',
                                    'cover_color': 'purple', 'due_date': '2026-10-01',
                                    'dependencies': [prerequisite['id']],
                                    'checklist': [{'text': 'Restart proof', 'done': True}]}.items():
                assert changed[field] == expected, (field, changed)
            request('PATCH', f"/api/tasks/{prerequisite['id']}", {
                'revision': prerequisite['revision'], 'dependencies': [task_id]}, (400, 409, 422))
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
            history = request('GET', '/api/activity')['items']
            assert len(history) >= 3, history
            cursor = str(min(int(event.get('seq', event['id'])) for event in history))
            first = first_event(cursor)
            assert int(first['id']) > int(cursor), (cursor, first)
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
            def a2a_restart():
                persisted = rpc('tasks/get', {'id': peer_task['id']})
                assert 'result' in persisted, persisted
                assert persisted['result']['id'] == peer_task['id'], persisted
            run_phase('a2a_restart', a2a_restart)
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

            def mcp_stdio_roundtrip():
                async def exercise():
                    from mcp import Client
                    from mcp.client.stdio import StdioServerParameters
                    transport = StdioServerParameters(command=command[0],
                        args=command[1:] + [json.dumps(['service', 'mcp'])],
                        env=environment)
                    async with Client(transport, read_timeout_seconds=8) as client:
                        catalog = await client.list_tools()
                        create = next(tool for tool in catalog.tools if tool.name == 'create_task')
                        properties = create.input_schema.get('properties', {})
                        fields = {'title': 'Created through stdio MCP'}
                        arguments = {'repo_id': repo_id}
                        if 'task' in properties:
                            arguments['task'] = fields
                        else:
                            arguments.update(fields)
                        result = await client.call_tool('create_task', arguments)
                        assert not result.is_error, result
                    rows = request('GET', f'/api/repos/{repo_id}/tasks')['items']
                    assert sum(row['title'] == fields['title'] for row in rows) == 1, rows
                asyncio.run(asyncio.wait_for(exercise(), timeout=25))
            run_phase('mcp_stdio', mcp_stdio_roundtrip)

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
                    # Verify the same effective configuration used by the successful call.
                    assert settings['llm_key_configured'] is True, settings
                    assert settings['llm_url'] == environment['TRACKER_LLM_URL'], settings
                    assert settings['llm_model'] == 'fixture-model', settings
                    request('PATCH', '/api/settings', {'llm_key': ''})
                    assert request('GET', '/api/settings')['llm_key_configured'] is True
                    request('PATCH', '/api/settings', {'llm_key_clear': True})
                    stop()
                    start()
                    cleared = request('GET', '/api/settings')
                    assert cleared['llm_key_configured'] is False, cleared
                    calls_before = len(llm_calls)
                    disabled = request('POST', '/api/assistant', {
                        'question': 'This must not reach the gateway', 'repo_id': repo_id},
                        expected=(400, 409, 503))
                    assert 'error' in disabled, disabled
                    assert len(llm_calls) == calls_before, 'Explicit clear reused environment key'
                finally:
                    gateway.shutdown()
                    gateway.server_close()
                    gateway_thread.join(timeout=2)

            run_phase('llm_gateway', llm_gateway)

            def two_peer_instances():
                with socket.socket() as listener:
                    listener.bind(('127.0.0.1', 0))
                    peer_port = listener.getsockname()[1]
                peer_base = f'http://127.0.0.1:{peer_port}'
                peer_token = 'disposable-peer-' + str(uuid.uuid4())
                peer_environment = dict(environment, TRACKER_DATA_DIR=str(root / 'peer-data'),
                                        TRACKER_ACCESS_TOKEN=peer_token, TRACKER_MAC_URL='',
                                        TRACKER_LLM_URL='', TRACKER_LLM_KEY='')
                peer_process = subprocess.Popen(command + ['--litai-serve', '--host',
                                                '127.0.0.1', '--port', str(peer_port)],
                                                env=peer_environment, stdout=log, stderr=log)
                def peer_request(method, path, body=None, expected=200, authenticated=True):
                    headers = {'Content-Type': 'application/json'}
                    if authenticated:
                        headers['Authorization'] = 'Bearer ' + peer_token
                    req = urllib.request.Request(peer_base + path, method=method,
                            data=None if body is None else json.dumps(body).encode(), headers=headers)
                    try:
                        response = urllib.request.urlopen(req, timeout=5)
                    except urllib.error.HTTPError as error:
                        response = error
                    with response:
                        raw = response.read().decode()
                        assert response.status == expected, (path, response.status, raw)
                        return entity_response(json.loads(raw)) if raw else None
                try:
                    deadline = time.monotonic() + 20
                    while time.monotonic() < deadline:
                        if peer_process.poll() is not None:
                            raise AssertionError('Peer service exited before readiness')
                        try:
                            peer_request('GET', '/health')
                            break
                        except OSError:
                            time.sleep(0.1)
                    else:
                        raise AssertionError('Peer service did not become ready')
                    peer_request('GET', '/api/repos', expected=401, authenticated=False)
                    remote_repo = peer_request('POST', '/api/repos', {
                        'name': 'Peer-owned repository',
                        'remote_url': 'https://example.test/peer/repository.git'}, expected=201)
                    registered = request('POST', '/api/peers', {
                        'url': peer_base, 'name': 'Isolated peer', 'token': peer_token}, 201)
                    def peer_response_redaction():
                        assert peer_token not in json.dumps(registered), registered
                        assert peer_token not in json.dumps(request('GET', '/api/peers'))
                    run_phase('peer_response_redaction', peer_response_redaction)
                    peer_message = {'kind': 'message', 'role': 'user',
                        'messageId': str(uuid.uuid4()), 'parts': [{'kind': 'data', 'data': {
                            'operation': 'create_task', 'repo_id': remote_repo['id'],
                            'task': {'title': 'Created through authenticated peer'}}}]}
                    sent = request('POST', f"/api/peers/{registered['id']}/messages",
                                   {'message': peer_message})
                    def peer_task(response):
                        envelope = response.get('response', response)
                        assert isinstance(envelope, dict) and envelope.get('error') is None, response
                        result = envelope.get('result', envelope.get('remote_task', envelope.get('task', envelope)))
                        assert isinstance(result, dict) and result.get('kind') == 'task', response
                        return result
                    sent_task = peer_task(sent)
                    assert sent_task['status']['state'] == 'completed', sent
                    retried = request('POST', f"/api/peers/{registered['id']}/messages",
                                      {'message': peer_message})
                    assert peer_task(retried)['id'] == sent_task['id'], retried
                    rows = peer_request('GET', f"/api/repos/{remote_repo['id']}/tasks")['items']
                    assert sum(t['title'] == 'Created through authenticated peer'
                               for t in rows) == 1, rows
                    request('DELETE', f"/api/peers/{registered['id']}", expected=(200, 204))
                    assert all(p['id'] != registered['id']
                               for p in request('GET', '/api/peers')['items'])
                finally:
                    peer_process.terminate()
                    try:
                        peer_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        peer_process.kill()
                        peer_process.wait(timeout=5)
            run_phase('two_peer_instances', two_peer_instances)

            def git_and_reporter():
                git_root = (root / 'git-fixture').resolve()
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
                git_repo = request('POST', '/api/repos', {
                    'name': 'Git DAG fixture', 'local_path': str(git_root)}, 201)
                empty_graph = request('GET', f"/api/repos/{git_repo['id']}/graph")
                assert not empty_graph['commits'], empty_graph
                def check_unborn_state():
                    assert empty_graph.get('state', empty_graph.get('status')) in ('empty', 'unborn'), empty_graph
                run_phase('unborn_git_state', check_unborn_state)
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
                graph = request('GET', f"/api/repos/{git_repo['id']}/graph")
                def real_branch_refs():
                    refs = graph.get('refs', [])
                    for expected_name, expected_hash in [('main', merge_hash), ('feature', feature_hash)]:
                        assert any(ref.get('name') in (expected_name, f'refs/heads/{expected_name}')
                                   and ref.get('hash') == expected_hash for ref in refs), refs
                run_phase('real_branch_refs', real_branch_refs)
                commits = {commit['hash']: commit for commit in graph['commits']}
                assert set(commits[merge_hash]['parents']) == {feature_hash, main_hash}, graph
                assert commits[feature_hash]['parents'] == [base_hash], graph
                assert commits[main_hash]['parents'] == [base_hash], graph

                git('checkout', '--detach', merge_hash)
                detached = request('GET', f"/api/repos/{git_repo['id']}/graph")
                assert merge_hash in {c['hash'] for c in detached['commits']}, detached
                git('checkout', 'main')

                child_pid_file = root / 'reported-child.pid'
                child_release_file = root / 'release-reported-child'
                child_code = (
                    'import os, pathlib, time; '
                    f'pathlib.Path({str(child_pid_file)!r}).write_text(str(os.getpid())); '
                    f'path = pathlib.Path({str(child_release_file)!r}); '
                    'deadline = time.monotonic() + 75\n'
                    'while not path.exists() and time.monotonic() < deadline: time.sleep(0.1)\n'
                )
                reporter_env = dict(environment, TRACKER_URL=base,
                                    TRACKER_ACCESS_TOKEN='')
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
                                             and item.get('status') in ('running', 'active')), None)
                            if observed:
                                break
                        if reporter.poll() is not None:
                            raise AssertionError('Host reporter exited before reporting its child')
                        time.sleep(0.1)
                    assert observed, ('Host reporter did not publish the running child PID',
                                      request('GET', '/api/sessions'), request('GET', '/api/repos'))
                    assert observed['hostname'] == socket.gethostname(), observed
                    assert observed['repo_id'] == git_repo['id'], observed
                    assert observed['branch'] == 'main', observed
                    stop()
                    time.sleep(22)  # Cross a real 20-second reporter heartbeat attempt.
                    assert reporter.poll() is None, 'Backend outage terminated the reporter'
                    os.kill(child_pid, 0)  # The actual wrapped coding child must remain alive.
                    start()
                    assert reporter.poll() is None
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
                def local_checkout_alias():
                    alias = root / 'git-alias'
                    alias.symlink_to(git_root, target_is_directory=True)
                    ids_before = {item['id'] for item in request('GET', '/api/repos')['items']}
                    aliased = request('POST', '/api/repos', {
                        'name': 'Same checkout through alias', 'local_path': str(alias)}, (200, 201, 409))
                    ids_after = {item['id'] for item in request('GET', '/api/repos')['items']}
                    assert ids_after == ids_before, (git_repo, aliased)
                    if 'id' in aliased:
                        assert aliased['id'] == git_repo['id'], (git_repo, aliased)
                    else:
                        assert aliased.get('error'), aliased
                run_phase('local_checkout_alias', local_checkout_alias)
            run_phase('git_and_reporter', git_and_reporter)

            def bounded_git_history():
                checkout = (root / 'long-history').resolve()
                checkout.mkdir()
                git_env = dict(environment, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
                subprocess.run(['git', '-C', str(checkout), 'init', '-b', 'main'],
                               env=git_env, check=True, capture_output=True)
                count = 1005
                stream = []
                for index in range(1, count + 1):
                    message = f'History commit {index}\n'
                    stream.append(f'commit refs/heads/main\nmark :{index}\n'
                                  f'committer Fixture <fixture@example.test> {1700000000 + index} +0000\n'
                                  f'data {len(message)}\n{message}')
                    if index > 1:
                        stream.append(f'from :{index - 1}\n')
                    stream.append('\n')
                subprocess.run(['git', '-C', str(checkout), 'fast-import', '--quiet'],
                               input=''.join(stream), text=True, env=git_env,
                               check=True, capture_output=True, timeout=20)
                repo = request('POST', '/api/repos', {
                    'name': 'Bounded history', 'local_path': str(checkout)}, 201)
                graph = request('GET', f"/api/repos/{repo['id']}/graph")
                assert 0 < len(graph['commits']) < count, len(graph['commits'])
                # The real repository and boundary parents prove truncation; this metadata is optional.
                if 'truncated' in graph:
                    assert graph['truncated'], graph
                loaded = [commit for commit in graph['commits'] if not commit.get('boundary', False)]
                placeholders = {commit['hash'] for commit in graph['commits'] if commit.get('boundary', False)}
                known = {commit['hash'] for commit in loaded}
                boundary = {parent for commit in loaded
                            for parent in commit['parents'] if parent not in known}
                assert boundary, 'Truncation dropped real parents outside the returned window'
                actual_lines = subprocess.check_output(
                    ['git', '-C', str(checkout), 'rev-list', '--all', '--parents'],
                    env=git_env, text=True, timeout=5).splitlines()
                actual = {parts[0]: parts[1:] for parts in map(str.split, actual_lines)}
                assert placeholders <= boundary, (placeholders, boundary)
                assert boundary <= actual.keys(), boundary
                for commit in loaded:
                    assert commit['parents'] == actual[commit['hash']], commit
                print(f'Bounded history: {len(known)}/{count} commits, {len(boundary)} boundary parents',
                      file=sys.stderr)
            run_phase('bounded_git_history', bounded_git_history)

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
                    fleet_id = fleet_repo['id']
                    deadline = time.monotonic() + 15
                    existing = None
                    while time.monotonic() < deadline:
                        page = request('GET', f'/api/repos/{fleet_id}/tasks')
                        existing = next((item for item in page['items']
                                         if item['title'] == 'Existing fleet task'), None)
                        if existing:
                            break
                        time.sleep(0.2)
                    assert existing, ('MAC tasks were not imported', page,
                                      request('GET', '/health'))
                    def imported_metadata():
                        assert existing['labels'] == ['fleet'], existing
                    run_phase('mac_metadata_import', imported_metadata)
                    def stable_poll():
                        time.sleep(5.5)
                        polled = request('GET', f"/api/tasks/{existing['id']}")
                        assert polled['revision'] == existing['revision'], (
                            'Unchanged MAC polling changed the task revision', existing, polled)
                    run_phase('mac_poll_stability', stable_poll)
                    def equivalent_registration():
                        equivalent = request('POST', '/api/repos', {
                            'name': 'Equivalent SSH registration',
                            'remote_url': 'git@example.test:team/mac-owned.git'}, (200, 201, 409))
                        if 'error' not in equivalent:
                            assert equivalent['id'] == fleet_id and equivalent['authority'] == 'mac', equivalent
                        repositories = request('GET', '/api/repos')['items']
                        assert len(repositories) == 1 and repositories[0]['id'] == fleet_id, repositories
                    run_phase('mac_equivalent_registration', equivalent_registration)
                    assert not fleet.writes, ('Read-only startup mutated the fleet', fleet.writes)
                    unmatched = request('POST', '/api/repos', {
                        'name': 'Confirmed absent from MAC',
                        'remote_url': 'https://example.test/unrelated/local-only.git'}, 201)
                    assert unmatched['authority'] == 'local', unmatched
                    local_task = request('POST', f"/api/repos/{unmatched['id']}/tasks", {
                        'title': 'Local work with fleet configured'}, 201)
                    assert local_task['authority'] == 'local', local_task
                    assert not fleet.writes, ('Unmatched local work mutated the fleet', fleet.writes)
                    created = request('POST', f'/api/repos/{fleet_id}/tasks', {
                        'title': 'Route to fleet', 'description': 'Must be MAC owned'}, 201)
                    assert any(method == 'POST' and path == '/tasks'
                               and body.get('project') == fleet.project
                               for method, path, body in fleet.writes), fleet.writes
                    async def mcp_fleet_create():
                        from mcp import Client
                        async with Client(base + '/mcp', read_timeout_seconds=8) as client:
                            catalog = await client.list_tools()
                            tool = next(item for item in catalog.tools if item.name == 'create_task')
                            properties = tool.input_schema.get('properties', {})
                            fields = {'title': 'Route MAC task through MCP'}
                            arguments = {'repo_id': fleet_id}
                            if 'task' in properties:
                                arguments['task'] = fields
                            else:
                                arguments.update(fields)
                            result = await client.call_tool('create_task', arguments)
                            assert not result.is_error, result
                        assert any(method == 'POST' and path == '/tasks'
                                   and body.get('project') == fleet.project
                                   and body.get('title') == fields['title']
                                   for method, path, body in fleet.writes), fleet.writes
                    asyncio.run(asyncio.wait_for(mcp_fleet_create(), timeout=20))
                    async def stdio_fleet_create():
                        from mcp import Client
                        from mcp.client.stdio import StdioServerParameters
                        transport = StdioServerParameters(command=command[0],
                            args=command[1:] + [json.dumps(['service', 'mcp'])], env=environment)
                        async with Client(transport, read_timeout_seconds=8) as client:
                            catalog = await client.list_tools()
                            tool = next(item for item in catalog.tools if item.name == 'create_task')
                            properties = tool.input_schema.get('properties', {})
                            fields = {'title': 'Route MAC task through stdio MCP'}
                            arguments = {'repo_id': fleet_id}
                            if 'task' in properties:
                                arguments['task'] = fields
                            else:
                                arguments.update(fields)
                            deadline = time.monotonic() + 10
                            while True:
                                result = await client.call_tool('create_task', arguments)
                                if not result.is_error:
                                    break
                                # A fresh stdio process may still be discovering the fleet.
                                # Retry only explicit unavailability, with a finite bound;
                                # all other errors and any missing upstream write still fail.
                                serialized = result.model_dump_json()
                                assert 'mac_unavailable' in serialized and time.monotonic() < deadline, result
                                await asyncio.sleep(0.2)
                            assert not result.is_error, result
                        assert any(method == 'POST' and path == '/tasks'
                                   and body.get('project') == fleet.project
                                   and body.get('title') == fields['title']
                                   for method, path, body in fleet.writes), fleet.writes
                    run_phase('mac_stdio_initialization',
                              lambda: asyncio.run(asyncio.wait_for(stdio_fleet_create(), timeout=25)))
                    via_a2a = rpc('message/send', {'message': {
                        'kind': 'message', 'role': 'user', 'messageId': str(uuid.uuid4()),
                        'parts': [{'kind': 'data', 'data': {
                            'operation': 'create_task', 'repo_id': fleet_id,
                            'task': {'title': 'Route MAC task through A2A'}}}]}})
                    assert via_a2a['result']['status']['state'] == 'completed', via_a2a
                    assert any(method == 'POST' and path == '/tasks'
                               and body.get('project') == fleet.project
                               and body.get('title') == 'Route MAC task through A2A'
                               for method, path, body in fleet.writes), fleet.writes
                    existing = request('GET', f"/api/tasks/{existing['id']}")
                    request('PATCH', f"/api/tasks/{existing['id']}", {
                        'revision': existing['revision'], 'labels': ['updated']})
                    preserved = next(item for item in fleet.tasks if item['id'] == 'task_fixture_1')
                    assert preserved['metadata']['foreign_key'] == 'preserve', preserved
                    assert preserved['metadata']['project_tracker']['labels'] == ['updated'], preserved
                    fleet_states = request('GET', f'/api/repos/{fleet_id}/states')['items']
                    fleet_state_field = next(key for key in ('key', 'name', 'id') if any(st.get(key) == existing['state'] for st in fleet_states))
                    state_by_name = {item['name'].lower().replace(' ', '_'): item[fleet_state_field] for item in fleet_states}
                    def mac_lifecycle_success():
                        assert 'in_progress' in state_by_name, ('MAC workflow omits unoccupied in_progress state', fleet_states)
                        refreshed = request('GET', f"/api/tasks/{created['id']}")
                        moved = request('PATCH', f"/api/tasks/{created['id']}", {
                            'revision': refreshed['revision'], 'state': state_by_name['in_progress']})
                        assert moved['state'] == state_by_name['in_progress'], moved
                        upstream = next(t for t in fleet.tasks if t['title'] == 'Route to fleet')
                        assert upstream['state'] == 'in_progress', upstream
                        assert any(method == 'POST' and path == f"/tasks/{upstream['id']}/transition"
                                   and body.get('target_state') == 'in_progress'
                                   for method, path, body in fleet.writes), fleet.writes
                    run_phase('mac_lifecycle_success', mac_lifecycle_success)
                    def mac_lifecycle_rejection():
                        assert 'completed' in state_by_name, ('MAC workflow omits unoccupied completed state', fleet_states)
                        refreshed = request('GET', f"/api/tasks/{created['id']}")
                        request('PATCH', f"/api/tasks/{created['id']}", {
                            'revision': refreshed['revision'], 'state': state_by_name['completed']},
                            (400, 403, 409, 422))
                        unchanged = request('GET', f"/api/tasks/{created['id']}")
                        assert unchanged['state'] != state_by_name['completed'], unchanged
                        upstream = next(t for t in fleet.tasks if t['title'] == 'Route to fleet')
                        assert any(method == 'POST' and path == f"/tasks/{upstream['id']}/transition"
                                   and body.get('target_state') == 'completed'
                                   for method, path, body in fleet.writes), fleet.writes
                    run_phase('mac_lifecycle_rejection', mac_lifecycle_rejection)
                    fleet.unavailable = True
                    time.sleep(6)
                    unknown = request('POST', '/api/repos', {
                        'name': 'Unknown during outage',
                        'remote_url': 'https://example.test/unknown/during-outage.git'}, 201)
                    assert unknown['authority'] == 'unresolved', unknown
                    request('POST', f"/api/repos/{unknown['id']}/tasks", {
                        'title': 'Must wait for authority resolution'}, 503)
                    def mac_outage_status():
                        request('POST', f'/api/repos/{fleet_id}/tasks', {
                            'title': 'Must not become a local shadow'}, 503)
                    run_phase('mac_outage_status', mac_outage_status)
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
                'authenticated peer roundtrip and retry idempotency',
                'peer credential redaction and removal',
                'real Git fork and merge parent edges', 'MAC discovery and task routing',
                'MAC write routing through official MCP and A2A',
                'physical-host reporter child PID and stopped lifecycle',
                'reporter preserves coding child across backend outage',
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
