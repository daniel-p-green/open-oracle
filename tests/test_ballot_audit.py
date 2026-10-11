"""Actual Strands SDK + retained sample; authored tool events, no model inference/network."""
import os
os.environ['OTEL_SDK_DISABLED'] = 'true'

from dataclasses import replace
from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
import unittest
from unittest.mock import patch

from strands.models import Model
from strands.types.exceptions import EventLoopException
from open_oracle.ballot_audit import BallotAudit, MEASURES, MeasureDraft, local_model, run_audit_batch
from open_oracle.corpus import Corpus, KCEB_HASH
from open_oracle.session_control import operation, SessionCancelled
from strands_quality.research_corpus import Registry, Scope


def tool_results(messages):
    rows = {}
    for message in messages:
        for block in message.get('content', []):
            result = block.get('toolResult')
            if not result:
                continue
            for value in result['content']:
                data = value.get('json')
                if data is None and 'text' in value:
                    try:
                        data = json.loads(value['text'])
                    except ValueError:
                        continue
                if isinstance(data, dict):
                    rows[result['toolUseId']] = data
    return rows


class AuditModel(Model):
    """Synthetic contract fixture reads IDs from real tool results, never supplies scores."""

    def __init__(self, mode='normal'):
        self.mode, self.calls = mode, 0

    def update_config(self, **kwargs):
        pass

    def get_config(self):
        return {'model_id': 'synthetic-ballot-audit-contract'}

    async def structured_output(self, *args, **kwargs):
        raise AssertionError('Unexpected legacy API')
        yield

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        self.calls += 1
        data = tool_results(messages)
        ids = [m['measure_id'] for m in data.get('resolve', {}).get('measures', [])]
        if self.mode == 'bypass':
            calls = [('AuditDraft', {'measures': [{'measure_id': m} for m in MEASURES]}, 'final')]
        elif self.calls == 1:
            calls = ([('resolve_ballot_audit', {}, 'resolve')] if self.mode == 'unactivated' else
                     [('skills', {'skill_name': 'ballot-accessibility-audit'}, 'skill')])
        elif self.calls == 2:
            calls = [('resolve_ballot_audit', {}, 'resolve')]
        elif self.calls == 3:
            calls = [('read_measure_evidence', {'measure_id': m}, 'read-' + m) for m in ids]
            if self.mode == 'tool-error':
                calls.insert(0, ('read_measure_evidence', {'measure_id': 'not-in-scope'}, 'invalid'))
        elif self.calls == 4 and self.mode != 'skip-scores':
            calls = [('test_ballot_readability', {'measure_id': m}, 'score-' + m) for m in ids]
        elif self.calls == 5 and self.mode == 'context':
            calls = [('search_audit_context', {'measure_id': 'combat', 'purpose': 'legal_reference',
                       'query': 'March April 2027 2037'}, 'context')]
        elif self.calls == 6 and self.mode == 'context':
            matches = data['context']['matches']
            row = next(r for r in matches if r['source_id'] == 'combat-6096-selected-v1')
            calls = [('read_audit_context', {'chunk_id': row['chunk_id']}, 'context-read')]
        else:
            measures = [{'measure_id': m, 'claims': []} for m in ids]
            if self.mode == 'evidence-gaps':
                measures[0]['missing_aspects'] = ['baseline', 'yes', 'no', 'terms']
            elif self.mode == 'uncited-gap-claim':
                measures[0]['claims'] = [{'aspect': 'baseline', 'text': 'MISSING: existing plan details.',
                                           'citations': []}]
            elif self.mode == 'omit':
                measures.pop()
            elif self.mode == 'duplicate':
                measures[-1] = measures[0]
            elif self.mode in {'citation', 'citation-span', 'wrong-span', 'wrong-quote', 'wrong-measure', 'unread', 'context'}:
                source = data.get('context-read') if self.mode == 'context' else data['read-amendment-3']['chunks'][0]
                quote = source['text'][:200].rsplit(' ', 1)[0]
                if self.mode == 'wrong-quote':
                    quote = 'This quotation is invented and absent from the original.'
                measures[0]['claims'] = [{'aspect': 'decision', 'text': 'Synthetic draft for boundary testing.',
                    'citations': [{'chunk_id': source['chunk_id'] if self.mode != 'unread' else 'not-read', 'quote': quote}]}]
                if self.mode in {'citation-span', 'wrong-span'}:
                    measures[0]['claims'][0]['citations'] = [{'chunk_id': source['chunk_id'],
                        'citation_span_id': source['citation_spans'][0]['citation_span_id']
                        if self.mode == 'citation-span' else '0' * 64}]
                if self.mode == 'wrong-measure':
                    measures[-1]['claims'] = measures[0]['claims']
                    measures[0]['claims'] = []
                if self.mode == 'context':
                    measures[-1]['claims'] = measures[0]['claims']
                    measures[0]['claims'] = []
            calls = [('AuditDraft', {'measures': measures}, 'final')]
        yield {'messageStart': {'role': 'assistant'}}
        for name, args, ident in calls:
            yield {'contentBlockStart': {'start': {'toolUse': {'toolUseId': ident, 'name': name}}}}
            yield {'contentBlockDelta': {'delta': {'toolUse': {'input': json.dumps(args)}}}}
            yield {'contentBlockStop': {}}
        yield {'messageStop': {'stopReason': 'tool_use'}}


