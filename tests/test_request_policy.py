"""Full-request advice preflight, not a general semantic-intent classifier."""
import unittest
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.triage import DecisionsTriage, TriagedEngine

class RequestPolicyTests(unittest.TestCase):
    def test_evaluative_and_personal_fit_requests_are_boundaries_before_retrieval(self):
        c=Corpus()
        def forbidden(*args):raise AssertionError('Advice must not invoke a provider')
        for question in (
            'Is the COMBAT question a good idea for families like mine?',
            'Is COMBAT a good idea?', 'Is COMBAT good for my family?',
            'Do you think Amendment 7 is a bad idea?',
            'Should we approve Amendment 7?',
            'What is the COMBAT tax rate and is COMBAT a good idea?'):
            for engine in (EvidenceLoop(c,selector=forbidden),TriagedEngine(EvidenceLoop(c,selector=forbidden),DecisionsTriage(transport=forbidden),c)):
                with self.subTest(question=question,engine=type(engine).__name__):
                    response=engine.answer(question)
                    self.assertEqual(response['status'],'neutrality_boundary')
                    self.assertEqual(response['evidence'],[])
                    self.assertIsNone(response['card'])
                    self.assertNotIn('speech',response)
    def test_source_explanation_and_attributed_candidate_queries_remain_available(self):
        engine=EvidenceLoop(Corpus())
        for question in ('What is the COMBAT tax rate and how long would it last?',
                         'What do Pollard and Fields say about property taxes?'):
            with self.subTest(question=question):
                self.assertEqual(engine.answer(question)['status'],'answered')
