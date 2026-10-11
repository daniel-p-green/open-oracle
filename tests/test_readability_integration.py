"""Actual SDK dispatch, authored provider events, no live inference."""
import json
import threading
import unittest

from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.orchestration import select_with_strands
from open_oracle.session_control import operation, SessionCancelled
from test_strands import OfflineToolModel


class ReadabilityModel(OfflineToolModel):
    def __init__(self, unread=False, skip=False):
        super().__init__()
        self.unread, self.skip, self.schemas = unread, skip, []

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        self.calls += 1
        self.schemas = tool_specs
        steps = [('resolve_contest', {}), ('search_evidence', {'selected_contest_id': 'combat'}),
                 ('read_evidence', {'evidence_id': 'combat:jceb-sample'})]
        if not self.skip:
            steps.append(('test_ballot_readability', {'evidence_id': 'amendment-3:jceb-sample' if self.unread else 'combat:jceb-sample'}))
        if self.calls <= len(steps):
            name, args = steps[self.calls - 1]
        else:
            spec = next(s for s in tool_specs if 'evidence_ids' in s.get('inputSchema', {}).get('json', {}).get('properties', {}))
            name, args = spec['name'], {'evidence_ids': ['combat:jceb-sample']}
        yield {'messageStart': {'role': 'assistant'}}
        yield {'contentBlockStart': {'start': {'toolUse': {'toolUseId': f'readability-{self.calls}', 'name': name}}}}
        yield {'contentBlockDelta': {'delta': {'toolUse': {'input': json.dumps(args)}}}}
        yield {'contentBlockStop': {}}
        yield {'messageStop': {'stopReason': 'tool_use'}}


class ReadabilityIntegrationTests(unittest.TestCase):
    def test_actual_agent_tool_scores_read_same_contest_with_narrow_schema(self):
        model = ReadabilityModel()
        loop = EvidenceLoop(Corpus(), selector=lambda *a: select_with_strands(model, *a, execution='synthetic_sdk'))
        result = loop.answer('What is the COMBAT reading level?')
        self.assertEqual(result['status'], 'answered')
        self.assertEqual(model.calls, 5)
        report = result['readability']['reports'][0]
        self.assertIn('separate from the general fund', report['scored_text'])
        self.assertEqual(report['provenance']['id'], 'combat:jceb-sample')
        self.assertEqual(report['factual_fidelity_status'], 'not_evaluated')
        spec = next(s for s in model.schemas if s['name'] == 'test_ballot_readability')
        self.assertEqual(set(spec['inputSchema']['json']['properties']), {'evidence_id'})
        receipt = result['operational_receipt']
        self.assertTrue(receipt['finalized'])
        self.assertEqual(receipt['execution'], 'synthetic_sdk')
        self.assertEqual(receipt['model_attempts_started'], 5)
        self.assertTrue(any(e['name'] == 'test_ballot_readability' and e['status'] == 'success' for e in receipt['tool_events']))
        self.assertEqual(receipt['released_sources'][0]['id'], 'combat:jceb-sample')
        self.assertNotIn('readability_analysis', json.dumps(result['trace']))
        self.assertNotIn(report['raw_text'], json.dumps(receipt))
        self.assertNotIn('speech', result)

    def test_missing_or_unread_tool_result_cannot_count_as_completed(self):
        for model in (ReadabilityModel(skip=True), ReadabilityModel(unread=True)):
            with self.assertRaisesRegex(ValueError, 'readability tool workflow'):
                select_with_strands(model, 'COMBAT readability', {}, 'combat', Corpus())

    def test_normal_request_retains_four_model_calls_and_no_scoring_tool(self):
        model = OfflineToolModel()
        result = EvidenceLoop(Corpus(), selector=lambda *a: select_with_strands(model, *a)).answer('What is the COMBAT tax rate?')
        self.assertEqual(model.calls, 4)
        self.assertNotIn('readability', result)
        self.assertFalse(any(t['name'] == 'test_ballot_readability' for t in result['operational_receipt']['tool_events']))

    def test_exact_source_scoring_is_not_model_inference_or_quality_approval(self):
        result = EvidenceLoop(Corpus()).answer('What is the COMBAT Flesch reading level?')
        self.assertEqual(result['readability']['execution'], 'strands_tool_direct')
        self.assertEqual(result['review']['status'], 'not_run')
        self.assertEqual(result['operational_receipt']['model_attempts_started'], 0)
        self.assertIsNone(result['operational_receipt']['usage'])
        self.assertEqual(result['readability']['reports'][0]['counts']['words'], 92)
        missing = EvidenceLoop(Corpus()).answer('COMBAT fiscal summary readability')
        self.assertEqual(missing['readability']['status'], 'unavailable')

    def test_config_hash_excludes_visitor_question_scope_and_request_id(self):
        loop = EvidenceLoop(Corpus())
        a = loop.answer('What is the COMBAT tax rate?', {'authority': 'JCEB'}, request_id='private-one')
        b = loop.answer('Explain COMBAT', {'authority': 'KCEB'}, request_id='private-two')
        self.assertEqual(a['operational_receipt']['config_sha256'], b['operational_receipt']['config_sha256'])
        serialized = json.dumps(a['operational_receipt'])
        self.assertNotIn('private-one', serialized)
        self.assertNotIn('authority', serialized)
        self.assertEqual(sum(loop.operation_metrics.snapshot()['completed_operation_counts'].values()), 2)

    def test_cancelled_request_finishes_one_content_free_error_operation(self):
        loop = EvidenceLoop(Corpus())
        signal = threading.Event()
        with self.assertRaises(SessionCancelled), operation(signal):
            signal.set()
            loop.answer('Do not retain this visitor sentence')
        metrics = loop.operation_metrics.snapshot()
        self.assertEqual(metrics['completed_operation_counts'], {'unavailable': 1})
        self.assertNotIn('Do not retain this visitor sentence', json.dumps(metrics))
        self.assertIsNone(metrics['unique_visitor_count'])

    def test_outer_receipt_finalization_occurs_after_review(self):
        from open_oracle.operational_receipts import current_receipt
        class Reviewer:
            def review(self, envelope):
                self.receipt = current_receipt.get()
                self.assertion = self.receipt.snapshot()['finalized']
                return {'status': 'accepted', 'execution': 'offline_stub'}
        reviewer = Reviewer()
        result = EvidenceLoop(Corpus(), reviewer=reviewer).answer('COMBAT')
        self.assertFalse(reviewer.assertion)
        self.assertTrue(reviewer.receipt.snapshot()['finalized'])
        self.assertEqual(result['operational_receipt']['release']['review_execution'], 'synthetic_sdk')
        self.assertIsNone(current_receipt.get())
