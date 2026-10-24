import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import wave
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fresh_speech import FreshSpeechPipeline,reading_for,words
from journey import QUESTION_PIN
from jobs import Budget,Jobs
from providers import Held


def parent():
    return {'mode':'fresh_grounded_generation','source_version':QUESTION_PIN,'raw_visitor_input_sent':False,
            'request_fit':'unconfirmed','unit':{'operation':'simpler','language':'en','sections':[
                {'source_id':'question','text':'The question asks about a congressional plan.'}]}}


class FreshSpeechTests(unittest.TestCase):
    def test_whole_final_waveform_matches_without_expected_text_bias_and_holds_disagreement(self):
        class Provider:
            def __init__(self):self.bad=False;self.calls=[]
            def speak(self,text,cancel,**bounds):
                self.text=text;self.calls.append('live');return {'pcm':b'\1\0'*24000,'transcript':text,'finalized':True,
                    'reason':'close_requested','errors':[],'backend_events':0,'usage':{'seconds':55}}
            def transcribe(self,wav,cancel):
                self.calls.append('asr')
                with wave.open(io.BytesIO(wav),'rb') as audio:self_test.assertEqual(audio.getnframes(),24000)
                return {'text':self.text.replace('not','') if self.bad else self.text,'languages':[{'code':'en'}]}
        self_test=self;provider=Provider();pipeline=FreshSpeechPipeline(provider);cancel=threading.Event();meter=[]
        result,wav=pipeline.run_task('speech:en',cancel,lambda _:None,lambda *args:meter.append(args),prior=parent())
        self.assertEqual(result['sha256'],hashlib.sha256(wav).hexdigest());self.assertTrue(result['independent_asr_match'])
        self.assertIn('unconfirmed',result['reading']);self.assertIn('human review pending',result['reading'])
        self.assertEqual(provider.calls,['live','asr']);self.assertEqual([stage for stage,_ in meter],['fresh_audio','transcription'])
        provider.bad=True
        with self.assertRaisesRegex(Held,'independent_transcript_mismatch'):pipeline.run_task('speech:en',cancel,lambda _:None,lambda *_:None,prior=parent())
        bad=parent();bad['source_version']='different'
        with self.assertRaises(Held):reading_for(bad,'en')
        with self.assertRaisesRegex(Held,'translation_review_required'):pipeline.run_task('speech:es',cancel,lambda _:None,lambda *_:None,prior=parent())
        cancel.set();count=len(provider.calls)
        with self.assertRaises(Held):pipeline.run_task('speech:en',cancel,lambda _:None,lambda *_:None,prior=parent())
        self.assertEqual(len(provider.calls),count)
        self.assertEqual(words('A.I House Bill No.1 (2025)'),words('AI House Bill number one (two thousand twenty-five)'))
        self.assertNotEqual(words('No one approves it'),words('number one approves it'))
        self.assertNotEqual(words('does not verify'),words('does verify'))

    def test_same_owner_parent_revocation_and_audio_expiry_keep_budget_conservative(self):
        class Pipeline:
            def run_task(self,task,cancel,stage,meter,prior=None):
                stage('audio' if task.startswith('speech:') else 'text')
                if prior:now[0]+=70
                return ({'mode':'fresh_checked_speech'} if prior else parent()),b'public wave fixture'
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'ledger.json';path.write_text(json.dumps({'authorization_usd_max':200,'runs':[]}))
            now=[0.0];jobs=Jobs(Pipeline(),Budget(path),max_runs=4,clock=lambda:now[0])
            try:
                token=jobs.capabilities()['session_token'];other=jobs.capabilities()['session_token']
                jobs.start(token,'public_parent_0001','journey:simpler:en');jobs.workers[-1].join(1)
                with self.assertRaisesRegex(Held,'parent_unavailable'):jobs.start(other,'public_audio_00001','speech:en',parent_request='public_parent_0001')
                jobs.start(token,'public_audio_00001','speech:en',parent_request='public_parent_0001');jobs.workers[-1].join(1)
                self.assertEqual(jobs.audio(token,'public_audio_00001'),b'public wave fixture')
                now[0]=125
                self.assertEqual(jobs.audio(token,'public_audio_00001'),b'public wave fixture')
                with self.assertRaises(Held):jobs.audio(other,'public_audio_00001')
                jobs.cancel(token,'public_parent_0001')
                with self.assertRaises(Held):jobs.audio(token,'public_audio_00001')
                self.assertIsNone(jobs.public(token,'public_audio_00001')['result'])
                jobs.start(token,'public_parent_0002','journey:simpler:en');jobs.workers[-1].join(1)
                jobs.start(token,'public_audio_00002','speech:en',parent_request='public_parent_0002');jobs.workers[-1].join(1)
                prior=jobs.owners[token]['jobs']['public_parent_0002']['result']
                prior['unit']['sections'][0]['text']=('The question asks about a congressional plan. '*14).strip()
                with self.assertRaisesRegex(Held,'speech_too_long'):jobs.start(token,'overlong_audio_001','speech:en',parent_request='public_parent_0002')
                now[0]=316
                with self.assertRaises(Held):jobs.audio(token,'public_audio_00002')
                reservations=[row['reserved_usd'] for row in json.loads(path.read_text())['runs']]
                self.assertEqual(reservations,[.01,.10,.01,.10])
            finally:jobs.close()
