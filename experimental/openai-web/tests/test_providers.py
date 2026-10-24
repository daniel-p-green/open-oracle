import copy
import asyncio
from unittest import mock
from types import SimpleNamespace
import json
from pathlib import Path
import sys
import threading
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from providers import Held, Pipeline, OpenAIProvider, admitted_corpus, DISCLAIMER

CORPUS = admitted_corpus(Path(__file__).resolve().parents[1] / 'fixtures/combat.json')
USAGE = {'input_tokens': 100, 'output_tokens': 0, 'input_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0}}


class FakeProvider:
    def __init__(self): self.calls = []
    def route(self, cancel):
        self.calls.append('route')
        return {'answers': [{'type': 'choice', 'name': 'route', 'choice': 'rate', 'confidence': 1}], 'usage': USAGE}
    def generate(self, corpus, cancel):
        self.calls.append('generate')
        draft = {'claim_ids': ['rate'], 'explanation': corpus['claims']['rate']['text']}
        return {'status': 'completed', 'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(draft)}]}], 'usage': USAGE}
    def review(self, corpus, text, cancel):
        self.calls.append('review')
        return {'answers': [{'type': 'predicate', 'name': 'support', 'probability': 1}], 'usage': USAGE}
    def speak(self, text, cancel):
        self.calls.append('speak')
        return {'pcm': b'\x01\x00' * 24000, 'transcript': text, 'finalized': True,
                'reason': 'close_requested', 'errors': [], 'backend_events': 0, 'usage': {'seconds': 1}}


class PipelineTests(unittest.TestCase):
    def run_pipeline(self, provider=None, cancel=None):
        provider = provider or FakeProvider()
        stages, usage = [], []
        result = Pipeline(CORPUS, provider).run(cancel or threading.Event(), stages.append, lambda *args: usage.append(args))
        return result, provider, stages, usage

    def test_full_public_path_returns_bound_citation_and_private_audio(self):
        (result, pcm), provider, stages, usage = self.run_pipeline()
        self.assertEqual(provider.calls, ['route', 'generate', 'review', 'speak'])
        self.assertEqual(stages, ['routing', 'text', 'review', 'audio'])
        self.assertEqual(len(usage), 4)
        claim = result['claims'][0]
        self.assertEqual(claim['quote'], result['source']['text'][claim['start']:claim['end']])
        self.assertEqual(result['reading'], claim['text'] + DISCLAIMER)
        self.assertEqual(result['audio']['bytes'], len(pcm))
        self.assertFalse(result['playback_enabled'])
        self.assertNotIn('pcm', json.dumps(result))

    def test_tampered_corpus_cannot_start_provider_work(self):
        altered = copy.deepcopy(CORPUS); altered['claims']['rate']['text'] = 'Vote Yes'
        provider = FakeProvider()
        with self.assertRaises(Held): Pipeline(altered, provider)
        self.assertEqual(provider.calls, [])

    def test_unsupported_or_uncertain_route_abstains_before_generation(self):
        for answer in [{'type': 'choice', 'name': 'route', 'choice': 'abstain', 'confidence': 1},
                       {'type': 'choice', 'name': 'route', 'choice': 'rate', 'confidence': .5},
                       {'type': 'refusal', 'name': 'route'},
                       {'type': 'choice', 'name': 'route', 'choice': 'rate', 'confidence': float('nan')}]:
            provider = FakeProvider(); provider.route = lambda cancel: {'answers': [answer], 'usage': USAGE}
            with self.assertRaises(Held): self.run_pipeline(provider)
            self.assertEqual(provider.calls, [])

    def test_incomplete_or_unadmitted_generated_text_never_reaches_audio(self):
        for status, text in [('incomplete', '{}'), ('completed', '{"claim_ids":["rate"],"explanation":"Vote Yes"}'),
                             ('completed', '{"claim_ids":["rate","yes"],"explanation":"The printed rate is one-quarter of one cent."}'), ('completed', 'invalid')]:
            provider = FakeProvider()
            provider.generate = lambda corpus, cancel: {'status': status, 'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': text}]}], 'usage': USAGE}
            with self.assertRaises(Held): self.run_pipeline(provider)
            self.assertNotIn('speak', provider.calls)

    def test_missing_or_failed_support_check_never_reaches_audio(self):
        for answers in [[], [{'type': 'predicate', 'name': 'support', 'probability': .94}], [{'type': 'refusal', 'name': 'support'}]]:
            provider = FakeProvider(); provider.review = lambda *args: {'answers': answers, 'usage': USAGE}
            with self.assertRaises(Held): self.run_pipeline(provider)
            self.assertNotIn('speak', provider.calls)

    def test_spontaneous_mismatched_partial_silent_or_unfinalized_audio_is_held(self):
        changes = [{'transcript': 'Hello! Vote Yes.'}, {'finalized': False}, {'errors': ['live_error']},
                   {'backend_events': 1}, {'pcm': bytes(48000)}, {'pcm': b'abc'}, {'usage': {'seconds': None}}, {'reason': 'connection_lost'}]
        for change in changes:
            provider = FakeProvider(); original = provider.speak
            def speak(text, cancel):
                result = original(text, cancel); result.update(change); return result
            provider.speak = speak
            with self.assertRaises(Held): self.run_pipeline(provider)

    def test_cancellation_after_billable_stage_records_usage_but_stops_next_call(self):
        cancel = threading.Event(); provider = FakeProvider(); original = provider.route
        def route(signal):
            result = original(signal); cancel.set(); return result
        provider.route = route
        usage = []
        with self.assertRaises(Held): Pipeline(CORPUS, provider).run(cancel, lambda _: None, lambda *args: usage.append(args))
        self.assertEqual(provider.calls, ['route']); self.assertEqual(len(usage), 1)

    def test_provider_failure_is_not_retried(self):
        provider = FakeProvider(); calls = []
        def failing(cancel): calls.append(1); raise Held('provider_unavailable')
        provider.route = failing
        with self.assertRaises(Held): self.run_pipeline(provider)
        self.assertEqual(calls, [1])

    def test_adapter_mutation_of_its_corpus_copy_does_not_change_source_authority(self):
        provider = FakeProvider(); original = provider.generate
        def mutate(corpus, cancel):
            result = original(corpus, cancel); corpus['sources'][0]['url'] = 'https://attacker.invalid'; return result
        provider.generate = mutate
        (result, _), *_ = self.run_pipeline(provider)
        self.assertEqual(result['source']['url'], CORPUS['sources'][0]['url'])