class BallotAuditTests(unittest.TestCase):
    def test_gap_declarations_cannot_duplicate_or_contradict_claims(self):
        for data in [
            {'missing_aspects': ['no', 'no']},
            {'missing_aspects': ['no'], 'claims': [{'aspect': 'no', 'text': 'A claim.',
                'citations': [{'chunk_id': 'fixture', 'quote': 'A fixture quotation.'}]}]},
        ]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                MeasureDraft.model_validate({'measure_id': 'proposition-a', **data})

    def test_proposition_a_can_report_gaps_without_uncited_claims(self):
        packet = BallotAudit(measures=('proposition-a',)).run(
            AuditModel('evidence-gaps'), execution='synthetic_sdk')
        entry = packet['measures'][0]
        self.assertEqual(entry['draft_claims'], [])
        self.assertIn('baseline_explanation_not_established', entry['gaps'])
        self.assertFalse(packet['public_display'])

    def test_missing_evidence_note_cannot_pass_as_uncited_claim(self):
        with self.assertRaisesRegex(EventLoopException, 'Audit model budget exceeded'):
            BallotAudit(measures=('proposition-a',)).run(
                AuditModel('uncited-gap-claim'), execution='synthetic_sdk')

    def test_batch_fallback_cannot_hide_changed_original_or_cancellation(self):
        corpus = Corpus()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ballot.pdf'
            path.write_bytes(corpus.originals['kceb-sample'].read_bytes())
            corpus.originals = {**corpus.originals, 'kceb-sample': path}

            def corrupt_after_initial_checks():
                path.write_bytes(b'changed approved original')
                return AuditModel('bypass')

            with self.assertRaisesRegex(ValueError, 'Original changed'):
                run_audit_batch(corrupt_after_initial_checks, corpus=corpus, measures=('combat',),
                                execution='synthetic_sdk')
        signal = Event()
        model = AuditModel()

        def cancel_before_inference():
            signal.set()
            return model

        with self.assertRaises(SessionCancelled), operation(signal):
            run_audit_batch(cancel_before_inference, measures=('combat',), execution='synthetic_sdk')
        self.assertEqual(model.calls, 0)

    def test_serial_measure_requests_combine_only_complete_private_results(self):
        packet = run_audit_batch(AuditModel, execution='synthetic_sdk')
        self.assertEqual([m['measure_id'] for m in packet['measures']], list(MEASURES))
        self.assertEqual(packet['model_calls'], 30)
        self.assertEqual(packet['model_calls_per_measure'], dict.fromkeys(MEASURES, 5))
        self.assertFalse(packet['public_display'])
        self.assertEqual(len(packet['trace']), 18)
        fallback = run_audit_batch(lambda: AuditModel('skip-scores'), execution='synthetic_sdk')
        self.assertFalse(fallback['model_drafts_complete'])
        self.assertEqual(fallback['execution'], 'synthetic_sdk_with_tools_only_fallback')
        for entry in fallback['measures']:
            self.assertEqual(entry['generation']['status'], 'unavailable')
            self.assertEqual(entry['draft_claims'], [])
            self.assertIn('model_draft_unavailable', entry['gaps'])
            self.assertEqual(entry['readability'][0]['provenance']['sha256'], KCEB_HASH)

    def test_offline_sample_reproduces_all_six_questions_and_five_fiscal_summaries(self):
        packet = BallotAudit().prepare()
        self.assertEqual(packet['execution'], 'strands_tools_direct_no_inference')
        self.assertEqual(packet['model_calls'], 0)
        expected = [(52, -36.295, 31.24), (81, -48.7578, 40.1827),
                    (46, -10.8941, 26.2065), (48, 8.3025, 24.0258),
                    (42, 11.1193, 22.1424), (92, 20.3711, 21.8457)]
        self.assertEqual([m['measure_id'] for m in packet['measures']], list(MEASURES))
        self.assertEqual(sum(len(m['readability']) for m in packet['measures']), 11)
        for measure, (words, fre, fkgl) in zip(packet['measures'], expected):
            report = measure['readability'][0]
            self.assertEqual(report['counts']['words'], words)
            self.assertEqual(report['scores'], {'flesch_reading_ease': fre, 'flesch_kincaid_grade_level': fkgl})
            self.assertEqual(report['provenance']['sha256'], KCEB_HASH)
            self.assertEqual(report['factual_fidelity_status'], 'not_evaluated')
            self.assertIn('no_explanation_not_established', measure['gaps'])
        self.assertIn('Trust Fund', packet['measures'][-1]['readability'][0]['scored_text'])
        self.assertFalse(packet['public_display'])
        self.assertFalse(packet['speech'])
        self.assertIsNone(packet['ballot_average'])

    def test_actual_native_skill_agent_reads_and_scores_complete_sample(self):
        model = AuditModel('citation-span')
        packet = BallotAudit().run(model, execution='synthetic_sdk')
        self.assertEqual(model.calls, 5)
        self.assertEqual(packet['model_calls'], 5)
        self.assertEqual(packet['execution'], 'synthetic_sdk')
        self.assertEqual(packet['release_state'], 'private_awaiting_quality_review')
        claim = packet['measures'][0]['draft_claims'][0]
        self.assertEqual(claim['support_status'], 'exact_citation_checked_meaning_not_reviewed')
        self.assertEqual(claim['citations'][0]['source_id'], 'kceb-sample')
        self.assertEqual(len(packet['trace']), 13)
        self.assertNotIn('Synthetic draft', json.dumps(packet['trace']))

    def test_tool_bypass_missing_scores_omissions_duplicates_and_forged_citations_are_held(self):
        for mode in ('bypass', 'skip-scores', 'omit', 'duplicate', 'wrong-quote', 'wrong-measure',
                     'unread', 'unactivated', 'wrong-span'):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                BallotAudit().run(AuditModel(mode), execution='synthetic_sdk')

    def test_recovered_tool_error_does_not_substitute_for_a_successful_read_or_score(self):
        packet = BallotAudit().run(AuditModel('tool-error'), execution='synthetic_sdk')
        self.assertEqual(packet['tool_errors'], [{'tool': 'read_measure_evidence', 'status': 'error'}])
        self.assertEqual(len(packet['measures']), 6)
        self.assertFalse(packet['public_display'])

    def test_context_retrieval_uses_existing_role_hash_scope_and_exact_quote_checks(self):
        packet = BallotAudit().run(AuditModel('context'), execution='synthetic_sdk')
        citation = packet['measures'][-1]['draft_claims'][0]['citations'][0]
        self.assertEqual(citation['source_id'], 'combat-6096-selected-v1')
        self.assertEqual(citation['role'], 'adopted_proposal')
        self.assertFalse(citation['fresh_http'])
        self.assertTrue(any(t['tool'] == 'search_audit_context' for t in packet['trace']))

    def test_wrong_authority_election_version_and_unsupported_measure_fail_before_model(self):
        for scope in (Scope(authority='JCEB'), Scope(authority='KCEB', election_date='2024-11-05'),
                      Scope(authority='KCEB', versions=(('kceb-sample', '0' * 64),))):
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                BallotAudit(scope=scope)
        with self.assertRaises(ValueError):
            BallotAudit(measures=('blue-springs',))

    def test_changed_original_is_rechecked_at_read_and_requests_cannot_be_reused(self):
        audit = BallotAudit(measures=('combat',))
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ballot.pdf'
            source = audit.registry.sources['kceb-sample']
            path.write_bytes(source.original_path.read_bytes())
            sources = [replace(s, original_path=path) if s.id == source.id else s
                       for s in audit.registry.sources.values()]
            audit.registry = Registry(sources, list(audit.registry.chunks.values()))
            audit.evidence.registry = audit.registry
            audit.begin()
            audit.tools[0]()
            audit.tools[1](measure_id='combat')
            path.write_bytes(b'changed original')
            with self.assertRaisesRegex(ValueError, 'Original changed'):
                audit.tools[2](measure_id='combat')
        with self.assertRaisesRegex(ValueError, 'cannot be reused'):
            audit.prepare()

    def test_out_of_order_tools_and_cancel_do_not_produce_packet(self):
        audit = BallotAudit(measures=('combat',))
        with self.assertRaises(ValueError):
            audit.tools[2](measure_id='combat')
        signal = Event()
        with self.assertRaises(SessionCancelled), operation(signal):
            signal.set()
            with self.assertRaises((SessionCancelled, TimeoutError)):
                BallotAudit().prepare()

    def test_local_provider_is_loopback_no_retry_and_rejects_remote_or_incapable_models(self):
        def response(value):
            return BytesIO(json.dumps(value).encode())

        with patch('urllib.request.urlopen', side_effect=[
                response({'models': [{'name': 'installed:latest'}]}),
                response({'capabilities': ['completion', 'tools']})]):
            model = local_model('installed:latest')
        self.assertEqual(model.client_args['base_url'], 'http://127.0.0.1:11434/v1/')
        self.assertEqual(model.client_args['max_retries'], 0)
        self.assertEqual(model.get_config()['params']['reasoning_effort'], 'none')
        for info in ({'remote_host': 'https://remote.invalid'}, {'remote_model': 'remote'},
                     {'capabilities': ['decision']}):
            with self.subTest(info=info), patch('urllib.request.urlopen', side_effect=[
                    response({'models': [{'name': 'installed:latest'}]}), response(info)]):
                with self.assertRaises(ValueError):
                    local_model('installed:latest')


if __name__ == '__main__':
    unittest.main()
