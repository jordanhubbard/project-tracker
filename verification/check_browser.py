#!/usr/bin/env python3
"""Exercise a disposable service in Chrome and retain rendering/interaction evidence.

Usage: python verification/check_browser.py /path/to/main.js
This checks board behavior; graph and protocol checks remain separate.
"""

import argparse, json, os, re, socket, subprocess, tempfile, time, traceback, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
from service_response import entity_response

def open_task(page, title):
    control = page.get_by_role('button', name=f'Edit task {title}', exact=True).or_(page.get_by_role('button', name=f'Open task {title}', exact=True))
    if control.count():
        control.first.click(); return
    card = page.locator('[draggable="true"]').filter(has=page.get_by_text(title, exact=True))
    button = card.get_by_role('button', name='Open', exact=True)
    if button.count():
        button.click(); return
    title_button = page.get_by_role('button', name=title, exact=True)
    if title_button.count():
        title_button.first.click(); return
    page.get_by_role('heading', name=title, exact=True).first.click()

def title_control(page, **kwargs):
    return page.get_by_text(kwargs['name'], exact=kwargs.get('exact', False))

def gateway_control(page):
    return page.get_by_label(re.compile(r"^(?:(?:LLM|Assistant) )?Gateway URL$", re.I)).last

def list_control(page, action, name):
    direct = page.get_by_role('button', name=f'{action} list {name}', exact=True)
    if direct.count():
        direct.click()
        return
    page.get_by_role('button', name=f'List menu for {name}', exact=True).click()
    if action == 'Delete':
        page.get_by_role('dialog').get_by_role('button', name='Delete list', exact=True).click()

