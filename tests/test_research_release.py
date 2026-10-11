"""Real SDK tool dispatch with authored observations; no paid inference."""
from copy import deepcopy
from threading import Event
import json
import unittest
from open_oracle.corpus import Corpus
from open_oracle.research_release import FORMS, research_reviewed
from open_oracle.session_control import operation, SessionCancelled
from strands_quality.research_agent import Quote, ResearchRequest
from strands_quality.research_corpus import Scope, load_verified_corpus
from test_research import ResearchModel

class BoundModel(ResearchModel):
    def __init__(self, defect=None): super().__init__();self.defect=defect
    def final_calls(self,specs,data):
        claims=[];gaps=[]
        for p in self.parts:
            if p['purpose']=='prediction':
                gaps.append({'part_id':p['id'],'reason':'unsupported_prediction'});continue
            read=data['read-'+p['id']]
            span=read['citation_spans'][0]['citation_span_id']
            if self.defect=='cross_part' and p['id']=='duration': span=data['read-rate']['citation_spans'][0]['citation_span_id']
            if self.defect=='forged_id':span='0'*64
            text=FORMS[p['id']]
            if self.defect=='unsupported_text':text='COMBAT will reduce crime.'
            claims.append({'part_id':p['id'],'text':text,'citations':[{'chunk_id':read['chunk_id'],'citation_span_id':span}]})
        if self.defect=='dropped_part':claims=claims[:1]
        return [('CitedAnswer',{'claims':claims,'gaps':gaps},'final')]

class Review:
    execution='offline_stub'
    def __init__(self,action=None):self.calls=0;self.action=action
    def review(self,envelope):
        self.calls+=1
        if self.action:self.action(envelope)
        return {'status':'accepted','execution':'offline_stub','threshold':0.95,'calibration':'not_validated'}

class ReleaseTests(unittest.TestCase):
    def call(self,model=None,review=None,question='What is the COMBAT rate and how long does it last?',**kw):
        return research_reviewed(question,authority='JCEB',model=model or BoundModel(),execution='synthetic_sdk',reviewer=review or Review(),**kw)
    def test_part_bound_line_break_citations_with_outer_review_receipt(self):
        review=Review();result=self.call(review=review)
        self.assertTrue(result['public_display']);self.assertEqual(result['status'],'answered');self.assertFalse(result['speech'])
        self.assertEqual(review.calls,1)
        self.assertEqual(len(result['claims']),2)
        for claim in result['claims']:
            cite=claim['citations'][0];self.assertIn('\n',cite['quote'])
            self.assertEqual(cite['text'],cite['quote'])
        receipt=result['receipt'];self.assertTrue(receipt['finalized']);self.assertEqual(receipt['release']['review'],'accepted')
        self.assertIn('decisions',receipt['stages_ms']);self.assertEqual(receipt['released_sources'][0]['id'],'jceb-sample')
        self.assertEqual(len([e for e in receipt['tool_events'] if e['name']=='read_evidence_chunk']),2)
        self.assertNotIn('one-quarter',json.dumps(receipt));self.assertNotIn('What is',json.dumps(receipt))
    def test_forged_cross_part_and_dropped_sources_fail_before_review(self):
        for defect in ('cross_part','forged_id','dropped_part','unsupported_text'):
            review=Review()
            with self.assertRaises(ValueError):self.call(BoundModel(defect),review)
            self.assertEqual(review.calls,0)
    def test_predicted_crime_reduction_gets_explicit_refusal(self):
        r=self.call(question='Will COMBAT reduce crime by 20%?')
        self.assertEqual(r['status'],'insufficient_evidence');self.assertTrue(r['public_display'])
        self.assertEqual(r['claims'],[]);self.assertEqual(r['evidence'],[])
        self.assertIn('cannot support that prediction',r['answer']);self.assertFalse(r['speech'])
    def test_mixed_supported_and_gap_covers_both(self):
        r=self.call(question='What is the COMBAT rate and will it reduce crime by 20%?')
        self.assertEqual(r['fact_validation']['covered_parts'],['prediction','rate'])
        self.assertIn('cannot support that prediction',r['answer'])
    def test_review_cannot_mutate_released_envelope(self):
        review=Review(lambda env: env['response'].update(answer='Vote yes.'))
        r=self.call(review=review);self.assertNotIn('Vote yes',r['answer'])
    def test_erase_during_review_blocks_delivery(self):
        signal=Event();review=Review(lambda env:signal.set())
        with self.assertRaises(SessionCancelled),operation(signal):
            with self.assertRaises(TimeoutError):self.call(review=review)
    def test_rejected_review_holds_answer_and_removes_draft(self):
        class Reject(Review):
            def review(self,e):return {'status':'rejected','execution':'offline_stub'}
        r=self.call(review=Reject());self.assertFalse(r['public_display']);self.assertEqual(r['claims'],[])
        self.assertEqual(r['status'],'unavailable');self.assertEqual(r['receipt']['release']['review'],'rejected')
    def test_unrelated_question_has_no_model_call(self):
        for q in ('What is the COMBAT rate and current law?', 'How should I vote on COMBAT?', 'COMBAT who is the best candidate?', 'What is the COMBAT rate and abortion?', 'What is the COMBAT rate and why was it proposed?'):
            m=BoundModel()
            with self.assertRaises(ValueError):self.call(model=m,question=q)
            self.assertEqual(m.calls,0)
    def test_late_cancel_clears_recorded_release_and_finalizes_error(self):
        signal=Event()
        r=ResearchRequest(load_verified_corpus(Corpus()),scope=Scope(),model=BoundModel(),execution='synthetic_sdk',cancel=signal)
        def adapter(request,draft):
            request.receipt.release(status='answered',binding='supported',review='accepted',review_execution='synthetic_sdk',evidence_ids=['jceb-sample'])
            signal.set()
            return {'status':'answered'}
        with self.assertRaises(TimeoutError):r._run('What is the COMBAT rate and how long does it last?',release_adapter=adapter)
        receipt=r.receipt.snapshot()
        self.assertTrue(receipt['finalized']);self.assertEqual(receipt['release']['status'],'unavailable')
        self.assertEqual(receipt['released_sources'],[]);self.assertEqual(receipt['error_category'],'timeout_or_budget')

    def test_two_quote_locators_or_neither_rejected(self):
        for args in ({},{'citation_span_id':'0'*64,'exact_quote':'A long enough quote'}):
            with self.assertRaises(ValueError):Quote(chunk_id='c',**args)
    def test_legacy_normalized_quotation_still_rejected(self):
        registry=load_verified_corpus(Corpus());chunk=next(c for c in registry.chunks.values() if 'COMBAT, at the rate' in c.text)
        with self.assertRaises(ValueError):registry.citation(chunk.id,'at the rate of one-quarter of one cent')

if __name__=='__main__':unittest.main()