class LiveDispatchTests(unittest.TestCase):
    def test_precancelled_live_request_never_connects(self):
        cancel = threading.Event(); cancel.set()
        provider = object.__new__(OpenAIProvider); provider._headers = {}
        connect = mock.Mock(side_effect=AssertionError('must not connect'))
        with mock.patch.dict(sys.modules, {'websockets': SimpleNamespace(connect=connect)}):
            with self.assertRaises(Held): asyncio.run(provider._speak('public', cancel))
        connect.assert_not_called()

    def test_cancel_during_handshake_never_starts_a_billable_session(self):
        cancel = threading.Event(); sent = []
        class Connection:
            async def __aenter__(self): cancel.set(); return self
            async def __aexit__(self, *args): pass
            async def send(self, value): sent.append(value)
        provider = object.__new__(OpenAIProvider); provider._headers = {}
        with mock.patch.dict(sys.modules, {'websockets': SimpleNamespace(connect=lambda *a, **k: Connection())}):
            with self.assertRaises(Held): asyncio.run(provider._speak('public', cancel))
        self.assertEqual(sent, [])



class LiveMemoryTests(unittest.TestCase):
    def test_transcript_overflow_discards_later_deltas_while_still_finalizing_usage(self):
        cancel = threading.Event()
        class Connection:
            def __init__(self): self.events = asyncio.Queue()
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            def __aiter__(self): return self
            async def __anext__(self): return json.dumps(await self.events.get())
            async def send(self, raw):
                event = json.loads(raw)
                if event['type'] == 'session.start':
                    await self.events.put({'type': 'session.started'})
                    await self.events.put({'type': 'session.output_transcript.delta', 'delta': 'x' * 2500})
                    for _ in range(100): await self.events.put({'type': 'session.output_transcript.delta', 'delta': 'x' * 1000})
                elif event['type'] == 'session.close':
                    await self.events.put({'type': 'session.closed', 'reason': 'close_requested', 'usage': {'seconds': 1}})
        provider = object.__new__(OpenAIProvider); provider._headers = {}
        sleep = asyncio.sleep
        async def fast_sleep(_): await sleep(0)
        with mock.patch.dict(sys.modules, {'websockets': SimpleNamespace(connect=lambda *a, **k: Connection())}), mock.patch('asyncio.sleep', fast_sleep):
            result = asyncio.run(provider._speak('public', cancel))
        self.assertTrue(result['finalized']); self.assertLessEqual(len(result['transcript']), 2000)
        self.assertEqual(result['errors'], ['transcript_bound'])

if __name__ == '__main__': unittest.main()
