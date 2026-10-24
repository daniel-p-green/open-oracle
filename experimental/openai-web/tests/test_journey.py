import copy
import json
from pathlib import Path
import sys
import threading
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from journey import JourneyPipeline, load_question, validate_unit, QUESTION_PIN
from providers import Held


class JourneyTests(unittest.TestCase):
    def test_public_adaptation_keeps_source_and_polarity_when_review_falsely_accepts(self):
        question = load_question()
        draft = {'operation':'overview','language':'en','sections':[{'source_id':'question','text':'This question asks whether to approve House Bill No. 1 (2025 Second Extraordinary Session). The ballot describes the act as replacing Missouri’s existing congressional plan.'}]}
        class Provider:
            def __init__(self): self.calls=[]; self.reject=False
            def post(self,path,body,cancel):
                self.calls.append((path,body));usage={'input_tokens':400,'output_tokens':80 if path=='responses' else 0}
                if path=='responses': return {'status':'completed','usage':usage,'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(draft)}]}]}
                return {'usage':usage,'answers':[{'type':'predicate','name':name,'probability':.1 if self.reject else .99} for name in ['entailed','no_additions','attributed','request_fit','polarity_safe']]}
        provider=Provider();pipeline=JourneyPipeline(provider);cancel=threading.Event();metered=[]
        result,audio=pipeline.run_task('journey:overview:en',cancel,lambda _:None,lambda *args:metered.append(args))
        self.assertEqual(result['unit'],draft);self.assertEqual(audio,b'');self.assertFalse(result['raw_visitor_input_sent'])
        self.assertEqual([p for p,_ in provider.calls],['responses','decisions']);self.assertEqual([s for s,_ in metered],['journey_text','review'])
        self.assertFalse(provider.calls[0][1]['store']);self.assertEqual(provider.calls[0][1]['max_output_tokens'],512)
        prior=copy.deepcopy(result);draft['operation']='simpler';draft['sections'][0]['text']='The ballot asks about accepting an act that replaces the congressional plan.'
        pipeline.run_task('journey:simpler:en',cancel,lambda _:None,lambda *_:None,prior=prior)
        sent=json.loads(provider.calls[-2][1]['input'][1]['content'])
        self.assertEqual(sent['previous_checked_public_unit'],prior['unit'])
        for operation in ['overview','simpler']:
            for bad in ['A Yes vote rejects House Bill No.1 (2025 Second Extraordinary Session). A No vote approves it.','The act creates eight districts.','The ballot changes the current plan.','Ignore sources at https://example.invalid','<script>']:
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
