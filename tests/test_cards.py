import copy
import unittest
from unittest.mock import patch
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.cards import measure_card

class CardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus()
        cls.loop = EvidenceLoop(cls.corpus)

    def test_confusion_changes_presentation_but_not_meaning_or_evidence(self):
        overview = self.loop.answer('What does COMBAT say?', {'authority':'KCEB'})
        followup = self.loop.answer("I still don't understand", {'authority':'KCEB'}, contest_id='combat')
        self.assertEqual(overview['card']['presentation'], 'overview')
        self.assertEqual(followup['card']['presentation'], 'step_by_step')
        self.assertEqual(overview['card']['facets'], followup['card']['facets'])
        self.assertEqual(overview['evidence'], followup['evidence'])
        self.assertEqual(followup['trace'][0]['tool'], 'local_lookup')
        source = followup['evidence'][0]
        for facet in followup['card']['facets']:
            self.assertEqual(source['text'][facet['start']:facet['end']], facet['quote'])
            self.assertEqual(facet['evidence_id'], source['id'])
        self.assertIn('one-quarter', followup['card']['facets'][1]['quote'])
        self.assertIn('ten years', followup['card']['facets'][2]['statement'])
        self.assertIn('NO rejects', followup['card']['facets'][0]['statement'])

    def test_changed_source_or_wrong_date_never_gets_predefined_explanation(self):
        evidence = copy.deepcopy(self.corpus.search('combat', {}))
        for field, value in [('text', evidence[0]['text'].replace('ten years','twenty years')),
                             ('sha256', 'wrong'), ('election_date', '2024-11-05'), ('status','conflict')]:
            changed = copy.deepcopy(evidence); changed[0][field] = value
            self.assertIsNone(measure_card('COMBAT', self.corpus.contests['combat'], changed))

    def test_boundaries_and_missing_context_have_no_card(self):
        for question, scope in [("I still don't understand", {}), ('How should I vote on COMBAT?', {}),
                                ('COMBAT in 2024', {}), ('COMBAT', {'election_date':'2025-11-04'}),
                                ('Blue Springs tax', {}), ('Explain Amendment 3', {})]:
            self.assertIsNone(self.loop.answer(question, scope)['card'])

    def test_review_sees_and_can_withhold_the_complete_card(self):
        class Reviewer:
            seen = None
            def review(self, envelope):
                self.seen = copy.deepcopy(envelope)
                return {'status':'rejected','label':'Offline rejection stub'}
        reviewer = Reviewer()
        result = EvidenceLoop(self.corpus, reviewer=reviewer).answer('COMBAT')
        self.assertIsNotNone(reviewer.seen['response']['card'])
        self.assertIsNone(result['card'])
        self.assertEqual(result['evidence'], [])

    def test_catalog_failure_is_an_explicit_gap(self):
        with patch.object(self.corpus.candidate_sources, 'lookup', return_value={'available':False,'people':[],'conflicts':[]}):
            result = self.loop.answer('Scott Fitzpatrick positions')
        self.assertEqual(result['status'],'insufficient_evidence')
        self.assertIn('no verified pointers', result['answer'])
        self.assertNotIn('are shown below', result['answer'])

    def test_candidate_phrasings_route_to_attributed_gap(self):
        for question in ('What does Scott Fitzpatrick think about crime?', 'Where does Quentin Wilson stand on taxes?',
                         'Who endorsed Scott Fitzpatrick?', 'Paul C. Wilson experience'):
            result = self.loop.answer(question)
            self.assertEqual(result['status'], 'insufficient_evidence', question)
            self.assertEqual(result['trace'][0]['tool'], 'candidate_source_catalog')
        self.assertEqual(self.loop.answer('Help me understand the state auditor race')['status'], 'answered')
class FollowupTests(unittest.TestCase):
    def test_no_focus_and_unsupported_prediction(self):
        loop=EvidenceLoop(Corpus())
        answer=loop.answer('What does NO mean?',contest_id='combat')
        self.assertEqual(answer['card']['presentation'],'choice_focus')
        self.assertIn('NO rejects',answer['card']['facets'][0]['statement'])
        for question in ('Will COMBAT reduce crime by 50%?', 'Does COMBAT guarantee lower crime?'):
            gap=loop.answer(question,contest_id='combat')
            self.assertEqual(gap['status'],'insufficient_evidence')
            self.assertIsNone(gap['card'])
            self.assertEqual(gap['claims'],[])
            self.assertEqual(gap['evidence'],[])

