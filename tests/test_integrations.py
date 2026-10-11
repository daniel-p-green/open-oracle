import math
import unittest
from unittest.mock import patch

from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.openai_integrations import CHECKS, DecisionsReviewer, LiveSessions, parse_answer, post_openai


def accepted():
    return {'answers': [{'type': 'predicate', 'name': n, 'probability': 0.99} for n in CHECKS]}


class ContractTests(unittest.TestCase):
    def test_predicates_use_actual_decisions_contract_and_label_stub(self):
        calls = []
        def stub(resource, payload):
            calls.append((resource, payload)); return accepted()
        r = DecisionsReviewer(stub).review({'question': 'COMBAT', 'evidence': []})
        self.assertEqual((r['status'], r['execution']), ('accepted', 'offline_stub'))
        self.assertEqual(calls[0][0], 'decisions')
        self.assertEqual(calls[0][1]['model'], 'gpt-6-luna')
        self.assertEqual([q['name'] for q in calls[0][1]['questions']], list(CHECKS))
        self.assertEqual(r['calibration'], 'not_validated')

    def test_fail_closed_on_bad_answers(self):
        for mutation in ('missing', 'duplicate', 'reordered', 'nan', 'boolean', 'unknown', 'wrong-type'):
            data = accepted()
            if mutation == 'missing': data['answers'].pop()
            if mutation == 'duplicate': data['answers'][1]['name'] = data['answers'][0]['name']
            if mutation == 'reordered': data['answers'].reverse()
            if mutation == 'nan': data['answers'][0]['probability'] = math.nan
            if mutation == 'boolean': data['answers'][0]['probability'] = True
            if mutation == 'unknown': data['answers'][0]['name'] = 'unknown'
            if mutation == 'wrong-type': data['answers'][0]['type'] = 'choice'
            with self.subTest(mutation=mutation):
                self.assertEqual(DecisionsReviewer(lambda *a: data).review({})['status'], 'unavailable')

    def test_refusal_and_low_probability_reject(self):
        data = accepted(); data['answers'][0] = {'type': 'refusal', 'name': 'source_support'}
        result = DecisionsReviewer(lambda *a: data).review({})
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(result['checks'][0]['status'], 'refused')
        data = accepted(); data['answers'][2]['probability'] = 0.5
        self.assertEqual(DecisionsReviewer(lambda *a: data).review({})['status'], 'rejected')

    def test_typed_choices_and_fractional_scores(self):
        q = {'name': 'route', 'type': 'choice', 'choices': [{'value': True}, {'value': 'true'}]}
        self.assertIs(parse_answer(q, {'name': 'route', 'type': 'choice', 'choice': True})['value'], True)
        self.assertEqual(parse_answer(q, {'name': 'route', 'type': 'choice', 'choice': 'true'})['value'], 'true')
        with self.assertRaises(ValueError): parse_answer(q, {'name': 'route', 'type': 'choice', 'choice': 1})
        q = {'name': 'quality', 'type': 'score', 'levels': ['bad', 'partial', 'good']}
        self.assertEqual(parse_answer(q, {'name': 'quality', 'type': 'score', 'score': 1.4})['value'], 1.4)
        with self.assertRaises(ValueError): parse_answer(q, {'name': 'quality', 'type': 'score', 'score': 3})

    def test_real_transport_disabled_before_network(self):
        with patch.dict('os.environ', {}, clear=True), patch('open_oracle.openai_integrations.urlopen') as network:
            with self.assertRaises(ValueError): post_openai('decisions', {})
            network.assert_not_called()

    def test_rejected_review_does_not_release_claims(self):
        reviewer = DecisionsReviewer(lambda *a: {'answers': []})
        r = EvidenceLoop(Corpus(), reviewer=reviewer).answer('COMBAT')
        self.assertEqual(r['status'], 'unavailable')
        self.assertEqual(r['evidence'], [])
        self.assertEqual(r['claims'], [])
        candidate = EvidenceLoop(Corpus(), reviewer=reviewer).answer('Show Dustin Coffell positions')
        self.assertEqual(candidate['status'], 'unavailable')
        self.assertEqual(candidate['candidate_sources'], [])

    def test_bedrock_server_requires_review_before_release(self):
        from open_oracle.server import make_server
        selector=lambda *a: ([], [])
        with patch('open_oracle.orchestration.build_bedrock_selector',return_value=selector), \
             patch('open_oracle.openai_integrations.require_live_authorization',side_effect=ValueError('No permitted OpenAI credential')):
            with self.assertRaises(ValueError): make_server(port=0,bedrock=True)
        with patch('open_oracle.orchestration.build_bedrock_selector',return_value=selector), \
             patch('open_oracle.openai_integrations.require_live_authorization'), \
             patch('open_oracle.openai_integrations.DecisionsReviewer') as review:
            server=make_server(port=0,bedrock=True)
            server.server_close()
            review.assert_called_once()

    def test_live_contract_and_input_validation(self):
        calls = []
        def stub(resource, body):
            calls.append((resource, body))
            return {'session': {'id': 'offline-session'}, 'transport': {'type': 'webrtc', 'sdp': 'v=0\r\nanswer'}}
        live = LiveSessions(stub)
        self.assertEqual(live.create('v=0\r\noffer')['execution'], 'offline_stub')
        self.assertEqual(calls[0][0], 'live/sessions')
        self.assertEqual(calls[0][1]['session']['model'], 'gpt-live-1')
        self.assertEqual(calls[0][1]['session']['audio'], {'output': {'voice': 'cedar'}})
        self.assertEqual(calls[0][1]['session']['delegation'], {'type': 'client'})
        self.assertFalse(calls[0][1]['session']['store'])
        for invalid in (None, {}, 'not-sdp', 'v=0' + 'x' * 65536):
            with self.assertRaises(ValueError): live.create(invalid)
        self.assertEqual(len(calls), 1)
        with self.assertRaises(ValueError): LiveSessions(lambda *a: {'session': {}, 'transport': {}}).create('v=0')

    def test_provider_failure_and_malformed_payload_are_scrubbed(self):
        def fail(*args):
            raise TimeoutError('PRIVATE_PROVIDER_DIAGNOSTIC')
        for transport in (fail, lambda *a: None, lambda *a: {'answers': [None] * 5}):
            result = DecisionsReviewer(transport).review({})
            self.assertEqual(result['status'], 'unavailable')
            self.assertNotIn('PRIVATE_PROVIDER_DIAGNOSTIC', str(result))
        for raw in (None, [], {'session': {'id': ''}, 'transport': {'type': 'webrtc', 'sdp': 'v=0'}}):
            with self.assertRaises(ValueError):
                LiveSessions(lambda *a: raw).create('v=0')

    def test_live_response_releases_only_allowlisted_metadata(self):
        raw = {'api_key': 'MUST_NOT_RETURN', 'session': {'id': 'offline-id', 'secret': 'MUST_NOT_RETURN'},
               'transport': {'type': 'webrtc', 'sdp': 'v=0', 'secret': 'MUST_NOT_RETURN'}}
        result = LiveSessions(lambda *a: raw).create('v=0')
        self.assertNotIn('MUST_NOT_RETURN', str(result))
        self.assertEqual(set(result['session']), {'id'})
        self.assertEqual(set(result['transport']), {'type', 'sdp'})


if __name__ == '__main__':
    unittest.main()
