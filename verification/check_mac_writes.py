#!/usr/bin/env python3
"""Verify MAC behavior with an isolated service and authenticated synthetic upstream.

Never reads production credentials or writes production tasks. Output is private QA
data; use a fresh --output directory for each run.
"""

import argparse, http.server, json, os, socket, subprocess, threading, time, urllib.request, urllib.error
from pathlib import Path


def upstream_ids(task):
    return [
        entry["id"] if isinstance(entry, dict) else entry
        for entry in task.get("upstream_dependencies", [])
    ]


ap = argparse.ArgumentParser()
ap.add_argument("source")
ap.add_argument("--browser", action="store_true")
ap.add_argument("--output", default="_build/mac-writes")
a = ap.parse_args()
source = Path(a.source).resolve()
out = Path(a.output)
out.mkdir(parents=True, exist_ok=True)
tasks = {
    t["id"]: t
    for t in [
        dict(
            id="dependent",
            project="alpha",
            title="Dependent",
            description="Keep text",
            state="open",
            priority=1,
            dependencies=["prerequisite", "missing", "foreign"],
            metadata={
                "foreign": {"keep": True},
                "project_tracker": {"labels": ["fleet"]},
            },
        ),
        dict(
            id="prerequisite",
            project="alpha",
            title="Prerequisite",
            state="open",
            priority=1,
            dependencies=[],
            metadata={},
        ),
        dict(
            id="foreign",
            project="beta",
            title="Other project",
            state="open",
            priority=1,
            dependencies=[],
            metadata={},
        ),
    ]
}
calls = []
failure = False
failure_format = "html"


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def handle_request(self):
        if self.headers.get("Authorization") != "Bearer fixture-only":
            self.send_error(401)
            return
        if failure:
            error_body = {
                "html": b"<html><body>Service unavailable</body></html>",
                "json": b'{"detail":"Service unavailable"}',
                "empty": b"",
                "malformed_json": b"{broken",
            }[failure_format]
            self.send_response(503)
            self.send_header(
                "Content-Type",
                "text/html" if failure_format == "html" else "application/json",
            )
            self.send_header("Content-Length", str(len(error_body)))
            self.end_headers()
            self.wfile.write(error_body)
            return
        path = self.path.split("?")[0]
        method = self.command
        body = json.loads(
            self.rfile.read(int(self.headers.get("Content-Length", 0))) or "{}"
        )
        status = 200
        if method == "GET":
            if path == "/projects":
                result = [{"project": "alpha"}, {"project": "beta"}]
            elif path == "/bridge/repositories":
                result = []
            elif path == "/tasks":
                result = list(tasks.values())
            elif path.startswith("/tasks/"):
                result = tasks[path.split("/")[-1]]
            else:
                result = []
        else:
            calls.append({"method": method, "path": path, "body": body})
            if method == "POST" and path == "/tasks":
                result = dict(body, id="created", state="open")
                tasks["created"] = result
                status = 201
            elif method == "PUT" and path.startswith("/tasks/"):
                uid = path.split("/")[-1]
                tasks[uid].update({k: v for k, v in body.items() if k != "actor"})
                result = tasks[uid]
            elif path.endswith("/transition"):
                uid = path.split("/")[-2]
                tasks[uid]["state"] = body["target_state"]
                result = tasks[uid]
            else:
                self.send_error(404)
                return
        encoded = json.dumps(result).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    do_GET = handle_request
    do_POST = handle_request
    do_PUT = handle_request


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
with socket.socket() as s:
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
url = f"http://127.0.0.1:{port}"
env = {
    k: v
    for k, v in os.environ.items()
    if not k.startswith(("TRACKER_", "MAC_", "OPENAI_"))
}
env.update(
    TRACKER_DATA_DIR=str((out / "data").resolve()),
    TRACKER_MAC_URL=f"http://127.0.0.1:{server.server_port}",
    TRACKER_MAC_TOKEN="fixture-only",
)
log = (out / "server.log").open("w")
p = subprocess.Popen(
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
)


