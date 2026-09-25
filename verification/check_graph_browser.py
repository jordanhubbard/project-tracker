#!/usr/bin/env python3
"""Verify real Git ancestry and browser graph interactions in an isolated service."""
from test_tools import NODE, CHROME

import argparse, json, os, re, socket, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from service_response import entity_response

def commit_node(page, commit_hash):
    node = page.locator(f'svg [role="button"][data-hash="{commit_hash}"]')
    return node if node.count() else page.locator('svg').get_by_role('button', name=re.compile(commit_hash[:8]))

def commit_circle(node):
    return node if node.evaluate("n=>n.tagName.toLowerCase()") == 'circle' else node.locator('circle').first


def expect_selected_hash(page, commit_hash):
    inspector = page.locator('#commit-inspector, .commit-inspector, .inspector, [aria-label=\"Commit inspector\"]').first
    expect(inspector).to_contain_text(commit_hash, timeout=5000)
    value = inspector.locator('dt').filter(has_text=re.compile(r'^Hash$')).locator('xpath=following-sibling::dd[1]')
    if value.count():
        expect(value).to_have_text(commit_hash, timeout=5000)
    else:
        expect(inspector.get_by_text(re.compile(r'^(?:Hash:\s*)?' + re.escape(commit_hash) + r'$'))).to_be_visible(timeout=5000)

def label_overlaps(page):
    return page.locator('svg').first.evaluate("""svg => {
                            const nodes=[...svg.querySelectorAll('[role=button]')].map(n=>({hash:(n.getAttribute('aria-label')||'').match(/[a-f0-9]{7,64}/)?.[0],rect:n.getBoundingClientRect()}));
                            const result=[];
                            for(const label of svg.querySelectorAll('text')) {
                                const own=nodes.find(n=>n.hash && label.textContent.includes(n.hash));
                                if(!own) continue;
                                const r=label.getBoundingClientRect();
                                for(const node of nodes) if(node.hash!==own.hash) {
                                    const b=node.rect;
                                    if(Math.min(r.right,b.right)-Math.max(r.left,b.left)>1 && Math.min(r.bottom,b.bottom)-Math.max(r.top,b.top)>1)
                                        result.push({label:label.textContent,node:node.hash});
                                }
                            }
                            return result;
                        }""")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("entrypoint", type=Path)
