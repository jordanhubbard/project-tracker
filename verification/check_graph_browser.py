#!/usr/bin/env python3
"""Verify real Git ancestry and browser graph interactions in an isolated service."""

import argparse, json, os, re, socket, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from service_response import entity_response

def commit_circle(node):
    return node if node.evaluate("n=>n.tagName.toLowerCase()") == 'circle' else node.locator('circle').first


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("entrypoint", type=Path)
parser.add_argument("--node", default="/opt/homebrew/opt/node@22/bin/node")
parser.add_argument(
    "--output", type=Path, default=Path("_build/graph-browser-behavior")
)
parser.add_argument("--irregular-times", action="store_true",
                    help="Use commit times at 0, 10, 100 and 110 seconds and verify horizontal spacing")
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
        gitroot = (Path(data) / "checkout").resolve()
        gitroot.mkdir()
        git_env = dict(
            env,
            GIT_AUTHOR_NAME="Graph fixture",
            GIT_AUTHOR_EMAIL="fixture@example.test",
            GIT_COMMITTER_NAME="Graph fixture",
            GIT_COMMITTER_EMAIL="fixture@example.test",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_DATE="2026-09-01T12:00:00Z",
            GIT_COMMITTER_DATE="2026-09-01T12:00:00Z",
        )

        def git(*args):
            return subprocess.check_output(
                ["git", "-C", str(gitroot), *args],
                env=git_env,
                stderr=subprocess.PIPE,
                text=True,
            ).strip()

        git("init", "-b", "main")
        (gitroot / "base").write_text("base")
        git("add", ".")
        git("commit", "-m", "Base")
        basehash = git("rev-parse", "HEAD")
        git("checkout", "-b", "feature")
        (gitroot / "feature").write_text("feature")
        git("add", ".")
        if args.irregular_times:
            git_env.update(GIT_AUTHOR_DATE="2026-09-01T12:00:10Z", GIT_COMMITTER_DATE="2026-09-01T12:00:10Z")
        git("commit", "-m", "Feature")
        featurehash = git("rev-parse", "HEAD")
        git("checkout", "main")
        (gitroot / "main").write_text("main")
        git("add", ".")
        if args.irregular_times:
            git_env.update(GIT_AUTHOR_DATE="2026-09-01T12:01:40Z", GIT_COMMITTER_DATE="2026-09-01T12:01:40Z")
        git("commit", "-m", "Main")
        mainhash = git("rev-parse", "HEAD")
        if args.irregular_times:
            git_env.update(GIT_AUTHOR_DATE="2026-09-01T12:01:50Z", GIT_COMMITTER_DATE="2026-09-01T12:01:50Z")
        git("merge", "--no-ff", "feature", "-m", "Merge feature")
        mergehash = git("rev-parse", "HEAD")
        repo = api(
            "POST",
            "/api/repos",
            {"name": "Git branch fixture", "local_path": str(gitroot)},
        )
        graph = api("GET", f"/api/repos/{repo['id']}/graph")
        commits = {c["hash"]: c for c in graph["commits"]}
        assert set(commits[mergehash]["parents"]) == {mainhash, featurehash}
        assert commits[mainhash]["parents"] == [basehash] and commits[featurehash][
            "parents"
        ] == [basehash]
        (out / "git-api.json").write_text(json.dumps(graph, indent=2) + "\n")
        states = api("GET", f"/api/repos/{repo['id']}/states")["items"]
        probe = api('POST', f"/api/repos/{repo['id']}/tasks", {'title': 'Workflow representation probe'})
        state_field = next(key for key in ('key', 'name', 'id') if any(st.get(key) == probe['state'] for st in states))
        api('DELETE', f"/api/tasks/{probe['id']}")
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
                        "state": st[state_field],
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
                    page.on("response", lambda r: issues.append(f"HTTP {r.status}: {r.url}") if r.status >= 400 else None)
                    page.goto(base, wait_until="domcontentloaded")
                    try:
                        page.get_by_role("button", name=re.compile(r"^Open board(?: for .+)?$", re.I)).or_(
                            page.get_by_role("link", name=re.compile(r"^Open board(?: for .+)?$", re.I))
                        ).click()
                    except Exception:
                        page.screenshot(
                            path=str(out / f"{name}-startup.png"), full_page=True
                        )
                        (out / f"{name}-startup.aria.txt").write_text(
                            page.locator("body").aria_snapshot()
                        )
                        (out / f"{name}-startup-errors.json").write_text(
                            json.dumps(issues, indent=2)
                        )
                        raise
                    page.wait_for_timeout(700)
                    page.screenshot(path=str(out / f"{name}-board.png"), full_page=True)
                    (out / f"{name}-board.aria.txt").write_text(
                        page.locator("body").aria_snapshot()
                    )
                    dimensions = page.evaluate(
                        "({viewport:innerWidth,document:document.documentElement.scrollWidth})"
                    )
                    reporter_verified = False
                    if name == "desktop":
                        pid_file = Path(data) / "browser-reporter.pid"
                        release_file = Path(data) / "browser-reporter.release"
                        child_code = (
                            'import os, pathlib, time; '
                            f'pathlib.Path({str(pid_file)!r}).write_text(str(os.getpid())); '
                            f'path = pathlib.Path({str(release_file)!r}); '
                            'deadline = time.monotonic() + 25\n'
                            'while not path.exists() and time.monotonic() < deadline: time.sleep(0.1)\n'
                        )
                        reporter_args = ['service', 'session', '--repo', str(gitroot),
                                         '--cli', 'other', '--', sys.executable, '-c', child_code]
                        reporter = subprocess.Popen(
                            [args.node, str(args.entrypoint.resolve()), json.dumps(reporter_args)],
                            env=dict(env, TRACKER_URL=base), stdout=log, stderr=log)
                        try:
                            deadline = time.monotonic() + 10
                            while not pid_file.exists() and time.monotonic() < deadline:
                                page.wait_for_timeout(100)
                            child_pid = int(pid_file.read_text())
                            page.get_by_role("button", name="Fleet", exact=True).or_(
                                page.get_by_role("link", name="Fleet", exact=True)
                            ).or_(page.get_by_role("tab", name="Fleet", exact=True)).click()
                            pid_cell = page.get_by_role("cell", name=str(child_pid), exact=True)
                            host_cell = page.get_by_role('cell', name=socket.gethostname(), exact=True)
                            host_cell.wait_for(timeout=10000)
                            row = host_cell.locator('..')
                            pid_visible = pid_cell.count() > 0
                            if not pid_visible:
                                issues.append(f'Fleet row omits actual child PID {child_pid}')
                            assert any(item.get('pid') == child_pid for item in api('GET', '/api/sessions')['items'])
                            assert socket.gethostname() in row.inner_text(), row.inner_text()
                            assert 'other' in row.inner_text() and 'main' in row.inner_text(), row.inner_text()
                            release_file.touch()
                            assert reporter.wait(timeout=8) == 0
                            row.get_by_text(re.compile(r"^stopped$", re.I)).wait_for(timeout=4000)
                            page.screenshot(path=str(out / "desktop-reporter-fleet.png"), full_page=True)
                            reporter_verified = pid_visible
                        finally:
                            release_file.touch()
                            if reporter.poll() is None:
                                reporter.terminate()
                                try:
                                    reporter.wait(timeout=5)
                                except subprocess.TimeoutExpired:
                                    reporter.kill()
                                    reporter.wait(timeout=5)
                    checks = []
                    back = page.get_by_role('button', name='Back to board', exact=True)
                    if back.count(): back.click()
                    for mode in ("Graph", "Timeline"):
                        if mode == "Timeline":
                            page.get_by_role("button", name=re.compile(r"^(?:Back to board|Board)$")).or_(
                                page.get_by_role("link", name=re.compile(r"^(?:Back to board|Board)$"))
                            ).or_(page.get_by_role("tab", name=re.compile(r"^(?:Back to board|Board)$"))).first.click()
                            page.wait_for_timeout(200)
                        page.get_by_role("button", name=mode, exact=True).or_(
                            page.get_by_role("link", name=mode, exact=True)
                        ).or_(page.get_by_role("tab", name=mode, exact=True)).click()
                        page.wait_for_timeout(400)
                        if page.get_by_role("combobox", name=re.compile("branch", re.I)).or_(page.locator("#branch-filter")).input_value():
                            page.get_by_role("combobox", name=re.compile("branch", re.I)).or_(page.locator("#branch-filter")).select_option(label="All branches")
                        expect(page.locator("svg [role=button]")).to_have_count(4, timeout=2000)
                        page.screenshot(
                            path=str(out / f"{name}-{mode.lower()}.png"), full_page=True
                        )
                        invalid = page.locator("svg").evaluate_all(
                            "els => els.flatMap(el => [...el.querySelectorAll('*')].flatMap(n => [...n.attributes].filter(a => /NaN|Infinity/.test(a.value)).map(a => a.name + '=' + a.value)))"
                        )
                        timeline_positions = {}
                        if mode == "Timeline" and args.irregular_times:
                            nodes = page.locator("svg [role=button]")
                            for index in range(nodes.count()):
                                node = nodes.nth(index)
                                commit_circle(node).click()
                                label = node.get_attribute("aria-label") or ""
                                short_hash = re.search(r"[a-f0-9]{7,64}", label)
                                if short_hash:
                                    expect(page.locator("#commit-inspector, .commit-inspector, .inspector")).to_contain_text(re.compile(r"Hash\s*" + short_hash.group()), timeout=2000)
                                details = page.locator("#commit-inspector, .commit-inspector, .inspector").inner_text()
                                match = re.search(r"\bHash\s+([a-f0-9]{40,64})\b", details)
                                center = commit_circle(node).evaluate(
                                    "n => {const p = n.ownerSVGElement.createSVGPoint(); p.x=n.cx.baseVal.value; p.y=n.cy.baseVal.value; return p.matrixTransform(n.getCTM()).x}"
                                )
                                if match:
                                    timeline_positions[match.group(1)] = center
                            if not all(h in timeline_positions for h in (basehash, featurehash, mainhash)):
                                issues.append("Timeline: missing individually selectable timestamp nodes")
                            else:
                                near = timeline_positions[featurehash] - timeline_positions[basehash]
                                far = timeline_positions[mainhash] - timeline_positions[basehash]
                                if far <= 0 or abs(near / far - 0.1) > 0.03:
                                    issues.append(f"Timeline: 0/10/100-second spacing is not proportional: {timeline_positions}")
                        commit_circle(page.locator("svg [role=button]").first).click()
                        expect(page.locator("#commit-inspector, .commit-inspector, .inspector")).to_contain_text(mergehash, timeout=2000)
                        selected = page.locator("#commit-inspector, .commit-inspector, .inspector").inner_text()
                        if re.search(r'\b(?:undefined|NaN)\b', selected):
                            issues.append(f'{mode} commit inspector contains an undefined value')
                        initial_width = page.locator("svg").first.evaluate("n=>n.getBoundingClientRect().width")
                        page.get_by_role("button", name="Zoom in", exact=True).click()
                        page.wait_for_function("w=>document.querySelector('svg')?.getBoundingClientRect().width>w", arg=initial_width, timeout=2000)
                        zoomed = page.locator("svg").first.evaluate(
                            "(node)=>node.getBoundingClientRect().width"
                        )
                        page.get_by_role("button", name="Reset", exact=True).click()
                        page.wait_for_function("w=>document.querySelector('svg')?.getBoundingClientRect().width<w", arg=zoomed, timeout=2000)
                        reset = page.locator("svg").first.evaluate(
                            "(node)=>node.getBoundingClientRect().width"
                        )
                        page.wait_for_function("hash=>[...document.querySelectorAll('select option')].some(o=>o.value===hash || o.value==='refs/heads/feature' || ['feature','refs/heads/feature'].includes(o.textContent))", arg=featurehash, timeout=2000)
                        options = page.locator("#branch-filter, select").filter(has=page.locator("option", has_text="All branches")).locator("option").evaluate_all(
                            "nodes => nodes.map(node => ({value:node.value, text:node.textContent}))"
                        )
                        feature_option = next(
                            option["value"]
                            for option in options
                            if option["value"] in (featurehash, "refs/heads/feature")
                            or option["text"] in ("feature", "refs/heads/feature")
                        )
                        page.get_by_role("combobox", name=re.compile("branch", re.I)).or_(page.locator("#branch-filter")).select_option(feature_option)
                        expect(page.locator("svg [role=button]").first).to_have_attribute("aria-label", re.compile(featurehash[:7]), timeout=2000)
                        commit_circle(page.locator("svg [role=button]").first).click()
                        expect(page.locator("#commit-inspector, .commit-inspector, .inspector")).to_contain_text(re.compile(r"Hash\s*" + featurehash), timeout=2000)
                        filtered = page.locator("#commit-inspector, .commit-inspector, .inspector").inner_text()
                        inspector_bounds = page.locator(
                            "#commit-inspector, .commit-inspector, .inspector"
                        ).bounding_box()
                        deadline = time.monotonic() + 2
                        while True:
                            try:
                                page.locator("#commit-inspector, .commit-inspector, .inspector").scroll_into_view_if_needed(timeout=1000)
                                break
                            except Exception:
                                if time.monotonic() >= deadline:
                                    raise
                        inspector_bounds = page.locator(
                            "#commit-inspector, .commit-inspector, .inspector"
                        ).bounding_box()
                        page.screenshot(
                            path=str(out / f"{name}-{mode.lower()}-filtered.png"),
                            full_page=True,
                        )
                        if invalid:
                            issues.append(f"{mode}: invalid SVG coordinates")
                        selected_hash = re.search(
                            r"\bHash\s+([a-f0-9]{40,64})\b", selected
                        )
                        filtered_hash = re.search(
                            r"\bHash\s+([a-f0-9]{40,64})\b", filtered
                        )
                        if not selected_hash or selected_hash.group(1) != mergehash:
                            issues.append(
                                f"{mode}: initial selection did not show the merge hash"
                            )
                        if not filtered_hash or filtered_hash.group(1) != featurehash:
                            issues.append(
                                f"{mode}: filtered selection did not show the feature hash"
                            )
                        if zoomed <= reset:
                            issues.append(f"{mode}: zoom did not change visible width")
                        if (
                            inspector_bounds is None
                            or inspector_bounds["x"] < 0
                            or inspector_bounds["x"] + inspector_bounds["width"]
                            > width + 1
                        ):
                            issues.append(
                                f"{mode}: inspector outside horizontal viewport: {inspector_bounds}"
                            )
                        live_width = page.evaluate(
                            "document.documentElement.scrollWidth"
                        )
                        if live_width > width:
                            issues.append(
                                f"{mode}: document overflow {live_width}>{width}"
                            )
                        checks.append(
                            {
                                "mode": mode,
                                "timeline_positions": timeline_positions,
                                "svg_count": page.locator("svg").count(),
                                "invalid_coordinates": invalid,
                                "selected": selected,
                                "filtered_selection": filtered,
                                "zoomed_width": zoomed,
                                "reset_width": reset,
                                "inspector_visible": page.locator(
                                    "#commit-inspector, .commit-inspector, .inspector"
                                ).is_visible(),
                            }
                        )
                    if dimensions["document"] > dimensions["viewport"]:
                        issues.append(f"Board document overflow: {dimensions}")
                    evidence.append(
                        {
                            "viewport": name,
                            "issues": issues,
                            "dimensions": dimensions,
                            "graph_checks": checks,
                            "real_git_parent_edges": True,
                            "actual_reporter_visible": reporter_verified,
                        }
                    )
                    page.close()
            finally:
                browser.close()
            (out / "result.json").write_text(json.dumps(evidence, indent=2) + "\n")
            print(json.dumps(evidence))
            if any(item["issues"] for item in evidence):
                raise SystemExit(1)
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        log.close()
