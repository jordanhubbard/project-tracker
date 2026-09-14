"""Verify rejected local dependency writes through actual HTTP and durable state."""
import argparse,json,os,socket,sqlite3,subprocess,sys,tempfile,time,urllib.request,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from service_response import entity_response
from test_tools import NODE
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='tracker-invalid-edges-') as td:
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 env={k:v for k,v in os.environ.items() if not k.startswith(('TRACKER_','MAC_','OPENAI_'))};env.update(TRACKER_DATA_DIR=td,TRACKER_MAC_URL='',TRACKER_MAC_TOKEN='')
 log=(a.output/'server.log').open('w');proc=subprocess.Popen([NODE,str(a.source.resolve()/'main.js'),'--litai-serve','--host','127.0.0.1','--port',str(port)],env=env,stdout=log,stderr=log)
 def req(method,path,body=None):
  r=urllib.request.Request(f'http://127.0.0.1:{port}'+path,method=method,headers={'Content-Type':'application/json'},data=None if body is None else json.dumps(body).encode())
  try:
   with urllib.request.urlopen(r,timeout=5) as response:return response.status,entity_response(json.load(response))
  except urllib.error.HTTPError as error:return error.code,json.loads(error.read())
 def good(method,path,body=None):
  status,result=req(method,path,body);assert status in (200,201),(status,result);return result
 try:
  for _ in range(100):
   try:good('GET','/health');break
   except OSError:time.sleep(.1)
  else:raise AssertionError('Service did not start')
  repo=good('POST','/api/repos',{'name':'Dependency validation','remote_url':'https://example.test/dependency-validation.git'})
  other=good('POST','/api/repos',{'name':'Other validation','remote_url':'https://example.test/other-validation.git'})
  b=good('POST',f"/api/repos/{repo['id']}/tasks",{'title':'Prerequisite'})
  c=good('POST',f"/api/repos/{other['id']}/tasks",{'title':'Other prerequisite'})
  task=good('POST',f"/api/repos/{repo['id']}/tasks",{'title':'Dependent','dependencies':[b['id']]})
  databases=[x for x in Path(td).rglob('*') if x.is_file() and x.open('rb').read(16)==b'SQLite format 3\x00'];assert len(databases)==1,databases
  def snapshot():
   with sqlite3.connect(str(databases[0])) as db:return {table:db.execute('SELECT * FROM '+table+' ORDER BY rowid').fetchall() for table in ('tasks','events')}
  baseline=snapshot();checks=[]
  cases=[('self',task,[task['id']]),('unknown',task,['missing-validation-task']),('cross_repository',task,[c['id']]),('cycle',b,[task['id']])]
  for name,target,deps in cases:
   status,error=req('PATCH',f"/api/tasks/{target['id']}",{'revision':target['revision'],'expected_revision':target['revision'],'dependencies':deps,'title':'Must not persist'})
   assert status in (400,409,422),(name,status,error)
   assert 'internal_error' not in json.dumps(error),(name,error)
   assert snapshot()==baseline,name+' changed rows or events'
   checks.append({'case':name,'status':status,'unchanged_tasks_and_events':True})
  for name,deps in [('unknown_create',['missing-validation-task']),('cross_repository_create',[c['id']])]:
   status,error=req('POST',f"/api/repos/{repo['id']}/tasks",{'title':'Must not create','dependencies':deps})
   assert status in (400,409,422),(name,status,error)
   assert snapshot()==baseline,name+' changed rows or events'
   checks.append({'case':name,'status':status,'unchanged_tasks_and_events':True})
  result={'ok':True,'checks':checks};(a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
 finally:
  proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
  log.close()
