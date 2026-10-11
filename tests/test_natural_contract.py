"""Natural intake must hold unknown intent instead of answering with a roster."""
import unittest
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop

class NaturalContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.engine=EvidenceLoop(Corpus())
    def test_candidate_proposals_without_topic_cannot_pass_as_roster_answer(self):
        for q in ('What do Pollard and Fields propose?', 'What have Pollard and Fields promised?', 'What is Pollard and Fields agenda?'):
            r=self.engine.answer(q)
            self.assertEqual(r['status'],'insufficient_evidence');self.assertIsNone(r['card']);self.assertIn('priorities and property',r['answer']);self.assertNotIn('printed roster below',r['answer'])
    def test_supported_topic_still_returns_balanced_originals(self):
        r=self.engine.answer('How do Pollard and Fields differ on property taxes?')
        self.assertEqual(r['status'],'answered');self.assertEqual(len(r['card']['responses']),2);self.assertEqual(r['fact_validation']['status'],'supported')
    def test_new_embedding_paraphrase_does_not_widen_release_grammar(self):
        for q in ('How long would renewal last?','How long would COMBAT renewal last?'):
            r=self.engine.answer(q);self.assertEqual(r['status'],'insufficient_evidence');self.assertIsNone(r['card']);self.assertIsNone(r['view_plan'])
    def test_prediction_and_voting_advice_remain_held(self):
        r=self.engine.answer('Does COMBAT guarantee less crime?');self.assertEqual(r['status'],'insufficient_evidence')
        r=self.engine.answer('Should I vote yes on COMBAT?');self.assertEqual(r['status'],'neutrality_boundary')
