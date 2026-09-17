#!/usr/bin/env python3
"""Independent TRACK-010 MAC stream and steerable agent-session acceptance."""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from service_response import entity_response
from test_tools import NODE


ACCESS_TOKEN = "track010-browser-access"
MAC_TOKEN = "track010-upstream-access"


class Hub:
    def __init__(self):
        self.lock = threading.Lock()
        self.paths: list[str] = []
        self.stream_connections = 0

    def handler(self):
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                return

            def send_json(self, status, value):
                body = json.dumps(value).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.headers.get("Authorization") != "Bearer " + MAC_TOKEN:
                    self.send_json(401, {"detail": "unauthorized"})
                    return
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path
                with fixture.lock:
                    fixture.paths.append(path)
                if path == "/projects":
                    self.send_json(200, [{"project": "live-project", "project_id": "project_live",
                                          "repository_url": "https://example.test/live.git",
                                          "metadata": {"mode": "live"}}])
                elif path == "/projects/live-project":
                    self.send_json(200, {"project": "live-project", "project_id": "project_live",
                                         "repository_url": "https://example.test/live.git",
                                         "metadata": {"mode": "live"}})
                elif path == "/bridge/repositories":
                    self.send_json(200, [{"id": "bridge_live", "name": "live", "source": "git",
                                          "project": "live-project",
                                          "metadata": {"repository_url": "https://example.test/live.git"}}])
                elif path == "/tasks":
                    self.send_json(200, [{"id": "task_live", "title": "Observe live work",
                                          "description": "fixture", "project": "live-project",
                                          "priority": 1, "state": "running", "metadata": {},
                                          "owner_agent_id": "agent_live", "dependencies": [],
                                          "required_capabilities": [], "created_at": "2026-09-15T00:00:00Z",
                                          "updated_at": "2026-09-15T00:00:01Z"}])
                elif path == "/agents":
                    self.send_json(200, [{"id": "agent_live", "name": "live-agent",
                                          "machine_id": "machine_live", "status": "working",
                                          "health_status": "healthy", "current_task_id": "task_live",
                                          "hermes_instance_id": "hermes_live", "capabilities": ["coding"],
                                          "resources": {}, "last_seen_at": "2026-09-15T00:00:02Z"}])
                elif path == "/machines":
                    self.send_json(200, [{"id": "machine_live", "hostname": "fixture-host",
                                          "status": "online"}])
                elif path == "/tasks/task_live/transcript":
                    self.send_json(200, [{"id": "turn_1", "sequence": 1, "kind": "agent",
                                          "actor": "agent_live", "content": "visible upstream turn",
                                          "created_at": "2026-09-15T00:00:03Z"}])
                elif path == "/events":
                    self.send_json(200, [{"sequence": 1, "event_type": "task.state.changed",
                                          "subject_id": "task_live", "project": "live-project",
                                          "created_at": "2026-09-15T00:00:04Z"}])
                elif path == "/events/stream":
                    with fixture.lock:
                        fixture.stream_connections += 1
                    lines = (json.dumps({"sequence": 1, "event_type": "task.state.changed",
                                         "subject_id": "task_live", "project": "live-project",
                                         "created_at": "2026-09-15T00:00:04Z"}) + "\n").encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/x-ndjson")
                    self.send_header("Content-Length", str(len(lines)))
                    self.end_headers()
                    self.wfile.write(lines)
                else:
                    self.send_json(404, {"detail": "not found"})

        return Handler


