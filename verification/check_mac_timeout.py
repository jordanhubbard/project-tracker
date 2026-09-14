#!/usr/bin/env python3
"""Verify MAC behavior with an isolated service and authenticated synthetic upstream.

Never reads production credentials or writes production tasks. Output is private QA
data; use a fresh --output directory for each run.
"""

import argparse, http.server, json, os, select, signal, socket, subprocess, threading, time, urllib.request
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("entrypoint", type=Path)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
entrypoint = args.entrypoint.resolve(strict=True)
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
mode = "healthy"
started = threading.Event()
closed = threading.Event()
shutdown = threading.Event()
timing = {}


class Fixture(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.headers.get("Authorization") != "Bearer fixture-only":
            self.send_error(401)
            return
        route = self.path.split("?")[0]
        if route == "/tasks" and mode == "stall":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "100")
            self.end_headers()
            self.wfile.write(b"[")
            self.wfile.flush()
            timing.setdefault("started", time.monotonic())
            started.set()
            try:
                while (
                    not shutdown.is_set() and time.monotonic() - timing["started"] < 70
                ):
                    ready, _, _ = select.select([self.connection], [], [], 0.1)
                    if ready and not self.connection.recv(1):
                        timing["closed"] = time.monotonic()
                        closed.set()
                        break
            except (ConnectionResetError, BrokenPipeError):
                timing["closed"] = time.monotonic()
                closed.set()
            finally:
                self.close_connection = True
            return
        if route == "/projects":
            value = [{"project": "alpha"}]
        elif route == "/tasks":
            value = [
                {
                    "id": "up-one",
                    "project": "alpha",
                    "title": "Preserved task",
                    "state": "open",
                    "priority": 1,
                    "dependencies": [],
                    "metadata": {},
                }
            ]
        else:
            value = []
        body = json.dumps(value).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


fixture = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
fixture.daemon_threads = True
threading.Thread(target=fixture.serve_forever, daemon=True).start()
with socket.socket() as reserved:
    reserved.bind(("127.0.0.1", 0))
    port = reserved.getsockname()[1]
base = f"http://127.0.0.1:{port}"
env = {
    k: v
    for k, v in os.environ.items()
    if not k.startswith(("TRACKER_", "MAC_", "OPENAI_"))
}
env.update(
    TRACKER_DATA_DIR=str(out / "data"),
    TRACKER_MAC_URL=f"http://127.0.0.1:{fixture.server_port}",
    TRACKER_MAC_TOKEN="fixture-only",
)
log = (out / "server.log").open("w")
child = subprocess.Popen(
    [
        "/opt/homebrew/opt/node@22/bin/node",
        str(entrypoint),
        "--litai-serve",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ],
    env=env,
    stdout=log,
    stderr=log,
    start_new_session=True,
)
result = {"ok": False, "entrypoint": str(entrypoint), "checks": {}}


def api(route):
    with urllib.request.urlopen(base + route, timeout=5) as response:
        return json.load(response)


def eventually(fn, timeout=30):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        assert child.poll() is None, "Tracker exited"
        try:
            value = fn()
            if value:
                return value
            last = "condition not met"
        except (OSError, KeyError, StopIteration) as error:
            last = str(error)
        time.sleep(0.1)
    raise AssertionError(("Timed out", last))


def repository():
    return next(
        repo
        for repo in api("/api/repos")["items"]
        if repo.get("mac_project") == "alpha"
    )


def sync_ok(repo):
    if "last_sync_ok" in repo:
        return repo["last_sync_ok"]
    health = api("/health")
    if "mac_last_sync_ok" in health:
        return health["mac_last_sync_ok"]
    fleet = health.get("fleet", health)
    if "last_sync_ok" in fleet:
        return fleet["last_sync_ok"]
    return api("/api/overview")["mac"]["last"]["ok"]


try:
    repo = eventually(lambda: (r if sync_ok(r := repository()) is True else None))
    initial = api("/api/repos/" + repo["id"] + "/tasks")["items"]
    assert len(initial) == 1
    task = api("/api/tasks/" + initial[0]["id"])
    mode = "stall"
    assert started.wait(30), "No scheduled task read reached the fixture"
    deadline = timing["started"] + 65
    while not closed.is_set() and time.monotonic() < deadline:
        assert child.poll() is None, "Tracker exited"
        time.sleep(0.1)
    assert closed.is_set(), (
        "The stalled HTTP body connection remained open past the default60-second deadline plus5-second margin"
    )
    elapsed = timing["closed"] - timing["started"]
    assert 59 <= elapsed < 65, elapsed
    result["checks"]["default_body_timeout_closes_connection"] = True
    result["body_timeout_seconds"] = round(elapsed, 3)
    failed = eventually(
        lambda: (
            r if sync_ok(r := repository()) is False and r.get("sync_error") else None
        ),
        timeout=5,
    )
    cached = api("/api/tasks/" + task["id"])
    assert cached["title"] == task["title"] and cached["revision"] == task["revision"]
    result["checks"]["failure_preserves_cached_task"] = True
    mode = "healthy"
    recovered = eventually(
        lambda: (
            r
            if sync_ok(r := repository()) is True and not r.get("sync_error")
            else None
        )
    )
    refreshed = api("/api/tasks/" + task["id"])
    assert (
        refreshed["title"] == task["title"]
        and refreshed["revision"] == task["revision"]
    )
    result["checks"]["later_synchronization_recovers_without_task_churn"] = True
    result["ok"] = True
except BaseException as error:
    result["error"] = str(error)
    raise
finally:
    shutdown.set()
    if child.poll() is None:
        os.killpg(child.pid, signal.SIGTERM)
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=5)
    fixture.shutdown()
    fixture.server_close()
    log.close()
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
