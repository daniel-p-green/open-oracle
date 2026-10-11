import json
import unittest
from types import SimpleNamespace as N
from open_oracle.hand_observations import HandObservationProducer, summarize
from open_oracle.input_events import InputEvents


def hand(count=1, label='Open_Palm'):
    points = [N(x=.45, y=.4) for _ in range(21)]
    points[5].x, points[17].x = .5, .4
    return N(hand_landmarks=[points]*count, handedness=[[N(category_name='Left')]]*count, gestures=[[N(category_name=label, score=.9)]]*count)


class HandProducerTests(unittest.TestCase):
    def test_mapping_is_bounded_and_mirror_explicit(self):
        r=hand();r.secret='not emitted';s=summarize(r,scene_stable=True)
        self.assertEqual(set(s['hand']), {'x','y','palm_width','score','label','side'})
        self.assertAlmostEqual(s['hand']['palm_width'],.1)
        self.assertAlmostEqual(summarize(r,mirror_x=True)['hand']['x'],1-s['hand']['x'])
        self.assertNotIn('secret',json.dumps(s))
    def test_ambiguity_or_malformed_is_not_single_hand_or_departure(self):
        self.assertEqual(summarize(hand(3),scene_stable=True),{'hand_count':2,'scene_stable':True,'hand':None})
        r=hand();r.hand_landmarks[0][0].x=float('nan')
        self.assertEqual(summarize(r),{'hand_count':0,'scene_stable':False,'hand':None})
    def test_synthetic_default_and_real_preconditions(self):
        p=HandObservationProducer();events=p.observe(hand(),100)
        self.assertTrue(all(e['synthetic'] for e in events))
        for options in ({'synthetic':False},{'synthetic':False,'camera_authorized':True}):
            with self.assertRaises(ValueError):HandObservationProducer(**options)
    def test_real_summary_pipe_allowlist_and_frame_freshness(self):
        p=HandObservationProducer(synthetic=False,camera_authorized=True,foreground_user_ready=True)
        inbox=InputEvents(hand_gestures=True,clock=lambda:10)
        for event in p.observe(hand(),100,scene_stable=True):self.assertTrue(inbox.accept(event))
        self.assertEqual(inbox.snapshot()['events'][0]['type'],'hand_observed')
        with self.assertRaises(ValueError):p.observe(hand(),100)
        self.assertTrue(inbox.accept(p.presenter('next',100)))
        self.assertTrue(inbox.accept(p.stop(100,failed=True)))
        self.assertFalse(inbox.snapshot()['available'])
        with self.assertRaises(ValueError):p.observe(hand(),200)
    def test_payload_extensions_cannot_override_envelope_or_emit_media(self):
        p=HandObservationProducer()
        for fields in ({'image':'pixels'},{'synthetic':False},{'schema':'override'}):
            with self.assertRaises(ValueError):p.envelope('ready',100,**fields)
    def test_synthetic_pipe_rejected_and_scene_default_unstable(self):
        p=HandObservationProducer();inbox=InputEvents(hand_gestures=True)
        self.assertFalse(any(inbox.accept(e) for e in p.observe(hand(),100)))
        self.assertFalse(summarize(hand())['scene_stable'])

if __name__=='__main__':unittest.main()
