#!/usr/bin/env python3
from test_tools import NODE, CHROME
import argparse, json, os, re, socket, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
from service_response import entity_response
parser = argparse.ArgumentParser(description="Verify peer registration and remote task creation through Chrome.")
parser.add_argument('entrypoint', type=Path)
parser.add_argument('--node', default=NODE)
parser.add_argument('--output', type=Path, default=Path('_build/peer-browser'))
args = parser.parse_args()
entry = args.entrypoint.resolve(strict=True)
out = args.output; out.mkdir(parents=True, exist_ok=True)
processes=[]
with tempfile.TemporaryDirectory() as root:
  log=(out/'server.log').open('w')
  def request(base, method, path, body=None, token=None):
    headers={'Content-Type':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    req=urllib.request.Request(base+path, method=method, headers=headers,
          data=None if body is None else json.dumps(body).encode())
    with urllib.request.urlopen(req, timeout=5) as r:return entity_response(json.load(r))
  def start(name, token=''):
    with socket.socket() as s:s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
    env={k:v for k,v in os.environ.items() if not k.startswith(('TRACKER_','MAC_','OPENAI_'))}
    env.update(TRACKER_DATA_DIR=str(Path(root)/name),TRACKER_MAC_URL='',TRACKER_ACCESS_TOKEN=token)
    p=subprocess.Popen([args.node,str(entry),'--litai-serve','--host','127.0.0.1','--port',str(port)],env=env,stdout=log,stderr=log);processes.append(p)
    base=f'http://127.0.0.1:{port}'
    for _ in range(100):
      try:request(base,'GET','/health');return base
      except OSError:time.sleep(.1)
    raise AssertionError('startup failed')
  try:
    a=start('a'); token='disposable-ui-peer-token'; b=start('b',token)
    remote=request(b,'POST','/api/repos',{'name':'Remote only','remote_url':'https://example.test/remote/only.git'},token)
    with sync_playwright() as p:
      browser=p.chromium.launch(executable_path=CHROME)
      page=browser.new_page(viewport={'width':1440,'height':1000});page.set_default_timeout(5000)
      errors=[]
      page.on('pageerror', lambda e: (errors.append(str(e)), (out/'page-errors.json').write_text(json.dumps(errors))))
      page.goto(a)
      page.get_by_role('heading',name='Project overview').wait_for()
      register = page.get_by_role('button',name=re.compile(r'^(?:Register (?:a )?|Add )repository$'))
      (register.first if register.count() else page.get_by_role('button', name='Create', exact=True).first).click()
      page.get_by_label(re.compile(r'^(?:(?:Repository |Display )?Name)',re.I)).fill('Local only')
      page.get_by_label(re.compile(r'^Remote URL',re.I)).fill('https://example.test/local/only.git')
      page.get_by_role('dialog').get_by_role('button', name=re.compile(r'^(?:Register(?: repository| locally)?|Save)$')).click()
      try: page.get_by_role('dialog').wait_for(state='hidden')
      except Exception:
        page.screenshot(path=str(out/'registration-failure.png'),full_page=True)
        (out/'registration-failure.aria.txt').write_text(page.locator('body').aria_snapshot())
        (out/'registration-failure.json').write_text(json.dumps({'url':page.url,'repos':request(a,'GET','/api/repos'),'page_errors':errors},indent=2))
        errors.append('Registration dialog remained open after submission')
        page.get_by_role('dialog').get_by_role('button',name='Cancel',exact=True).click()
      local=next(repo for repo in request(a,'GET','/api/repos')['items'] if repo['name']=='Local only')
      assert local['remote_url']=='https://example.test/local/only.git' and local['authority']=='local'
      page.get_by_role('button',name='Agents & peers',exact=True).click()
      if not page.get_by_label(re.compile(r'^(?:Peer (?:base )?URL|Base URL|Peer A2A endpoint URL)$')).count():
        page.get_by_role('button', name=re.compile(r'^Register (?:a )?peer$')).click()
      display = page.get_by_role('textbox', name=re.compile(r'^(?:Name|Display name|Peer name)$'))
      if display.count(): display.fill('Remote verification peer')
      page.get_by_label(re.compile(r'^(?:Peer (?:base )?URL|Base URL|Peer A2A endpoint URL)$')).fill(b)
      page.get_by_label(re.compile(r'^(?:(?:Peer bearer t|Peer t|T)oken \(stored backend-only\)|Peer access token \((?:write only|stored backend-only)\)|Bearer credential \(stored on this backend only\)|Access token \(write only\)|Bearer token \(stored backend-only\)|Peer token \(write only\)|Access token \(stored backend-only\)|Outbound token \(write-only\)|Peer access token|Peer bearer token|Access token).*$')).and_(page.locator('input:visible')).fill(token)
      scope = page.get_by_role('dialog') if page.get_by_role('dialog').count() else page
      scope.get_by_role('button',name=re.compile(r'^(?:Register(?: peer)?|Save)$')).click()
      page.get_by_role('button',name=re.compile(r'^Send (?:a )?message(?: to .+)?$')).click()
      control=page.get_by_role('combobox',name=re.compile(r'^Remote repository id')).or_(page.get_by_role('textbox',name=re.compile(r'^Remote repository id')))
      page.wait_for_timeout(500)
      (out/'dialog.aria.txt').write_text(page.locator('body').aria_snapshot())
      page.screenshot(path=str(out/'remote-selection.png'),full_page=True)
      evidence={'local_registration_ui':True,'local_id':local['id'],'remote_id':remote['id'], 'control':control.evaluate('(e)=>({tag:e.tagName,options:[...e.querySelectorAll("option")].map(o=>({value:o.value,label:o.textContent}))})')}
      (out/'result.json').write_text(json.dumps(evidence,indent=2))
      page.screenshot(path=str(out/'remote-selection.png'),full_page=True)
      if evidence['control']['tag']=='SELECT':
        assert any(o['value']==remote['id'] for o in evidence['control']['options']), 'Remote repository is absent; selector contains only local IDs'
        control.select_option(remote['id'])
      else:control.fill(remote['id'])
      page.get_by_label('Task title',exact=True).fill('Created through peer UI')
      page.get_by_role('dialog').get_by_role('button',name=re.compile(r'^(?:Send(?: create_task| message)?|Save)$')).click();page.wait_for_timeout(1000)
      tasks=request(b,'GET',f"/api/repos/{remote['id']}/tasks",token=token)['items']
      assert any(t['title']=='Created through peer UI' for t in tasks), tasks
      assert token not in json.dumps(request(a,'GET','/api/peers'))
      active_dialog = page.get_by_role('dialog')
      if active_dialog.count():
        active_dialog.get_by_role('button', name=re.compile(r'^(?:Close|Cancel)$')).click()
      page.once('dialog', lambda d: d.accept())
      page.get_by_role('button',name=re.compile(r'^Remove(?: peer(?: .+)?)?$')).click()
      confirm = page.get_by_role('dialog').get_by_role('button', name=re.compile(r'^(?:Confirm|Remove(?: peer)?)$'))
      if confirm.count(): confirm.click()
      deadline=time.monotonic()+2
      while request(a,'GET','/api/peers')['items'] and time.monotonic()<deadline:page.wait_for_timeout(100)
      assert not request(a,'GET','/api/peers')['items']
      assert not errors, errors
      evidence.update(ok=True, remote_task_created=True, peer_removed=True, page_errors=errors)
      (out/'result.json').write_text(json.dumps(evidence,indent=2))
      browser.close()
  finally:
    for p in processes:
      p.terminate()
      try:p.wait(timeout=5)
      except subprocess.TimeoutExpired:p.kill();p.wait()
    log.close()