def eventually(callback, timeout=30):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            value = callback()
            if value:
                return value
        except (AssertionError, KeyError, OSError, urllib.error.HTTPError) as error:
            last = error
        time.sleep(0.15)
    raise AssertionError(f"timed out waiting for live operation: {last}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrypoint", type=Path)
    parser.add_argument("--node", default=NODE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    entrypoint = args.entrypoint.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    hub = Hub()
    hub_server = ThreadingHTTPServer(("127.0.0.1", 0), hub.handler())
    threading.Thread(target=hub_server.serve_forever, daemon=True).start()
    with tempfile.TemporaryDirectory(prefix="tracker-live-operations-") as temp:
        root = Path(temp)
        repo = root / "repo"
        repo.mkdir()
        subprocess.run(["/usr/bin/git", "init", "-b", "main", str(repo)], check=True,
                       stdout=subprocess.DEVNULL)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        environment = {key: value for key, value in os.environ.items()
                       if not key.startswith(("TRACKER_", "MAC_", "OPENAI_"))}
        environment.update(TRACKER_DATA_DIR=str(root / "data"), TRACKER_ACCESS_TOKEN=ACCESS_TOKEN,
                           TRACKER_MAC_URL=f"http://127.0.0.1:{hub_server.server_port}",
                           TRACKER_MAC_TOKEN=MAC_TOKEN)
        log = (output / "server.log").open("w")
        server = subprocess.Popen([args.node, str(entrypoint), "--litai-serve", "--host",
                                   "127.0.0.1", "--port", str(port)], env=environment,
                                  stdout=log, stderr=log, start_new_session=True)

        def request(path, method="GET", body=None, expected=(200,)):
            req = urllib.request.Request(base + path,
                data=json.dumps(body).encode() if body is not None else None,
                method=method, headers={"Content-Type": "application/json",
                                        "Authorization": "Bearer " + ACCESS_TOKEN})
            try:
                with urllib.request.urlopen(req, timeout=20) as response:
                    assert response.status in expected, response.status
                    return entity_response(json.load(response))
            except urllib.error.HTTPError as error:
                if error.code not in expected:
                    raise
                return entity_response(json.load(error))

        reporter = None
        try:
            eventually(lambda: request("/health"))
            def imported_session():
                sessions = request("/api/agent-sessions").get("items", [])
                match = next((item for item in sessions
                              if item.get("source") == "mac-task-transcript"
                              and item.get("mac_project") == "live-project"
                              and item.get("task_id")), None)
                assert match, sessions
                return match

            imported = eventually(imported_session)
            imported_id = imported.get("session_id") or imported["id"]
            imported_turns = request(
                f"/api/agent-sessions/{urllib.parse.quote(imported_id)}/conversation?after=0&limit=100"
            )
            assert "visible upstream turn" in json.dumps(imported_turns), imported_turns
            eventually(lambda: hub.stream_connections > 0)

            child_code = (
                "import sys\n"
                "tty = sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty()\n"
                "print('TTY:' + str(tty).lower(), flush=True)\n"
                "if not tty: raise SystemExit(23)\n"
                "line=sys.stdin.readline()\n"
                "print('ECHO:'+line.strip(), flush=True)\n"
                "sys.stdin.readline()\n"
            )
            reporter_args = ["service", "agent-session", "--repo", str(repo), "--cli", "other",
                             "--task-id", "task_live", "--", sys.executable, "-c", child_code]
            reporter_env = dict(environment, TRACKER_URL=base, TRACKER_ACCESS_TOKEN=ACCESS_TOKEN)
            reporter = subprocess.Popen([args.node, str(entrypoint), json.dumps(reporter_args)],
                                        env=reporter_env, stdout=log, stderr=log)

            def local_session():
                values = request("/api/agent-sessions").get("items", [])
                return next((item for item in values if item.get("source") == "tracker-cli"
                             and item.get("status") in ("running", "active")), None)

            session = eventually(local_session)
            session_id = session.get("session_id") or session["id"]

            def conversation_contains(text):
                value = request(f"/api/agent-sessions/{urllib.parse.quote(session_id)}/conversation?after=0&limit=100")
                records = value.get("items", value.get("records", []))
                return records if text in json.dumps(records) else None

            eventually(lambda: conversation_contains("TTY:true"))
            command = {"idempotency_key": "track010-text-1",
                       "expected_revision": session.get("revision", 0), "kind": "text",
                       "payload": {"text": "oscilloscope\n"}}
            first = request(f"/api/agent-sessions/{urllib.parse.quote(session_id)}/commands",
                            "POST", command, (200, 201, 202))
            second = request(f"/api/agent-sessions/{urllib.parse.quote(session_id)}/commands",
                             "POST", command, (200, 201, 202))
            assert (first.get("id") or first.get("command_id")) == (second.get("id") or second.get("command_id"))
            eventually(lambda: conversation_contains("ECHO:oscilloscope"))

            try:
                request(f"/api/agent-sessions/{urllib.parse.quote(session_id)}/commands", "POST",
                        dict(command, idempotency_key="track010-oversize",
                             payload={"text": "x" * 17000}), (400, 413, 422))
            except urllib.error.HTTPError:
                raise AssertionError("oversized steering command was not rejected")

            result = {"kind": "track-010-independent-live-operations", "ok": True,
                      "session_id": session_id, "stream_connections": hub.stream_connections}
            (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        finally:
            if reporter and reporter.poll() is None:
                reporter.terminate()
                try:
                    reporter.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    reporter.kill()
                    reporter.wait(timeout=5)
            if server.poll() is None:
                os.killpg(server.pid, signal.SIGTERM)
                server.wait(timeout=10)
            log.close()
            hub_server.shutdown()
            hub_server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
