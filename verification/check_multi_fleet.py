#!/usr/bin/env python3
"""Independently verify named fleet isolation, management and selector behavior."""
from test_tools import NODE, CHROME

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

from mac_fixture import MacFixture
from playwright.sync_api import sync_playwright


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def clean_environment():
    return {key: value for key, value in os.environ.items()
            if not key.startswith(("TRACKER_", "MAC_", "OPENAI_"))}


def request(base, method, path, body=None, expected=(200,)):
    call = urllib.request.Request(
        base + path,
        data=None if body is None else json.dumps(body).encode(),
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(call, timeout=8) as response:
            assert response.status in expected, (response.status, path)
            return json.load(response) if response.status != 204 else None
    except urllib.error.HTTPError as error:
        payload = json.load(error)
        assert error.code in expected, (error.code, path, payload)
        return payload


def eventually(operation, timeout=20):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            value = operation()
            if value:
                return value
        except (AssertionError, OSError, urllib.error.URLError) as error:
            last = error
        time.sleep(0.2)
    raise AssertionError(f"condition did not become true: {last}")


def collection(payload, *names):
    """Accept the generic or resource-named collection envelope."""
    for name in ("items", *names):
        if isinstance(payload.get(name), list):
            return payload[name]
    raise AssertionError(payload)


def reject_insecure_file(node, entrypoint, root, fleets_file):
    env = clean_environment()
    env.update(TRACKER_DATA_DIR=str(root / (fleets_file.name + "-data")),
               TRACKER_MAC_FLEETS_FILE=str(fleets_file))
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [node, str(entrypoint), "--litai-serve", "--host", "127.0.0.1", "--port", str(port)],
        env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.monotonic() + 8
        started = False
        while time.monotonic() < deadline and process.poll() is None:
            try:
                request(base, "GET", "/health")
                started = True
                break
            except (OSError, urllib.error.URLError):
                time.sleep(0.2)

        if started:
            projection = request(base, "GET", "/api/fleets")
            serialized = json.dumps(projection)
            assert collection(projection, "fleets") == [], projection
            assert projection.get("errors"), projection
            assert ("0600" in serialized or "group or other" in serialized or
                    "symbolic link" in serialized or "symlink" in serialized or
                    "regular file" in serialized), projection
        else:
            assert process.poll() not in (None, 0), "invalid fleet configuration was not rejected"
            serialized = process.stdout.read()
            assert ("0600" in serialized or "group or other" in serialized or
                    "symbolic link" in serialized or "symlink" in serialized or
                    "regular file" in serialized), serialized

        # A rejection may stop startup or leave the local tracker available, but
        # neither response path may disclose file credentials.
        try:
            secrets = [row.get("token") for row in json.loads(fleets_file.read_text())]
        except (OSError, ValueError, TypeError):
            secrets = []
        for secret in filter(None, secrets):
            assert secret not in serialized, "fleet-file rejection leaked a token"
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrypoint", type=Path)
    parser.add_argument("--node", default=NODE)
    parser.add_argument("--output", type=Path, default=Path("_build/multi-fleet"))
    args = parser.parse_args()
    entrypoint = args.entrypoint.resolve(strict=True)
    args.output.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="tracker-multi-fleet-") as temporary:
        root = Path(temporary)
        insecure = root / "fleets-0644.json"
        insecure.write_text("[]\n")
        insecure.chmod(0o644)
        reject_insecure_file(args.node, entrypoint, root, insecure)
        secure = root / "fleets-0600.json"
        secure.write_text("[]\n")
        secure.chmod(0o600)
        symlink = root / "fleets-link.json"
        symlink.symlink_to(secure)
        reject_insecure_file(args.node, entrypoint, root, symlink)

        with MacFixture() as north, MacFixture() as south:
            north.token = "north-token"
            south.token = "south-token"
            port = free_port()
            base = f"http://127.0.0.1:{port}"
            env = clean_environment()
            env.update(TRACKER_DATA_DIR=str(root / "service-data"))
            log_path = args.output / "service.log"
            with log_path.open("w") as log:
                process = subprocess.Popen(
                    [args.node, str(entrypoint), "--litai-serve", "--host", "127.0.0.1",
                     "--port", str(port)],
                    env=env, stdout=log, stderr=log,
                )
                try:
                    eventually(lambda: request(base, "GET", "/health"))
                    request(base, "POST", "/api/fleets", {
                        "id": "north", "name": "North", "url": north.url, "token": north.token,
                    }, (201,))
                    request(base, "POST", "/api/fleets", {
                        "id": "south", "name": "South", "url": south.url, "token": south.token,
                    }, (201,))

                    def two_repositories():
                        page = request(base, "GET", "/api/repos?fleet=all")
                        items = [item for item in collection(page, "repositories")
                                 if item.get("authority") == "mac"]
                        if len(items) != 2:
                            raise AssertionError({
                                "repositories": page,
                                "fleets": request(base, "GET", "/api/fleets"),
                            })
                        return items

                    repositories = eventually(two_repositories)
                    assert {item["fleet_id"] for item in repositories} == {"north", "south"}, repositories
                    assert len({item["id"] for item in repositories}) == 2, repositories
                    by_fleet = {item["fleet_id"]: item for item in repositories}

                    for fleet_id in ("north", "south"):
                        scoped = collection(request(base, "GET", f"/api/repos?fleet={fleet_id}"), "repositories")
                        assert len(scoped) == 1 and scoped[0]["fleet_id"] == fleet_id, scoped
                    assert collection(request(base, "GET", "/api/repos?fleet=local"), "repositories") == []

                    tasks = eventually(lambda: collection(request(base, "GET", "/api/tasks?fleet=all"), "tasks"))
                    fixture_tasks = [item for item in tasks if item.get("title") == "Existing fleet task"]
                    assert len(fixture_tasks) == 2, fixture_tasks
                    assert len({item["id"] for item in fixture_tasks}) == 2, fixture_tasks
                    assert {item["fleet_id"] for item in fixture_tasks} == {"north", "south"}, fixture_tasks

                    for fleet_id, fleet in (("north", north), ("south", south)):
                        request(base, "POST", f"/api/repos/{by_fleet[fleet_id]['id']}/tasks",
                                {"title": f"Write to {fleet_id}"}, (201,))
                        assert any(method == "POST" and path == "/tasks" and
                                   body.get("title") == f"Write to {fleet_id}"
                                   for method, path, body in fleet.writes), fleet.writes

                    duplicate = request(base, "POST", "/api/fleets", {
                        "id": "north", "name": "Duplicate", "url": north.url, "token": north.token,
                    }, (409,))
                    assert "duplicate" in json.dumps(duplicate).lower(), duplicate
                    renamed = request(base, "PATCH", "/api/fleets/north", {"name": "North renamed"})
                    assert renamed["name"] == "North renamed" and "token" not in renamed, renamed
                    south.token = "south-rotated-token"
                    rotated = request(base, "PATCH", "/api/fleets/south", {"token": south.token})
                    assert "token" not in rotated, rotated

                    removed = request(base, "DELETE", "/api/fleets/north")
                    assert removed.get("configured") is False, removed
                    cached_north = collection(
                        request(base, "GET", "/api/repos?fleet=north"), "repositories")
                    assert len(cached_north) == 1 and cached_north[0]["fleet_id"] == "north", cached_north
                    request(base, "POST", "/api/fleets", {
                        "id": "north", "name": "North restored", "url": north.url, "token": north.token,
                    }, (201,))
                    eventually(lambda: len(collection(
                        request(base, "GET", "/api/repos?fleet=north"), "repositories")) == 1)

                    south.unavailable = True
                    request(base, "POST", "/api/sync", {})
                    states = {item["id"]: item.get("state", item.get("sync_state"))
                              for item in collection(request(base, "GET", "/api/fleets"), "fleets")}
                    assert states["north"] in {"live", "healthy", "ok"}, states
                    assert states["south"] in {"stale", "failed", "unavailable"}, states

                    with sync_playwright() as playwright:
                        browser = playwright.chromium.launch(headless=True, executable_path=CHROME)
                        for name, width, height in (("desktop", 1440, 1000), ("mobile", 390, 844)):
                            page = browser.new_page(viewport={"width": width, "height": height})
                            errors = []
                            page.on("pageerror", lambda error: errors.append(str(error)))
                            page.goto(base, wait_until="domcontentloaded")
                            selector = page.get_by_label("Fleet", exact=True)
                            eventually(lambda: selector.locator("option").count() == 4)
                            labels = selector.locator("option").all_text_contents()
                            assert labels[0:2] == ["All fleets", "Local"], labels
                            assert any("North restored" in label for label in labels), labels
                            assert any("South" in label for label in labels), labels
                            selector.select_option("north")
                            page.wait_for_url("**fleet=north**")
                            selector.focus()
                            selector.press("End")
                            selector.press("Enter")
                            page.wait_for_timeout(200)
                            assert "fleet=" in page.url, page.url
                            page.go_back()
                            page.wait_for_timeout(200)
                            assert "fleet=north" in page.url, page.url
                            assert "Partial outage" in page.locator("body").inner_text(), page.locator("body").inner_text()
                            assert not errors, errors
                            page.screenshot(path=str(args.output / f"{name}.png"), full_page=True)
                            page.close()
                        browser.close()
                finally:
                    process.terminate()
                    try:
                        process.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)

    report = {"kind": "multi-fleet-independent", "ok": True,
              "checks": ["secure file handling", "overlapping identities", "scoped APIs",
                         "isolated writes", "settings CRUD", "partial outage",
                         "desktop and mobile selector navigation"]}
    (args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
