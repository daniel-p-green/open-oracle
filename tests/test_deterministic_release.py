import copy
import unittest
from unittest.mock import patch
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.claim_bindings import assess_claim, fact_catalog, validate_factual_display, diagnose_unbound_text
from open_oracle.source_fallback import make_fallback, validate_fallback
from open_oracle.view_plan import make_view_plan, validate_view_plan
from open_oracle.agui import release_events

class BindingTests(unittest.TestCase):
 def setUp(self):
  self.corpus=Corpus();self.response=EvidenceLoop(self.corpus).answer('Explain COMBAT',request_id='fixed',contest_id='combat')
  self.facts=fact_catalog(self.corpus,self.response['evidence'],'combat')
 def test_numeric_entity_and_date_values_bind_to_actual_spans(self):
  for key in ('measure.rate','measure.duration','measure.jurisdiction','measure.name','election.date'):
   self.assertEqual(assess_claim(self.facts[key],self.facts)['status'],'supported')
  equivalent={**self.facts['measure.rate'],'value':'1/4'}
  self.assertEqual(assess_claim(equivalent,self.facts)['status'],'supported')
  self.assertEqual(' '.join(self.facts['measure.rate']['quote'].split()),'at the rate of one-quarter of one cent')
  date=self.facts['election.date'];self.assertEqual(self.corpus.jceb[date['start']:date['end']],date['quote'])
  self.assertEqual(date['binding'],'printed_document_header')
 def test_known_fact_conflicts_are_contradictory_unknown_claims_unsupported(self):
  for key,value,unit in [('measure.rate','5','percent'),('measure.duration','20','year'),('measure.jurisdiction','Clay County',None),('election.date','2024-11-05',None)]:
   self.assertEqual(assess_claim({**self.facts[key],'value':value,'unit':unit},self.facts)['status'],'contradictory')
  self.assertEqual(assess_claim({'key':'crime.reduction','kind':'number','value':'50','unit':'percent'},self.facts)['status'],'unsupported')
  for prediction in ('COMBAT guarantees that crime falls by 50 percent.','This tax guarantees that crime falls by 50 percent.'):
   self.assertEqual(diagnose_unbound_text(prediction,self.facts)['status'],'unsupported')
  self.assertEqual(diagnose_unbound_text('The COMBAT sales tax is 5 percent.',self.facts)['status'],'contradictory')
 def test_source_anchor_identity_offsets_and_hash_cannot_be_replaced(self):
  for field,value in [('evidence_id','amendment-3:jceb-sample'),('start',0),('quote','ten years'),('text_sha256','0'*64),('source_sha256','0'*64)]:
   self.assertEqual(assess_claim({**self.facts['measure.rate'],field:value},self.facts)['status'],'unsupported')
 def test_judge_acceptance_cannot_authorize_numeric_entity_date_or_semantic_tampering(self):
  for answer in ('The COMBAT sales tax is 5 percent.','The proposed continuation lasts twenty years.','COMBAT does not last ten years.','This is on your personal ballot.'):
   changed=copy.deepcopy(self.response);changed['answer']=answer
   self.assertIn(validate_factual_display(changed,self.corpus)['status'],('unsupported','contradictory'))
  for field,value in [('election_date','2024-11-05'),('jurisdiction','Clay County, Missouri'),('title','A 5 percent tax')]:
   changed=copy.deepcopy(self.response);changed['card'][field]=value
   self.assertIn(validate_factual_display(changed,self.corpus)['status'],('unsupported','contradictory'))
 def test_mutating_a_corpus_alias_does_not_rebind_the_original(self):
  self.response['evidence'][0]['text']='Invented source through shared object alias.'
  self.assertEqual(validate_factual_display(self.response,self.corpus)['status'],'unsupported')
  self.assertIsNone(make_fallback(self.response,self.corpus))

 def test_detached_claim_quote_and_unknown_widget_do_not_inherit_fact_approval(self):
  r=copy.deepcopy(self.response);r['claims'][0]['quote']='The COMBAT rate is 5 percent.'
  self.assertEqual(validate_factual_display(r,self.corpus)['reason'],'quoted_claim_binding_failed')
  r=copy.deepcopy(self.response);r['card']={'type':'sandbox','html':'<script>bad()</script>'}
  self.assertEqual(validate_factual_display(r,self.corpus)['reason'],'unregistered_component_data')

