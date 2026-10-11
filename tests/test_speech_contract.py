import unittest
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop

class ReviewFixture:
    """Synthetic decision labels solely to exercise application release, not API proof."""
    def __init__(self, execution='offline_stub', status='accepted'): self.execution, self.status = execution, status
    def review(self, envelope): return {'execution':self.execution,'status':self.status,'label':'Offline contract fixture'}
class SpeechContractTests(unittest.TestCase):
    def test_default_or_mock_review_cannot_authorize_speech(self):
        for reviewer in (None, ReviewFixture()):
            r=EvidenceLoop(Corpus(),reviewer=reviewer).answer('What is the COMBAT tax rate?')
            self.assertNotIn('speech',r)
    def test_bound_exact_visible_answer_requires_real_api_execution_and_acceptance(self):
        r=EvidenceLoop(Corpus(),reviewer=ReviewFixture('real_api')).answer('What is the COMBAT tax rate?',request_id='voice-turn')
        self.assertEqual(r['speech']['text'],r['answer'])
        self.assertEqual(r['speech']['request_id'],'voice-turn')
        self.assertTrue(r['speech']['evidence_bindings'])
        for b in r['speech']['evidence_bindings']:
            e=next(e for e in r['evidence'] if e['id']==b['id'])
            self.assertEqual(b['text'],e['text']);self.assertEqual(b['sha256'],e['sha256'])
        self.assertEqual(set(r['stage_ms']),{'resolve_retrieve_construct','source_guards','decisions'})
    def test_rejection_and_gaps_cannot_authorize_explanation_speech(self):
        for question,reviewer in [('COMBAT',ReviewFixture('real_api','rejected')),('Show Dustin Coffell positions',ReviewFixture('real_api'))]:
            self.assertNotIn('speech',EvidenceLoop(Corpus(),reviewer=reviewer).answer(question))
if __name__=='__main__':unittest.main()
