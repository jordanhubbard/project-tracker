#!/usr/bin/env python3
"""Verify the visible cookie-login flow on an isolated token-protected backend."""
from test_tools import NODE, CHROME
import argparse,json,os,re,socket,subprocess,tempfile,time,urllib.request,urllib.error,uuid
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
p=argparse.ArgumentParser(description=__doc__);p.add_argument('entrypoint',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--node',default=NODE);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 base=f'http://127.0.0.1:{port}';token='disposable-login-'+uuid.uuid4().hex
 env={k:v for k,v in os.environ.items() if not k.startswith(('TRACKER_','MAC_','OPENAI_'))};env.update(TRACKER_DATA_DIR=tmp,TRACKER_MAC_URL='',TRACKER_ACCESS_TOKEN=token)
 log=(a.output/'server.log').open('w');proc=subprocess.Popen([a.node,str(a.entrypoint.resolve()),'--litai-serve','--host','127.0.0.1','--port',str(port)],env=env,stdout=log,stderr=log)
 try:
  for _ in range(100):
   try:urllib.request.urlopen(base+'/health',timeout=2).close();break
   except OSError:time.sleep(.1)
  req=urllib.request.Request(base+'/api/repos',data=json.dumps({'name':'Protected repository','remote_url':'https://example.test/private/project.git'}).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+token},method='POST')
  urllib.request.urlopen(req,timeout=5).close()
  for path in ['/api/repos','/api/sessions','/api/events']:
   try:
    with urllib.request.urlopen(base+path,timeout=3) as response:
     raise AssertionError(f'Unauthenticated {path} returned {response.status}')
   except urllib.error.HTTPError as error:
    assert error.code in (401,403),(path,error.code)
  foreign=urllib.request.Request(base+'/api/login',data=json.dumps({'password':token}).encode(),headers={'Content-Type':'application/json','Origin':'http://example.test'},method='POST')
  try:
   with urllib.request.urlopen(foreign,timeout=3) as response:
    raise AssertionError(f'Cross-origin login returned {response.status}')
  except urllib.error.HTTPError as error:
   assert error.code in (401,403),error.code
  results=[]
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=CHROME)
   for name,width in [('desktop',1440),('mobile',390)]:
    context=browser.new_context(viewport={'width':width,'height':1000});page=context.new_page();page.set_default_timeout(5000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    try:
     page.goto(base)
     password=page.get_by_label(re.compile(r'^\s*(?:Access token|Password|Tracker access token)\s*$',re.I))
     expect(password).to_be_visible();expect(password).to_have_attribute('type','password')
     expect(page.locator('body')).not_to_contain_text('Protected repository')
     submit=page.get_by_role('button',name=re.compile(r'^(?:Sign in|Log in|Login)$',re.I))
     password.fill('invalid-disposable-token');submit.click()
     expect(page.locator('body')).to_contain_text(re.compile('invalid|incorrect|not valid|not accepted|unauthorized|not match|authentication failed',re.I))
     expect(password).to_be_visible();expect(page.locator('body')).not_to_contain_text('Protected repository')
     page.screenshot(path=str(a.output/f'{name}-invalid.png'),full_page=True)
     password.fill(token);submit.click()
     expect(page.get_by_role('heading',name='Project overview',exact=True)).to_be_visible()
     expect(page.get_by_text('Connected',exact=True)).to_be_visible()
     expect(page.get_by_role('heading',name='Protected repository',exact=True)).to_be_visible()
     cookies=context.cookies();assert any(c['httpOnly'] and c['sameSite'] in ('Strict','Lax') for c in cookies),cookies
     assert token not in page.url and token not in page.locator('body').inner_text()
     storage=page.evaluate('JSON.stringify({local:{...localStorage},session:{...sessionStorage}})');assert token not in storage, 'Access token retained in browser storage'
     page.reload();expect(page.get_by_role('heading',name='Project overview',exact=True)).to_be_visible()
     page.screenshot(path=str(a.output/f'{name}-authenticated.png'),full_page=True)
     context.clear_cookies();page.reload();expect(password).to_be_visible()
     expect(page.locator('body')).not_to_contain_text('Protected repository');assert not errors,errors
     results.append({'viewport':name,'ok':True,'visible_login':True,'unauthenticated_data_and_events_denied':True,'cross_origin_login_denied':True,'invalid_token_feedback':True,'authenticated_overview_and_events':True,'http_only_same_site_cookie':True,'reload_session':True,'cleared_session_returns_to_login':True,'no_token_in_url_storage_or_text':True})
    except Exception:
     (a.output/f'{name}-failure.aria.txt').write_text(page.locator('body').aria_snapshot());page.screenshot(path=str(a.output/f'{name}-failure.png'),full_page=True);raise
    finally:context.close()
   browser.close()
  (a.output/'result.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
 finally:
  proc.terminate()
  try:proc.wait(timeout=8)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
  log.close()
