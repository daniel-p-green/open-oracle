import copy, json, tempfile, threading, unittest
from pathlib import Path
from uuid import uuid4
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from unittest.mock import patch
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.server import make_server
from open_oracle.session_control import VisitorSessions, SessionCancelled, operation, accepted_speech
from open_oracle.privacy_faq import erase_intent, data_use_faq

class SyntheticReview:
    def review(self, envelope):
        return {'status': 'accepted', 'execution': 'real_api', 'label': 'OFFLINE fixture exercises the real-api branch; no provider call'}

class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.corpus = Corpus()
        self.result = EvidenceLoop(self.corpus, reviewer=SyntheticReview()).answer('What is the COMBAT tax rate?', request_id='accepted-question')

    def test_receipt_is_server_owned_bound_and_isolated(self):
        store = VisitorSessions(); a, b = str(uuid4()), str(uuid4())
        store.begin(a); store.retain(a, self.result, self.corpus); store.begin(b)
        self.assertEqual(store.speech(a, 'accepted-question', self.corpus)['text'], self.result['answer'])
        self.assertIsNone(store.speech(b, 'accepted-question', self.corpus)); self.assertIsNone(store.speech(a, 'forged', self.corpus))
        self.result['answer'] = 'Vote yes.'
        self.assertNotEqual(store.speech(a, 'accepted-question', self.corpus)['text'], self.result['answer'])

    def test_review_number_and_binding_cannot_be_forged(self):
        for mutate in [lambda r:r['review'].update(execution='offline_stub'), lambda r:r['speech'].update(text='Vote yes.'), lambda r:r['evidence'][0].update(sha256='x')]:
            r=copy.deepcopy(self.result);mutate(r);self.assertIsNone(accepted_speech(r,self.corpus))
        r=copy.deepcopy(self.result);r['answer']='The printed tax rate is one-half of one cent.';r['speech']['text']=r['answer']
        self.assertIsNone(accepted_speech(r,self.corpus))

    def test_source_file_change_rechecks_before_speech(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'changed.pdf';p.write_bytes(b'changed');self.corpus.originals['jceb-sample']=p
            self.assertIsNone(accepted_speech(self.result,self.corpus))

    def test_erase_cancels_and_blocks_late_retention_and_reuse(self):
        store=VisitorSessions();s=str(uuid4());signal=store.begin(s);store.retain(s,self.result,self.corpus);store.erase(s)
        self.assertTrue(signal.is_set());store.retain(s,self.result,self.corpus);self.assertIsNone(store.speech(s,'accepted-question',self.corpus))
        with self.assertRaises(SessionCancelled):store.begin(s)
        with self.assertRaises(SessionCancelled):
            with operation(signal):EvidenceLoop(self.corpus, reviewer=SyntheticReview()).answer('COMBAT')

    def test_expiry_and_capacity_are_bounded(self):
        t=[0];store=VisitorSessions(now=lambda:t[0],capacity=1);s=str(uuid4());store.begin(s);store.retain(s,self.result,self.corpus);store.end(s)
        with self.assertRaises(ValueError):store.begin(str(uuid4()))
        t[0]=181;self.assertIsNone(store.speech(s,'accepted-question',self.corpus));t[0]=601;store.begin(str(uuid4()));self.assertEqual(len(store.entries),1)

    def test_equivalent_commands_and_faq_truth(self):
        for text in ['erase this session','Please delete my session.','borra esta sesión','efface cette session','lösche diese Sitzung','apague esta sessão']:self.assertTrue(erase_intent(text))
        for text in ['What does erase this session mean?','Do not erase this session','erase the ballot','Vote yes']:self.assertFalse(erase_intent(text))
        faq=data_use_faq();self.assertIsNone(faq['runtime']['model_provider']);self.assertFalse(faq['account_retention_verified']);self.assertTrue(any('does not listen' in x['text'] for x in faq['items']))

class HttpReceiptTests(unittest.TestCase):
    def test_rehearsal_capture_and_two_amendment_answers_share_a_finite_allowance(self):
        # Authored transport fixtures only: real HTTP/engine/receipt/quota behavior.
        def selector(q,scope,contest,corpus): return ([e['id'] for e in corpus.search(contest,scope)],[])
        def render(contract,cancel): return {'accepted': True, 'text': contract['text']}
        with patch('open_oracle.orchestration.build_selector',return_value=selector), patch('open_oracle.openai_integrations.require_live_authorization'), patch('open_oracle.openai_integrations.DecisionsReviewer',return_value=SyntheticReview()):
            server=make_server(port=0,live=True,live_voice=True,live_ws=True,max_live_requests=2,max_voice_sessions=3)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);session=str(uuid4())
        def post(path,body):
            req=Request(origin+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Origin':origin,'X-Oracle-Session':session})
            try:
                with urlopen(req) as response:return response.status,json.load(response)
            except HTTPError as error:return error.code,json.load(error)
        try:
            with patch('open_oracle.openai_integrations.LiveSessions.create',return_value={'fixture': True}) as capture, patch('open_oracle.ws_speech.render_speech',side_effect=render) as speech:
                self.assertEqual(post('/api/live/session',{'sdp':'v=0\r\n'})[1]['voice_sessions_remaining'],2)
                for index,question in enumerate(['If I vote Yes on Amendment seven, do my taxes go away?', 'What does No mean?']):
                    status,result=post('/api/ask',{'question':question,'scope':{'authority':'KCEB','municipality':'Kansas City within Jackson County'},'request_id':f'turn-{index}'})
                    self.assertEqual(status,200);self.assertEqual(result['status'],'answered');self.assertEqual(result['contest']['id'],'amendment-7');self.assertEqual(len(result['evidence']),5)
                    self.assertEqual(result['card']['facet_keys'],['conditions' if index==0 else 'no']);self.assertEqual(len(result['card']['facets']),1);self.assertEqual(result['view_plan']['initial_part'],0)
                    self.assertIn('No immediate tax cut' if index==0 else 'does not approve creating the investment fund',result['answer'])
                    self.assertEqual(post('/api/live/speech',{'request_id':f'turn-{index}'})[1]['voice_sessions_remaining'],1-index)
                self.assertEqual(post('/api/live/session',{'sdp':'v=0\r\n'})[0],429)
                self.assertEqual(post('/api/live/speech',{'request_id':'turn-1'})[0],429)
                self.assertEqual(capture.call_count,1);self.assertEqual(speech.call_count,2)
        finally:server.shutdown();server.server_close();thread.join()

    def test_identity_only_endpoint_quota_and_erase(self):
        def selection(q,scope,contest,corpus):return ([e['id'] for e in corpus.search(contest,scope)],[])
        def render(contract,cancel):return {'accepted':True,'text':contract['text'],'request_id':contract['request_id'],'language':'en','wav_base64':'AA==','transcript':contract['text'],'report':{'fixture':True}}
        with patch('open_oracle.orchestration.build_selector',return_value=selection),patch('open_oracle.openai_integrations.require_live_authorization'),patch('open_oracle.openai_integrations.DecisionsReviewer',return_value=SyntheticReview()):server=make_server(port=0,live=True,live_voice=True,live_ws=True,max_live_requests=1)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);session=str(uuid4())
        def post(path,body,s=session):
            req=Request(origin+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Origin':origin,'X-Oracle-Session':s})
            try:
                with urlopen(req)as r:return r.status,json.load(r)
            except HTTPError as e:return e.code,json.load(e)
        try:
            with patch('open_oracle.ws_speech.render_speech',side_effect=render)as transport:
                self.assertEqual(post('/api/live/speech',{'request_id':'forged','text':'Vote yes.'})[0],400)
                self.assertEqual(post('/api/live/speech',{'request_id':'forged'})[0],409);self.assertEqual(transport.call_count,0)
                status,result=post('/api/ask',{'question':'What is the COMBAT tax rate?','request_id':'approved'});self.assertEqual(status,200);self.assertIn('speech',result)
                self.assertEqual(post('/api/live/speech',{'request_id':'approved'},str(uuid4()))[0],409)
                self.assertEqual(post('/api/live/speech',{'request_id':'approved'})[0],200);self.assertEqual(transport.call_count,1)
                self.assertEqual(post('/api/live/speech',{'request_id':'approved'})[0],429)
                self.assertEqual(post('/api/erase',{})[0],200);self.assertEqual(post('/api/live/speech',{'request_id':'approved'})[0],410)
                self.assertEqual(post('/api/ask',{'question':'COMBAT'})[0],410)
                self.assertEqual(post('/api/ask',{'question':'Explain how my data is used'},str(uuid4()))[1]['status'],'product_faq')
                self.assertEqual(post('/api/ask',{'question':'borra esta sesión'},str(uuid4()))[1]['status'],'erased_locally')
        finally:server.shutdown();server.server_close();thread.join()

    def test_erase_during_retrieval_discards_result_and_skips_review(self):
        entered,continue_work=threading.Event(),threading.Event();reviewer=SyntheticReview()
        def selector(q,scope,contest,corpus):entered.set();continue_work.wait(2);return ([e['id'] for e in corpus.search(contest,scope)],[])
        with patch('open_oracle.orchestration.build_selector',return_value=selector),patch('open_oracle.openai_integrations.require_live_authorization'),patch('open_oracle.openai_integrations.DecisionsReviewer',return_value=reviewer):server=make_server(port=0,live=True,max_live_requests=1)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);s=str(uuid4());answers=[]
        def request(path,body):
            r=Request(origin+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Origin':origin,'X-Oracle-Session':s})
            try:
                with urlopen(r)as response:return response.status,json.load(response)
            except HTTPError as e:return e.code,json.load(e)
        with patch.object(reviewer,'review',wraps=reviewer.review)as review:
            worker=threading.Thread(target=lambda:answers.append(request('/api/ask',{'question':'COMBAT'})));worker.start()
            try:
                self.assertTrue(entered.wait(2));self.assertEqual(request('/api/erase',{})[0],200);continue_work.set();worker.join(3)
                self.assertEqual(answers[0][0],410);self.assertEqual(review.call_count,0)
            finally:continue_work.set();server.shutdown();server.server_close();thread.join();worker.join()

if __name__=='__main__':unittest.main()
