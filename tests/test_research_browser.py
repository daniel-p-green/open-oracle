import json
import unittest
from copy import deepcopy
from threading import Event
from open_oracle.corpus import Corpus
from open_oracle.research_release import requested_parts
from open_oracle.research_engine import ResearchEvidenceLoop
from open_oracle.research_display import validate_display
from open_oracle.agui import release_events
from open_oracle.quality_policy import release_block
from open_oracle.session_control import operation, SessionCancelled
from test_research_release import BoundModel, Review

class BrowserResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.corpus=Corpus()
    def loop(self, reviewer=None):
        return ResearchEvidenceLoop(self.corpus, BoundModel, reviewer or Review(), 'synthetic_sdk')
    def result(self, q='What is the COMBAT rate and how long does it last?', authority='JCEB'):
        return self.loop().answer(q, {'authority':authority}, 'fixture-run')
    def test_complete_projection_rebinds_after_json_and_preserves_context(self):
        r=json.loads(json.dumps(self.result()))
        self.assertEqual(r['status'],'answered')
        self.assertEqual(validate_display(r,self.corpus)['status'],'supported')
        self.assertIsNone(release_block(r,self.corpus))
        self.assertIn('Trust Fund',' '.join(r['evidence'][0]['text'].split()))
        self.assertEqual(r['evidence'][0]['source_id'],'jceb-sample')
        self.assertFalse(r['speech'])
        self.assertEqual(len([e for e in r['receipt']['tool_events'] if e['name']=='read_evidence_chunk']),2)
    def test_percent_variants_keep_all_requested_parts(self):
        for percent in ('20 percent','20%'):
            q='What is the COMBAT rate and will it reduce crime by '+percent+'?'
            self.assertEqual(requested_parts(q),{'rate','prediction'})
            r=self.result(q)
            self.assertEqual(r['fact_validation']['covered_parts'],['prediction','rate'])
            self.assertIn('cannot support that prediction',r['answer'])
            self.assertEqual(validate_display(r,self.corpus)['status'],'supported')
    def test_unbound_number_and_unsupported_extra_refuse_entire_question_without_model(self):
        model=BoundModel(); loop=ResearchEvidenceLoop(self.corpus,lambda:model,Review(),'synthetic_sdk')
        r=loop.answer('What is the COMBAT rate and its question number?',{'authority':'JCEB'})
        self.assertEqual(r['status'],'insufficient_evidence');self.assertIn('no part was answered',r['answer'])
        self.assertEqual(model.calls,0)
    def test_missing_authority_and_historical_date_do_not_call_model(self):
        model=BoundModel();loop=ResearchEvidenceLoop(self.corpus,lambda:model,Review(),'synthetic_sdk')
        self.assertEqual(loop.answer('COMBAT rate',{})['status'],'clarification')
        self.assertEqual(loop.answer('COMBAT rate',{'authority':'JCEB','election_date':'2024-11-05'})['status'],'insufficient_evidence')
        self.assertEqual(model.calls,0)
    def test_changed_prose_sources_authority_and_card_fail_independently(self):
        r=self.result()
        for mutate in (lambda x:x.update(answer='Vote yes.'),lambda x:x['evidence'][0].update(text='different source'),
                       lambda x:x['scope'].update(authority='KCEB'),lambda x:x.update(card={'type':'measure_explanation'}),
                       lambda x:x['claims'][0]['citations'][0].update(quote='at the rate of one percent'),
                       lambda x:x.update(choices=[{'title':'Vote yes','id':'yes'}])):
            bad=deepcopy(r); mutate(bad)
            self.assertEqual(validate_display(bad,self.corpus)['status'],'unsupported')
            self.assertIsNotNone(release_block(bad,self.corpus))
    def test_kceb_source_is_not_jceb_projection(self):
        r=self.result(authority='KCEB')
        self.assertEqual(r['status'],'answered')
        self.assertEqual(r['evidence'][0]['source_id'],'kceb-sample')
        self.assertEqual(r['evidence'][0]['authority'],'KCEB')
        self.assertEqual(validate_display(r,self.corpus)['status'],'supported')
    def test_agui_needs_real_review_and_revalidates_projection(self):
        from open_oracle.research_release import research_reviewed
        raw=research_reviewed('COMBAT rate',authority='JCEB',model=BoundModel(),execution='synthetic_sdk',reviewer=Review())
        raw['request_id']='raw-run';raw['review']['execution']='real_api'
        with self.assertRaisesRegex(ValueError,'Factual display bindings'):
            release_events(raw,'thread','raw-run',self.corpus)
        r=self.result()
        with self.assertRaises(ValueError):release_events(r,'thread','fixture-run',self.corpus)
        # Authored review metadata tests the boundary only, never live proof.
        r['review']['execution']='real_api'
        self.assertEqual(release_events(r,'thread','fixture-run',self.corpus)[-1]['type'],'RUN_FINISHED')
        r['evidence'][0]['text']='tampered'
        with self.assertRaises(ValueError):release_events(r,'thread','fixture-run',self.corpus)
    def test_prediction_only_has_explicit_gap_and_no_source_claim(self):
        r=self.result('Would COMBAT reduce crime by 20 percent?')
        self.assertEqual(r['status'],'insufficient_evidence');self.assertEqual(r['claims'],[])
        self.assertEqual(validate_display(r,self.corpus)['status'],'supported')
    def test_erase_during_review_discards_response(self):
        signal=Event();loop=self.loop(Review(lambda envelope:signal.set()))
        with self.assertRaises(SessionCancelled),operation(signal):loop.answer('COMBAT rate',{'authority':'JCEB'})
    def test_rejected_review_removes_all_sources_and_claims(self):
        class Reject(Review):
            def review(self,e):return {'status':'rejected','execution':'offline_stub'}
        r=self.loop(Reject()).answer('COMBAT rate',{'authority':'JCEB'})
        self.assertEqual(r['status'],'unavailable');self.assertEqual(r['claims'],[]);self.assertEqual(r['evidence'],[])