parser.add_argument("--node", default=NODE)
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
            '--litai-serve',
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
            if response.status == 204:
                assert method == 'DELETE', (method, path)
                return None
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
        feature_task_title = 'Feature-only branch association probe'
        main_task_title = 'Main-only branch association probe'
        for title, branch in [(feature_task_title, 'feature'), (main_task_title, 'main')]:
            api('POST', f"/api/repos/{repo['id']}/tasks", {'title': title, 'branch': branch})
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path=CHROME,
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
                        ).or_(page.locator('.repo-card[role="button"], button.repo-card')).first.click()
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
                            repository_view = page.locator("main:visible")
                            repository_view.get_by_role("button", name="Fleet", exact=True).or_(
                                repository_view.get_by_role("link", name="Fleet", exact=True)
                            ).or_(repository_view.get_by_role("tab", name="Fleet", exact=True)).click()
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
                            page.get_by_role('button', name=re.compile(r'^(?:Back to board|Board)$')).or_(page.get_by_role('tab', name='Board', exact=True)).or_(page.get_by_role('link', name='Board', exact=True)).first.click()
                            page.get_by_role('button', name='Graph', exact=True).or_(page.get_by_role('tab', name='Graph', exact=True)).or_(page.get_by_role('link', name='Graph', exact=True)).click()
                            page.wait_for_timeout(400)
                            commit_circle(commit_node(page, mergehash)).click()
                            expect_selected_hash(page, mergehash)
                            if socket.gethostname() not in page.locator('main:visible').inner_text():
                                issues.append('Graph omits the active coding-session host association')
                            page.screenshot(path=str(out / 'desktop-active-session-graph.png'), full_page=True)
                            page.get_by_role('button', name=re.compile(r'^(?:Back to board|Board)$')).or_(page.get_by_role('tab', name='Board', exact=True)).or_(page.get_by_role('link', name='Board', exact=True)).first.click()
                            repository_view.get_by_role('button', name='Fleet', exact=True).or_(repository_view.get_by_role('tab', name='Fleet', exact=True)).or_(repository_view.get_by_role('link', name='Fleet', exact=True)).click()
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
                        overlaps = label_overlaps(page)
                        if overlaps: issues.append(f'{mode}: commit labels overlap other node hit targets: {overlaps}')
                        timeline_positions = {}
                        if mode == "Timeline" and args.irregular_times:
                            nodes = page.locator("svg [role=button]")
                            for index in range(nodes.count()):
                                node = nodes.nth(index)
                                commit_circle(node).click()
                                label = node.get_attribute("aria-label") or ""
                                short_hash = re.search(r"[a-f0-9]{7,64}", label)
                                expected_hash = node.get_attribute('data-hash') or commit_circle(node).get_attribute('data-hash')
                                if expected_hash:
                                    expect_selected_hash(page, expected_hash)
                                elif short_hash:
                                    matching_hashes = [h for h in commits if h.startswith(short_hash.group())]
                                    assert len(matching_hashes) == 1, (label, matching_hashes)
                                    expect_selected_hash(page, matching_hashes[0])
                                details = page.locator('#commit-inspector, .commit-inspector, .inspector, [aria-label=\"Commit inspector\"]').first.inner_text()
                                match = re.search(r"\b([a-f0-9]{40,64})\b", details)
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
                        layout_metrics = page.locator('.graph-scroller, .chart-scroller').evaluate_all("nodes => nodes.map(n => ({bounds:n.getBoundingClientRect().toJSON(),clientHeight:n.clientHeight,scrollHeight:n.scrollHeight,gridRows:getComputedStyle(n.parentElement).gridTemplateRows,svg:n.querySelector('svg')?.getBoundingClientRect().toJSON()}))")
                        (out / f'{name}-{mode.lower()}-layout.json').write_text(json.dumps(layout_metrics, indent=2))
                        if name == 'mobile':
                            assert layout_metrics, 'Missing measured chart viewport'
                            assert all(item['clientHeight'] >= 180 for item in layout_metrics), layout_metrics

                        commit_circle(commit_node(page, mergehash)).click()
                        expect_selected_hash(page, mergehash)
                        selected = page.locator('#commit-inspector, .commit-inspector, .inspector, [aria-label=\"Commit inspector\"]').first.inner_text()
                        if re.search(r'\b(?:undefined|NaN)\b', selected):
                            issues.append(f'{mode} commit inspector contains an undefined value')
                        initial_width = page.locator("svg").first.evaluate("n=>n.getBoundingClientRect().width")
                        initial_node_width = commit_circle(page.locator('svg [role=button]').first).evaluate('n=>n.getBoundingClientRect().width')
                        page.get_by_role('button', name='Zoom in', exact=True).click()
                        page.wait_for_timeout(400)
                        zoomed = page.locator('svg').first.evaluate('n=>n.getBoundingClientRect().width')
                        zoomed_node_width = commit_circle(page.locator('svg [role=button]').first).evaluate('n=>n.getBoundingClientRect().width')
                        overlaps = label_overlaps(page)
                        if overlaps: issues.append(f'{mode} after Zoom in: commit labels overlap other node hit targets: {overlaps}')
                        if zoomed_node_width <= initial_node_width + .1:
                            issues.append(f'{mode}: Zoom in did not enlarge commit geometry ({initial_node_width} -> {zoomed_node_width})')
                        page.get_by_role('button', name=re.compile(r'^Reset(?: zoom| the graph scale)?$')).click()
                        page.wait_for_timeout(400)
                        reset = page.locator('svg').first.evaluate('n=>n.getBoundingClientRect().width')
                        reset_node_width = commit_circle(page.locator('svg [role=button]').first).evaluate('n=>n.getBoundingClientRect().width')
                        overlaps = label_overlaps(page)
                        if overlaps: issues.append(f'{mode} after Reset: commit labels overlap other node hit targets: {overlaps}')
                        if abs(reset_node_width - initial_node_width) > .1:
                            issues.append(f'{mode}: Reset did not restore commit geometry')
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
                        filtered_node = commit_node(page, featurehash)
                        expect(filtered_node).to_be_visible(timeout=2000)
                        commit_circle(filtered_node).click()
                        expect_selected_hash(page, featurehash)
                        filtered = page.locator('#commit-inspector, .commit-inspector, .inspector, [aria-label=\"Commit inspector\"]').first.inner_text()
                        if feature_task_title not in filtered or main_task_title in filtered:
                            issues.append(f'{mode}: filtered feature inspector does not distinguish actual branch task associations')

                        inspector_bounds = page.locator(
                            "#commit-inspector, .commit-inspector, .inspector, [aria-label=\"Commit inspector\"]"
                        ).first.bounding_box()
                        deadline = time.monotonic() + 2
                        while True:
                            try:
                                page.locator('#commit-inspector, .commit-inspector, .inspector, [aria-label=\"Commit inspector\"]').first.scroll_into_view_if_needed(timeout=1000)
                                break
                            except Exception:
                                if time.monotonic() >= deadline:
                                    raise
                        inspector_bounds = page.locator(
                            "#commit-inspector, .commit-inspector, .inspector, [aria-label=\"Commit inspector\"]"
                        ).first.bounding_box()
                        page.screenshot(
                            path=str(out / f"{name}-{mode.lower()}-filtered.png"),
                            full_page=True,
                        )
                        if invalid:
                            issues.append(f"{mode}: invalid SVG coordinates")
                        selected_hash = re.search(
                            r"\b([a-f0-9]{40,64})\b", selected
                        )
                        filtered_hash = re.search(
                            r"\b([a-f0-9]{40,64})\b", filtered
                        )
                        if not selected_hash or selected_hash.group(1) != mergehash:
                            issues.append(
                                f"{mode}: initial selection did not show the merge hash"
                            )
                        if not filtered_hash or filtered_hash.group(1) != featurehash:
                            issues.append(
                                f"{mode}: filtered selection did not show the feature hash"
                            )
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
                                    "#commit-inspector, .commit-inspector, .inspector, [aria-label=\"Commit inspector\"]"
                                ).first.is_visible(),
                            }
                        )
                        task_region = page.locator('#commit-inspector, .commit-inspector, .inspector, [aria-label=\"Commit inspector\"]').first
                        task_link = task_region.get_by_role('link', name=re.compile(re.escape(feature_task_title))).or_(task_region.get_by_role('button', name=re.compile(re.escape(feature_task_title))))
                        if not task_link.count():
                            issues.append(f'{mode}: related task is plain text without an actionable link')
                        else:
                            task_link.first.click()
                            expect(page.get_by_label('Title', exact=True)).to_have_value(feature_task_title)
                            page.screenshot(path=str(out / f'{name}-{mode.lower()}-related-task.png'), full_page=True)
                            # Persist through the editor opened from this association.
                            description = f'Related task edit from {name} {mode}'
                            page.get_by_label('Description', exact=True).fill(description)
                            page.get_by_role('dialog').get_by_role('button', name='Save', exact=True).click()
                            page.get_by_role('dialog').wait_for(state='hidden')
                            linked_task = next(t for t in api('GET', f"/api/repos/{repo['id']}/tasks")['items'] if t['title'] == feature_task_title)
                            assert linked_task['description'] == description, linked_task
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
