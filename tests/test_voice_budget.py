import json,threading,unittest
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from unittest.mock import patch
from open_oracle.server import make_server
class Reviewer:
    def __init__(self):self.calls=0
    def review(self,*args):self.calls+=1;return {'status':'accepted','execution':'offline_stub','label':'Offline budget test'}
class BudgetTests(unittest.TestCase):
    def test_cap_blocks_both_api_transports_before_paid_review(self):
        reviewer=Reviewer()
        with patch('open_oracle.openai_integrations.require_live_authorization'),patch('open_oracle.openai_integrations.DecisionsReviewer',return_value=reviewer):
            server=make_server(port=0,decisions=True,max_live_requests=1)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url='http://127.0.0.1:'+str(server.server_port)
        def post(path,payload):
            request=Request(url+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
            try:
                with urlopen(request) as r:return r.status,r.read().decode()
            except HTTPError as e:return e.code,e.read().decode()
        try:
            self.assertEqual(post('/api/ask',{'question':'COMBAT'})[0],200)
            self.assertEqual(post('/api/ask',{'question':'COMBAT'})[0],429)
            self.assertEqual(post('/api/ag-ui',{'threadId':'voice-budget','runId':'voice-budget-run','messages':[{'id':'u','role':'user','content':'COMBAT'}],'state':{},'tools':[],'context':[],'forwardedProps':{}})[0],429)
            self.assertEqual(reviewer.calls,1)
        finally:server.shutdown();server.server_close();thread.join()
    def test_cap_configuration_rejects_unbounded_or_boolean_values(self):
        for limit in (0,-1,True,'1'):
            with self.assertRaises(ValueError):make_server(port=0,max_live_requests=limit)
        for limit in (0,-1,True,'2',25):
            with self.assertRaises(ValueError):make_server(port=0,max_voice_sessions=limit)
if __name__=='__main__':unittest.main()
