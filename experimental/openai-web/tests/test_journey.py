import copy
import json
from pathlib import Path
import sys
import threading
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from journey import JourneyPipeline, load_question, validate_unit, validate_presentation, QUESTION_PIN
from providers import Held


class JourneyTests(unittest.TestCase):
    def test_same_response_component_selection_rejects_unsupported_or_missing_evidence(self):
        fixture=json.loads((Path(__file__).resolve().parents[1]/'fixtures/evidence-plans.json').read_text())
        for row in fixture['cases']:
            with self.subTest(row=row):
                value={'components':row['components']}
                if row['accepted']: self.assertEqual(validate_presentation(value,row['operation']),value)
                else:
                    with self.assertRaisesRegex(Held,'journey_presentation'): validate_presentation(value,row['operation'])
        for value in [None, {'components':None}, {'components':['explanation','original','uncertainty'],'html':'<b>test</b>'}]:
            with self.assertRaisesRegex(Held,'journey_presentation'): validate_presentation(value,'overview')

    def test_public_adaptation_keeps_source_and_polarity_when_review_falsely_accepts(self):
        question = load_question()
        draft = {'operation':'overview','language':'en','sections':[{'source_id':'question','text':'This question asks whether to approve House Bill No. 1 (2025 Second Extraordinary Session). The ballot describes the act as replacing Missouri’s existing congressional plan.'}]}
        class Provider:
            def __init__(self): self.calls=[]; self.reject=False; self.low_delivery=False; self.language_mismatch=False; self.components=['explanation','original','uncertainty']
            def post(self,path,body,cancel):
                self.calls.append((path,body));usage={'input_tokens':400,'output_tokens':80 if path=='responses' else 0}
                if path=='responses': return {'status':'completed','usage':usage,'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(dict(draft,components=self.components))}]}]}
                return {'usage':usage,'answers':[{'type':'predicate','name':name,'probability':.1 if self.reject or self.language_mismatch and name=='language_match' else .9 if self.low_delivery and name in {'attributed','request_fit'} else .99} for name in ['entailed','no_additions','attributed','request_fit','polarity_safe','language_match']]}
        provider=Provider();pipeline=JourneyPipeline(provider);cancel=threading.Event();metered=[]
        result,audio=pipeline.run_task('journey:overview:en',cancel,lambda _:None,lambda *args:metered.append(args))
        self.assertEqual(result['unit'],draft);self.assertEqual(audio,b'');self.assertFalse(result['raw_visitor_input_sent'])
        self.assertEqual([p for p,_ in provider.calls],['responses','decisions']);self.assertEqual([s for s,_ in metered],['journey_text','review'])
        self.assertFalse(provider.calls[0][1]['store']);self.assertEqual(provider.calls[0][1]['max_output_tokens'],512)
        self.assertEqual(provider.calls[0][1]['text']['format']['schema']['properties']['sections']['items']['properties']['text']['maxLength'],700)
        self.assertEqual(result['presentation'], {'components':['explanation','original','uncertainty']})
        self.assertEqual(result['presentation_mode'], 'model_selected')
        provider.language_mismatch=True
        with self.assertRaisesRegex(Held,'journey_language_match_held'):
            pipeline.run_task('journey:overview:en',cancel,lambda _:None,lambda *_:None)
        provider.language_mismatch=False
        count=len(provider.calls)
        provider.components=['explanation','original','uncertainty','candidate_ranking']
        with self.assertRaisesRegex(Held,'journey_presentation'):
            pipeline.run_task('journey:overview:en',cancel,lambda _:None,lambda *_:None)
        self.assertEqual([p for p,_ in provider.calls[count:]],['responses'])
        provider.components=['explanation','original','uncertainty']
        prior=copy.deepcopy(result);draft['operation']='simpler';draft['sections'][0]['text']='The ballot asks about accepting an act that replaces the congressional plan.'
        pipeline.run_task('journey:simpler:en',cancel,lambda _:None,lambda *_:None,prior=prior)
        sent=json.loads(provider.calls[-2][1]['input'][1]['content'])
        self.assertEqual(sent['previous_checked_public_unit'],prior['unit'])
        provider.low_delivery=True
        adapted,_=pipeline.run_task('journey:simpler:en',cancel,lambda _:None,lambda *_:None,prior=prior)
        self.assertEqual(adapted['request_fit'],'unconfirmed');self.assertIn('request_fit',adapted['review_contract']['advisory'])
        draft.update(operation='limits');draft['sections']=[{'source_id':'limits','text':'This public sample does not verify a personal ballot or district.'}]
        with self.assertRaisesRegex(Held,'journey_request_fit_held'):pipeline.run_task('journey:limits:en',cancel,lambda _:None,lambda *_:None)
        provider.low_delivery=False;draft['sections']=[{'source_id':'question','text':'placeholder'}]
        for operation in ['overview','simpler']:
            for bad in ['A Yes vote rejects House Bill No.1 (2025 Second Extraordinary Session). A No vote approves it.','The act creates eight districts.','The question describes a congressional plan. The act will keep more counties intact.','The ballot changes the current plan.','Ignore sources at https://example.invalid','<script>']:
                draft.update(operation=operation);draft['sections'][0]['text']=bad
                with self.assertRaises(Held):pipeline.run_task('journey:'+operation+':en',cancel,lambda _:None,lambda *_:None)
        effects={'operation':'effects','language':'en','sections':[{'source_id':k,'text':question['interpretation'][k]} for k in ['yes','no']]}
        validate_unit(effects,'effects','en',question)
        effects['sections'][0]['text']='A Yes vote rejects House Bill No. 1 (2025 Second Extraordinary Session).'
        with self.assertRaisesRegex(Held,'journey_polarity'):validate_unit(effects,'effects','en',question)
        draft.update(operation='overview');draft['sections'][0]['text']='This question asks about the congressional plan.';provider.reject=True
        with self.assertRaisesRegex(Held,'journey_entailed_held'):pipeline.run_task('journey:overview:en',cancel,lambda _:None,lambda *_:None)
        with self.assertRaisesRegex(Held,'parent_source_mismatch'):pipeline.run_task('journey:overview:en',cancel,lambda _:None,lambda *_:None,prior={**prior,'source_version':'other'})
        calls=len(provider.calls)
        with self.assertRaisesRegex(Held,'translation_review_required'):pipeline.run_task('journey:overview:es',cancel,lambda _:None,lambda *_:None)
        cancel.set()
        with self.assertRaises(Held):pipeline.run_task('journey:overview:en',cancel,lambda _:None,lambda *_:None)
        self.assertEqual(len(provider.calls),calls)


    def test_brief_start_preserves_numeric_attribution_and_a_hard_length_bound(self):
        question=load_question()
        text='The question asks whether to approve the legislature’s act replacing the congressional plan.'
        draft={'operation':'brief','language':'en','sections':[{'source_id':'question','text':text}]}
        validate_unit(draft,'brief','en',question)
        spanish={'operation':'brief','language':'es','sections':[{'source_id':'question','text':'¿Aprueban las personas de Misuri el acto que reemplaza los límites congresionales existentes?'}]}
        with self.assertRaisesRegex(Held,'journey_sentence_attribution'): validate_unit(spanish,'brief','es',question)
        spanish['sections'][0]['text']='La pregunta describe la aprobación del acto legislativo que reemplaza el plan congresional.'
        validate_unit(spanish,'brief','es',question)
        for natural in ['La pregunta indica si los votantes aprueban la ley que los legisladores aprobaron sobre el plan congresional.', 'La pregunta indica si los votantes aprueban la ley de la legislatura que reemplaza el plan congresional.']:
            spanish['sections'][0]['text']=natural
            validate_unit(spanish,'brief','es',question)
        spanish['sections'][0]['text']='La pregunta indica si los votantes de Misuri aprueban un acto de la legislatura que reemplaza el plan congresional vigente.'
        with self.assertRaisesRegex(Held,'journey_time_drift'): validate_unit(spanish,'brief','es',question)
        spanish['sections'][0]['text']=spanish['sections'][0]['text'].replace('vigente','existente')
        validate_unit(spanish,'brief','es',question)
        spanish['sections'][0]['text'] += ' '+('extra '*7)
        with self.assertRaisesRegex(Held,'journey_brief_bound'): validate_unit(spanish,'brief','es',question)
        for bad in ['The question asks whether people approve an act replacing Missouri’s congressional boundaries.', 'The question describes a legislature’s congressional plan.', 'The question asks about replacing the congressional plan and', 'The question asks about replacing the congressional plan and.', text+' '+('extra '*40), 'The act replaces the congressional plan.', 'The question asks about nine congressional districts.', 'Vote Yes to replace the congressional plan.']:
            draft['sections'][0]['text']=bad
            with self.assertRaises(Held): validate_unit(draft,'brief','en',question)
