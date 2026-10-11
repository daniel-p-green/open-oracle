"""Real installed SDK/hook dispatch with a synthetic no-network Model."""
import json
import os
os.environ['OTEL_SDK_DISABLED'] = 'true'
import unittest
from pydantic import BaseModel
from strands import Agent, tool
from strands.hooks import HookProvider, BeforeToolCallEvent
from strands.models import Model
from strands_quality.receipts import EvidenceReceipt

CANARY = 'PRIVATE_VISITOR_AUDIO_ADDRESS_SECRET_4828'
HASH = 'a' * 64


class Selection(BaseModel):
    evidence_ids: list[str]


class ScriptedModel(Model):
    """Synthetic scripted model events; no inference or hosted implementation."""
    def __init__(self, fail=False, parallel=False, repeat=False):
        self.calls, self.fail, self.parallel, self.repeat = 0, fail, parallel, repeat
    def update_config(self, **kwargs): pass
    def get_config(self): return {'model_id': 'synthetic-receipt-test'}
    async def structured_output(self, *args, **kwargs):
        raise AssertionError('Legacy output method not used')
        yield
    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        self.calls += 1
        if self.fail and self.calls == 2:
            raise ConnectionError(CANARY)
        if self.repeat or self.calls == 1:
            calls = [('resolve_contest', {})]
        elif self.calls == 2:
            calls = [('search_evidence', {'selected_contest_id': 'combat'})]
        elif self.calls == 3:
            calls = [('read_evidence', {'evidence_id': 'combat:jceb-sample'})]
            if self.parallel:
                calls += [('read_evidence', {'evidence_id': 'combat:jceb-sample'})]
        else:
            schema = next(s for s in tool_specs if 'evidence_ids' in
                          s.get('inputSchema', {}).get('json', {}).get('properties', {}))
            calls = [(schema['name'], {'evidence_ids': ['combat:jceb-sample']})]
        yield {'messageStart': {'role': 'assistant'}}
        for index, (name, args) in enumerate(calls):
            yield {'contentBlockStart': {'start': {'toolUse': {
                'toolUseId': f'{CANARY}-{self.calls}-{index}', 'name': name}}}}
            yield {'contentBlockDelta': {'delta': {'toolUse': {'input': json.dumps(args)}}}}
            yield {'contentBlockStop': {}}
        yield {'messageStop': {'stopReason': 'tool_use'}}
        yield {'metadata': {'usage': {'inputTokens': 10, 'outputTokens': 1, 'totalTokens': 11},
                            'metrics': {'latencyMs': 1}}}


def make_agent(receipt, model=None, hooks=(), read_error=False):
    executed = []
    @tool
    def resolve_contest() -> dict:
        """Resolve authorized synthetic contest."""
        executed.append('resolve_contest')
        return {'contest_id': 'combat', 'private': CANARY}
    @tool
    def search_evidence(selected_contest_id: str) -> list:
        """Search synthetic authorized evidence."""
        executed.append('search_evidence')
        return [{'id': 'combat:jceb-sample', 'text': CANARY}]
    @tool
    def read_evidence(evidence_id: str) -> dict:
        """Read a synthetic source to exercise framework events."""
        executed.append('read_evidence')
        if read_error:
            raise ValueError(CANARY)
        return {'id': evidence_id, 'text': CANARY}
    agent = Agent(model=model or ScriptedModel(), tools=[resolve_contest, search_evidence, read_evidence],
                  hooks=[receipt, *hooks], structured_output_model=Selection,
                  callback_handler=None, retry_strategy=None)
    return agent, executed


