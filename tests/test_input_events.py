import io,json,threading,unittest
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from unittest.mock import patch
from open_oracle.input_events import InputEvents
from open_oracle.server import make_server

class InputTests(unittest.TestCase):
 def setUp(self):
  self.clock=10.0;self.inbox=InputEvents(clock=lambda:self.clock,presence=True,wave=True)
 def event(self,type='ready',source='camera',sequence=1,session='producer-session',**extra):
  return {'schema':'open-oracle-input/v1','type':type,'source':source,'session_id':session,'sequence':sequence,'monotonic_ms':(self.clock-10)*1000,'synthetic':False,**extra}
 def prime(self):
  self.assertTrue(self.inbox.accept(self.event()));self.assertTrue(self.inbox.accept(self.event('frame_acquired',sequence=2)))
 def test_ready_is_not_frame_proof_or_default_capability(self):
  self.inbox.accept(self.event());self.assertFalse(self.inbox.snapshot()['available']);default=InputEvents(clock=lambda:self.clock);default.accept(self.event());default.accept(self.event('frame_acquired',sequence=2));self.assertTrue(default.snapshot()['available']);self.assertFalse(any(default.snapshot()['capabilities'].values()))
 def test_metadata_only_and_bounded_queue(self):
  self.prime()
  for i in range(3,103):self.inbox.accept(self.event('presence_detected',sequence=i,audio='not retained',image='not retained',question='not retained'))
  data=self.inbox.snapshot();self.assertEqual(len(data['events']),64);self.assertTrue(data['discontinuity']);self.assertEqual(set(data['events'][0]),{'schema','type','source','session_id','sequence','monotonic_ms','synthetic'})
 def test_rejects_synthetic_missing_malformed_duplicate_stale_future(self):
  self.prime()
  for e in [self.event('start_requested','camera_wave',3,synthetic=True),self.event('start_requested','camera_wave',3,synthetic=None),self.event('start_requested',['camera_wave'],3),self.event('start_requested','camera_wave',True),self.event('start_requested','camera_wave',2),self.event('start_requested','camera_wave',3,monotonic_ms=float('nan')),self.event('start_requested','camera_wave',3,monotonic_ms=1000)]:self.assertFalse(self.inbox.accept(e))
  self.clock=13;self.assertFalse(self.inbox.accept(self.event('start_requested','camera_wave',3,monotonic_ms=0)))
 def test_frame_lease_eof_error_unknown_not_departure(self):
  self.prime();self.assertTrue(self.inbox.snapshot()['available']);self.clock+=4;self.assertFalse(self.inbox.snapshot()['available']);self.inbox.accept(self.event('frame_acquired',sequence=3));self.assertTrue(self.inbox.snapshot()['available']);self.inbox.accept(self.event('error',sequence=4));self.assertFalse(self.inbox.snapshot()['available']);self.assertNotIn('departure_confirmed',json.dumps(self.inbox.snapshot()))
 def test_closed_producer_cannot_reactivate_without_new_ready(self):
  self.prime();self.inbox.stopped();self.assertFalse(self.inbox.snapshot()['available']);self.assertFalse(self.inbox.accept(self.event('frame_acquired',sequence=3)))
 def test_consumer_bounds_record_and_handles_invalid_json(self):
  self.inbox.consume(io.StringIO('invalid\n'+json.dumps(self.event())+'\n'+json.dumps(self.event('frame_acquired',sequence=2))+'\n'));self.assertFalse(self.inbox.snapshot()['available']);self.assertEqual(self.inbox.sequence,2)
  self.inbox.consume(io.StringIO('x'*8193+'\n'));self.assertFalse(self.inbox.snapshot()['available'])
 def test_new_sessions_need_ready_and_retired_sessions_cannot_replay(self):
  self.prime();self.assertFalse(self.inbox.accept(self.event('start_requested','camera_wave',1,'different-session')));self.assertTrue(self.inbox.accept(self.event(session='different-session')));self.assertFalse(self.inbox.accept(self.event(session='producer-session')))
 def test_invalid_cursor_and_lease(self):
  for v in [-1,True,'1']:
   with self.assertRaises(ValueError):self.inbox.snapshot(v)
  for v in [0,float('nan'),20]:
   with self.assertRaises(ValueError):InputEvents(lease_seconds=v)

class HttpInputTests(unittest.TestCase):
 def test_disabled_route_and_loopback_only_guard(self):
  server=make_server(port=0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with self.assertRaises(HTTPError) as error:urlopen(f'http://127.0.0.1:{server.server_port}/api/input-events')
   self.assertEqual(error.exception.code,404)
  finally:server.shutdown();server.server_close();thread.join()
  with self.assertRaises(ValueError):make_server(host='0.0.0.0',port=0,input_events=InputEvents())
 def test_actual_http_only_reads_sanitized_inputs_and_rejects_foreign_origin(self):
  inbox=InputEvents();server=make_server(port=0,input_events=inbox);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{server.server_port}'
  try:
   health=json.load(urlopen(url+'/api/health'));self.assertTrue(health['input_events']['enabled']);self.assertEqual(health['voice'],'not_connected');data=json.load(urlopen(url+'/api/input-events?after=0'));self.assertFalse(data['available'])
   for path in ['/api/input-events?after=-1','/api/input-events?after=garbage']:
    with self.assertRaises(HTTPError) as error:urlopen(url+path)
    self.assertEqual(error.exception.code,400)
   with self.assertRaises(HTTPError) as error:urlopen(Request(url+'/api/input-events',headers={'Origin':'https://unrelated.example'}))
   self.assertEqual(error.exception.code,403)
   with self.assertRaises(HTTPError) as error:urlopen(Request(url+'/api/input-events',data=b'{}',headers={'Content-Type':'application/json'}))
   self.assertEqual(error.exception.code,404)
  finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':unittest.main()