class ResearchHttpTests(unittest.TestCase):
    def test_opt_in_server_routes_both_transports_and_caps_third_request(self):
        from unittest.mock import patch
        from threading import Thread
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError
        from open_oracle.server import make_server
        class FixtureReview(Review):
            def review(self,e):return {'status':'accepted','execution':'real_api','fixture_only':True}
        corpus=Corpus();review=FixtureReview()
        # Fixture metadata exercises the transport gate; zero API inference.
        loop=ResearchEvidenceLoop(corpus,BoundModel,review,'synthetic_sdk')
        with patch('open_oracle.openai_integrations.require_live_authorization'),patch('open_oracle.openai_integrations.DecisionsReviewer',return_value=review),patch('open_oracle.research_engine.build_research_engine',return_value=loop):
            server=make_server(port=0,live=True,research=True,max_live_requests=2,corpus=corpus)
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        origin='http://127.0.0.1:'+str(server.server_port)
        def post(route,data):
            request=Request(origin+route,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
            with urlopen(request,timeout=10) as response:return response.read().decode()
        try:
            result=json.loads(post('/api/ask',{'question':'COMBAT rate and how long does it last?','scope':{'authority':'JCEB'},'request_id':'http-fixture'}))
            self.assertEqual(result['status'],'answered');self.assertEqual(result['request_id'],'http-fixture')
            self.assertEqual(result['operational_receipt']['execution'],'synthetic_sdk')
            sse=post('/api/ag-ui',{'runId':'sse-fixture','threadId':'test-thread','messages':[{'role':'user','content':'Would COMBAT reduce crime by 20 percent?'}],'forwardedProps':{'scope':{'authority':'JCEB'}}})
            events=[json.loads(line[6:]) for line in sse.splitlines() if line.startswith('data: ')]
            r=next(e['snapshot']['response'] for e in events if e['type']=='STATE_SNAPSHOT')
            self.assertEqual(r['status'],'insufficient_evidence');self.assertIn('cannot support that prediction',r['answer'])
            with self.assertRaises(HTTPError) as error:post('/api/ask',{'question':'COMBAT rate','scope':{'authority':'JCEB'}})
            self.assertEqual(error.exception.code,429)
        finally:
            server.shutdown();server.server_close();thread.join(timeout=2)

if __name__=='__main__':unittest.main()