def task_state(st):
    return st[state_field]

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
                        "state": task_state(st),
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
                    board_url = page.url
                    page.wait_for_timeout(700)
                    page.screenshot(path=str(out / f"{name}-board.png"), full_page=True)
                    (out / f"{name}-board.aria.txt").write_text(
                        page.locator("body").aria_snapshot()
                    )
                    dimensions = page.evaluate(
                        "({viewport:innerWidth,document:document.documentElement.scrollWidth})"
                    )
                    if dimensions['document'] > dimensions['viewport']:
                        overflow = page.evaluate("""() => [...document.querySelectorAll('body *')].map(e => {
                            const r=e.getBoundingClientRect(); const p=e.parentElement; const s=getComputedStyle(e);
                            return {tag:e.tagName,id:e.id,cls:String(e.className),left:r.left,right:r.right,width:r.width,
                                    overflow:s.overflowX,position:s.position,parent:p?.className};
                        }).filter(e=>e.width>0 && e.right>innerWidth+1).slice(0,40)""")
                        (out / f'{name}-overflow.json').write_text(json.dumps(overflow, indent=2))
                    checks = []
                    if name in ("desktop", "mobile"):

                        def check(label, fn):
                            try:
                                fn()
                                checks.append({"check": label, "passed": True})
                            except Exception as e:
                                traceback.print_exc()
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
                                if page.url != board_url: page.goto(board_url)

                        def board_scroll():
                            handle = page.locator('main').evaluate_handle("""root => [...root.querySelectorAll('*')].find(e =>
                                e.clientWidth > 100 && e.scrollWidth > e.clientWidth + 32 &&
                                ['auto','scroll'].includes(getComputedStyle(e).overflowX))""")
                            scroller = handle.as_element()
                            assert scroller is not None, 'Board has no local horizontal scroll container'
                            scroller.hover()
                            page.mouse.wheel(10000, 0)
                            try:
                                deadline = time.monotonic() + 2
                                while time.monotonic() < deadline:
                                    position = scroller.evaluate('e=>({left:e.scrollLeft,width:e.clientWidth,total:e.scrollWidth})')
                                    if position['left'] + position['width'] >= position['total'] - 2:
                                        break
                                    page.wait_for_timeout(100)
                                assert position['left'] > 0, position
                                assert position['left'] + position['width'] >= position['total'] - 2, position
                                after = page.evaluate('({viewport:innerWidth,document:document.documentElement.scrollWidth})')
                                (out / f'{name}-board-scroll.json').write_text(json.dumps({'scroll':position,'dimensions':after}, indent=2))
                                assert after['document'] <= after['viewport'], after
                            finally:
                                page.mouse.wheel(-10000, 0)
                                deadline = time.monotonic() + 2
                                while scroller.evaluate('e=>e.scrollLeft') > 1 and time.monotonic() < deadline:
                                    page.wait_for_timeout(100)

                        check('board horizontal scrolling stays inside the viewport', board_scroll)

                        def create():
                            page.get_by_role(
                                "button", name="Add task", exact=True
                            ).first.click()
                            page.get_by_label("Title", exact=True).fill(
                                f"Browser-created task {name}"
                            )
                            page.get_by_role(
                                "textbox", name="Description", exact=True
                            ).fill("Saved from browser")
                            page.get_by_label(
                                re.compile(r"^Labels", re.I)
                            ).fill("QA")
                            page.get_by_role("dialog").get_by_role(
                                "button", name=re.compile(r"^(?:Save(?: task)?|Create(?: task)?)$")
                            ).click()
                            page.get_by_role("dialog").wait_for(state="hidden")
                            title_control(page,
                                name=f"Browser-created task {name}", exact=True
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
                            open_task(page, f"Browser-created task {name}")
                            page.get_by_role(
                                "textbox", name="Description", exact=True
                            ).fill("Updated in browser")
                            page.get_by_role("dialog").get_by_role(
                                "button", name=re.compile(r"^(?:Save(?: task)?|Create(?: task)?)$")
                            ).click()
                            page.get_by_role("dialog").wait_for(state="hidden")
                            changed = api("GET", f"/api/tasks/{task['id']}")
                            assert changed[
                                "description"
                            ] == "Updated in browser" and changed["labels"] == ["QA"]
                            page.get_by_role(
                                "combobox",
                                name=re.compile(f"Move.*Browser-created task {name}"),
                            ).select_option(task_state(states[1]))
                            page.wait_for_timeout(400)
                            assert (
                                api("GET", f"/api/tasks/{task['id']}")["state"]
                                == task_state(states[1])
                            )

                        check(
                            "edit preserves labels and keyboard move persists",
                            edit_move,
                        )

                        def edit_all_attributes():
                            task = next(t for t in api('GET', f"/api/repos/{repo['id']}/tasks")['items']
                                        if t['title'] == f'Browser-created task {name}')
                            prerequisite = api('POST', f"/api/repos/{repo['id']}/tasks", {
                                'title': f'Browser prerequisite {name}', 'state': task_state(api('GET', f"/api/repos/{repo['id']}/states")['items'][0])})
                            title_control(page, name=prerequisite['title'], exact=True).wait_for(timeout=2000)
                            open_task(page, task['title'])
                            dialog = page.get_by_role('dialog')
                            dialog.get_by_label(re.compile(r'^Assignee$', re.I)).fill('QA operator')
                            dialog.get_by_label(re.compile(r'^Branch$', re.I)).fill('feature/browser-verification')
                            dialog.get_by_label(re.compile(r'^Due date$', re.I)).fill('2026-10-02')
                            dialog.get_by_role('combobox', name=re.compile(r'^Cover(?: colou?r)?$', re.I)).select_option('purple')
                            dialog.get_by_role('combobox', name=re.compile(r'^Priority')).select_option('2')
                            dialog.get_by_label(re.compile(r'^Labels', re.I)).fill('QA, UI')
                            dialog.get_by_role('listbox', name=re.compile(r'^(?:Depends on|Dependencies)', re.I)).select_option(prerequisite['id'])
                            dialog.get_by_role('button', name=re.compile(r'^Add checklist item$', re.I)).click()
                            check_text = dialog.get_by_role('textbox', name=re.compile(r'^Checklist item', re.I))
                            if not check_text.count():
                                check_text = dialog.locator('.checklist-editor li').last.get_by_role('textbox')
                            check_text.last.fill('Review browser attributes')
                            dialog.get_by_role('checkbox', name=re.compile(r'^(?:Done|Completed:|Checklist item completed?|Checklist item \d+ (?:done|complete))', re.I)).last.check()
                            dialog.get_by_role('button', name=re.compile(r'^Save(?: task)?$')).click()
                            dialog.wait_for(state='hidden')
                            saved = api('GET', f"/api/tasks/{task['id']}")
                            assert saved['assignee'] == 'QA operator', saved
                            assert saved['branch'] == 'feature/browser-verification', saved
                            assert saved['due_date'].startswith('2026-10-02'), saved
                            assert saved['cover_color'] == 'purple' and saved['priority'] == 2, saved
                            assert saved['labels'] == ['QA', 'UI'] and saved['dependencies'] == [prerequisite['id']], saved
                            assert any(item['text'] == 'Review browser attributes' and item['done']
                                       for item in saved['checklist']), saved
                            assert saved['description'] == task['description'] and saved['state'] == task['state'], saved
                            page.reload()
                            title_control(page, name=task['title'], exact=True).wait_for()
                            assert api('GET', f"/api/tasks/{task['id']}") == saved

                        check('task dialog persists all editable attributes', edit_all_attributes)

                        def remote():
                            created = api(
                                "POST",
                                f"/api/repos/{repo['id']}/tasks",
                                {
                                    "title": f"Remote change visible {name}",
                                    "priority": 1,
                                },
                            )
                            title_control(page,
                                name=f"Remote change visible {name}", exact=True
                            ).wait_for(timeout=2000)

                            updated_title = f"Remote attribute update visible {name}"
                            api("PATCH", f"/api/tasks/{created['id']}", {
                                "revision": created['revision'], "title": updated_title,
                                "description": "Updated by an independent HTTP client"})
                            title_control(page, name=updated_title, exact=True).wait_for(timeout=2000)
                            assert not title_control(page, name=f"Remote change visible {name}", exact=True).is_visible()
                            open_task(page, updated_title)
                            description = page.get_by_role("textbox", name="Description", exact=True)
                            description.wait_for()
                            assert description.input_value() == "Updated by an independent HTTP client"
                            page.keyboard.press("Escape")
                            page.get_by_role("dialog").wait_for(state="hidden")

                        check("second-client SSE update", remote)

                        def search_tasks():
                            local_filter = page.get_by_role("searchbox", name=re.compile("filter", re.I))
                            search = local_filter if local_filter.count() else page.get_by_role("searchbox").first
                            search.fill(f"Browser-created task {name}")
                            search.press("Tab")
                            title_control(page, name=f"Browser-created task {name}", exact=True).wait_for()
                            page.wait_for_timeout(300)
                            assert not title_control(page, name=f"Remote attribute update visible {name}", exact=True).is_visible()
                            search.fill("")
                            search.press("Tab")
                            title_control(page, name=f"Remote attribute update visible {name}", exact=True).wait_for()

                        check("search filters and restores task cards", search_tasks)

                        def drag_task():
                            # Start after the earlier edit/move phase settles, so this
                            # independently exercises the actual drag/drop path.
                            page.wait_for_timeout(500)
                            task = next(t for t in api("GET", f"/api/repos/{repo['id']}/tasks")["items"]
                                        if t['title'] == f"Browser-created task {name}")
                            destination = states[2]
                            card = page.locator('[draggable="true"]').filter(
                                has=page.get_by_text(task['title'], exact=True))
                            heading = title_control(page, name=re.compile(
                                r"^" + re.escape(destination.get('display_name', destination['name'])) + r"(?:\s|$)", re.I))
                            column = page.locator(f'[data-state-id="{destination["id"]}"]')
                            lists = column.get_by_role("list")
                            target = lists.first if lists.count() else column
                            card.drag_to(target)
                            deadline = time.monotonic() + 2
                            while time.monotonic() < deadline:
                                if api("GET", f"/api/tasks/{task['id']}")["state"] == task_state(destination):
                                    return
                                page.wait_for_timeout(100)
                            raise AssertionError("Drag did not persist the destination state")

                        if name == "desktop":
                            check("drag moves a task between lists", drag_task)
                        else:
                            def mobile_move():
                                page.wait_for_timeout(500)
                                task = next(t for t in api("GET", f"/api/repos/{repo['id']}/tasks")["items"]
                                            if t['title'] == f"Browser-created task {name}")
                                page.get_by_role("combobox", name=re.compile(
                                    f"Move.*Browser-created task {name}")).select_option(task_state(states[2]))
                                deadline = time.monotonic() + 2
                                while time.monotonic() < deadline:
                                    if api("GET", f"/api/tasks/{task['id']}")["state"] == task_state(states[2]):
                                        return
                                    page.wait_for_timeout(100)
                                raise AssertionError("Mobile keyboard move did not persist")
                            check("mobile accessible move with loaded revision", mobile_move)

                        def workflow():
                            current = api('GET', f"/api/repos/{repo['id']}/states")['items']
                            old = current[0]
                            new_name = f'Ready {name}'
                            list_control(page, 'Rename', old['name'])
                            dialog = page.get_by_role('dialog')
                            dialog.get_by_role('textbox', name='List name', exact=True).fill(new_name)
                            dialog.get_by_role('button', name=re.compile(r'^(?:Save|Rename(?: list)?)$')).click()
                            dialog.wait_for(state='hidden')
                            saved = next(x for x in api('GET', f"/api/repos/{repo['id']}/states")['items'] if x['id'] == old['id'])
                            assert saved['name'] == new_name, saved

                        check("rename workflow state", workflow)

                        def workflow_lifecycle():
                            added_name = f'Browser column {name}'
                            page.get_by_role('button', name=re.compile(r'^(?:\+ )?Add list$')).click()
                            dialog = page.get_by_role('dialog')
                            page.wait_for_timeout(400)
                            if not dialog.is_visible():
                                new_states = api('GET', f"/api/repos/{repo['id']}/states")['items']
                                added_default = new_states[-1]
                                page.get_by_role('button', name=f"Rename list {added_default['name']}", exact=True).click()
                            dialog.get_by_role('textbox', name='List name', exact=True).fill(added_name)
                            dialog.get_by_role('button', name=re.compile(r'^(?:Save|Add list)$')).click()
                            dialog.wait_for(state='hidden')
                            current = api('GET', f"/api/repos/{repo['id']}/states")['items']
                            added = next(x for x in current if x['name'] == added_name)
                            page.get_by_role('button', name=f'Move list {added_name} left', exact=True).click()
                            page.wait_for_timeout(400)
                            current = api('GET', f"/api/repos/{repo['id']}/states")['items']
                            assert current[-2]['id'] == added['id'], current
                            page.reload()
                            page.get_by_role('button', name=f'Delete list {added_name}', exact=True).or_(page.get_by_role('button', name=f'List menu for {added_name}', exact=True)).wait_for()
                            assert api('GET', f"/api/repos/{repo['id']}/states")['items'] == current
                            migrating = api('POST', f"/api/repos/{repo['id']}/tasks", {'title': f'Workflow migration {name}', 'state': task_state(added)})
                            title_control(page, name=migrating['title'], exact=True).wait_for()
                            destination = next(x for x in current if x['id'] != added['id'])
                            list_control(page, 'Delete', added_name)
                            dialog.get_by_role('combobox', name=re.compile(r'Destination|Move.*to',re.I)).select_option(label=destination['name'])
                            dialog.get_by_role('button', name=re.compile(r'Delete|Confirm',re.I)).click()
                            dialog.wait_for(state='hidden')
                            assert all(x['id'] != added['id'] for x in api('GET', f"/api/repos/{repo['id']}/states")['items'])
                            assert api('GET', f"/api/tasks/{migrating['id']}")['state'] == task_state(destination)

                        check("add reorder and delete populated workflow state", workflow_lifecycle)

                        def remote_only_graph():
                            page.get_by_role("button", name="Graph", exact=True).or_(
                                page.get_by_role("link", name="Graph", exact=True)
                            ).or_(page.get_by_role("tab", name="Graph", exact=True)).click()
                            page.locator("main").get_by_text(re.compile("checkout", re.I)).first.wait_for()
                            assert page.locator('main svg [role="button"]').count() == 0
                            page.get_by_role("button", name=re.compile(r"^(?:Back to board|Board)$")).or_(
                                page.get_by_role("link", name="Board", exact=True)
                            ).or_(page.get_by_role("tab", name="Board", exact=True)).first.click()
                            page.get_by_role("button", name="Add task", exact=True).first.wait_for()

                        check("remote-only graph explains checkout requirement", remote_only_graph)

                        def inspector():
                            page.get_by_role("button", name="Inspector", exact=True).or_(
                                page.get_by_role("link", name="Inspector", exact=True)
                            ).or_(page.get_by_role("tab", name="Inspector", exact=True)).click()
                            page.get_by_role('textbox', name=re.compile(r'^(?:Repository )?Description$',re.I)).wait_for()
                            origin = page.get_by_role('textbox', name='Remote URL', exact=True)
                            if origin.count():
                                assert origin.input_value() == repo['remote_url']
                            else:
                                page.get_by_text(repo['remote_url'], exact=False).wait_for()
                            page.get_by_role("textbox", name=re.compile(r"^(?:Repository )?Description$", re.I)).fill(
                                f"Repository description from {name}")
                            page.get_by_role("button", name=re.compile(r"^Save(?: (?:description|repository(?: details)?))?$")).click()
                            deadline = time.monotonic() + 2
                            while time.monotonic() < deadline:
                                detail = api("GET", f"/api/repos/{repo['id']}")
                                if detail.get('repository', detail)['description'] == f"Repository description from {name}":
                                    return
                                page.wait_for_timeout(100)
                            raise AssertionError("Repository inspector did not persist description")

                        check("repository inspector displays origin and saves description", inspector)

                        def activity():
                            if name == "mobile":
                                page.get_by_role(
                                    "button",
                                    name=re.compile(
                                        "^menu$|sidebar|(?:Toggle|Show|Hide) repositories", re.I
                                    ),
                                ).click()
                            page.get_by_role("button", name="Activity", exact=True, include_hidden=True).or_(
                                page.get_by_role("link", name="Activity", exact=True, include_hidden=True)
                            ).click()
                            page.get_by_role(
                                "heading", name=re.compile("Activity", re.I)
                            ).wait_for()
                            assert (
                                "Remote attribute update visible"
                                in page.locator("main").inner_text()
                            )
                            if name == "mobile":
                                navigation = (
                                    page.get_by_role(
                                        "button", name="Activity", exact=True, include_hidden=True
                                    )
                                    .or_(
                                        page.get_by_role(
                                            "link", name="Activity", exact=True, include_hidden=True
                                        )
                                    )
                                    .bounding_box()
                                )
                                if navigation and navigation["x"] >= 0 and page.get_by_role("button", name=re.compile("^menu$|sidebar|(?:Toggle|Show|Hide) repositories", re.I)).count():
                                    page.get_by_role(
                                        "button",
                                        name=re.compile(
                                            "^menu$|sidebar|(?:Toggle|Show|Hide) repositories", re.I
                                        ),
                                    ).click()

                        check("activity navigation shows task events", activity)

                        def settings():
                            def open_settings():
                                page.get_by_role('button', name=re.compile(r'^(?:Open settings|Settings)$', re.I)).first.click()
                                page.get_by_role('heading', name='Settings', exact=True).wait_for()
                                edit = page.get_by_role('button', name='Edit settings', exact=True)
                                if edit.count(): edit.click()
                            open_settings()
                            gateway_control(page).fill(
                                "http://127.0.0.1:9/v1"
                            )
                            page.get_by_label(re.compile(r"^(?:(?:LLM|Assistant) )?(?:API )?key", re.I)).fill(
                                "disposable-browser-secret"
                            )
                            page.get_by_label(re.compile(r"^(?:(?:LLM|Assistant) )?Model$", re.I)).fill(
                                "browser-fixture-model"
                            )
                            page.get_by_role(
                                "button", name=re.compile(r"^Save(?: settings)?$")
                            ).click()
                            page.wait_for_timeout(500)
                            saved = api("GET", "/api/settings")
                            assert (
                                saved["llm_url"] == "http://127.0.0.1:9/v1"
                                and saved["llm_model"] == "browser-fixture-model"
                            )
                            assert "disposable-browser-secret" not in json.dumps(saved)
                            if not gateway_control(page).is_visible():
                                open_settings()
                            gateway_control(page).wait_for(state="visible")
                            assert (
                                page.get_by_label(re.compile(r"^(?:(?:LLM|Assistant) )?(?:API )?key", re.I)).input_value()
                                == ""
                            )
                            page.reload(wait_until="domcontentloaded")
                            if not gateway_control(page).is_visible():
                                open_settings()
                            gateway_control(page).wait_for()
                            assert (
                                gateway_control(page).input_value()
                                == "http://127.0.0.1:9/v1"
                            )
                            assert (
                                page.get_by_label(re.compile(r"^(?:(?:LLM|Assistant) )?Model$", re.I)).input_value()
                                == "browser-fixture-model"
                            )
                            assert (
                                page.get_by_label(re.compile(r"^(?:(?:LLM|Assistant) )?(?:API )?key", re.I)).input_value()
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
