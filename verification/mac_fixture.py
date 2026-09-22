"""MAC HTTP contract fixture for isolated Project Tracker acceptance.

The /projects response follows mac.services._hermes_project_contexts, rather
than pretending that the endpoint returns raw ProjectRecord rows.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from urllib.parse import urlsplit


class MacFixture:
    token = 'isolated-test-token'
    project = 'fixture-project'
    remote_url = 'https://example.test/team/mac-owned.git'

    def __init__(self):
        self.unavailable = False
        self.writes = []
        self.reads = []
        self.tasks = [{
            'id': 'task_fixture_1', 'title': 'Existing fleet task',
            'description': 'A task from the MAC authority', 'project': self.project,
            'state': 'open', 'priority': 1, 'owner_agent_id': None,
            'dependencies': [], 'required_capabilities': [],
            'metadata': {'foreign_key': 'preserve', 'project_tracker': {'labels': ['fleet']}},
            'created_at': self.now(), 'updated_at': self.now(),
        }]
        self.lock = threading.RLock()
        self.server = None
        self.thread = None

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    def summary(self):
        return {
            'project': self.project, 'project_id': 'project_fixture_1',
            'status': 'active', 'description': 'Synthetic fleet project',
            'repository_url': self.remote_url, 'default_branch': 'main',
            'repository_registration': self.remote_url + '#main',
            'metadata': {'repository_url': self.remote_url},
            'task_count': len(self.tasks), 'active_count': 0,
            'state_counts': {'open': len(self.tasks)}, 'active_agent_ids': [],
        }

    def handle(self, method, path, body):
        if self.unavailable:
            return 503, {'detail': 'Synthetic fleet outage'}
        if method == 'GET':
            self.reads.append(path)
            if path == '/projects':
                return 200, [self.summary()]
            if path == f'/projects/{self.project}':
                return 200, self.summary()
            if path == '/bridge/repositories':
                return 200, [{
                    'id': 'repository_fixture_1', 'name': 'mac-owned',
                    'path': '/fixture/mac-owned', 'source': 'git',
                    'project': self.project, 'enabled': True,
                    'metadata': {'repository_url': self.remote_url},
                }]
            if path == '/tasks':
                return 200, deepcopy(self.tasks)
            if path in ['/agents', '/machines']:
                return 200, []
            if path == '/events/stream':
                # This fixture models an older hub without the canonical stream.
                # Keep the probe classified as a read so the tracker can prove its
                # documented bounded-polling fallback without a false mutation.
                return 404, {'detail': 'Event stream not available'}
            if path == '/events':
                # Bounded gap filling is also a read, even when this older fixture
                # does not implement the endpoint.
                return 404, {'detail': 'Events endpoint not available'}
            if path.startswith('/tasks/'):
                task = next((t for t in self.tasks if t['id'] == path.split('/')[2]), None)
                return (200, deepcopy(task)) if task else (404, {'detail': 'Task not found'})
        self.writes.append((method, path, deepcopy(body)))
        if method == 'POST' and path == '/tasks':
            if body.get('project') != self.project:
                return 422, {'detail': 'Wrong project routing'}
            if not isinstance(body.get('priority', 0), int):
                return 422, {'detail': 'MAC priority must be an integer'}
            task = dict(body, id=f'task_fixture_{len(self.tasks) + 1}', state='open',
                        owner_agent_id=None, created_at=self.now(), updated_at=self.now())
            self.tasks.append(task)
            return 200, deepcopy(task)
        if method == 'PUT' and path.startswith('/tasks/'):
            task = next((t for t in self.tasks if t['id'] == path.split('/')[2]), None)
            if task is None:
                return 404, {'detail': 'Task not found'}
            task.update({k: deepcopy(v) for k, v in body.items() if k != 'actor'})
            task['updated_at'] = self.now()
            return 200, deepcopy(task)
        if method == 'POST' and path.endswith('/transition'):
            task = next((t for t in self.tasks if t['id'] == path.split('/')[2]), None)
            if task is None:
                return 404, {'detail': 'Task not found'}
            if body.get('target_state') == 'completed':
                return 400, {'detail': 'Synthetic lifecycle gate rejected completion'}
            task['state'] = body['target_state']
            task['updated_at'] = self.now()
            return 200, deepcopy(task)
        return 404, {'detail': 'Fixture route not found'}

    def __enter__(self):
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def dispatch(self):
                if self.headers.get('Authorization') != 'Bearer ' + fixture.token:
                    status, result = 401, {'detail': 'Fixture authentication required'}
                else:
                    size = int(self.headers.get('Content-Length', '0'))
                    body = json.loads(self.rfile.read(size)) if size else None
                    with fixture.lock:
                        status, result = fixture.handle(self.command, urlsplit(self.path).path, body)
                payload = json.dumps(result).encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_PUT = do_DELETE = dispatch

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
