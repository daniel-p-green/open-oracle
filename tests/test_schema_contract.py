"""Offline SDK/schema/privacy counterexamples; no provider inference."""
import json
from unittest import TestCase
from pydantic import ValidationError, ConfigDict
from jsonschema import Draft202012Validator
from strands.tools.structured_output.structured_output_tool import StructuredOutputTool
from strands_quality.research_agent import CitedAnswer, ResearchRequest
from strands_quality.research_corpus import Scope, load_verified_corpus
from strands_quality.schema_validation import collector,normalized_path,CATEGORIES,FIELD_PATHS
from open_oracle.corpus import Corpus
from test_research_release import BoundModel,Review
from open_oracle.research_engine import ResearchEvidenceLoop

CANARY='PRIVATE_SCHEMA_CANARY_WITH_SECRET_like_credential'

class SchemaContractTests(TestCase):
    def test_prior_sdk_nullable_lists_reproduced_and_repaired_schema_rejects_them(self):
        class LegacyAnswer(CitedAnswer):
            model_config=ConfigDict(extra='forbid',frozen=True,hide_input_in_errors=True,json_schema_extra={})
        old=StructuredOutputTool(LegacyAnswer).tool_spec['inputSchema']['json']
        bad={'claims':None,'gaps':None}
        self.assertTrue(Draft202012Validator(old).is_valid(bad))
        with self.assertRaises(ValidationError) as ctx:LegacyAnswer.model_validate(bad)
        self.assertEqual({e['type'] for e in ctx.exception.errors(include_input=False)}, {'list_type'})
        new=StructuredOutputTool(CitedAnswer).tool_spec['inputSchema']['json']
        self.assertEqual(new['properties']['claims']['type'],'array')
        self.assertEqual(new['properties']['gaps']['type'],'array')
        self.assertEqual(set(new['required']), {'claims','gaps'})
        self.assertFalse(Draft202012Validator(new).is_valid(bad))
        self.assertTrue(Draft202012Validator(new).is_valid({'claims':[],'gaps':[]}))
        self.assertEqual(CitedAnswer(claims=[],gaps=[]).claims,[])
    def test_error_projection_omits_values_messages_context_urls_and_unknown_extra_keys(self):
        bad={'claims':[{'part_id':CANARY,'text':CANARY,'citations':[{'chunk_id':CANARY,'exact_quote':None,'citation_span_id':None}]}], 'gaps':None, CANARY:CANARY}
        captured=[];token=collector.set(lambda **e:captured.append(e))
        try:
            with self.assertRaises(ValidationError):CitedAnswer.model_validate(bad)
        finally:collector.reset(token)
        self.assertTrue(captured)
        self.assertNotIn(CANARY,json.dumps(captured))
        self.assertTrue(all(set(e)=={'schema','schema_sha256','category','field_path'} for e in captured))
        self.assertTrue(all(e['category'] in CATEGORIES and e['field_path'] in FIELD_PATHS for e in captured))
        self.assertIn('unrecognized_field',{e['field_path'] for e in captured})
        self.assertEqual(normalized_path(('claims',987,'citations',123,'exact_quote')),'claims.*.citations.*.exact_quote')
        self.assertEqual(normalized_path(('claims',CANARY,'text')),'unrecognized_field')
        self.assertEqual(normalized_path(('claims',True,'text')),'unrecognized_field')
    def test_actual_sdk_validation_failures_capture_paths_then_repair_without_provider(self):
        class InvalidThenValid(BoundModel):
            def __init__(self):super().__init__();self.attempts=0
            def final_calls(self,*args):
                self.attempts+=1
                if self.attempts<=2:return [('CitedAnswer',{'claims':None,'gaps':None},'malformed')]
                return super().final_calls(*args)
        model=InvalidThenValid();r=ResearchRequest(load_verified_corpus(Corpus()),scope=Scope(),model=model,execution='synthetic_sdk')
        # The integrated receipt implements the independently validating collector.
        self.assertTrue(hasattr(r.receipt,'schema_validation'))
        result=r.run('What is the COMBAT rate and how long would it last?')
        self.assertEqual(len(result['claims']),2)
        events=result['receipt']['schema_events']
        self.assertEqual(len(events),4)
        self.assertEqual({e['category'] for e in events},{'list_type'})
        self.assertEqual({e['field_path'] for e in events},{'claims','gaps'})
        self.assertFalse(result['public_display'])
    def test_failed_engine_returns_completed_safe_receipt_and_never_draft(self):
        class AlwaysInvalid(BoundModel):
            def final_calls(self,*args):return [('CitedAnswer',{'claims':None,'gaps':None},'malformed')]
        loop=ResearchEvidenceLoop(Corpus(),AlwaysInvalid,Review(),execution='synthetic_sdk')
        response=loop.answer('What is the COMBAT rate?',{'authority':'JCEB'})
        self.assertEqual(response['status'],'unavailable')
        self.assertFalse(response['public_display']);self.assertEqual(response['claims'],[]);self.assertEqual(response['evidence'],[])
        receipt=response['operational_receipt']
        self.assertTrue(receipt['finalized']);self.assertGreater(receipt['model_attempts_started'],0)
        self.assertGreater(len(receipt['schema_events']),0)
        self.assertNotIn('tool_input',json.dumps(receipt))
        self.assertNotIn('citation_span_id',json.dumps(receipt))

    def test_receipt_independently_rejects_private_metadata_and_bounds_storage(self):
        from strands_quality.receipts import EvidenceReceipt
        from strands_quality.schema_validation import SCHEMA_NAME
        receipt=EvidenceReceipt(config_hash='a'*64,execution='synthetic_sdk',source_catalog={},max_events=1)
        event={'schema':SCHEMA_NAME,'schema_sha256':'b'*64,'category':'list_type','field_path':'claims'}
        for bad in ({**event,'message':CANARY},{**event,'category':CANARY},
                    {**event,'field_path':CANARY},{**event,'schema_sha256':CANARY}):
            with self.assertRaises(ValueError):receipt.schema_validation(**bad)
        receipt.schema_validation(**event)
        receipt.schema_validation(**event)
        snapshot=receipt.finish()
        self.assertEqual(snapshot['schema_events'],[event])
        self.assertEqual(snapshot['schema_dropped_event_count'],1)
        self.assertNotIn(CANARY,json.dumps(snapshot))
        receipt.schema_validation(**event)
        self.assertEqual(receipt.snapshot(),snapshot)
        snapshot['schema_events'].clear()
        self.assertEqual(receipt.snapshot()['schema_events'],[event])

    def test_request_context_collectors_do_not_cross_threads_or_survive_reset(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        barrier=Barrier(2)
        def validate(field):
            captured=[]
            token=collector.set(lambda **event:captured.append(event))
            try:
                barrier.wait(timeout=3)
                with self.assertRaises(ValidationError):
                    CitedAnswer.model_validate({'claims':None if field=='claims' else [],
                                                'gaps':None if field=='gaps' else []})
            finally:
                collector.reset(token)
            self.assertIsNone(collector.get())
            return captured
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(validate,['claims','gaps']))
        self.assertEqual([[event['field_path'] for event in result] for result in results],
                         [['claims'],['gaps']])
        self.assertIsNone(collector.get())
