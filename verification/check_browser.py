#!/usr/bin/env python3
"""Exercise a disposable service in Chrome and retain rendering/interaction evidence.

Usage: python verification/check_browser.py /path/to/main.js
This checks board behavior; graph and protocol checks remain separate.
"""

import argparse, json, os, re, socket, subprocess, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
from service_response import entity_response

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("entrypoint", type=Path)
parser.add_argument("--node", default="/opt/homebrew/opt/node@22/bin/node")
parser.add_argument("--output", type=Path, default=Path("_build/browser-behavior"))
args = parser.parse_args()
out = args.output
out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="tracker-browser-") as data:
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("TRACKER_", "MAC_", "OPENAI_"))
    }
    env.update(TRACKER_DATA_DIR=data, TRACKER_MAC_URL="", TRACKER_LLM_KEY="")
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    log = (out / "server.log").open("w")
    process = subprocess.Popen(
        [
            args.node,
            str(args.entrypoint.resolve()),
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

    def api(method, path, body=None):
        r = urllib.request.Request(
            base + path,
            data=None if body is None else json.dumps(body).encode(),
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(r, timeout=5) as response:
            return entity_response(json.load(response))

    try:
        for _ in range(100):
            try:
                api("GET", "/health")
                break
            except OSError:
                time.sleep(0.1)
        repo = api(
            "POST",
            "/api/repos",
            {
                "name": "Project Tracker",
                "remote_url": "https://example.test/team/project-tracker.git",
                "description": "Repository and task workspace",
            },
        )
        states = api("GET", f"/api/repos/{repo['id']}/states")["items"]
        titles = [
            "Design the repository overview",
            "Show coding sessions by physical host",
            "Review live task updates",
            "Connect the agent workspace",
            "Publish the branch timeline",
        ]
        for i, st in enumerate(states):
            for j in range(2):
                api(
                    "POST",
                    f"/api/repos/{repo['id']}/tasks",
                    {
                        "title": titles[(i + j) % 5],
                        "state": st["id"],
                        "priority": 1,
                        "description": "Diagnostic fixture for visual and interaction review.",
                        "labels": ["Design" if j else "Platform"],
                        "cover_color": ["purple", "blue", "green", "orange"][i % 4]
                        if j == 0
                        else None,
                        "checklist": [{"text": "Review in browser", "done": False}],
                        "branch": "main",
                    },
                )
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            )
            evidence = []
            try:
                for name, width, height in [
                    ("desktop", 1440, 1000),
                    ("mobile", 390, 844),
                ]:
                    page = browser.new_page(viewport={"width": width, "height": height})
                    page.set_default_timeout(4000)
                    issues = []
                    page.on("pageerror", lambda e: issues.append(str(e)))
                    page.on(
                        "console",
                        lambda m: issues.append(m.text) if m.type == "error" else None,
                    )
                    page.goto(base, wait_until="domcontentloaded")
                    page.get_by_role("button", name="Open board", exact=True).or_(
                        page.get_by_role("link", name="Open board", exact=True)
                    ).click()
                    page.wait_for_timeout(700)
                    page.screenshot(path=str(out / f"{name}-board.png"), full_page=True)
                    (out / f"{name}-board.aria.txt").write_text(
                        page.locator("body").aria_snapshot()
                    )
                    dimensions = page.evaluate(
                        "({viewport:innerWidth,document:document.documentElement.scrollWidth})"
                    )
                    checks = []
                    if name in ("desktop", "mobile"):

                        def check(label, fn):
                            try:
                                fn()
                                checks.append({"check": label, "passed": True})
                            except Exception as e:
                                checks.append(
                                    {
                                        "check": label,
                                        "passed": False,
                                        "error": str(e)[:700],
                                    }
                                )
                                page.screenshot(
                                    path=str(
                                        out
                                        / (
                                            name
                                            + "_"
                                            + label.replace(" ", "_")
                                            + ".png"
                                        )
                                    ),
                                    full_page=True,
                                )
                                (
                                    out
                                    / (
                                        name
                                        + "_"
                                        + label.replace(" ", "_")
                                        + ".aria.txt"
                                    )
                                ).write_text(page.locator("body").aria_snapshot())
                                page.keyboard.press("Escape")

                        def create():
                            page.get_by_role(
                                "button", name="Add task", exact=True
                            ).click()
                            page.get_by_label("Title", exact=True).fill(
                                f"Browser-created task {name}"
                            )
                            page.get_by_role(
                                "textbox", name="Description", exact=True
                            ).fill("Saved from browser")
                            page.get_by_label(
                                "Labels (comma separated)", exact=True
                            ).fill("QA")
                            page.get_by_role(
                                "button", name=re.compile(r"^Save(?: task)?$")
                            ).click()
                            page.get_by_role("dialog").wait_for(state="hidden")
                            page.get_by_text(
                                f"Browser-created task {name}", exact=True
                            ).wait_for()

                        check("create task through dialog", create)

                        def edit_move():
                            task = next(
                                t
                                for t in api("GET", f"/api/repos/{repo['id']}/tasks")[
                                    "items"
                                ]
                                if t["title"] == f"Browser-created task {name}"
                            )
                            page.get_by_text(
                                f"Browser-created task {name}", exact=True
                            ).click()
                            page.get_by_role(
                                "textbox", name="Description", exact=True
                            ).fill("Updated in browser")
                            page.get_by_role(
                                "button", name=re.compile(r"^Save(?: task)?$")
                            ).click()
                            page.get_by_role("dialog").wait_for(state="hidden")
                            changed = api("GET", f"/api/tasks/{task['id']}")
                            assert changed[
                                "description"
                            ] == "Updated in browser" and changed["labels"] == ["QA"]
                            page.get_by_role(
                                "combobox",
                                name=re.compile(f"Move.*Browser-created task {name}"),
                            ).select_option(states[1]["id"])
                            page.wait_for_timeout(400)
                            assert (
                                api("GET", f"/api/tasks/{task['id']}")["state"]
                                == states[1]["id"]
                            )

                        check(
                            "edit preserves labels and keyboard move persists",
                            edit_move,
                        )

                        def remote():
                            api(
                                "POST",
                                f"/api/repos/{repo['id']}/tasks",
                                {
                                    "title": f"Remote change visible {name}",
                                    "priority": 1,
                                },
                            )
                            page.get_by_text(
                                f"Remote change visible {name}", exact=True
                            ).wait_for(timeout=2000)

                        check("second-client SSE update", remote)

                        def workflow():
                            current = api("GET", f"/api/repos/{repo['id']}/states")[
                                "items"
                            ]
                            old_name = current[0]["name"]
                            new_name = "Ready" if name == "desktop" else "Mobile ready"

                            def rename(dialog):
                                if "|" in dialog.default_value:
                                    dialog.accept(
                                        "\n".join(
                                            f"{item['id']}|{new_name if index == 0 else item['name']}"
                                            for index, item in enumerate(current)
                                        )
                                    )
                                else:
                                    dialog.accept(new_name)

                            page.once("dialog", rename)
                            control = page.get_by_role(
                                "button", name=f"Edit {old_name}", exact=True
                            )
                            if not control.count():
                                control = page.get_by_role(
                                    "button", name="Edit workflow", exact=True
                                ).first
                            control.click()
                            page.wait_for_timeout(500)
                            assert any(
                                x["name"] == new_name
                                for x in api("GET", f"/api/repos/{repo['id']}/states")[
                                    "items"
                                ]
                            )

                        check("rename workflow state", workflow)

                        def activity():
                            if name == "mobile":
                                page.get_by_role(
                                    "button",
                                    name=re.compile(
                                        "menu|sidebar|Toggle repositories", re.I
                                    ),
                                ).click()
                            page.get_by_role("button", name="Activity", exact=True).or_(
                                page.get_by_role("link", name="Activity", exact=True)
                            ).click()
                            page.get_by_role(
                                "heading", name=re.compile("Activity", re.I)
                            ).wait_for()
                            assert (
                                "Remote change visible"
                                in page.locator("main").inner_text()
                            )
                            if name == "mobile":
                                navigation = (
                                    page.get_by_role(
                                        "button", name="Activity", exact=True
                                    )
                                    .or_(
                                        page.get_by_role(
                                            "link", name="Activity", exact=True
                                        )
                                    )
                                    .bounding_box()
                                )
                                if navigation and navigation["x"] >= 0:
                                    page.get_by_role(
                                        "button",
                                        name=re.compile(
                                            "menu|sidebar|Toggle repositories", re.I
                                        ),
                                    ).click()

                        check("activity navigation shows task events", activity)

                        def settings():
                            page.get_by_role(
                                "button", name="Settings", exact=True
                            ).click()
                            page.get_by_label("Gateway URL", exact=True).fill(
                                "http://127.0.0.1:9/v1"
                            )
                            page.get_by_label(re.compile(r"^API key")).fill(
                                "disposable-browser-secret"
                            )
                            page.get_by_label("Model", exact=True).fill(
                                "browser-fixture-model"
                            )
                            page.get_by_role(
                                "button", name="Save settings", exact=True
                            ).click()
                            page.wait_for_timeout(500)
                            saved = api("GET", "/api/settings")
                            assert (
                                saved["llm_url"] == "http://127.0.0.1:9/v1"
                                and saved["llm_model"] == "browser-fixture-model"
                            )
                            assert "disposable-browser-secret" not in json.dumps(saved)
                            assert (
                                page.get_by_label(re.compile(r"^API key")).input_value()
                                == ""
                            )
                            page.reload(wait_until="domcontentloaded")
                            if not page.get_by_label(
                                "Gateway URL", exact=True
                            ).is_visible():
                                page.get_by_role(
                                    "button", name="Settings", exact=True
                                ).click()
                            page.get_by_label("Gateway URL", exact=True).wait_for()
                            assert (
                                page.get_by_label(
                                    "Gateway URL", exact=True
                                ).input_value()
                                == "http://127.0.0.1:9/v1"
                            )
                            assert (
                                page.get_by_label("Model", exact=True).input_value()
                                == "browser-fixture-model"
                            )
                            assert (
                                page.get_by_label(re.compile(r"^API key")).input_value()
                                == ""
                            )

                        check("settings persist and secrets stay write-only", settings)

                    if dimensions["document"] > dimensions["viewport"]:
                        issues.append(f"Document overflow: {dimensions}")
                    evidence.append(
                        {
                            "viewport": name,
                            "issues": issues,
                            "dimensions": dimensions,
                            "interactions": checks,
                        }
                    )
                    page.close()
            finally:
                browser.close()
            (out / "result.json").write_text(json.dumps(evidence, indent=2) + "\n")
            print(json.dumps(evidence))
            if any(
                item["issues"] or any(not c["passed"] for c in item["interactions"])
                for item in evidence
            ):
                raise SystemExit(1)
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        log.close()
