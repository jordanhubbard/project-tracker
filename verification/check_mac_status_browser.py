"""Isolated MAC outage/recovery through already-open browser views."""
import sys,json,os,re,socket,subprocess,tempfile,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from mac_fixture import MacFixture
from service_response import entity_response
entry=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as tmp, MacFixture() as fleet:
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 base=f'http://127.0.0.1:{port}'
 env={k:v for k,v in os.environ.items() if not k.startswith(('TRACKER_','MAC_','OPENAI_'))}
 env.update(TRACKER_DATA_DIR=tmp,TRACKER_MAC_URL=fleet.url,TRACKER_MAC_TOKEN=fleet.token)
 log=(out/'server.log').open('w');proc=subprocess.Popen(['/opt/homebrew/opt/node@22/bin/node',str(entry),'--litai-serve','--host','127.0.0.1','--port',str(port)],env=env,stdout=log,stderr=log)
 def request(path):
  with urllib.request.urlopen(base+path,timeout=5) as r:return entity_response(json.load(r))
 try:
  for _ in range(100):
   try:request('/health');break
   except OSError:time.sleep(.1)
  repo=next(r for r in request('/api/repos')['items'] if r['authority']=='mac')
  tasks=request(f"/api/repos/{repo['id']}/tasks")['items'];task=tasks[0]
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
   context=browser.new_context(viewport={'width':1440,'height':1000});overview=context.new_page();inspector=context.new_page();board=context.new_page()
   errors=[]
   for page in [overview,inspector,board]:
    page.set_default_timeout(15000);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base)
    expect(page.get_by_text('Connected',exact=True)).to_be_visible()
   inspector.locator('.repo-card').filter(has=inspector.get_by_role('heading',name=repo['name'],exact=True)).get_by_role('button',name='Inspector',exact=True).click()
   board.locator('.repo-card').filter(has=board.get_by_role('heading',name=repo['name'],exact=True)).get_by_role('button',name='Open board',exact=True).click()
   card=overview.locator('.repo-card').filter(has=overview.get_by_role('heading',name=repo['name'],exact=True))
   sync_value=inspector.locator('main .error-state').filter(has_text=re.compile('^Sync error:'))
   expect(sync_value).to_have_count(0);expect(card).not_to_contain_text('Sync error:')
   overview.evaluate("""() => { window.probeEvents=[]; window.probeSource=new EventSource('/api/events'); window.probeReady=false; probeSource.onopen=()=>window.probeReady=true; probeSource.addEventListener('repository.changed',e=>probeEvents.push({id:e.lastEventId,data:JSON.parse(e.data)})); }""")
   overview.wait_for_function('window.probeReady');overview.evaluate('window.probeEvents=[]')
   writes=len(fleet.writes);fleet.unavailable=True
   expect(card).to_contain_text('Sync error:',timeout=20000);expect(sync_value).to_be_visible(timeout=20000)
   overview.screenshot(path=str(out/'overview-outage.png'),full_page=True);inspector.screenshot(path=str(out/'inspector-outage.png'),full_page=True)
   outage_events=overview.evaluate('window.probeEvents');assert outage_events,outage_events
   overview.wait_for_timeout(11000)
   assert overview.evaluate('window.probeEvents')==outage_events,'Repeated failure emitted duplicate repo updates'
   board.get_by_role('button',name=f"Edit task {task['title']}",exact=True).click();dialog=board.get_by_role('dialog')
   dialog.get_by_label('Title',exact=True).fill('Outage must reject this edit');dialog.get_by_role('button',name='Save',exact=True).click()
   expect(board.get_by_role('alert')).to_contain_text(re.compile('unavailable|offline|503|outage|failed',re.I))
   assert request(f"/api/repos/{repo['id']}/tasks")['items']==tasks
   assert len(fleet.writes)==writes
   board.screenshot(path=str(out/'mutation-rejected.png'),full_page=True)
   dialog.get_by_role('button',name='Cancel',exact=True).click()
   fleet.unavailable=False
   try:
    expect(card).not_to_contain_text('Sync error:',timeout=20000);expect(sync_value).to_have_count(0,timeout=20000)
   except Exception:
    (out/'recovery-failure.json').write_text(json.dumps({'repository':request(f"/api/repos/{repo['id']}"),'overview':card.inner_text(),'inspector':sync_value.all_text_contents(),'events':overview.evaluate('window.probeEvents')},indent=2)+'\n')
    overview.screenshot(path=str(out/'recovery-failure.png'),full_page=True)
    raise
   recovery_events=overview.evaluate('window.probeEvents');assert len(recovery_events)>len(outage_events)
   overview.wait_for_timeout(11000)
   assert overview.evaluate('window.probeEvents')==recovery_events,'Unchanged healthy poll emitted duplicate repo updates'
   assert request(f"/api/repos/{repo['id']}/tasks")['items']==tasks
   assert len(fleet.writes)==writes
   assert not errors,errors
   overview.screenshot(path=str(out/'overview-recovered.png'),full_page=True);inspector.screenshot(path=str(out/'inspector-recovered.png'),full_page=True)
   (out/'result.json').write_text(json.dumps({'ok':True,'open_views_updated_without_reload':True,'unchanged_tasks':True,'no_duplicate_status_events':True,'rejected_mutation_no_writes':True,'events':recovery_events,'page_errors':errors},indent=2)+'\n')
   browser.close()
 finally:
  proc.terminate()
  try:proc.wait(timeout=8)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
  log.close()
