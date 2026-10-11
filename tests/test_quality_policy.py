import unittest
from unittest.mock import patch
from open_oracle.quality_policy import recommendation_block,review_projection,release_block
from open_oracle.openai_integrations import DecisionsReviewer
from open_oracle.engine import EvidenceLoop
from open_oracle.corpus import Corpus
class RecommendationGuardTests(unittest.TestCase):
 def test_blocks_explicit_assistant_advice_and_unicode_variants(self):
  for text in ('Vote YES.','You should vote NO.','Please cast your vote against the proposal.','I recommend you vote YES.','Vo\u200bte ＮＯ.','Vota sí.','Votez non.','I endorse a YES vote.'):
   with self.subTest(text=text):self.assertEqual(recommendation_block({'answer':text}),'explicit_assistant_vote_recommendation')
 def test_neutral_definitions_denials_and_typed_quotes_are_not_advice(self):
  for text in ('YES approves the proposal. NO rejects it.',"I do not recommend how to vote.",'The question asks whether the county should continue the tax.'):
   self.assertIsNone(recommendation_block({'answer':text}))
  self.assertIsNone(recommendation_block({'answer':'Read their attributed responses.','evidence':[{'text':'Vote YES.'}],'card':{'type':'candidate_comparison','responses':[{'candidate_name':'Test speaker','quote':'Vote YES.','evidence_id':'typed-quote'}]}}))
 def test_all_owned_card_text_is_scanned_and_quote_boundaries_projected(self):
  for r in ({'card':{'title':'Vote YES.'}},{'card':{'facets':[{'title':'Answer','statement':'Vote YES.'}]}},{'limitations':['I recommend you vote NO.']}):self.assertTrue(recommendation_block(r))
  p=review_projection({'question':'Vote YES?', 'response':{'answer':'NO rejects the proposal.','card':{'type':'candidate_comparison','responses':[{'candidate_name':'Public speaker','quote':'Vote YES.','evidence_id':'q'}]},'evidence':[{'text':'Vote YES.'}]}})
  self.assertEqual(p['assistant_authored'],['NO rejects the proposal.']);self.assertEqual(p['attributed_quotes'][0]['text'],'Vote YES.');self.assertIn('Vote YES?',p['visitor_request'])
 def test_guard_precedes_network_even_if_transport_would_accept(self):
  calls=[]
  r=DecisionsReviewer(lambda *args:calls.append(args)).review({'response':{'answer':'Vote YES.'}})
  self.assertEqual(r['status'],'rejected');self.assertEqual(r['execution'],'deterministic_guard');self.assertEqual(calls,[])
 def test_exact_source_release_also_blocks_poisoned_owned_card(self):
  # A future renderer/card regression must not bypass the rule because no AI review is enabled.
  with patch('open_oracle.engine.measure_card',return_value={'type':'measure_explanation','title':'Vote YES.','facets':[],'limit':'Retained sample.'}):
   r=EvidenceLoop(Corpus()).answer('Explain COMBAT',contest_id='combat')
  self.assertEqual(r['status'],'unavailable');self.assertEqual(r['evidence'],[]);self.assertEqual(r['claims'],[]);self.assertIsNone(r['card']);self.assertEqual(r['review']['execution'],'deterministic_guard')

class SourceAndTranslationBoundaryTests(unittest.TestCase):
 def test_attributed_quote_cannot_launder_new_assistant_advice(self):
  import copy
  from open_oracle.demo_sources import CONTEST
  corpus=Corpus();response=EvidenceLoop(corpus).answer('Compare Pollard and Fields priorities',contest_id=CONTEST)
  self.assertIsNone(release_block(response,corpus))
  for field,value in [('quote','Vote YES.'),('candidate_name','Unbound speaker'),('passage_sha256','0'*64)]:
   altered=copy.deepcopy(response);altered['card']['responses'][0][field]=value
   with self.subTest(field=field):self.assertEqual(release_block(altered,corpus),'attributed_quote_unbound')
 def test_fabricated_source_and_missing_evidence_block_without_judge(self):
  import copy
  corpus=Corpus();response=EvidenceLoop(corpus).answer('Explain COMBAT',contest_id='combat')
  altered=copy.deepcopy(response);altered['evidence'][0]['text']='Invented original wording.'
  self.assertEqual(release_block(altered,corpus),'evidence_unbound')
  response['evidence']=[];self.assertEqual(release_block(response,corpus),'evidence_missing')
 def test_self_declared_translation_review_is_insufficient(self):
  calls=[]
  for status in ('unreviewed','reviewed'):
   r=DecisionsReviewer(lambda *args:calls.append(args)).review({'response':{'language':'es','translation_status':status,'answer':'Un voto NO rechaza la propuesta.'}})
   self.assertEqual(r['status'],'rejected');self.assertEqual(r['reason'],'translation_not_implemented_or_verified')
  self.assertEqual(calls,[])
 def test_malformed_and_nullable_fields_fail_closed_or_preserve_safe_prose(self):
  for response in ({'card':{'facets':'bad'}},{'limitations':{}},{'card':[]},{'evidence':[None]}):
   self.assertEqual(release_block(response),'invalid_response_shape')
  self.assertIsNone(release_block({'answer':'NO rejects the proposal.','limitations':None,'card':{'facets':None}}))
