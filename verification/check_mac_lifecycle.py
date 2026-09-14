#!/usr/bin/env python3
"""Verify MAC behavior with an isolated service and authenticated synthetic upstream.

Never reads production credentials or writes production tasks. Output is private QA
data; use a fresh --output directory for each run.
"""

import argparse, copy, http.server, json, os, signal, socket, subprocess, threading, time, urllib.request
from pathlib import Path
from service_response import entity_response

STATES = [
    "open",
    "waiting",
    "blocked",
    "claimed",
    "running",
    "needs_review",
    "needs_input",
    "stopped",
    "reviewing",
    "completed",
    "failed",
    "cancelled",
]
ap = argparse.ArgumentParser()
ap.add_argument("source")
ap.add_argument("--output", required=True)
a = ap.parse_args()
source = Path(a.source).resolve()
out = Path(a.output).resolve()
out.mkdir(parents=True, exist_ok=True)
tasks = [
    dict(
        id="state-" + state,
        project="alpha",
        title="State " + state,
        state=state,
        priority=1,
        dependencies=[],
        metadata={},
    )
    for state in STATES + ["provider_extra"]
]
tasks.append(
    dict(
        id="only-open",
        project="beta",
        title="Only open",
        state="open",
        priority=1,
        dependencies=[],
        metadata={},
    )
)
projects = ["alpha", "beta", "gamma"]
requests = []
lock = threading.Lock()


class Fixture(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.headers.get("Authorization") != "Bearer fixture-only":
            self.send_error(401)
            return
        route = self.path.split("?")[0]
        with lock:
            requests.append(route)
            if route == "/projects":
                result = [{"project": name} for name in projects]
            elif route == "/tasks":
                result = copy.deepcopy(tasks)
            elif route.startswith("/tasks/"):
                result = next(t for t in tasks if t["id"] == route.rsplit("/", 1)[1])
            else:
                result = []
        body = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        self.send_error(405)

    def do_PUT(self):
        self.send_error(405)

    def do_DELETE(self):
        self.send_error(405)


fixture = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
threading.Thread(target=fixture.serve_forever, daemon=True).start()
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
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
child = None
result = {"ok": False, "source": str(source), "checks": {}}


def api(route, method="GET", body=None):
    request = urllib.request.Request(
        base + route,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return entity_response(json.load(response))


def launch():
    return subprocess.Popen(
        [
            "/opt/homebrew/opt/node@22/bin/node",
            str(source / "main.js"),
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


def stop():
    global child
    if child and child.poll() is None:
        os.killpg(child.pid, signal.SIGTERM)
        child.wait(timeout=15)
    child = None


def eventually(fn, timeout=35):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        assert child.poll() is None, "Tracker exited"
        try:
            value = fn()
            if value:
                return value
        except (OSError, KeyError, StopIteration) as error:
            last = str(error)
        time.sleep(0.25)
    raise AssertionError(("Timed out", last))


def all_tasks():
    repos = api("/api/repos")["items"]
    items = [
        t for repo in repos for t in api("/api/repos/" + repo["id"] + "/tasks")["items"]
    ]
    details = [api("/api/tasks/" + task["id"]) for task in items]
    return {t.get("upstream_id", t.get("mac_id")): t for t in details}


def state_of(task):
    return task.get("state_name", task.get("state"))


def workflow():
    return {
        repo["mac_project"]: {
            s["name"]: s["id"]
            for s in api("/api/repos/" + repo["id"] + "/states")["items"]
        }
        for repo in api("/api/repos")["items"]
    }


try:
    child = launch()
    initial = eventually(lambda: (d if len(d := all_tasks()) == len(tasks) else None))
    for task in tasks:
        assert state_of(initial[task["id"]]) == task["state"], (
            task["state"],
            state_of(initial[task["id"]]),
        )
    result["checks"]["all_native_and_observed_imported_states"] = True
    workflows = workflow()
    assert set(workflows) == {"alpha", "beta", "gamma"}, workflows.keys()
    for name, states in workflows.items():
        assert set(STATES) <= set(states), (name, set(STATES) - set(states))
        assert not {"in_progress", "review"} & set(states), (name, states)
    assert "provider_extra" in workflows["alpha"]
    result["checks"]["supported_empty_columns"] = True
    with lock:
        tasks[0]["state"] = "provider_later"
    updated = eventually(
        lambda: (
            d
            if state_of((d := all_tasks())["state-open"]) == "provider_later"
            else None
        )
    )
    assert updated["state-open"]["revision"] == initial["state-open"]["revision"] + 1
    updated_workflows = workflow()
    for project, states in workflows.items():
        for name, state_id in states.items():
            assert updated_workflows[project][name] == state_id
    assert "provider_later" in updated_workflows["alpha"]
    result["checks"]["later_observed_state_and_stable_workflow_ids"] = True
    with lock:
        poll_count = requests.count("/tasks")
    eventually(lambda: requests.count("/tasks") >= poll_count + 2)
    unchanged = all_tasks()
    assert {k: t["revision"] for k, t in updated.items()} == {
        k: t["revision"] for k, t in unchanged.items()
    }
    assert updated_workflows == workflow()
    result["checks"]["unchanged_poll"] = True
    stop()
    child = launch()
    restarted = eventually(lambda: (d if len(d := all_tasks()) == len(tasks) else None))
    assert updated_workflows == workflow()
    for key, previous in unchanged.items():
        assert restarted[key]["id"] == previous["id"]
        assert restarted[key]["revision"] == previous["revision"]
        assert state_of(restarted[key]) == state_of(previous)
    result["checks"]["restart"] = True
    # A complete successful snapshot may remove an entire discovered project.
    # Preserve a separate local task while sweeping every cached MAC repository.
    repo_ids = {r["mac_project"]: r["id"] for r in api("/api/repos")["items"]}
    local_repo = api("/api/repos", "POST", {
        "name": "Local retention fixture", "remote_url": "https://example.test/local/retained.git"
    })
    assert local_repo["authority"] == "local", local_repo
    local_task = api("/api/repos/" + local_repo["id"] + "/tasks", "POST", {
        "title": "Keep local work", "description": "Preserve through fleet removal", "priority": 1
    })
    beta = restarted["only-open"]
    with lock:
        projects[:] = ["beta"]
        tasks[:] = [t for t in tasks if t["project"] == "beta"]
    def mac_tasks():
        return {k: t for k, t in all_tasks().items() if t.get("authority") == "mac"}
    remaining = eventually(lambda: (d if set(d := mac_tasks()) == {"only-open"} else None))
    assert remaining["only-open"]["id"] == beta["id"]
    assert remaining["only-open"]["revision"] == beta["revision"]
    for project, repo_id in repo_ids.items():
        assert api("/api/repos/" + repo_id)["id"] == repo_id
    result["checks"]["removed_project_tasks_reconciled"] = True
    with lock:
        projects.clear()
        tasks.clear()
    eventually(lambda: not mac_tasks())
    time.sleep(6)
    assert not mac_tasks()
    kept = api("/api/tasks/" + local_task["id"])
    assert kept["revision"] == local_task["revision"]
    assert kept["title"] == local_task["title"]
    assert kept["description"] == local_task["description"]
    assert api("/api/repos/" + local_repo["id"])["authority"] == "local"
    result["checks"]["empty_success_preserves_local_work"] = True
    result["ok"] = True
finally:
    stop()
    fixture.shutdown()
    fixture.server_close()
    log.close()
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