def api(method, path, data=None):
    req = urllib.request.Request(
        url + path,
        data=json.dumps(data).encode() if data is not None else None,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def unchanged_poll_after_edit(edited):
    time.sleep(6)
    after = api("GET", "/api/tasks/" + edited["id"])
    assert after["revision"] == edited["revision"], (
        "Unchanged poll changed revision",
        edited["revision"],
        after["revision"],
    )
    assert set(after.get("dependencies", [])) == set(edited.get("dependencies", [])), (
        "Dependency projection changed after write",
        edited.get("dependencies"),
        after.get("dependencies"),
    )
    normalize = lambda task: sorted(
        json.dumps(ref, sort_keys=True)
        for ref in task.get("unresolved_dependencies", [])
    )
    assert normalize(after) == normalize(edited), (
        "Unresolved-reference detail changed after write"
    )


results = []


def check(name, fn):
    try:
        fn()
        results.append({"name": name, "ok": True})
    except Exception as e:
        results.append({"name": name, "ok": False, "error": str(e)})


try:
    for _ in range(40):
        assert p.poll() is None, "Tracker exited"
        try:
            health = api("GET", "/health")
            if health.get("fleet", health).get("last_sync_ok") or api(
                "GET", "/api/overview"
            ).get("mac", {}).get("last", {}).get("ok"):
                break
        except OSError:
            pass
        time.sleep(0.25)
    else:
        raise AssertionError("Sync failed")
    repos = api("GET", "/api/repos")["items"]
    repo = next(r for r in repos if r["mac_project"] == "alpha")
    byMac = {
        t.get("mac_id", t.get("upstream_id")): t
        for t in (
            api("GET", "/api/tasks/" + item["id"])
            for item in api("GET", "/api/repos/" + repo["id"] + "/tasks")["items"]
        )
    }
    dep = byMac["dependent"]
    prereq = byMac["prerequisite"]

    def create():
        api(
            "POST",
            "/api/repos/" + repo["id"] + "/tasks",
            {"title": "Created through tracker", "dependencies": [prereq["id"]]},
        )
        assert tasks["created"]["dependencies"] == ["prerequisite"], calls[-1]

    check("create translates tracker dependency IDs to MAC IDs", create)

    def upstream_dependency_events():
        original_refs = list(tasks["dependent"]["dependencies"])
        created_detail = next(
            item
            for item in (
                api("GET", "/api/tasks/" + row["id"])
                for row in api("GET", "/api/repos/" + repo["id"] + "/tasks")["items"]
            )
            if item.get("upstream_id", item.get("mac_id")) == "created"
        )
        try:
            before = api("GET", "/api/tasks/" + dep["id"])
            tasks["dependent"] = {
                **tasks["dependent"],
                "dependencies": original_refs + ["created"],
            }
            time.sleep(6)
            added = api("GET", "/api/tasks/" + dep["id"])
            assert created_detail["id"] in added["dependencies"], (
                "Dependency-only upstream change did not resolve"
            )
            assert added["revision"] == before["revision"] + 1, (
                "Dependency-only upstream change must advance exactly once",
                before["revision"],
                added["revision"],
            )
            tasks["dependent"] = {
                **tasks["dependent"],
                "title": "Upstream title and dependency edit",
                "dependencies": original_refs,
            }
            time.sleep(6)
            combined = api("GET", "/api/tasks/" + dep["id"])
            assert combined["title"] == "Upstream title and dependency edit"
            assert created_detail["id"] not in combined["dependencies"]
            assert combined["revision"] == added["revision"] + 1, (
                "Combined upstream change must advance exactly once",
                added["revision"],
                combined["revision"],
            )
            unchanged_poll_after_edit(combined)
        finally:
            if tasks["dependent"]["dependencies"] != original_refs:
                tasks["dependent"] = {
                    **tasks["dependent"],
                    "dependencies": original_refs,
                }
                time.sleep(6)

    check(
        "dependency-only and combined upstream changes advance exactly one revision, then remain stable",
        upstream_dependency_events,
    )

    def title_only():
        current = api("GET", "/api/tasks/" + dep["id"])
        api(
            "PATCH",
            "/api/tasks/" + dep["id"],
            {"revision": current["revision"], "title": "Title only"},
        )
        assert tasks["dependent"]["dependencies"] == [
            "prerequisite",
            "missing",
            "foreign",
        ]
        assert tasks["dependent"]["metadata"]["foreign"] == {"keep": True}

    check("title-only edit retains raw dependencies and foreign metadata", title_only)

    def editor_save():
        current = api("GET", "/api/tasks/" + dep["id"])
        edited = api(
            "PATCH",
            "/api/tasks/" + dep["id"],
            {
                "revision": current["revision"],
                "title": "Full editor save",
                "description": "Keep text",
                "dependencies": [prereq["id"]],
                "labels": ["fleet", "edited"],
            },
        )
        assert set(tasks["dependent"]["dependencies"]) == {
            "prerequisite",
            "missing",
            "foreign",
        }, tasks["dependent"]["dependencies"]
        unchanged_poll_after_edit(edited)

    check(
        "full editor dependency submission retains unresolved references", editor_save
    )

    def transition():
        current = api("GET", "/api/tasks/" + dep["id"])
        api(
            "PATCH",
            "/api/tasks/" + dep["id"],
            {"revision": current["revision"], "state": "waiting"},
        )
        assert tasks["dependent"]["state"] == "waiting"
        assert calls[-1]["path"] == "/tasks/dependent/transition"

    check("transition uses upstream lifecycle endpoint", transition)

    def explicit_removal():
        tasks["dependent"]["dependencies"] = ["prerequisite", "missing", "foreign"]
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            current = api("GET", "/api/tasks/" + dep["id"])
            if set(upstream_ids(current)) == {"prerequisite", "missing", "foreign"}:
                break
            time.sleep(0.2)
        else:
            raise AssertionError("Restored references did not sync")
        edited = api(
            "PATCH",
            "/api/tasks/" + dep["id"],
            {
                "revision": current["revision"],
                "remove_upstream_dependencies": ["missing"],
            },
        )
        assert set(tasks["dependent"]["dependencies"]) == {"prerequisite", "foreign"}, (
            tasks["dependent"]["dependencies"]
        )
        unchanged_poll_after_edit(edited)

    check(
        "explicit removal removes only the selected unresolved reference",
        explicit_removal,
    )

    def add_dependency():
        current_tasks = [
            api("GET", "/api/tasks/" + item["id"])
            for item in api("GET", "/api/repos/" + repo["id"] + "/tasks")["items"]
        ]
        added = next(
            t
            for t in current_tasks
            if t.get("mac_id", t.get("upstream_id")) == "created"
        )
        try:
            edited = api(
                "PATCH",
                "/api/tasks/" + dep["id"],
                {"dependencies": [prereq["id"], added["id"]]},
            )
            assert set(tasks["dependent"]["dependencies"]) == {
                "prerequisite",
                "created",
                "foreign",
            }, tasks["dependent"]["dependencies"]
            unchanged_poll_after_edit(edited)
        finally:
            api("PATCH", "/api/tasks/" + dep["id"], {"dependencies": [prereq["id"]]})

    check(
        "adding a new dependency to an existing task translates its ID", add_dependency
    )
    if a.browser:
        from playwright.sync_api import sync_playwright, expect
        import re

        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            )
            for viewport_name, width, height in [
                ("desktop", 1440, 1000),
                ("mobile", 390, 844),
            ]:

                def browser_edit():
                    original_title = "T" * 720
                    original_description = "D" * 110000
                    tasks["dependent"].update(
                        title=original_title,
                        description=original_description,
                        dependencies=["prerequisite", "missing", "foreign"],
                    )
                    deadline = time.monotonic() + 15
                    while time.monotonic() < deadline:
                        current = api("GET", "/api/tasks/" + dep["id"])
                        if current["title"] == original_title and set(
                            upstream_ids(current)
                        ) == {"prerequisite", "missing", "foreign"}:
                            break
                        time.sleep(0.2)
                    else:
                        raise AssertionError("Browser fixture did not synchronize")
                    context = browser.new_context(
                        viewport={"width": width, "height": height}
                    )
                    page = context.new_page()
                    page.set_default_timeout(12000)
                    errors = []
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    try:
                        page.goto(url)
                        expect(
                            page.get_by_text("Connected", exact=True)
                        ).to_be_visible()
                        card = page.locator(".repo-card").filter(
                            has=page.get_by_role(
                                "heading", name=repo["name"], exact=True
                            )
                        )
                        card.get_by_role(
                            "button", name="Open board", exact=True
                        ).click()

                        def open_editor():
                            task_card = page.locator(
                                '[data-task-id="' + dep["id"] + '"]'
                            )
                            expect(task_card).to_be_visible()
                            opener = task_card.get_by_role(
                                "button",
                                name="Open the task " + original_title,
                                exact=True,
                            )
                            if opener.count():
                                opener.click()
                            else:
                                task_card.locator(".card-title, .task-title").click()
                            dialog = page.get_by_role("dialog")
                            expect(
                                dialog.get_by_label("Title", exact=True)
                            ).to_have_value(original_title)
                            return dialog

                        dialog = open_editor()
                        text = dialog.inner_text()
                        assert "missing" in text and "foreign" in text, (
                            "Unresolved references are not visible",
                            text[-2000:],
                        )
                        dialog.get_by_label("Labels", exact=True).fill("browser-edited")
                        dialog.get_by_role(
                            "listbox", name="Dependencies", exact=True
                        ).select_option([prereq["id"]])
                        dialog.get_by_role("button", name="Save", exact=True).click()
                        expect(dialog).not_to_be_visible()
                        assert (
                            tasks["dependent"]["title"] == original_title
                            and tasks["dependent"]["description"]
                            == original_description
                        ), "Unchanged imported text was modified"
                        assert set(tasks["dependent"]["dependencies"]) == {
                            "prerequisite",
                            "missing",
                            "foreign",
                        }, tasks["dependent"]["dependencies"]
                        dialog = open_editor()
                        remove = dialog.get_by_role(
                            "checkbox",
                            name=re.compile(r"Remove.*missing|missing.*Remove", re.I),
                        )
                        if remove.count():
                            remove.check()
                        else:
                            dialog.get_by_role(
                                "button",
                                name=re.compile(
                                    r"Remove.*missing|missing.*Remove", re.I
                                ),
                            ).click()
                        assert "missing" in tasks["dependent"]["dependencies"], (
                            "Removal committed before Save"
                        )
                        page.screenshot(
                            path=str(out / (viewport_name + "-mac-dependencies.png")),
                            full_page=True,
                        )
                        dialog.get_by_role("button", name="Save", exact=True).click()
                        expect(dialog).not_to_be_visible()
                        assert set(tasks["dependent"]["dependencies"]) == {
                            "prerequisite",
                            "foreign",
                        }, tasks["dependent"]["dependencies"]
                        assert (
                            tasks["dependent"]["title"] == original_title
                            and tasks["dependent"]["description"]
                            == original_description
                        )
                        assert tasks["dependent"]["metadata"]["foreign"] == {
                            "keep": True
                        }
                        assert (
                            page.evaluate("document.documentElement.scrollWidth")
                            <= width
                        ), "Document overflow with long imported title"
                        assert not errors, errors
                    except Exception:
                        page.screenshot(
                            path=str(out / (viewport_name + "-failure.png")),
                            full_page=True,
                        )
                        (out / (viewport_name + "-failure.txt")).write_text(
                            page.locator("body").inner_text()
                        )
                        raise
                    finally:
                        context.close()

                check(
                    viewport_name
                    + " browser preserves imported fields and explicitly removes one reference",
                    browser_edit,
                )
            browser.close()
    failure = True

    def outage():
        before = api("GET", "/api/tasks/" + dep["id"])
        try:
            api(
                "PATCH",
                "/api/tasks/" + dep["id"],
                {"revision": before["revision"], "title": "Must not commit"},
            )
        except urllib.error.HTTPError as e:
            assert e.code == 503, e.code
        else:
            raise AssertionError("Unavailable mutation returned success")
        after = api("GET", "/api/tasks/" + dep["id"])
        assert (
            after["revision"] == before["revision"]
            and after["title"] == before["title"]
        )

    for failure_format in ["json", "html", "empty", "malformed_json"]:
        check(
            f"{failure_format} outage rejects mutation with 503 and preserves cache",
            outage,
        )
finally:
    result = {
        "source": str(source),
        "ok": bool(results) and all(r["ok"] for r in results),
        "checks": results,
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    p.terminate()
    try:
        p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
    server.shutdown()
    log.close()

raise SystemExit(0 if result["ok"] else 1)
