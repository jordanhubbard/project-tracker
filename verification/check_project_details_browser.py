#!/usr/bin/env python3
"""Verify TRACK-009 Inspector rendering at desktop and 390px widths."""
from __future__ import annotations

import argparse
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time
import urllib.request

from playwright.sync_api import expect, sync_playwright

from check_project_details import ACCESS_TOKEN, Fleet, MAC_TOKEN, PROJECTS, SECRET_VALUES
from service_response import entity_response
from test_tools import CHROME, NODE


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrypoint", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--node", default=NODE)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    assert CHROME, "Chrome is required for Inspector acceptance"

    fleet = Fleet()
    fleet_server = ThreadingHTTPServer(("127.0.0.1", 0), fleet.handler())
    import threading
    fleet_thread = threading.Thread(target=fleet_server.serve_forever, daemon=True)
    fleet_thread.start()
    with tempfile.TemporaryDirectory(prefix="tracker-project-detail-browser-") as data_dir:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        env = {key: value for key, value in os.environ.items() if not key.startswith(("TRACKER_", "MAC_", "OPENAI_"))}
        env.update(
            TRACKER_DATA_DIR=data_dir,
            TRACKER_MAC_URL=f"http://127.0.0.1:{fleet_server.server_port}",
            TRACKER_MAC_TOKEN=MAC_TOKEN,
            TRACKER_ACCESS_TOKEN=ACCESS_TOKEN,
        )
        log = (args.output / "server.log").open("w")
        process = subprocess.Popen(
            [args.node, str(args.entrypoint.resolve()), "--litai-serve", "--host", "127.0.0.1", "--port", str(port)],
            env=env,
            stdout=log,
            stderr=log,
        )

        def api(path, method="GET", body=None):
            request = urllib.request.Request(
                base + path,
                data=json.dumps(body).encode() if body is not None else None,
                method=method,
                headers={"Content-Type": "application/json", "Authorization": "Bearer " + ACCESS_TOKEN},
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                return entity_response(json.load(response))

        def ready_repo():
            repos = api("/api/repos")["items"]
            repo = next((item for item in repos if item.get("mac_project") == PROJECTS[0]), None)
            if not repo:
                return None
            return repo if api("/api/repos/" + repo["id"]).get("mac_project_detail") else None

        try:
            deadline = time.monotonic() + 40
            repo = None
            while time.monotonic() < deadline and repo is None:
                assert process.poll() is None, "Tracker exited"
                try:
                    repo = ready_repo()
                except OSError:
                    pass
                time.sleep(0.15)
            assert repo, "MAC project detail did not become ready"
            results = []
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path=CHROME)
                for name, width in (("desktop", 1440), ("mobile", 390)):
                    context = browser.new_context(viewport={"width": width, "height": 1000})
                    page = context.new_page()
                    page.set_default_timeout(15000)
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto(base)
                    password = page.get_by_label(re.compile(r"(?:Access token|Password|Tracker access token)", re.I))
                    password.fill(ACCESS_TOKEN)
                    page.get_by_role("button", name=re.compile(r"(?:Sign in|Log in|Login)", re.I)).click()
                    expect(page.get_by_text("Connected", exact=True)).to_be_visible()
                    project_heading = page.get_by_role("heading", name=repo["name"], exact=True)
                    project_heading.locator("xpath=ancestor::article[1]").get_by_role(
                        "button", name="Inspector", exact=True
                    ).click()
                    heading = page.get_by_role("heading", name="MAC project details", exact=True)
                    expect(heading).to_be_visible()
                    main = page.locator("main:visible")
                    expect(main).to_contain_text("[redacted]")
                    expect(main).to_contain_text("[truncated]")
                    expect(main).to_contain_text("false")
                    expect(main).to_contain_text("0")
                    expect(main).to_contain_text("null")
                    expect(main).to_contain_text(re.compile(r"(?:Empty (?:array|list)|\[\])", re.I))
                    expect(main).to_contain_text(re.compile(r"(?:Empty object|\{\})", re.I))
                    html = page.content()
                    storage = page.evaluate("JSON.stringify({local:{...localStorage},session:{...sessionStorage}})")
                    assert not any(secret in html or secret in storage for secret in SECRET_VALUES)
                    assert page.locator("[onerror]").count() == 0
                    summary = page.locator("summary").first
                    expect(summary).to_be_visible()
                    summary.focus()
                    assert summary.evaluate("element => element === document.activeElement")
                    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                    assert not errors, errors
                    page.screenshot(path=str(args.output / f"{name}-inspector.png"), full_page=True)
                    results.append({"viewport": name, "ok": True, "width": width})
                    context.close()
                browser.close()

            with fleet.lock:
                fleet.failed_details.add(PROJECTS[0])
            api("/api/sync", method="POST", body={})
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path=CHROME)
                context = browser.new_context(viewport={"width": 390, "height": 1000})
                page = context.new_page()
                page.goto(base)
                page.get_by_label(re.compile(r"(?:Access token|Password|Tracker access token)", re.I)).fill(ACCESS_TOKEN)
                page.get_by_role("button", name=re.compile(r"(?:Sign in|Log in|Login)", re.I)).click()
                stale_heading = page.get_by_role("heading", name=repo["name"], exact=True)
                stale_heading.locator("xpath=ancestor::article[1]").get_by_role(
                    "button", name="Inspector", exact=True
                ).click()
                expect(page.locator("main:visible")).to_contain_text(re.compile(r"false|stale", re.I))
                expect(page.locator("main:visible")).to_contain_text(re.compile(r"failure|error|unavailable", re.I))
                page.screenshot(path=str(args.output / "mobile-stale-detail.png"), full_page=True)
                context.close()
                browser.close()
            report = {"kind": "track-009-browser", "ok": True, "viewports": results, "stale_status_visible": True}
            (args.output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(report, sort_keys=True))
            return 0
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            fleet_server.shutdown()
            fleet_server.server_close()
            fleet_thread.join(timeout=5)
            log.close()


if __name__ == "__main__":
    raise SystemExit(main())
