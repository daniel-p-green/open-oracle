"""Simulation tests. No providers/capture/playback/network; original source read-only."""
import base64
from copy import deepcopy
import json
from pathlib import Path
import struct
import threading
import unittest

from backend import Conversation, transcript_matches
from open_oracle.corpus import Corpus

FIXTURES = json.loads((Path(__file__).with_name('proof') / 'synthetic-fixtures.json').read_text())


def final(snapshot, ticket):
    proof = snapshot.get('finality')
    return isinstance(proof, dict) and proof == {'kind': 'SYNTHETIC_ONLY',
        **{k: ticket[k] for k in ('epoch', 'generation', 'transcript_id')}}


def synthetic_render(contract, cancel):
    pcm = struct.pack('<h', 1000) * 480
    wav = b'RIFF' + struct.pack('<I', len(pcm) + 36) + b'WAVEfmt '
    wav += struct.pack('<IHHIIHH', 16, 1, 1, 24000, 48000, 2, 16) + b'data' + struct.pack('<I', len(pcm)) + pcm
    return {'accepted': True, **{k: contract[k] for k in ('request_id', 'text', 'language')},
            'transcript': contract['text'], 'wav_base64': base64.b64encode(wav).decode(),
            'usage': {'seconds': 0.02}, 'report': {'acknowledged': True, 'transcript_matches': True,
              'invalid_output': False, 'final_usage_confirmed': True, 'close_reason': 'close_requested'}}


class BackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus()

    def setUp(self):
        self.clock = 0
        self.c = Conversation(self.corpus, finalize=final, now=lambda: self.clock, max_turns=4)
        self.c.start()

    def begin(self, ordinal=1):
        ticket = {**self.c.identity(), 'turn_id': f'turn-{ordinal}',
                  'transcript_id': f'transcript-{ordinal}', 'request_id': f'request-{ordinal}'}
        snapshot = {'text': FIXTURES['turns'][(ordinal - 1) % 2]['question'],
                    'finality': {'kind': 'SYNTHETIC_ONLY',
                      **{k: ticket[k] for k in ('epoch', 'generation', 'transcript_id')}}}
        work = self.c.begin(ticket, snapshot)
        self.assertIsNotNone(work)
        return ticket, snapshot, work

    def release(self, ordinal=1):
        ticket, snapshot, work = self.begin(ordinal)
        result = deepcopy(FIXTURES['turns'][(ordinal - 1) % 2]['result'])
        result['request_id'] = result['speech']['request_id'] = ticket['request_id']
        release = self.c.release(ticket, result)
        self.assertIsNotNone(release)
        return release['ticket'], work

    def test_two_distinct_checked_turns_one_start(self):
        for i in (1, 2):
            ticket, _ = self.release(i)
            media = self.c.render(ticket, synthetic_render)
            self.assertEqual(media['ticket'], ticket)
            self.assertTrue(self.c.complete(ticket))
        self.assertEqual(self.c.metrics()['completed'], 2)
        self.assertEqual(self.c.state, 'listening')

    def test_missing_finality_disables_start_and_delta_cannot_submit(self):
        self.assertIsNone(Conversation(self.corpus).start())
        ticket = {**self.c.identity(), 'turn_id': 'turn', 'transcript_id': 'transcript', 'request_id': 'request'}
        for event in ({'text': 'partial'}, {'text': 'delegation', 'finality': {'kind': 'delegation'}},
                      {'text': 'quiet', 'finality': {'kind': 'silence_timeout'}}):
            self.assertIsNone(self.c.begin(ticket, event))
        self.assertEqual(self.c.attempts, 0)

    def test_replay_overlap_identity_and_finality_binding(self):
        ticket, snapshot, _ = self.begin()
        self.assertIsNone(self.c.begin(ticket, snapshot))
        self.c.interrupt()
        ticket.update(self.c.identity())
        snapshot['finality'].update(self.c.identity())
        self.assertIsNone(self.c.begin(ticket, snapshot))  # IDs used once across generations.
        bad = {**ticket, 'turn_id': 'fresh', 'transcript_id': 'fresh-transcript', 'request_id': 'fresh-request'}
        self.assertIsNone(self.c.begin(bad, snapshot))

    def test_unchecked_rejected_wrong_request_and_tampered_source_withheld(self):
        mutations = [lambda r: r['review'].update(execution='offline_stub'),
                     lambda r: r['review'].update(status='rejected'),
                     lambda r: r.update(answer='Unchecked rewritten answer'),
                     lambda r: r['speech'].update(request_id='other-request'),
                     lambda r: r['speech']['evidence_bindings'][0].update(sha256='0' * 64),
                     lambda r: r.update(review=None)]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                self.setUp(); ticket, _, _ = self.begin()
                result = deepcopy(FIXTURES['turns'][0]['result'])
                result['request_id'] = result['speech']['request_id'] = ticket['request_id']
                mutate(result)
                self.assertIsNone(self.c.release(ticket, result))
                self.assertIsNone(self.c.accepted_result)

    def test_stop_preserves_accepted_document_resume_requires_new_identity(self):
        self.c.document_ref = 'synthetic-local-document'
        ticket, work = self.release()
        text = self.c.accepted_result['answer']
        before = self.c.identity()
        self.c.stop()
        self.assertTrue(work.cancel.is_set())
        self.assertEqual(self.c.document_ref, 'synthetic-local-document')
        self.assertEqual(self.c.accepted_result['answer'], text)
        self.assertIsNone(self.c.render(ticket, synthetic_render))
        self.assertIsNone(self.c.start())
        self.assertNotEqual(self.c.resume(), before)
        self.assertIsNotNone(self.release(2)[0])

    def test_erase_rotates_epoch_clears_content_and_rejects_old_work(self):
        self.c.document_ref = 'synthetic-document'; ticket, work = self.release()
        before = self.c.epoch
        self.c.erase()
        self.assertNotEqual(self.c.epoch, before)
        self.assertIsNone(self.c.document_ref); self.assertIsNone(self.c.accepted_result)
        self.assertTrue(work.cancel.is_set()); self.assertIsNone(self.c.resume())
        self.c.start()
        self.assertIsNone(self.c.render(ticket, synthetic_render))

    def test_stop_during_render_discards_late_audio_and_signals_worker(self):
        ticket, work = self.release()
        entered, finish = threading.Event(), threading.Event(); result = []
        def delayed(contract, cancel):
            entered.set(); self.assertTrue(finish.wait(2))
            return synthetic_render(contract, cancel)
        worker = threading.Thread(target=lambda: result.append(self.c.render(ticket, delayed)))
        worker.start(); self.assertTrue(entered.wait(2))
        self.c.stop(); self.assertTrue(work.cancel.is_set()); finish.set(); worker.join(2)
        self.assertFalse(worker.is_alive()); self.assertEqual(result, [None])

    def test_identity_only_single_render_and_playback_ack(self):
        ticket, _ = self.release()
        self.assertIsNone(self.c.render({**ticket, 'speech_id': 'wrong'}, synthetic_render))
        self.assertIsNotNone(self.c.render(ticket, synthetic_render))
        self.assertIsNone(self.c.render(ticket, synthetic_render))
        self.assertFalse(self.c.complete({**ticket, 'playback_id': 'wrong'}))
        self.assertTrue(self.c.complete(ticket)); self.assertFalse(self.c.complete(ticket))

    def test_deadline_and_budget_do_not_reset_on_resume(self):
        ticket, _, work = self.begin(); self.clock = 75
        self.assertTrue(self.c.tick()); self.assertTrue(work.cancel.is_set())
        self.assertIsNone(self.c.release(ticket, FIXTURES['turns'][0]['result']))
        self.c.resume(); self.assertEqual(self.c.attempts, 1)
        self.c.max_turns = 2; self.begin(2); self.c.stop(); self.assertIsNone(self.c.resume())

    def test_control_ack_and_erase_context_require_ordered_matching_identity(self):
        self.assertIsNone(self.c.listen({**self.c.identity(), 'generation': 100}))
        old = self.c.identity(); self.c.stop()
        self.assertIsNone(self.c.invalidate(old))  # Late Stop must not cancel a newer generation.
        self.assertIsNone(self.c.listen({**self.c.identity(), 'epoch': 'wrong'}))
        current = self.c.identity()
        self.assertEqual(self.c.listen({**current, 'generation': current['generation'] + 1}), self.c.identity())
        self.c.stop()
        self.assertIsNone(self.c.erase({**self.c.identity(), 'epoch': 'new', 'generation': 100}))
        self.clock = 180
        self.assertIsNone(self.c.resume())
        self.assertIsNone(self.c.listen({**self.c.identity(), 'generation': self.c.generation + 1}))

    def test_render_source_rechecked_before_and_after(self):
        ticket, _ = self.release()
        source = self.c.active.result['evidence'][0]['source_id']
        old = self.corpus.originals[source]
        try:
            self.corpus.originals[source] = Path('/nonexistent/synthetic-source-test')
            self.assertIsNone(self.c.render(ticket, lambda *_: self.fail('Renderer must not run')))
        finally:
            self.corpus.originals[source] = old
        self.setUp(); ticket, _ = self.release()
        def changed_during_render(contract, cancel):
            self.corpus.originals[source] = Path('/nonexistent/synthetic-source-test')
            return synthetic_render(contract, cancel)
        try:
            self.assertIsNone(self.c.render(ticket, changed_during_render))
        finally:
            self.corpus.originals[source] = old

    def test_malformed_incomplete_mismatched_or_oversized_audio_withheld(self):
        mutations = [lambda m: m.update(report=None), lambda m: m.update(usage=None),
            lambda m: m['report'].update(acknowledged=False),
            lambda m: m['report'].update(final_usage_confirmed=False),
            lambda m: m['report'].update(close_reason='connection_lost'),
            lambda m: m['report'].update(invalid_output=True),
            lambda m: m.update(transcript='Unchecked extra ballot claim'),
            lambda m: m.update(wav_base64='!'), lambda m: m.update(wav_base64='A' * (6 * 1024 * 1024 + 1)),
            lambda m: m['usage'].update(seconds=float('nan')),
            lambda m: m.update(request_id='other-request')]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                self.setUp(); ticket, _ = self.release()
                def renderer(contract, cancel):
                    media = synthetic_render(contract, cancel); mutate(media); return media
                self.assertIsNone(self.c.render(ticket, renderer))

    def test_metrics_contain_only_closed_numeric_counts(self):
        self.release(); payload = self.c.metrics()
        self.assertTrue(all(type(v) is int and v >= 0 for v in payload.values()))
        self.assertNotIn('request', json.dumps(payload)); self.assertNotIn('COMBAT', json.dumps(payload))


if __name__ == '__main__':
    unittest.main()


class NumericFenceTests(unittest.TestCase):
    def test_sign_decimal_unit_and_hidden_controls_never_match(self):
        for actual in ('Rate −0.25 cents.', 'Rate 025 cents.', 'Rate 0.25 percent.', 'Rate 0.25\u200b cents.'):
            with self.subTest(actual=actual):
                self.assertFalse(transcript_matches('Rate 0.25 cents.', actual))

    def test_exact_unicode_whitespace_parity_matches(self):
        self.assertTrue(transcript_matches('Rate 0.25 cents.', 'Rate 0.25  cents.'))
