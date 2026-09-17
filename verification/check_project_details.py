#!/usr/bin/env python3
"""Independent TRACK-009 service acceptance with a synthetic MAC authority."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from service_response import entity_response
from test_tools import NODE


PROJECTS = ["alpha", "beta", "gamma", "space project", "nested/project"]
MAC_TOKEN = "synthetic-mac-credential"
ACCESS_TOKEN = "synthetic-tracker-access"
SECRET_VALUES = ["top-secret-token", "nested-password", "cookie-value"]


class Fleet:
    def __init__(self):
        self.lock = threading.RLock()
        self.detail_reads = []
        self.in_flight = 0
        self.max_in_flight = 0
        self.failed_details = set()
        self.global_outage = False
        self.generation = 1

    def summary(self, project):
        return {
            "project": project,
            "project_id": "id-" + project,
            "repository_url": f"https://example.test/team/{urllib.parse.quote(project, safe='')}.git",
            "default_branch": "main",
            "metadata": {"repository_url": f"https://example.test/team/{urllib.parse.quote(project, safe='')}.git"},
        }

    def detail(self, project):
        return {
            **self.summary(project),
            "metadata": {
                "generation": self.generation,
                "api_key": SECRET_VALUES[0],
                "nested": {"PasswordCredential": SECRET_VALUES[1], "false": False, "zero": 0, "null": None},
                "cookies": SECRET_VALUES[2],
                "html": "<img src=x onerror=alert(1)>",
                "empty_object": {},
                "empty_array": [],
                "long_unicode": "😀" * 5000,
                "many": list(range(150)),
                "bulk": {f"field_{i}": "x" * 1000 for i in range(100)},
            },
        }

    def handler(self):
        fleet = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def send(self, status, value):
                payload = json.dumps(value).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def do_GET(self):
                if self.headers.get("Authorization") != "Bearer " + MAC_TOKEN:
                    self.send(401, {"detail": "authentication required"})
                    return
                route = urllib.parse.urlsplit(self.path).path
                with fleet.lock:
                    if fleet.global_outage:
                        self.send(503, {"detail": "synthetic outage"})
                        return
                    if route == "/projects":
                        self.send(200, [fleet.summary(project) for project in PROJECTS])
                        return
                    if route == "/bridge/repositories":
                        self.send(200, [
                            {"id": "repo-" + str(index), "project": project, "source": "git",
                             "metadata": {"repository_url": fleet.summary(project)["repository_url"]}}
                            for index, project in enumerate(PROJECTS)
                        ])
                        return
                    if route == "/tasks":
                        self.send(200, [
                            {"id": "task-" + str(index), "project": project, "title": "Task " + project,
                             "state": "open", "priority": 1, "dependencies": [], "metadata": {}}
                            for index, project in enumerate(PROJECTS)
                        ])
                        return
                    if route == "/agents":
                        self.send(200, [])
                        return
                    if route == "/machines":
                        self.send(200, [])
                        return
                    if route.startswith("/projects/"):
                        project = urllib.parse.unquote(route.removeprefix("/projects/"))
                        fleet.detail_reads.append(route)
                        fleet.in_flight += 1
                        fleet.max_in_flight = max(fleet.max_in_flight, fleet.in_flight)
                        failed = project in fleet.failed_details
                    else:
                        self.send(404, {"detail": "not found"})
                        return
                time.sleep(0.08)
                with fleet.lock:
                    fleet.in_flight -= 1
                    if failed:
                        self.send(503, {"detail": "synthetic detail failure"})
                    else:
                        self.send(200, fleet.detail(project))

        return Handler


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def eventually(callback, timeout=35):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            value = callback()
            if value:
                return value
        except (AssertionError, KeyError, OSError, urllib.error.HTTPError) as error:
            last = str(error)
        time.sleep(0.15)
    raise AssertionError(f"timed out: {last}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    result = {"kind": "track-009-independent-service", "ok": False, "checks": {}}

    with tempfile.TemporaryDirectory(prefix="tracker-project-detail-") as data_dir:
        fleet = Fleet()
        fleet_server = ThreadingHTTPServer(("127.0.0.1", 0), fleet.handler())
        fleet_thread = threading.Thread(target=fleet_server.serve_forever, daemon=True)
        fleet_thread.start()
        port = free_port()
        base = f"http://127.0.0.1:{port}"
        env = {key: value for key, value in os.environ.items() if not key.startswith(("TRACKER_", "MAC_", "OPENAI_"))}
        env.update(
            TRACKER_DATA_DIR=data_dir,
            TRACKER_MAC_URL=f"http://127.0.0.1:{fleet_server.server_port}",
            TRACKER_MAC_TOKEN=MAC_TOKEN,
            TRACKER_ACCESS_TOKEN=ACCESS_TOKEN,
        )
        log = (output / "server.log").open("w")
        child = None

        def request(path, method="GET", body=None, authenticated=True):
            headers = {"Content-Type": "application/json"}
            if authenticated:
                headers["Authorization"] = "Bearer " + ACCESS_TOKEN
            req = urllib.request.Request(
                base + path,
                data=json.dumps(body).encode() if body is not None else None,
                method=method,
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                return entity_response(json.load(response))

        def launch():
            return subprocess.Popen(
                [NODE, str(source / "main.js"), "--litai-serve", "--host", "127.0.0.1", "--port", str(port)],
                env=env,
                stdout=log,
                stderr=log,
                start_new_session=True,
            )

        def stop():
            nonlocal child
            if child and child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait(timeout=15)
            child = None

        def repositories():
            return request("/api/repos")["items"]

        def details_by_project():
            repos = repositories()
            assert len([repo for repo in repos if repo.get("authority") == "mac"]) == len(PROJECTS)
            assert all("mac_project_detail" not in repo for repo in repos)
            return {repo["mac_project"]: request("/api/repos/" + repo["id"]) for repo in repos if repo.get("authority") == "mac"}

        def ready_details():
            values = details_by_project()
            return values if all(repo.get("mac_project_detail") for repo in values.values()) else None

        try:
            child = launch()
            eventually(lambda: request("/health"))
            try:
                request("/api/repos", authenticated=False)
                raise AssertionError("repository collection allowed unauthenticated access")
            except urllib.error.HTTPError as error:
                assert error.code == 401
            result["checks"]["authenticated_repository_detail"] = True

            initial = eventually(ready_details)
            expected_routes = {"/projects/" + urllib.parse.quote(project, safe="") for project in PROJECTS}
            with fleet.lock:
                assert set(fleet.detail_reads) == expected_routes, fleet.detail_reads
                assert fleet.max_in_flight <= 4, fleet.max_in_flight
                initial_read_count = len(fleet.detail_reads)
            result["checks"]["encoded_initial_reads_and_concurrency"] = True

            for repo in initial.values():
                detail = repo["mac_project_detail"]
                encoded = json.dumps(detail, ensure_ascii=False, separators=(",", ":")).encode()
                assert len(encoded) <= 65536, len(encoded)
                text = encoded.decode()
                assert all(secret not in text for secret in SECRET_VALUES)
                assert "[redacted]" in text and "[truncated]" in text
                assert detail.get("fresh") is True and detail.get("error") is None
                assert detail.get("fetched_at")
            result["checks"]["safe_bounded_public_detail"] = True

            time.sleep(6.2)
            with fleet.lock:
                assert len(fleet.detail_reads) == initial_read_count, fleet.detail_reads
            result["checks"]["automatic_refresh_throttled"] = True

            request("/api/sync", method="POST", body={})
            eventually(lambda: len(fleet.detail_reads) == initial_read_count + len(PROJECTS))
            result["checks"]["manual_refresh_bypasses_throttle"] = True

            before_failure = details_by_project()["beta"]["mac_project_detail"]
            with fleet.lock:
                fleet.failed_details.add("beta")
                fleet.generation += 1
            response = request("/api/sync", method="POST", body={})
            assert response.get("ok") is not False, response
            failed = details_by_project()["beta"]["mac_project_detail"]
            assert failed["fetched_at"] == before_failure["fetched_at"]
            assert failed["fresh"] is False and failed["error"]
            assert failed["metadata"] == before_failure["metadata"]
            result["checks"]["last_good_failure_isolation"] = True

            with fleet.lock:
                fleet.failed_details.clear()
            request("/api/sync", method="POST", body={})
            recovered = details_by_project()["beta"]["mac_project_detail"]
            assert recovered["fresh"] is True and recovered["error"] is None
            assert recovered["metadata"]["generation"] == fleet.generation
            result["checks"]["detail_recovery"] = True

            stop()
            with fleet.lock:
                fleet.global_outage = True
            child = launch()
            eventually(lambda: request("/health"))
            restarted = eventually(details_by_project)
            assert restarted["beta"]["mac_project_detail"]["metadata"]["generation"] == fleet.generation
            result["checks"]["restart_persistence_during_outage"] = True

            for path in Path(data_dir).rglob("*"):
                if path.is_file():
                    content = path.read_bytes()
                    assert all(secret.encode() not in content for secret in SECRET_VALUES), path
            result["checks"]["no_secret_persisted"] = True
            result["ok"] = all(result["checks"].values())
        finally:
            stop()
            fleet_server.shutdown()
            fleet_server.server_close()
            fleet_thread.join(timeout=5)
            log.close()
            (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")

    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
