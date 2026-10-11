"""Actual Strands Agent/tools with an offline event provider; never model inference."""
import json
import unittest
from strands.models import Model
from open_oracle.corpus import Corpus
from open_oracle.orchestration import select_with_strands


class OfflineToolModel(Model):
    def __init__(self, forged=False, contest_id='combat', evidence_ids=None):
        self.calls = 0
        self.forged = forged
        self.contest_id = contest_id
        self.evidence_ids = evidence_ids or ['combat:jceb-sample']

    def update_config(self, **kwargs):
        pass

    def get_config(self):
        return {'model_id': 'offline-contract-stub', 'context_window_limit': 128000}

    async def structured_output(self, *args, **kwargs):
        raise AssertionError('Unexpected legacy structured-output API')
        yield

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        self.calls += 1
        steps = [('resolve_contest', {}), ('search_evidence', {'selected_contest_id': self.contest_id})]
        steps += [('read_evidence', {'evidence_id': ident}) for ident in self.evidence_ids]
        if self.forged:
            steps = []
        if self.calls <= len(steps):
            name, arguments = steps[self.calls - 1]
        else:
            structured = [s for s in tool_specs if 'evidence_ids' in s.get('inputSchema', {}).get('json', {}).get('properties', {})]
            if not structured:
                raise AssertionError('Structured output tool missing')
            name, arguments = structured[0]['name'], {'evidence_ids': self.evidence_ids}
        yield {'messageStart': {'role': 'assistant'}}
        yield {'contentBlockStart': {'start': {'toolUse': {'toolUseId': f'offline-{self.calls}', 'name': name}}}}
        yield {'contentBlockDelta': {'delta': {'toolUse': {'input': json.dumps(arguments)}}}}
        yield {'contentBlockStop': {}}
        yield {'messageStop': {'stopReason': 'tool_use'}}


class StrandsTests(unittest.TestCase):
    def test_amendment_five_sources_are_read_within_existing_call_cap(self):
        ids = ['amendment-7:kceb-sample', 'amendment-7:proposal-investment', 'amendment-7:proposal-conditions', 'amendment-7:proposal-limit', 'amendment-7:sos-fair-language']
        class AmendmentModel(OfflineToolModel):
            async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
                self.calls += 1
                structured = [s for s in tool_specs if 'evidence_ids' in s.get('inputSchema', {}).get('json', {}).get('properties', {}) and s['name'] != 'read_amendment_sources']
                steps = [('resolve_contest', {}), ('search_evidence', {'selected_contest_id': 'amendment-7'}), ('read_amendment_sources', {'evidence_ids': ids}), (structured[0]['name'], {'evidence_ids': ids})]
                name, arguments = steps[self.calls - 1]
                yield {'messageStart': {'role': 'assistant'}}
                yield {'contentBlockStart': {'start': {'toolUse': {'toolUseId': f'fixture-{self.calls}', 'name': name}}}}
                yield {'contentBlockDelta': {'delta': {'toolUse': {'input': json.dumps(arguments)}}}}
                yield {'contentBlockStop': {}}
                yield {'messageStop': {'stopReason': 'tool_use'}}
        model = AmendmentModel()
        selected, trace = select_with_strands(model, 'If I vote Yes on Amendment seven, do my taxes go away?', {'authority': 'KCEB'}, 'amendment-7', Corpus())
        self.assertEqual(set(selected), set(ids))
        self.assertEqual(model.calls, 4)
        self.assertEqual([t['evidence_ids'][0] for t in trace if t['tool'] == 'read_evidence'], ids)
        self.assertTrue(all(not t['live'] for t in trace))

    def test_actual_sdk_resolves_searches_reads_and_selects(self):
        ids, trace = select_with_strands(OfflineToolModel(), 'What does COMBAT say?', {}, 'combat', Corpus())
        self.assertEqual(ids, ['combat:jceb-sample'])
        self.assertTrue(all(not t['live'] and t['provider_execution'] == 'unverified_provider' for t in trace))
        self.assertTrue(all(t['model'] == 'offline-contract-stub' and t['model_attempts'] == 4 for t in trace))
        self.assertEqual([t['tool'] for t in trace], ['resolve_contest', 'search_evidence', 'read_evidence'])

    def test_structured_selection_cannot_bypass_tools(self):
        with self.assertRaises(ValueError):
            select_with_strands(OfflineToolModel(forged=True), 'COMBAT', {}, 'combat', Corpus())


class BudgetAndDuplicateTests(unittest.TestCase):
    def test_tool_errors_do_not_allow_release_after_exceeded_budget(self):
        class BudgetModel(OfflineToolModel):
            async def stream(self, *args, **kwargs):
                if self.calls != 3:
                    async for event in super().stream(*args, **kwargs): yield event
                    return
                self.calls += 1
                yield {'messageStart': {'role': 'assistant'}}
                for i in range(6):
                    yield {'contentBlockStart': {'start': {'toolUse': {'toolUseId': f'budget-{i}', 'name': 'resolve_contest'}}}}
                    yield {'contentBlockDelta': {'delta': {'toolUse': {'input': '{}'}}}}
                    yield {'contentBlockStop': {}}
                yield {'messageStop': {'stopReason': 'tool_use'}}
        with self.assertRaises(TimeoutError):
            select_with_strands(BudgetModel(), 'COMBAT', {}, 'combat', Corpus())

    def test_duplicate_ids_are_deduplicated_after_same_request_read(self):
        class DuplicateModel(OfflineToolModel):
            async def stream(self, *args, **kwargs):
                async for event in super().stream(*args, **kwargs):
                    if self.calls == 4 and 'contentBlockDelta' in event:
                        event['contentBlockDelta']['delta']['toolUse']['input'] = json.dumps({'evidence_ids': ['combat:jceb-sample'] * 2})
                    yield event
        ids, _ = select_with_strands(DuplicateModel(), 'COMBAT', {}, 'combat', Corpus())
        self.assertEqual(ids, ['combat:jceb-sample'])
