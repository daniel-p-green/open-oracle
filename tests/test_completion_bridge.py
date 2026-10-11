"""Actual same-agent completion dispatch into core CitedAnswer; no live calls."""
import json
import unittest
from types import SimpleNamespace
from threading import Event
from test_evidence_completion import configuration, AuthoredCompletionModel, results, QUESTION
from open_oracle.corpus import Corpus
from strands_quality.research_corpus import Registry, Scope, load_verified_corpus
from strands_quality.research_agent import ResearchRequest, CitedAnswer, Claim, Quote
from strands_quality.evidence_completion import CompletionSetup

class BridgedModel(AuthoredCompletionModel):
    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        data = results(messages)
        async for event in super().stream(messages, tool_specs=tool_specs, system_prompt=system_prompt, **kwargs):
            start=event.get('contentBlockStart',{}).get('start',{}).get('toolUse')
            if start and start['name']=='EvidenceCompletionDraft': start['name']='CitedAnswer'
            delta=event.get('contentBlockDelta',{}).get('delta',{}).get('toolUse')
            if delta:
                value=json.loads(delta['input'])
                if 'findings' in value:
                    claims=[]
                    for row in value['findings']:
                        read=data.get('context-'+row['fact_id'],data.get('ballot-'+row['fact_id']))
                        claims.append({'part_id':row['fact_id'],'text':row['text'],'citations':[
                            {'chunk_id':read['chunk_id'],'citation_span_id':row['citation_span_ids'][0]}]})
                    delta['input']=json.dumps({'claims':claims,'gaps':[{'part_id':g['fact_id'],
                        'reason':'missing_legal_reference'} for g in value['gaps']]})
            yield event

class CompletionBridgeTests(unittest.TestCase):
    def request(self,registry=None,**kwargs):
        b,n,r=configuration()
        return ResearchRequest(registry or load_verified_corpus(Corpus()),scope=Scope(),
            model=BridgedModel(),execution='synthetic_sdk',completion_setup=CompletionSetup(b,n,r),
            max_turns=8,timeout_seconds=20,max_total_tokens=120,**kwargs)
    def test_same_agent_existing_cited_answer_all_three_fact_bindings(self):
        r=self.request();out=r.run(QUESTION)
        self.assertEqual(len(out['claims']),3)
        self.assertIsInstance(r.result.structured_output,CitedAnswer)
        self.assertEqual(out['evidence_completion']['reference_expansions'],1)
        self.assertEqual(r.model_calls,8)
        self.assertEqual(out['receipt']['model_attempts_started'],8)
        self.assertFalse(out['public_display']);self.assertFalse(out['speech'])
        self.assertEqual(r.read_by_part['expiry'],{'combat:combat-6096-selected-v1:existing_expiry'})
        self.assertNotIn(r.completion.primary.chunk_id,r.read_by_part['expiry'])
        self.assertTrue(all(t['name']!='other_tool' for t in out['receipt']['tool_events']))
        for claim in out['claims']:
            self.assertTrue(all(c['chunk_id'] in r.read_by_part[claim['part_id']] for c in claim['citations']))
    def test_missing_context_keeps_ballot_fact_and_explicit_two_gaps(self):
        full=load_verified_corpus(Corpus())
        registry=Registry([s for s in full.sources.values() if s.id!='combat-6096-selected-v1'],
            [c for c in full.chunks.values() if c.source_id!='combat-6096-selected-v1'])
        r=self.request(registry=registry);out=r.run(QUESTION)
        self.assertEqual(len(out['claims']),1);self.assertEqual(len(out['gaps']),2)
        self.assertEqual({g['reason'] for g in out['gaps']},{'missing_legal_reference'})
        self.assertEqual(out['evidence_completion']['reference_expansions'],1)
        self.assertFalse(out['public_display'])
    def test_default_request_does_not_expose_completion_tools(self):
        r=ResearchRequest(load_verified_corpus(Corpus()),scope=Scope(),model=BridgedModel(),execution='synthetic_sdk')
        self.assertIsNone(r.completion)
        self.assertNotIn('expand_approved_context',r.tool_names)
    def test_cross_fact_issued_id_cannot_bridge_claim(self):
        r=self.request();r.run(QUESTION);r._closed=False
        good=r.result.structured_output
        a,b=good.claims[:2]
        wrong=Quote(chunk_id=b.citations[0].chunk_id,citation_span_id=b.citations[0].citation_span_id)
        bad=CitedAnswer(claims=[Claim(part_id=a.part_id,text=a.text,citations=[wrong]),*good.claims[1:]],gaps=[])
        with self.assertRaises(ValueError):r.finalize(SimpleNamespace(structured_output=bad,metrics=r.result.metrics))
    def test_cancellation_before_dispatch_blocks_source_and_model(self):
        cancel=Event();cancel.set();r=self.request(cancel=cancel)
        with self.assertRaises(TimeoutError):r.run(QUESTION)
        self.assertEqual(r.model_calls,0);self.assertEqual(r.completion.reads,0)

    def test_shared_token_limit_holds_before_additional_source_work(self):
        r=self.request();r.max_total_tokens=20
        with self.assertRaises((ValueError,TimeoutError)):r.run(QUESTION)
        self.assertEqual(r.completion.expansions,0)
        self.assertTrue(r._closed)
        self.assertTrue(r.receipt.snapshot()['finalized'])

    def test_shared_model_limit_holds_before_expansion(self):
        r=self.request();r.max_turns=3
        with self.assertRaises((ValueError,TimeoutError)):r.run(QUESTION)
        self.assertEqual(r.completion.expansions,0)
        self.assertTrue(r._closed)

    def test_provisional_ballot_read_cannot_become_legal_finding(self):
        r=self.request();r.run(QUESTION);r._closed=False
        good=r.result.structured_output
        ballot=good.claims[0].citations[0]
        bad=CitedAnswer(claims=[good.claims[0],Claim(part_id='expiry',text='Unsupported expiry',citations=[ballot]),good.claims[2]],gaps=[])
        with self.assertRaises(ValueError):r.finalize(SimpleNamespace(structured_output=bad,metrics=r.result.metrics))
