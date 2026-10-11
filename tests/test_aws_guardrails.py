"""Authored service/response contract cases; no AWS inference or credentials."""
from copy import deepcopy
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).parents[1]
MODULE = ROOT / "open_oracle" / "aws_guardrails.py"
if not MODULE.exists():
    MODULE = ROOT / "stage" / "aws_guardrails.py"
CONFIG = ROOT / "proposed-create-guardrail.json"
if not CONFIG.exists():
    CONFIG = ROOT / "config" / "aws-guardrail-event-proposal.json"
spec = importlib.util.spec_from_file_location("isolated_aws_guardrails", MODULE)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

ARN = "arn:aws:bedrock:us-east-1:123456789012:guardrail/example123"
POLICY = m.GuardrailSpec(ARN, "1", "a" * 64)
TEXT = "The retained ballot asks whether to continue COMBAT for ten years."

def approved(text=TEXT):
    return {"action": "NONE", "guardrailCoverage": {"textCharacters": {
        "guarded": len(text), "total": len(text)}},
        "usage": {"contentPolicyUnits": 1, "sensitiveInformationPolicyUnits": 1,
                  "topicPolicyUnits": 1, "contextualGroundingPolicyUnits": 0},
        "assessments": [{"contentPolicy": {"filters": [{"detected": False, "action": "NONE"}]},
            "sensitiveInformationPolicy": {"piiEntities": []},
            "topicPolicy": {"topics": [{"detected": False, "action": "NONE"}]}}]}

class Client:
    def __init__(self, response=None, exception=None, after=lambda: None):
        self.response = approved() if response is None else response
        self.exception, self.after, self.calls = exception, after, []
    def apply_guardrail(self, **kwargs):
        self.calls.append(kwargs)
        self.after()
        if self.exception:
            raise self.exception
        return deepcopy(self.response)

