import json,threading,unittest
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from unittest.mock import patch
from open_oracle.server import make_server
class ReviewGuardTests(unittest.TestCase):
 def test_voice_slot_health_spent_once_and_no_second_provider_call(self):
  calls=[]
  class FakeLive:
   def create(self,sdp):calls.append(sdp);return{'session':{'id':'offline-fixture'},'transport':{'type':'webrtc','sdp':'v=0'}}
  with patch('open_oracle.openai_integrations.require_live_authorization'),patch('open_oracle.orchestration.build_selector',return_value=None),patch('open_oracle.openai_integrations.DecisionsReviewer'),patch('open_oracle.openai_integrations.LiveSessions',return_value=FakeLive()):server=make_server(port=0,live=True,live_voice=True,max_live_requests=1,operator_name='Test operator')
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{server.server_port}'
  def post():
   request=Request(url+'/api/live/session',data=json.dumps({'sdp':'v=0'}).encode(),headers={'Content-Type':'application/json','Origin':url})
   try:
    with urlopen(request) as response:return response.status
   except HTTPError as error:return error.code
  try:
   self.assertTrue(json.load(urlopen(url+'/api/health'))['voice_session_available']);self.assertEqual(post(),201);self.assertFalse(json.load(urlopen(url+'/api/health'))['voice_session_available']);self.assertEqual(post(),429);self.assertEqual(len(calls),1)
  finally:server.shutdown();server.server_close();thread.join()
 def test_operator_name_is_truthful_bounded_text(self):
  for name in ['', 'x'*101, 'newline\nname', True]:
   with self.assertRaises(ValueError):make_server(port=0,operator_name=name)
if __name__=='__main__':unittest.main()
