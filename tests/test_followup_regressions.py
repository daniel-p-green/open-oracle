"""Visitor-visible source-only multipart and volatile-context regressions; no providers."""
import copy
import json
import threading
import unittest
from uuid import uuid4
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from open_oracle.claim_bindings import validate_factual_display
from open_oracle.corpus import Corpus
from open_oracle.demo_sources import CONTEST
from open_oracle.engine import EvidenceLoop
from open_oracle.server import make_server
from open_oracle.session_control import VisitorSessions
from open_oracle.view_plan import validate_view_plan


class FollowupRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus()
        cls.engine = EvidenceLoop(cls.corpus)

    def test_combat_answers_both_requested_facts_and_marks_prediction_gap(self):
        for question, parts in [
            ('What is the COMBAT tax rate and how long would it last?', ['duration', 'rate']),
            ('What is the COMBAT tax rate and how long would it last and would it reduce crime by 20 percent?', ['duration', 'prediction', 'rate']),
        ]:
            with self.subTest(question=question):
                result = self.engine.answer(question)
                self.assertEqual(result['status'], 'answered', result)
                self.assertEqual(result['requested_parts'], parts)
                self.assertIn('one-quarter of one cent', result['answer'])
                self.assertIn('ten years', result['answer'])
                self.assertEqual(result['view_plan']['facet_keys'], ['rate', 'time'])
                self.assertTrue(validate_view_plan(result['view_plan'], result))
                self.assertIn('trust fund', ' '.join(result['evidence'][0]['text'].lower().split()))
                if 'prediction' in parts:
                    self.assertIn('cannot support that prediction', result['answer'])
                self.assertEqual(result['review']['status'], 'not_run')
        for question in ['Will COMBAT reduce crime by 20 percent?',
                         'What is the COMBAT tax rate and how long would it last and what is Question 2?',
                         'What is the COMBAT tax rate and what is the budget?']:
            with self.subTest(question=question):
                result = self.engine.answer(question)
                self.assertEqual(result['status'], 'insufficient_evidence')
                self.assertEqual(result['claims'], [])
                self.assertIsNone(result['card'])

    def test_candidate_mixed_request_keeps_balanced_supported_part_and_named_gap(self):
        for gap in ['climate', 'crime', 'housing']:
            result = self.engine.answer('Compare Pollard and Fields on property taxes and ' + gap)
            self.assertEqual(result['status'], 'answered', result)
            self.assertEqual(result['card']['topic'], 'property')
            self.assertEqual({x['candidate_name'] for x in result['card']['responses']}, {'LANCE POLLARD', 'CARLA FIELDS'})
            self.assertEqual(len(result['evidence']), 2)
            self.assertIn(gap if gap != 'housing' else 'other requested topic', result['answer'])
            self.assertIn('remains unanswered', result['answer'])
            self.assertEqual(result['fact_validation']['status'], 'supported')
            for response in result['card']['responses']:
                source = next(e for e in result['evidence'] if e['id'] == response['evidence_id'])
                self.assertEqual(response['quote'], source['text'])

    def test_two_supported_candidate_topics_require_all_four_originals(self):
        result = self.engine.answer('Compare Pollard and Fields priorities and property assessments')
        self.assertEqual(result['status'], 'answered', result)
        self.assertEqual(result['comparison_request']['topics'], ['issues', 'property'])
        self.assertEqual(len(result['evidence']), 4)
        self.assertEqual({e['topic'] for e in result['evidence']}, {'issues', 'property'})
        self.assertEqual(result['view_plan']['evidence_ids'], [e['id'] for e in result['evidence']])
        tampered = copy.deepcopy(result)
        tampered['evidence'] = tampered['evidence'][:2]
        tampered['claims'] = tampered['claims'][:2]
        self.assertEqual(validate_factual_display(tampered, self.corpus)['status'], 'unsupported')
        live_selector = lambda q, scope, contest, corpus: ([e['id'] for e in corpus.search(contest, scope)], [])
        held = EvidenceLoop(self.corpus, selector=live_selector).answer('Compare Pollard and Fields priorities and property assessments')
        self.assertEqual(held['status'], 'insufficient_evidence')
        self.assertEqual(held['evidence'], [])  # No unread second topic appended after optional selector.

    def test_malformed_coverage_and_view_plan_cannot_bypass_source_binding(self):
        candidate = self.engine.answer('Compare Pollard and Fields on property taxes and climate')
        for parts in [{}, {'topics': [], 'gaps': [], 'unclassified': False},
                      {'topics': ['property'], 'gaps': ['Vote for Fields'], 'unclassified': False},
                      {'topics': ['property'], 'gaps': [[]], 'unclassified': False}]:
            result = copy.deepcopy(candidate); result['comparison_request'] = parts
            self.assertEqual(validate_factual_display(result, self.corpus)['status'], 'unsupported')
        measure = self.engine.answer('What is the COMBAT tax rate and how long would it last?')
        for parts in [['rate', 'cost'], [dict(rate='unsupported')], ['duration', 'rate', 'rate']]:
            result = copy.deepcopy(measure); result['requested_parts'] = parts
            self.assertEqual(validate_factual_display(result, self.corpus)['status'], 'unsupported')
        plan = copy.deepcopy(measure['view_plan']); plan['facet_keys'] = ['rate', 'fund']
        self.assertFalse(validate_view_plan(plan, measure))

    def test_context_is_verified_scoped_volatile_and_erased(self):
        clock = [0]; store = VisitorSessions(now=lambda: clock[0])
        session = str(uuid4()); store.begin(session)
        result = self.engine.answer('Compare Pollard and Fields priorities', {'authority': 'JCEB'})
        store.retain(session, result, self.corpus); store.end(session)
        resolve = lambda q, scope=None, explicit=None: store.contextual_contest(session, q, scope or {'authority': 'JCEB'}, explicit, self.corpus)
        self.assertEqual(resolve('And property taxes?'), CONTEST)
        self.assertIsNone(resolve('property taxes'))  # Bare ambiguous request does not adopt context.
        self.assertIsNone(resolve('And property taxes?', {'authority': 'KCEB'}))
        self.assertIsNone(resolve('And property taxes?', {'authority': 'JCEB', 'district': 'Other district'}))
        self.assertIsNone(resolve('And property taxes?', {'authority': 'JCEB', 'election_date': '2024-11-05'}))
        self.assertIsNone(resolve('Compare Scott Fitzpatrick and Quentin Wilson priorities'))
        self.assertEqual(resolve('And property taxes?', explicit='combat'), 'combat')
        self.assertEqual(set(store.entries[session]['context']), {'contest_id', 'scope'})
        clock[0] = 601; self.assertIsNone(resolve('And property taxes?'))
        clock[0] = 0; store.erase(session); self.assertIsNone(resolve('And property taxes?'))
        store.retain(session, result, self.corpus)
        self.assertNotIn('context', store.entries[session])

    def test_http_followup_and_erase_use_existing_session_contract(self):
        server = make_server(port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        origin = 'http://127.0.0.1:' + str(server.server_port)
        session = str(uuid4())
        def post(path, body, ident=session):
            request = Request(origin + path, data=json.dumps(body).encode(), headers={
                'Content-Type': 'application/json', 'Origin': origin, 'X-Oracle-Session': ident})
            try:
                with urlopen(request, timeout=3) as response: return response.status, json.load(response)
            except HTTPError as error: return error.code, json.load(error)
        try:
            status, result = post('/api/ask', {'question': 'Compare Pollard and Fields priorities'})
            self.assertEqual(status, 200); self.assertEqual(result['mode'], 'exact_source')
            status, result = post('/api/ask', {'question': 'And property taxes?'})
            self.assertEqual(status, 200); self.assertEqual(result['card']['topic'], 'property')
            self.assertEqual(post('/api/erase', {})[0], 200)
            self.assertEqual(post('/api/ask', {'question': 'And property taxes?'})[0], 410)
            status, result = post('/api/ask', {'question': 'And property taxes?'}, str(uuid4()))
            self.assertEqual(status, 200); self.assertEqual(result['status'], 'insufficient_evidence')
        finally:
            server.shutdown(); server.server_close(); thread.join()