class Tests(unittest.TestCase):
    def gate(self, client=None, policy=POLICY, current=lambda: True, authorize=None):
        client = client or Client()
        calls = []
        g = m.BedrockGuardrailGate(policy, client, execution="synthetic", is_current=current,
                                  authorize_call=authorize or (lambda stage, n, binding: calls.append((stage, n, binding))))
        return g, client, calls

    def test_input_output_directions_and_guard_content(self):
        g,c,b = self.gate()
        for surface,direction in [("input","INPUT"),("text","OUTPUT"),("speech","OUTPUT")]:
            r=g.check(TEXT,surface=surface)
            self.assertEqual(r.status,"approved")
            self.assertEqual(c.calls[-1]["source"],direction)
            self.assertEqual(c.calls[-1]["content"],[{"text":{"text":TEXT,"qualifiers":["guard_content"]}}])
            self.assertEqual(c.calls[-1]["outputScope"],"FULL")
        self.assertEqual(g.attempts,3)
        self.assertEqual(len(b),3)

    def test_stage_reuse_does_not_retry(self):
        g,c,_=self.gate()
        self.assertEqual(g.check(TEXT,surface="text"),g.check(TEXT,surface="text"))
        self.assertEqual(len(c.calls),1)

    def test_changed_text_after_check_cannot_reuse_approval(self):
        g,c,_=self.gate()
        g.check(TEXT,surface="text")
        r=g.check(TEXT+" Vote yes.",surface="text")
        self.assertEqual((r.status,r.reason),("unavailable","surface_changed"))
        self.assertEqual(len(c.calls),1)

    def test_intervention_and_anonymization_never_return_replacement(self):
        g,_,_=self.gate(Client({'action':'GUARDRAIL_INTERVENED','outputs':[{'text':'AWS replacement'}],
                              'actionReason':'RAW_PRIVATE_REASON'}))
        r=g.check(TEXT,surface="text")
        self.assertEqual(r.status,"blocked")
        encoded=json.dumps(r.metadata())
        self.assertNotIn('replacement',encoded)
        self.assertNotIn('RAW_PRIVATE_REASON',encoded)

    def test_detect_only_finding_is_also_held(self):
        response=approved()
        response['assessments'][0]['topicPolicy']['topics'][0]={'detected':True,'action':'NONE'}
        g,_,_=self.gate(Client(response))
        self.assertEqual(g.check(TEXT,surface="text").status,"blocked")

    def test_sensitive_match_not_exported(self):
        response=approved()
        response['assessments'][0]['sensitiveInformationPolicy']['piiEntities']=[{
            'detected':True,'action':'ANONYMIZED','match':'SYNTHETIC_PRIVATE_MATCH'}]
        g,_,_=self.gate(Client(response))
        r=g.check(TEXT,surface="text")
        self.assertEqual(r.status,"blocked")
        self.assertNotIn('SYNTHETIC_PRIVATE_MATCH',json.dumps(r.metadata()))

    def test_blocked_attempt_keeps_available_numeric_usage(self):
        response=approved();response['action']='GUARDRAIL_INTERVENED'
        g,_,_=self.gate(Client(response))
        r=g.check(TEXT,surface='text')
        self.assertEqual(r.status,'blocked')
        self.assertEqual(r.metadata()['usage']['contentPolicyUnits'],1)

    def test_unknown_usage_key_is_not_exported(self):
        response=approved();response['usage']['PRIVATE_UNKNOWN_KEY']=1
        g,_,_=self.gate(Client(response))
        r=g.check(TEXT,surface='text')
        self.assertEqual(r.status,'unavailable')
        self.assertNotIn('PRIVATE_UNKNOWN_KEY',json.dumps(r.metadata()))

    def test_exception_no_retry_no_raw_error(self):
        for exception in [TimeoutError('PRIVATE'),PermissionError('PRIVATE'),RuntimeError('PRIVATE')]:
            with self.subTest(exception=type(exception).__name__):
                g,c,_=self.gate(Client(exception=exception))
                r=g.check(TEXT,surface="text")
                self.assertEqual((r.status,r.reason),("unavailable","provider_error"))
                self.assertEqual(r,g.check(TEXT,surface="text"))
                self.assertEqual(len(c.calls),1)
                self.assertNotIn('PRIVATE',json.dumps(r.metadata()))

    def test_partial_coverage_no_release(self):
        response=approved()
        response['guardrailCoverage']['textCharacters']['guarded']-=1
        g,_,_=self.gate(Client(response))
        self.assertEqual(g.check(TEXT,surface="text").reason,'incomplete_coverage')

    def test_too_small_complete_coverage_no_release(self):
        response=approved()
        response['guardrailCoverage']['textCharacters']={'guarded':1,'total':1}
        g,_,_=self.gate(Client(response))
        self.assertEqual(g.check(TEXT,surface="text").reason,'incomplete_coverage')

    def test_malformed_provider_shapes_fail_closed(self):
        responses=[{},[],{'action':'UNKNOWN'},approved()]
        responses[-1]['guardrailCoverage']['textCharacters']['guarded']=True
        for response in responses:
            with self.subTest(response=response):
                g,_,_=self.gate(Client(response))
                self.assertEqual(g.check(TEXT,surface="text").status,'unavailable')

    def test_missing_required_policy_usage_fails_closed(self):
        response=approved()
        response['usage']['topicPolicyUnits']=0
        g,_,_=self.gate(Client(response))
        self.assertEqual(g.check(TEXT,surface="text").reason,'required_policy_not_assessed')

    def test_empty_assessments_cannot_approve(self):
        response=approved();response['assessments']=[{}]
        g,_,_=self.gate(Client(response))
        self.assertEqual(g.check(TEXT,surface='text').reason,'required_policy_not_assessed')

    def test_false_authorization_return_cannot_call(self):
        g,c,_=self.gate(authorize=lambda s,n,binding:False)
        self.assertEqual(g.check(TEXT,surface='text').reason,'authorization_failed')
        self.assertEqual(len(c.calls),0)

    def test_actual_upload_binding_is_available_to_authorizer(self):
        import hashlib
        expected={
            'guardrailIdentifier':ARN,'guardrailVersion':'1','source':'OUTPUT','outputScope':'FULL',
            'content':[{'text':{'text':TEXT,'qualifiers':['guard_content']}}]}
        allowed=hashlib.sha256(json.dumps(expected,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        g,c,_=self.gate(authorize=lambda s,n,binding:binding==allowed)
        self.assertEqual(g.check(TEXT,surface='text').status,'approved')
        self.assertEqual(len(c.calls),1)
        g,c,_=self.gate(authorize=lambda s,n,binding:binding==allowed)
        self.assertEqual(g.check(TEXT+' changed',surface='text').status,'unavailable')
        self.assertEqual(len(c.calls),0)

    def test_topic_is_output_only(self):
        response=approved()
        response['usage']['topicPolicyUnits']=0
        g,_,_=self.gate(Client(response))
        self.assertEqual(g.check(TEXT,surface="input").status,'approved')

    def test_negative_boolean_and_non_numeric_usage_rejected(self):
        for value in [-1,True,'1']:
            response=approved()
            response['usage']['contentPolicyUnits']=value
            g,_,_=self.gate(Client(response))
            self.assertEqual(g.check(TEXT,surface="text").status,'unavailable')

    def test_cancel_before_call_no_work(self):
        g,c,b=self.gate(current=lambda:False)
        self.assertEqual(g.check(TEXT,surface='input').status,'cancelled')
        self.assertEqual((c.calls,b),([],[]))

    def test_cancel_during_call_and_reuse_hold(self):
        current=[True]
        g,c,_=self.gate(Client(after=lambda:current.__setitem__(0,False)),current=lambda:current[0])
        self.assertEqual(g.check(TEXT,surface='text').status,'cancelled')
        self.assertEqual(g.check(TEXT,surface='text').status,'cancelled')
        self.assertEqual(len(c.calls),1)

    def test_cancel_after_budget_before_provider_no_work(self):
        current=[True]
        g,c,_=self.gate(current=lambda:current[0],authorize=lambda s,n,binding:current.__setitem__(0,False))
        self.assertEqual(g.check(TEXT,surface='text').status,'cancelled')
        self.assertEqual((len(c.calls),g.attempts),(0,0))

    def test_authorization_failure_cannot_retry(self):
        def deny(s,n,binding): raise PermissionError('No live budget')
        g,c,_=self.gate(authorize=deny)
        self.assertEqual(g.check(TEXT,surface='text').reason,'authorization_failed')
        self.assertEqual(g.check(TEXT,surface='text').reason,'authorization_failed')
        self.assertEqual(len(c.calls),0)

    def test_authorization_error_does_not_expose_visitor_or_budget_details(self):
        def deny(s,n,binding): raise RuntimeError(TEXT+' private accounting')
        g,c,_=self.gate(authorize=deny)
        result=g.check(TEXT,surface='speech')
        self.assertEqual(result.status,'unavailable')
        self.assertNotIn(TEXT,json.dumps(result.metadata()))
        self.assertEqual((len(c.calls),g.attempts),(0,0))

    def test_unsupported_language_no_provider_call(self):
        g,c,_=self.gate()
        self.assertEqual(g.check(TEXT,surface='text',language='es').reason,'language_not_reviewed')
        self.assertEqual(len(c.calls),0)

    def test_content_bounds_do_not_truncate(self):
        for text in ['', ' ', 'a'*5001, None]:
            g,c,_=self.gate()
            self.assertEqual(g.check(text,surface='text').status,'unavailable')
            self.assertEqual(len(c.calls),0)

    def test_no_visitor_binding_or_output_in_metadata(self):
        g,_,_=self.gate()
        data=g.check(TEXT,surface='text').metadata()
        self.assertNotIn(TEXT,json.dumps(data))
        self.assertEqual(set(data),{'status','reason','surface','execution','guardrail_version',
                                   'configuration_sha256','guarded_characters','total_characters','usage'})
        self.assertNotIn('public_display',data)
        self.assertNotIn('source_support',data)

    def test_wrong_guardrail_response_binding_rejected(self):
        response=approved()
        response['assessments'][0]['appliedGuardrailDetails']={'guardrailArn':ARN,'guardrailVersion':'2'}
        g,_,_=self.gate(Client(response))
        self.assertEqual(g.check(TEXT,surface='text').status,'unavailable')

    def test_unreviewed_automated_reasoning_not_silent_pass(self):
        response=approved()
        response['assessments'][0]['automatedReasoningPolicy']={'findings':[]}
        g,_,_=self.gate(Client(response))
        self.assertEqual(g.check(TEXT,surface='text').status,'unavailable')

    def test_grounding_requires_source_query_and_output_only(self):
        policy=replace(POLICY,grounding_required=True)
        response=approved();response['usage']['contextualGroundingPolicyUnits']=1
        response['assessments'][0]['contextualGroundingPolicy']={'filters':[{
            'type':'GROUNDING','detected':False,'action':'NONE','score':0.9,'threshold':0.8}]}
        g,c,_=self.gate(Client(response),policy=policy)
        self.assertEqual(g.check(TEXT,surface='text').reason,'grounding_context_missing_or_invalid')
        ctx=m.GroundingContext('What duration is printed?',TEXT)
        self.assertEqual(g.check(TEXT,surface='input',grounding=ctx).reason,'grounding_not_input_policy')
        self.assertEqual(g.check(TEXT,surface='text',grounding=ctx).status,'approved')
        self.assertEqual([x['text']['qualifiers'] for x in c.calls[-1]['content']],
                         [['grounding_source'],['query'],['guard_content']])

    def test_grounding_not_configured_is_not_fake_check(self):
        g,c,_=self.gate()
        self.assertEqual(g.check(TEXT,surface='text',grounding=m.GroundingContext('Q','S')).reason,
                         'grounding_not_configured')
        self.assertEqual(len(c.calls),0)

    def test_grounding_query_bound_no_truncation(self):
        g,c,_=self.gate(policy=replace(POLICY,grounding_required=True))
        r=g.check(TEXT,surface='text',grounding=m.GroundingContext('a'*1001,'source'))
        self.assertEqual(r.status,'unavailable');self.assertEqual(len(c.calls),0)

    def test_draft_and_cross_scope_specs_rejected(self):
        for changes in [{'version':'DRAFT'},{'identifier':'example123'},{'region':'us-west-2'},
                        {'account':'000000000000'},{'configuration_sha256':'bad'},{'language':'es'}]:
            with self.assertRaises(ValueError):replace(POLICY,**changes)

    def test_live_factory_default_does_not_load_credentials(self):
        with self.assertRaisesRegex(ValueError,'not been verified'):
            m.build_live_gate(POLICY,is_current=lambda:True,authorize_call=lambda s,n,binding:None)

    def test_proposed_config_no_broad_civic_or_identity_filter(self):
        config=json.loads(CONFIG.read_text())
        topic=config['topicPolicyConfig']['topicsConfig'][0]
        self.assertFalse(topic['inputEnabled']);self.assertTrue(topic['outputEnabled'])
        self.assertLessEqual(len(topic['definition']),200)
        self.assertEqual(config['contentPolicyConfig']['tierConfig']['tierName'],'CLASSIC')
        self.assertNotIn('crossRegionConfig',config)
        entities={x['type'] for x in config['sensitiveInformationPolicyConfig']['piiEntitiesConfig']}
        self.assertFalse(entities & {'NAME','URL','ADDRESS'})

if __name__=='__main__':unittest.main()
