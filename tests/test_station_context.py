import unittest, threading, json
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from open_oracle.server import make_server, configured_station, station_context
STATION={'election_date':'2026-11-03','authority':'KCEB','municipality':'Kansas City within Jackson County'}
class StationTests(unittest.TestCase):
 def test_admin_context_cannot_be_overridden(self):
  self.assertEqual(station_context(STATION,{}),STATION)
  self.assertEqual(station_context(STATION,{'authority':'KCEB'}),STATION)
  for value in ({'authority':'JCEB'},{'election_date':'2024-11-05'},{'district':'foreign'}):
   with self.assertRaises(ValueError):station_context(STATION,value)
  for value in ({'authority':'unknown'},STATION|{'district':'other'},STATION|{'municipality':'\n'}):
   with self.assertRaises(ValueError):configured_station(value)
 def test_actual_http_station_and_script_delivery(self):
  server=make_server(port=0,station_scope=STATION);threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}'
  try:
   self.assertEqual(json.load(urlopen(url+'/api/health'))['station_scope'],STATION)
   for route in ('/render-bindings.js','/release-store.js','/icons/phosphor/phone.svg'):
    with urlopen(url+route) as response:self.assertEqual(response.status,200)
   for route in ('/api/render-catalog?authority=JCEB','/api/ask','/api/ag-ui'):
    if 'catalog' in route:req=url+route
    elif route.endswith('ask'):req=Request(url+route,data=json.dumps({'question':'Explain Amendment 7','scope':{'authority':'JCEB'}}).encode(),headers={'Content-Type':'application/json'})
    else:req=Request(url+route,data=json.dumps({'threadId':'thread','runId':'run','messages':[{'id':'m','role':'user','content':'Explain Amendment 7'}],'tools':[],'context':[],'forwardedProps':{'scope':{'authority':'JCEB'}}}).encode(),headers={'Content-Type':'application/json'})
    with self.assertRaises(HTTPError) as err:urlopen(req)
    self.assertEqual(err.exception.code,400)
   response=json.load(urlopen(Request(url+'/api/ask',data=json.dumps({'question':'What does No mean?','contest_id':'amendment-7'}).encode(),headers={'Content-Type':'application/json'})))
   self.assertEqual(response['status'],'answered');self.assertEqual(response['contest']['id'],'amendment-7')
  finally:server.shutdown();server.server_close()
if __name__=='__main__':unittest.main()