class ReceiptTests(unittest.TestCase):
    def receipt(self):
        return EvidenceReceipt(config_hash=HASH, execution='synthetic_sdk',
                               source_catalog={'combat:jceb-sample': HASH})

    def test_actual_hooks_complete_workflow_without_content_and_usage_once(self):
        receipt = self.receipt()
        agent, executed = make_agent(receipt)
        result = agent(CANARY, invocation_state={'private': CANARY}, limits={'turns': 5})
        self.assertEqual(result.structured_output.evidence_ids, ['combat:jceb-sample'])
        receipt.observe_result(result)  # Repeated observation must not sum usage.
        receipt.release(status='answered', binding='supported', review='not_run',
                        review_execution='not_run', evidence_ids=result.structured_output.evidence_ids)
        snapshot = receipt.finish()
        self.assertEqual(executed, ['resolve_contest', 'search_evidence', 'read_evidence'])
        self.assertEqual(snapshot['model_attempts_started'], 4)
        self.assertEqual([t['name'] for t in snapshot['tool_events']][:3], executed)
        self.assertEqual(snapshot['usage'], {'inputTokens': 40, 'outputTokens': 4, 'totalTokens': 44})
        self.assertTrue(all(t['status'] == 'success' for t in snapshot['tool_events']))
        self.assertNotIn(CANARY, json.dumps(snapshot))
        self.assertNotIn('usage', snapshot['tool_events'][0])

    def test_provider_exception_still_retains_prior_tool_and_sanitized_error(self):
        receipt = self.receipt()
        agent, _ = make_agent(receipt, ScriptedModel(fail=True))
        try:
            agent(CANARY)
        except Exception as error:
            snapshot = receipt.finish(error)
        else:
            self.fail('Expected synthetic provider failure')
        self.assertEqual(snapshot['tool_events'][0]['name'], 'resolve_contest')
        self.assertEqual(snapshot['error_category'], 'transport_error')
        self.assertEqual(snapshot['model_events'][-1]['status'], 'error')
        self.assertNotIn(CANARY, json.dumps(snapshot))

    def test_actual_tool_error_is_observed_without_error_message(self):
        receipt = self.receipt()
        agent, _ = make_agent(receipt, read_error=True)
        result = agent(CANARY)
        snapshot = receipt.finish(ValueError(CANARY))
        read = next(t for t in snapshot['tool_events'] if t['name'] == 'read_evidence')
        self.assertEqual(read['status'], 'error')
        self.assertEqual(read['error_category'], 'contract_error')
        self.assertNotIn(CANARY, json.dumps(snapshot))

    def test_cancelled_tool_never_executes_or_exposes_cancel_reason(self):
        class Deny(HookProvider):
            def register_hooks(self, registry):
                registry.add_callback(BeforeToolCallEvent, self.deny)
            def deny(self, event):
                if event.tool_use['name'] == 'read_evidence':
                    event.cancel_tool = CANARY
        receipt = self.receipt()
        agent, executed = make_agent(receipt, hooks=[Deny()])
        agent(CANARY)
        snapshot = receipt.finish()
        self.assertNotIn('read_evidence', executed)
        read = next(t for t in snapshot['tool_events'] if t['name'] == 'read_evidence')
        self.assertEqual(read['status'], 'cancelled')
        self.assertIsNone(read['duration_ms'])
        self.assertNotIn(CANARY, json.dumps(snapshot))

    def test_native_limit_and_parallel_tool_events_are_actual_sdk_events(self):
        receipt = self.receipt()
        model = ScriptedModel(repeat=True)
        agent, _ = make_agent(receipt, model)
        result = agent(CANARY, limits={'turns': 2})
        self.assertEqual(result.stop_reason, 'limit_turns')
        self.assertEqual(receipt.finish()['model_attempts_started'], 2)
        parallel = self.receipt()
        agent, executed = make_agent(parallel, ScriptedModel(parallel=True))
        agent(CANARY)
        snapshot = parallel.finish()
        self.assertEqual(executed.count('read_evidence'), 2)
        self.assertEqual(sum(t['name'] == 'read_evidence' for t in snapshot['tool_events']), 2)
        self.assertEqual(len({t['sequence'] for t in snapshot['tool_events']}), len(snapshot['tool_events']))

    def test_no_unaccepted_real_answer_or_unknown_source_can_be_recorded(self):
        receipt = EvidenceReceipt(config_hash=HASH, execution='real_api', source_catalog={'combat:jceb-sample': HASH})
        with self.assertRaises(ValueError):
            receipt.release(status='answered', binding='supported', review='not_run', review_execution='not_run')
        with self.assertRaises(ValueError):
            receipt.release(status='unavailable', binding='unsupported', review='rejected',
                            review_execution='real_api', evidence_ids=['combat:jceb-sample'])
        with self.assertRaises(ValueError):
            self.receipt().release(status='answered', binding='supported', review='not_run',
                                   review_execution='not_run', evidence_ids=[CANARY])

    def test_bounded_events_and_snapshot_ownership(self):
        receipt = EvidenceReceipt(config_hash=HASH, execution='synthetic_sdk', source_catalog={}, max_events=1)
        agent, _ = make_agent(receipt)
        agent(CANARY)
        first = receipt.finish()
        self.assertEqual(len(first['tool_events']), 1)
        self.assertGreater(first['dropped_event_count'], 0)
        first['tool_events'][0]['name'] = CANARY
        self.assertNotIn(CANARY, json.dumps(receipt.snapshot()))

    def test_final_receipt_cannot_be_revived_by_late_callbacks(self):
        receipt = self.receipt()
        agent, _ = make_agent(receipt)
        agent(CANARY)
        first = receipt.finish()
        # Exercise actual second SDK dispatch; operational record remains frozen.
        another, _ = make_agent(receipt)
        another(CANARY)
        self.assertEqual(receipt.snapshot(), first)
        with self.assertRaises(ValueError): receipt.stage('voice', .1)
        with self.assertRaises(ValueError):
            receipt.release(status='answered', binding='supported', review='not_run', review_execution='not_run')
