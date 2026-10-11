"""Authored offline routing/contract controls; no model or network inference."""
from copy import deepcopy
import json
import math
import threading
import unittest

from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.session_control import SessionCancelled, operation
from open_oracle.triage import (ContractFailure, ClassificationRefused, DecisionsTriage,
    GUARDS, INTENTS, VIEWS, MODEL, TriagedEngine, LocalCommandRequired,
    questions, ranking_questions, parse_decision, policy_hash, ranked_selector, routed_view)
from open_oracle.view_plan import validate_view_plan

CANARY = "PRIVATE-QUESTION-PAYLOAD-PROVIDER-ID-CANARY"
AMBIGUOUS = "COMBAT: please unpack this confusing sentence."


def choice_answer(question, chosen, confidence=0.95):
    choices = question['choices']
    return {'type': 'choice', 'name': question['name'], 'choice': chosen,
            'confidence': confidence,
            'probabilities': [{'value': item['value'],
                'probability': 0.95 if item['value'] == chosen else 0.05/(len(choices)-1)} for item in choices]}


def verdict(intent='measure_explanation', view='measure_parts', **guards):
    asked = questions()
    return {'model': MODEL, 'answers': [choice_answer(asked[0], intent),
        *[{'type': 'predicate', 'name': k, 'probability': guards.get(k, 0.02)} for k in GUARDS],
        choice_answer(asked[-1], view)],
        'usage': {'input_tokens': 410, 'output_tokens': 0, 'total_tokens': 410}}


class Recorder:
    def __init__(self, reply):
        self.reply, self.calls = reply, []
    def __call__(self, resource, payload):
        self.calls.append((resource, payload))
        if isinstance(self.reply, Exception): raise self.reply
        return deepcopy(self.reply)


class Counting:
    def __init__(self, corpus):
        self.inner, self.calls, self.args = EvidenceLoop(corpus), 0, []
        self.selector = lambda *args: ([], [])  # Identity must not change.
    def answer(self, *args):
        self.calls += 1
        self.args.append(deepcopy(args))
        return self.inner.answer(*args)


class TriageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.corpus = Corpus()
    def wrapped(self, reply=None):
        transport, engine = Recorder(reply if reply is not None else verdict()), Counting(self.corpus)
        return TriagedEngine(engine, DecisionsTriage(transport), self.corpus), engine, transport

    def test_single_bundle_native_choice_options(self):
        triaged, engine, transport = self.wrapped()
        result = triaged.answer(AMBIGUOUS, {}, 'r1')
        self.assertEqual(len(transport.calls), 1)
        resource, payload = transport.calls[0]
        self.assertEqual((resource, payload['model']), ('decisions', MODEL))
        self.assertEqual([q['name'] for q in payload['questions']], ['intent', *GUARDS, 'view'])
        self.assertEqual([c['value'] for c in payload['questions'][0]['choices']], list(INTENTS))
        self.assertTrue(all(set(c) == {'value','description'} for q in (payload['questions'][0],payload['questions'][-1]) for c in q['choices']))
        self.assertEqual(json.loads(payload['input'])['visitor_request'], AMBIGUOUS)
        self.assertEqual((engine.calls,result['triage']['classifier_attempts'],result['triage']['ranking_attempts']), (1,1,0))
        self.assertEqual(result['triage']['usage_status'], 'reported')

    def test_explicit_fallback_option_and_policy_hash(self):
        self.assertIn('other', INTENTS)
        self.assertEqual(len(policy_hash()), 64)
        self.assertEqual(policy_hash(), policy_hash())
        self.assertTrue(all('untrusted data' in q['instructions'] for q in questions()))
        names = [q['name'] for q in questions()]
        self.assertEqual(len(names),len(set(names)))

    def test_known_guards_and_intents_use_no_classifier(self):
        for q in ('Who should I vote for?', 'Where is my polling place?', 'What is on my ballot?',
                  'Explain COMBAT', 'Show the original COMBAT wording.', 'Show Missouri Amendment 3', 'Explain COMBAT in 2024', 'Who is a declared candidate?'):
            with self.subTest(q=q):
                triaged, engine, transport = self.wrapped()
                result = triaged.answer(q, {}, 'known')
                self.assertEqual((transport.calls,engine.calls),([],1))
                self.assertEqual(result['triage']['classifier_attempts'],0)
                self.assertTrue(result['triage']['engine_invoked'])

    def test_scope_and_identity_preserved_no_optional_call_on_conflict(self):
        for scope, ident in (({'authority':'unknown-authority'},None),
                             ({'authority':'KCEB','municipality':'Blue Springs'},None),
                             ({'election_date':'2024-11-05'},None), ({},'blue-springs'), ({},'not-a-contest')):
            triaged, engine, transport = self.wrapped()
            result=triaged.answer(AMBIGUOUS,scope,'scope',ident)
            self.assertEqual(transport.calls,[])
            self.assertEqual(engine.args[0],(AMBIGUOUS,scope,'scope',ident))
            self.assertNotEqual(result.get('triage',{}).get('route'),'personal_ballot')

    def test_multi_part_tail_is_not_truncated_or_replaced(self):
        q='COMBAT: what is the rate and duration, and will crime fall by half?'
        triaged,engine,transport=self.wrapped(verdict('logistics',asks_personal_eligibility=0.99))
        result=triaged.answer(q,{},'parts','combat')
        self.assertEqual((transport.calls,engine.args[0]),([],(q,{},'parts','combat')))
        self.assertEqual(result['triage']['reason'],'multipart_preserved')

    def test_classifier_multipart_does_not_apply_view_or_skip_engine(self):
        triaged,engine,_=self.wrapped(verdict(view='measure_rate',multiple_parts=0.99))
        result=triaged.answer(AMBIGUOUS,{},'multi')
        self.assertEqual(engine.calls,1)
        self.assertFalse(result['triage']['view']['applied'])

    def test_no_winning_intent_rewrites_original_or_bypasses_release(self):
        for intent,guards in [('vote_advice',{'asks_vote_recommendation':0.99}),
                              ('logistics',{}),('personal_ballot',{'asks_personal_eligibility':0.99}),
                              ('off_topic',{}),('other',{}),('measure_explanation',{'embedded_instructions':0.99})]:
            triaged,engine,_=self.wrapped(verdict(intent,**guards))
            response=triaged.answer(AMBIGUOUS,{},'never-rewrite','combat')
            baseline=engine.inner.answer(AMBIGUOUS,{},'never-rewrite','combat')
            self.assertEqual(engine.args[0],(AMBIGUOUS,{},'never-rewrite','combat'))
            for key in ('status','answer','evidence','card','review','fact_validation','view_plan'):
                self.assertEqual(response[key],baseline[key])

    def test_classifier_unknown_or_failed_shapes_fall_back_once(self):
        bads=[]
        r=verdict();r['answers'].pop();bads.append(r)
        r=verdict();r['answers'][0]['type']='score';bads.append(r)
        r=verdict();r['answers'][0]['name']='view';bads.append(r)
        r=verdict();r['answers'][0]['choice']='private-invented-category';bads.append(r)
        r=verdict();r['model']='unknown';bads.append(r)
        r=verdict();r['answers'][1]['probability']=math.nan;bads.append(r)
        r=verdict();r['answers'][0]={'type':'refusal','name':'intent'};bads.append(r)
        bads += [TimeoutError(CANARY), RuntimeError(CANARY), {'answers':'x'},None]
        for reply in bads:
            transport,engine=Recorder(reply),Counting(self.corpus)
            response=TriagedEngine(engine,DecisionsTriage(transport),self.corpus).answer(AMBIGUOUS,{},'bad')
            self.assertEqual((len(transport.calls),engine.calls,response['triage']['status']),(1,1,'unavailable'))
            self.assertNotIn(CANARY,json.dumps(response['triage']))
            self.assertIn(response['triage']['error_category'],('refused','malformed','timeout','transport_error'))
            self.assertNotIn('intent',response['triage'])

    def test_usage_unknown_on_transport_error_never_fabricated_zero(self):
        triaged,_,_=self.wrapped(TimeoutError(CANARY))
        meta=triaged.answer(AMBIGUOUS)['triage']
        self.assertEqual((meta['usage'],meta['usage_status'],meta['classifier_attempts']),({},'unknown',1))

    def test_choice_missing_or_invalid_distribution_is_rejected(self):
        question=questions()[0]
        for mutation in ('missing','duplicate','unknown','bool','nan','mass','confidence','no-confidence'):
            answer=choice_answer(question,'measure_explanation')
            if mutation=='missing': answer['probabilities'].pop()
            if mutation=='duplicate': answer['probabilities'][1]=deepcopy(answer['probabilities'][0])
            if mutation=='unknown': answer['probabilities'][1]['value']='unknown'
            if mutation=='bool': answer['probabilities'][0]['value']=True
            if mutation=='nan': answer['probabilities'][0]['probability']=math.nan
            if mutation=='mass': answer['probabilities'][0]['probability']=0.1
            if mutation=='confidence': answer['confidence']=1.01
            if mutation=='no-confidence': answer.pop('confidence')
            with self.subTest(mutation=mutation),self.assertRaises(ContractFailure): parse_decision(question,answer)

    def test_typed_boolean_choices_and_permuted_distribution(self):
        q={'type':'choice','name':'typed','choices':[{'value':True},{'value':'true'}]}
        answer={'type':'choice','name':'typed','choice':True,'confidence':0.91,
                'probabilities':[{'value':'true','probability':0.1},{'value':True,'probability':0.9}]}
        self.assertIs(parse_decision(q,answer)['value'],True)
        answer['choice']=1
        with self.assertRaises(ContractFailure):parse_decision(q,answer)

    def test_refusal_is_distinct_from_probability_zero(self):
        q=questions()[1]
        self.assertEqual(parse_decision(q,{'type':'predicate','name':q['name'],'probability':0})['value'],0)
        with self.assertRaises(ClassificationRefused):parse_decision(q,{'type':'refusal','name':q['name']})

    def test_score_levels_are_native_objects_and_fractional_expected_score(self):
        q=ranking_questions(1)[0]
        self.assertTrue(all(set(level)=={'label'} for level in q['levels']))
        answer={'type':'score','name':'p0','score':1.1,'confidence':0.55,
                'probabilities':[{'value':i,'label':q['levels'][i]['label'],'probability':p} for i,p in enumerate((0.1,0.7,0.2,0))]}
        self.assertEqual(parse_decision(q,answer)['value'],1.1)
        for mutation in ('bool','label','nan','expected','missing'):
            bad=deepcopy(answer)
            if mutation=='bool':bad['probabilities'][0]['value']=True
            if mutation=='label':bad['probabilities'][0]['label']='invented'
            if mutation=='nan':bad['score']=math.nan
            if mutation=='expected':bad['score']=2.2
            if mutation=='missing':bad['probabilities'].pop()
            with self.subTest(mutation=mutation),self.assertRaises(ContractFailure):parse_decision(q,bad)

    def test_rank_and_selector_compatibility_keep_every_passage_no_calls(self):
        transport=Recorder(RuntimeError('must not run'))
        triage=DecisionsTriage(transport)
        passages=[{'id':str(i),'text':'synthetic'} for i in range(20)]
        selected,meta=triage.rank('multi',passages)
        self.assertEqual((selected,meta['kept'],meta['ranking_attempts'],transport.calls),(passages,20,0,[]))
        selector=lambda *args:None
        self.assertIs(ranked_selector(selector,triage),selector)
        engine=Counting(self.corpus)
        original=engine.selector
        TriagedEngine(engine,triage,self.corpus)
        self.assertIs(engine.selector,original)

    def test_view_focus_uses_validated_catalog_and_only_accepted_facets(self):
        triaged,_,_=self.wrapped(verdict(view='measure_rate'))
        response=triaged.answer(AMBIGUOUS,{},'focus')
        self.assertTrue(response['triage']['view']['applied'])
        self.assertEqual(response['view_plan']['facet_keys'],['rate'])
        self.assertTrue(validate_view_plan(response['view_plan'],response))

    def test_uncertainty_abstains_from_view_at_full_precision(self):
        for confidence in (0.799999,0.2):
            raw=verdict(view='measure_rate');raw['answers'][-1]['confidence']=confidence
            triaged,_,_=self.wrapped(raw)
            self.assertFalse(triaged.answer(AMBIGUOUS)['triage']['view']['applied'])
        raw=verdict(view='measure_rate');probs=raw['answers'][-1]['probabilities']
        for p in probs:p['probability']=0.799999 if p['value']=='measure_rate' else (1-0.799999)/(len(probs)-1)
        triaged,_,_=self.wrapped(raw)
        self.assertFalse(triaged.answer(AMBIGUOUS)['triage']['view']['applied'])

    def test_multipart_requested_parts_and_generic_measure_keep_original_view(self):
        baseline=EvidenceLoop(self.corpus).answer('Explain COMBAT',{},'view')
        for mutation in ('question','parts','sections','bad-plan','no-facets','wrong-request','bad-choice','held-review'):
            response=deepcopy(baseline);question=''
            if mutation=='question':question='rate and duration?'
            if mutation=='parts':response['requested_parts']=['rate','duration','prediction']
            if mutation=='sections':response['card']['sections']=[{}]
            if mutation=='bad-plan':response['view_plan']['evidence_ids']=['unbound']
            if mutation=='no-facets':response['card']['facets']=[]
            if mutation=='wrong-request':response['request_id']='stale'
            if mutation=='held-review':response.update(mode='live_strands',review={'status':'rejected'})
            before=deepcopy(response)
            self.assertFalse(routed_view([] if mutation=='bad-choice' else 'measure_rate',response,question))
            self.assertEqual(response,before)
        generic=EvidenceLoop(self.corpus).answer('Explain Missouri Amendment 3',{},'generic')
        before=deepcopy(generic)
        self.assertFalse(routed_view('measure_rate',generic))
        self.assertEqual(generic,before)

    def test_routing_cannot_change_released_text_sources_review_or_speech(self):
        triaged,engine,_=self.wrapped(verdict(view='measure_rate'))
        response=triaged.answer(AMBIGUOUS,{},'unchanged')
        baseline=engine.inner.answer(AMBIGUOUS,{},'unchanged')
        for key in ('answer','evidence','card','review','fact_validation','speech','source_fallback','contest','scope'):
            self.assertEqual(response.get(key),baseline.get(key))

    def test_receipt_projects_only_trusted_enums_and_numbers(self):
        raw=verdict();raw['provider_id']=CANARY;raw['usage'].update(input_tokens=-1,extra=CANARY)
        raw['answers'][0]['probabilities'][0]['payload']=CANARY
        raw['answers'][-1]['probabilities'][0]['provider_id']=CANARY
        triaged,_,_=self.wrapped(raw)
        q=AMBIGUOUS+CANARY
        meta=triaged.answer(q,{},'private')['triage']
        self.assertNotIn(CANARY,json.dumps(meta))
        self.assertNotIn('input_tokens',meta['usage'])
        self.assertNotIn('error_type',meta)

    def test_no_raw_exception_class_names(self):
        private_type=type(CANARY,(RuntimeError,),{})
        triaged,_,_=self.wrapped(private_type(CANARY))
        self.assertNotIn(CANARY,json.dumps(triaged.answer(AMBIGUOUS)['triage']))

    def test_default_transport_is_unverified_not_real_inference(self):
        self.assertEqual(DecisionsTriage().execution,'unverified_provider')

    def test_local_commands_require_app_handler_without_any_provider(self):
        for question in ('Privacy','How my data is used','What does this guide record or send?','Erase this session','borra esta sesión'):
            triaged,engine,transport=self.wrapped()
            with self.assertRaises(LocalCommandRequired):triaged.answer(question)
            self.assertEqual((engine.calls,transport.calls),(0,[]))

    def test_long_input_never_silently_truncates_classifier(self):
        transport=Recorder(verdict())
        meta=DecisionsTriage(transport).classify('x'*2001)
        self.assertEqual((meta['status'],meta['classifier_attempts'],transport.calls),('unavailable',0,[]))
        self.assertEqual(meta['error_category'],'malformed')

    def test_pre_cancel_stops_before_classifier_and_engine(self):
        signal=threading.Event();signal.set()
        triaged,engine,transport=self.wrapped()
        with self.assertRaises(SessionCancelled),operation(signal):triaged.answer(AMBIGUOUS)
        self.assertEqual((engine.calls,transport.calls),(0,[]))

    def test_cancel_during_classification_never_falls_back(self):
        signal=threading.Event();engine=Counting(self.corpus)
        def transport(*args):signal.set();return verdict()
        with self.assertRaises(SessionCancelled),operation(signal):
            TriagedEngine(engine,DecisionsTriage(transport),self.corpus).answer(AMBIGUOUS)
        self.assertEqual(engine.calls,0)

    def test_transport_cancel_exception_propagates(self):
        triaged,engine,_=self.wrapped(SessionCancelled(CANARY))
        with self.assertRaises(SessionCancelled):triaged.answer(AMBIGUOUS)
        self.assertEqual(engine.calls,0)

    def test_cancel_during_engine_never_attaches_or_returns_late_view(self):
        signal=threading.Event()
        class Cancelling(Counting):
            def answer(self,*args):
                response=super().answer(*args);signal.set();return response
        engine=Cancelling(self.corpus)
        with self.assertRaises(SessionCancelled),operation(signal):
            TriagedEngine(engine,DecisionsTriage(Recorder(verdict())),self.corpus).answer(AMBIGUOUS)
        self.assertEqual(engine.calls,1)

    def test_observer_keeps_failed_cancelled_attempt_counts_without_payload(self):
        for reply in (verdict(), TimeoutError(CANARY), SessionCancelled(CANARY)):
            events=[]
            triage=DecisionsTriage(Recorder(reply),observer=events.append)
            try:triage.classify(AMBIGUOUS+CANARY)
            except SessionCancelled:pass
            self.assertEqual(sum(event['attempt_delta'] for event in events),1)
            self.assertEqual(len(events),2)
            self.assertEqual(events[0]['status'],'started')
            self.assertNotIn(CANARY,json.dumps(events))
            self.assertNotIn('error_type',json.dumps(events))

    def test_observer_failure_does_not_retry_or_bypass_engine(self):
        def observer(event):raise RuntimeError(CANARY)
        transport=Recorder(verdict());engine=Counting(self.corpus)
        result=TriagedEngine(engine,DecisionsTriage(transport,observer),self.corpus).answer(AMBIGUOUS)
        self.assertEqual((len(transport.calls),engine.calls,result['status']),(1,1,'answered'))

    def test_no_source_history_or_visitor_hash_in_policy_fingerprint(self):
        triaged,_,_=self.wrapped()
        a=triaged.answer(AMBIGUOUS,{},'request-A')['triage']
        b=triaged.answer(AMBIGUOUS+CANARY,{},'request-B')['triage']
        self.assertEqual(a['policy_sha256'],b['policy_sha256'])
        self.assertNotIn('request-B',json.dumps(b))

    def test_fixed_guard_and_uncertainty_reasons_are_advisory_not_approval(self):
        triaged,engine,_=self.wrapped(verdict('vote_advice',asks_vote_recommendation=0.99))
        result=triaged.answer(AMBIGUOUS)
        self.assertEqual(result['triage']['advisory_guardrail_reasons'],['asks_vote_recommendation'])
        self.assertEqual(result['triage']['routing_fallback_reason'],'guard_advisory')
        self.assertEqual(engine.calls,1)
        raw=verdict(view='measure_rate');raw['answers'][-1]['confidence']=0.79999
        triaged,_,_=self.wrapped(raw)
        self.assertEqual(triaged.answer(AMBIGUOUS)['triage']['routing_fallback_reason'],'low_confidence')

    def test_mandatory_engine_review_failure_remains_held_despite_high_classifier(self):
        class HeldReviewer:
            def review(self,envelope):return {'status':'rejected','execution':'offline_stub'}
        engine=EvidenceLoop(self.corpus,reviewer=HeldReviewer())
        result=TriagedEngine(engine,DecisionsTriage(Recorder(verdict(view='measure_rate'))),self.corpus).answer(AMBIGUOUS)
        self.assertEqual(result['status'],'unavailable')
        self.assertIsNone(result['card'])
        self.assertEqual(result['evidence'],[])
        self.assertFalse(result['triage']['view']['applied'])
        self.assertNotIn('speech',result)

    def test_actual_installed_sdk_serializes_native_text_choice_score_offline(self):
        import httpx2
        from openai import OpenAI
        captured=[]
        score=ranking_questions(1)[0]
        score_answer={'type':'score','name':'p0','score':1.1,'confidence':0.55,
            'probabilities':[{'value':i,'label':score['levels'][i]['label'],'probability':p} for i,p in enumerate((0.1,0.7,0.2,0))]}
        raw=verdict();raw['answers'].append(score_answer)
        raw['usage'].update(input_tokens_details={'cache_write_tokens':0,'cached_tokens':0},
                            output_tokens_details={'reasoning_tokens':0})
        def mock(request):
            captured.append((request.method,str(request.url),json.loads(request.content)))
            return httpx2.Response(200,json=raw,request=request)
        with httpx2.Client(transport=httpx2.MockTransport(mock)) as http:
            client=OpenAI(api_key='synthetic-offline-not-a-credential',base_url='https://offline.invalid/v1',http_client=http,max_retries=0)
            result=client.decisions.create(model=MODEL,input='Synthetic public wording',questions=questions()+[score]).model_dump()
        self.assertEqual((len(captured),captured[0][0],captured[0][1]),(1,'POST','https://offline.invalid/v1/decisions'))
        self.assertEqual(captured[0][2]['questions'][-1]['levels'],score['levels'])
        self.assertEqual(result['model'],MODEL)
        for q,a in zip(questions()+[score],result['answers']):parse_decision(q,a)


if __name__=='__main__':unittest.main()
