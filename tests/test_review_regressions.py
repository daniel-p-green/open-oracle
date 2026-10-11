"""Specific counterexamples from actual Opus5.5 review, not quality calibration."""
import os
os.environ['OTEL_SDK_DISABLED'] = 'true'
import asyncio
from importlib.util import find_spec
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch
import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from test_research import ResearchModel, Corpus
from strands_quality.research_corpus import Registry, Scope, load_verified_corpus
from strands_quality.research_agent import ResearchRequest, CitedAnswer, Gap


class ReviewRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.registry = load_verified_corpus(Corpus())
    def request(self, **kwargs):
        return ResearchRequest(self.registry, scope=kwargs.pop('scope', Scope()),
                               model=ResearchModel(), execution='synthetic_sdk', **kwargs)
    def call(self, req, name, **args): return getattr(req.agent.tool, name)(**args)
    def plan(self, req, purpose='ballot_fact', query='quarter cent', contest='combat', extra=()):
        result = self.call(req, 'plan_evidence', contest_id=contest, parts=[
            dict(id='part', question='Planted contract question', query=query, purpose=purpose), *extra])
        self.assertEqual(result['status'], 'success')
    def read(self, req, source_id='jceb-sample'):
        self.assertEqual(self.call(req, 'search_official_sources', part_id='part')['status'], 'success')
        self.assertEqual(self.call(req, 'acquire_official_source', source_id=source_id)['status'], 'success')
        self.assertEqual(self.call(req, 'search_indexed_evidence', part_id='part')['status'], 'success')
        candidates = [cid for cid in req.retrieved['part'] if self.registry.chunks[cid].source_id == source_id]
        cid = next((cid for cid in candidates if '67.547' in self.registry.chunks[cid].text), candidates[0])
        self.assertEqual(self.call(req, 'read_evidence_chunk', part_id='part', chunk_id=cid)['status'], 'success')
        return cid
    @staticmethod
    def gap_result(reason):
        return SimpleNamespace(structured_output=CitedAnswer(gaps=[Gap(part_id='part', reason=reason)]),
                               metrics=SimpleNamespace(accumulated_usage={'totalTokens': 0}))

    def test_current_law_effective_and_stale_dates_apply_to_every_purpose(self):
        for purpose in ('current_law', 'legal_reference'):
            for scope in (Scope(as_of='2020-01-01'), Scope(as_of='2027-06-01')):
                self.assertEqual(self.registry.rank('tax', scope, 'combat', purpose, {'rsmo-67.547'}), [])
        with self.assertRaisesRegex(ValueError, 'Unknown evidence purpose'):
            self.registry.rank('tax', Scope(), 'combat', 'made_up_purpose')
        with self.assertRaises(ValueError): Scope(as_of='2026-2-3')

    def test_quote_rejects_mid_word_mid_number_and_tiny_spans(self):
        from hashlib import sha256
        base = next(c for c in self.registry.chunks.values() if c.source_id == 'jceb-sample')
        text = 'The rate shall be 25 percent and the amount is $1,000,000. The total shall be 12.500 percent.'
        source = replace(self.registry.sources[base.source_id], text=text, extraction_sha256=sha256(text.encode()).hexdigest())
        chunk = replace(base, id='combat:quote-boundary', start=0, end=len(text), text=text,
                        sha256=sha256(text.encode()).hexdigest())
        reg = Registry([source], [chunk])
        for quote in ('5 percent and the amount', '$1,000', '500 percent.', 'T'):
            with self.assertRaisesRegex(ValueError, 'Quote'): reg.citation(chunk.id, quote)
        self.assertEqual(reg.citation(chunk.id, '25 percent and the amount')['quote_start'], 18)

    def test_reference_rejects_partial_token_and_decimal_rate_without_fabricating_edge(self):
        req = self.request()
        self.plan(req, 'legal_reference', '67.547')
        cid = self.read(req, 'combat-6096')
        for reference in ('67.54', '7.547', '67.5', '0.25'):
            result = self.call(req, 'lookup_legal_reference', part_id='part', chunk_id=cid, reference=reference)
            self.assertEqual(result['status'], 'error', reference)
            self.assertIn('whole original legal reference', result['content'][0]['text'])
            self.assertEqual(req.references, [])
            self.assertNotIn('missing_legal_reference', req.gaps['part'])

    def test_reference_lookup_enables_acquisition_without_independent_target_search(self):
        req = self.request()
        self.plan(req, 'legal_reference', 'Legislature', extra=[
            dict(id='law', question='Current referenced statute', query='sales tax', purpose='current_law')])
        cid = self.read(req, 'combat-6096')
        self.assertEqual(self.call(req, 'acquire_official_source', source_id='rsmo-67.547')['status'], 'error')
        edge = self.call(req, 'lookup_legal_reference', part_id='part', chunk_id=cid, reference='67.547')
        self.assertEqual(edge['status'], 'success')
        self.assertEqual(self.call(req, 'acquire_official_source', source_id='rsmo-67.547')['status'], 'success')
        self.assertIn('rsmo-67.547', req.searched['law'])
        self.call(req, 'lookup_legal_reference', part_id='part', chunk_id=cid, reference='67.547')
        self.assertEqual(len(req.references), 1)

    def test_unacquired_index_is_error_not_absence_and_success_clears_absence(self):
        req = self.request(); self.plan(req)
        self.call(req, 'search_official_sources', part_id='part')
        result = self.call(req, 'search_indexed_evidence', part_id='part')
        self.assertEqual(result['status'], 'error')
        self.assertNotIn('no_matching_source', req.gaps['part'])
        self.read(req)
        # Defensive finalizer rejects stale gap even if internal state is damaged.
        req.gaps['part'].add('no_matching_source')
        with self.assertRaisesRegex(ValueError, 'Retrieved evidence contradicts'):
            req.finalize(self.gap_result('no_matching_source'))
        self.call(req, 'search_indexed_evidence', part_id='part')
        self.assertNotIn('no_matching_source', req.gaps['part'])

    def test_read_but_not_stated_has_private_reviewable_exit(self):
        req = self.request();self.plan(req)
        self.assertEqual(self.call(req, 'record_source_gap', part_id='part', reason='not_stated_in_read_sources')['status'], 'error')
        self.read(req)
        result = self.call(req, 'record_source_gap', part_id='part', reason='not_stated_in_read_sources')
        self.assertEqual(result['status'], 'success')
        draft = req.finalize(self.gap_result('not_stated_in_read_sources'))
        self.assertEqual(draft['status'], 'abstained')
        self.assertFalse(draft['public_display'])
        req.prompt('What is the rate?')
        self.assertEqual(self.call(req, 'record_source_gap', part_id='part', reason='no_vote_advice')['status'], 'error')
        req.prompt('How should I vote on COMBAT?')
        self.assertEqual(self.call(req, 'record_source_gap', part_id='part', reason='no_vote_advice')['status'], 'success')

    def test_local_missing_metadata_fails_closed_and_needs_scope_is_specific(self):
        base = next(c for c in self.registry.chunks.values() if c.contest_id == 'blue-springs')
        for bad in (replace(base, location=None), replace(base, applicability='unknown')):
            with self.assertRaises(ValueError): Registry(list(self.registry.sources.values()), [bad])
        req = self.request(scope=Scope(municipality='Blue Springs', election_date='2024-11-05'))
        self.plan(req, query='tax', contest='blue-springs')
        self.assertEqual(self.call(req, 'record_source_gap', part_id='part', reason='needs_scope')['status'], 'error')

    def test_receipt_configuration_does_not_encode_visitor_municipality_or_district(self):
        a = self.request(scope=Scope(municipality='Blue Springs', district='District A'))
        b = self.request(scope=Scope(municipality='Independence', district='District B'))
        self.assertEqual(a.receipt.config_hash, b.receipt.config_hash)

    def test_extraction_parser_change_rejected_by_literal_pin(self):
        from strands_quality import research_corpus as module
        original = module._Visible.handle_data
        def changed(parser, data): original(parser, data + '\u200b')
        with patch.object(module._Visible, 'handle_data', changed):
            with self.assertRaisesRegex(ValueError, 'Extraction changed'):
                load_verified_corpus(Corpus())

    def test_kceb_ambiguous_marker_has_specific_load_error(self):
        corpus = Corpus();corpus.kceb += '\nQUESTION # 1\n'
        with self.assertRaisesRegex(ValueError, 'locator must be unique'): load_verified_corpus(corpus)

    @unittest.skipUnless(find_spec('ag_ui_strands'), 'Optional native adapter is not installed; run with the documented isolated extras')
    def test_native_final_call_can_cross_soft_budget_without_throwing_away_complete_draft(self):
        try: import ag_ui_strands
        except ImportError: self.skipTest('Optional isolated adapter extras absent')
        req = self.request(max_total_tokens=65)
        draft = asyncio.run(req.run_native_buffered('What is the COMBAT rate?'))
        self.assertEqual(draft['status'], 'answered')
        self.assertTrue(draft['final_call_crossed_token_cap'])
        self.assertEqual(draft['receipt']['usage']['totalTokens'], 72)

    @unittest.skipUnless(find_spec('ag_ui_strands'), 'Optional native adapter is not installed; run with the documented isolated extras')
    def test_native_clone_has_one_attempt_null_callback_and_no_stdout(self):
        try: import ag_ui_strands
        except ImportError: self.skipTest('Optional isolated adapter extras absent')
        from strands_quality.research_agent import Controls
        req = self.request();captured=[]
        original = Controls.capture
        def capture(provider, event):
            captured.append(event.agent)
            return original(provider, event)
        stdout = StringIO()
        with patch.object(Controls, 'capture', capture), redirect_stdout(stdout):
            asyncio.run(req.run_native_buffered('What is the COMBAT rate?'))
        self.assertEqual(stdout.getvalue(), '')
        self.assertTrue(captured)
        self.assertIsNot(captured[0], req.agent)
        self.assertEqual(captured[0]._retry_strategy._max_attempts, 1)
        self.assertIs(captured[0].callback_handler, req.agent.callback_handler)

    def test_completed_request_closes_tools_and_does_not_cancel_core_review_signal(self):
        from threading import Event
        event = Event();req = self.request(cancel=event)
        req.run('What is the COMBAT rate?')
        self.assertFalse(req.active())
        self.assertFalse(event.is_set())
        with self.assertRaises(TimeoutError): req.finalize(req.result)
        with self.assertRaisesRegex(ValueError, 'One request instance'): req.run('What is the rate?')

    def test_deadline_starts_at_invocation_not_construction(self):
        req = self.request()
        req.deadline = 0  # Simulate delay before beginning; no sleep needed.
        self.assertEqual(req.run('What is the COMBAT rate?')['status'], 'answered')


if __name__ == '__main__': unittest.main()