class FallbackAndPlanTests(unittest.TestCase):
 def setUp(self):self.corpus=Corpus()
 def test_rejected_clarity_keeps_only_bound_original_wording(self):
  class Reject:
   def review(self,envelope):return {'status':'rejected','execution':'offline_stub','label':'Synthetic clarity rejection'}
  r=EvidenceLoop(self.corpus,reviewer=Reject()).answer('Explain COMBAT',request_id='fixed',contest_id='combat')
  self.assertEqual(r['status'],'unavailable');self.assertIsNone(r['card']);self.assertEqual(r['evidence'],[]);self.assertEqual(r['claims'],[])
  f=r['source_fallback'];self.assertTrue(validate_fallback(f,r,self.corpus));self.assertNotIn('answer',f)
  self.assertIn('one-quarter',f['sources'][0]['text']);self.assertEqual(r['view_plan']['component'],'source_quotes')
  events=release_events(r,'visitor','fixed',self.corpus);self.assertIn('one-quarter',str(events));self.assertNotIn('Synthetic clarity rejection',str(f))
  bad=copy.deepcopy(r);bad['source_fallback']['sources'][0]['text']='Vote YES.'
  with self.assertRaises(ValueError):release_events(bad,'visitor','fixed',self.corpus)
 def test_bad_generated_facet_is_held_but_cannot_poison_original_fallback(self):
  from open_oracle.cards import measure_card
  def bad(*args):
   card=measure_card(*args);card['facets'][1]['statement']='The rate is 5 percent.';return card
  class Accept:
   def __init__(self):self.calls=0
   def review(self,envelope):self.calls+=1;return {'status':'accepted'}
  judge=Accept()
  with patch('open_oracle.engine.measure_card',side_effect=bad):r=EvidenceLoop(self.corpus,reviewer=judge).answer('Explain COMBAT',request_id='fixed',contest_id='combat')
  self.assertEqual(judge.calls,0);self.assertEqual(r['fact_validation']['status'],'contradictory');self.assertIsNone(r['card'])
  self.assertNotIn('5 percent',str(r['source_fallback']));self.assertTrue(validate_fallback(r['source_fallback'],r,self.corpus))
 def test_adaptive_focus_parts_and_candidate_quotes_are_source_references(self):
  for question,key,index in [('What is the COMBAT rate?','rate',1),('How long does COMBAT last?','time',2),('Where does COMBAT money go?','fund',4),('What does NO mean?','decision',0)]:
   r=EvidenceLoop(self.corpus).answer(question,request_id='fixed',contest_id='combat');p=r['view_plan']
   self.assertEqual((p['component'],p['facet_keys'],p['initial_part']),('measure_focus',[key],index));self.assertTrue(validate_view_plan(p,r))
   if index > 0:self.assertEqual(r['answer'],r['card']['facets'][index]['statement'])
  r=EvidenceLoop(self.corpus).answer("I still don't understand",request_id='fixed',contest_id='combat')
  self.assertEqual(r['view_plan']['component'],'measure_parts')
  from open_oracle.demo_sources import CONTEST
  r=EvidenceLoop(self.corpus).answer('Compare Pollard and Fields priorities',request_id='fixed',contest_id=CONTEST)
  self.assertEqual(r['view_plan']['component'],'candidate_quotes');self.assertTrue(validate_view_plan(r['view_plan'],r))
 def test_arbitrary_script_text_style_identity_and_facet_injection_cannot_enter_plan(self):
  r=EvidenceLoop(self.corpus).answer('Explain COMBAT',request_id='fixed',contest_id='combat');p=r['view_plan']
  for changes in ({'jsExpressions':['document.body.textContent="Vote YES"']},{'html':'<script>bad()</script>'},{'title':'Vote YES'},{'style':{'display':'none'}},{'component':'sandbox'},{'request_id':'old-visitor'},{'evidence_ids':['wrong-contest']},{'facet_keys':['invented']}):
   self.assertFalse(validate_view_plan({**p,**changes},r))
 def test_scoping_gaps_never_get_fallback_or_visual_fact_plan(self):
  for question,scope in [('What is Blue Springs tax?',{}),('Show my ballot',{}),('Explain COMBAT from 2024',{}),('Explain COMBAT',{'authority':'KCEB','municipality':'Blue Springs'})]:
   r=EvidenceLoop(self.corpus).answer(question,scope)
   self.assertNotIn('source_fallback',r);self.assertIsNone(r['view_plan'])

class RetrievalFailureFallbackTests(unittest.TestCase):
 def test_provider_failure_returns_scoped_local_originals_without_quality_call(self):
  class Review:
   def __init__(self):self.calls=0
   def review(self,envelope):self.calls+=1;return {'status':'accepted'}
  def fail(*args):raise TimeoutError('PROVIDER_DRAFT_MUST_NOT_LEAK')
  corpus=Corpus();review=Review();r=EvidenceLoop(corpus,selector=fail,reviewer=review).answer('Explain COMBAT',request_id='fixed',contest_id='combat')
  self.assertEqual(review.calls,0);self.assertEqual(r['status'],'unavailable');self.assertEqual(r['review']['execution'],'not_run')
  self.assertTrue(validate_fallback(r['source_fallback'],r,corpus));self.assertEqual(r['card'],None);self.assertEqual(r['evidence'],[])
  self.assertNotIn('PROVIDER_DRAFT_MUST_NOT_LEAK',str(release_events(r,'visitor','fixed',corpus)))
