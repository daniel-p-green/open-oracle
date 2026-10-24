import asyncio
import base64
import hashlib
import sys
import json
import struct
import time
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from voice_agent import admitted_action,PublicSyntheticVoiceLoop
from providers import Held


class NativeVoiceAdmissionTests(unittest.TestCase):
    def test_native_choices_cannot_add_rankings_or_apply_geography_to_a_nonmap_action(self):
        def answers(view='maps',focus='kansas_city'):
            return [{'type':'choice','name':'view','choice':view},
                {'type':'choice','name':'map_focus','choice':focus},
                {'type':'choice','name':'delivery','choice':'brief'}]
        self.assertEqual(admitted_action(answers())['map_focus'],'kansas_city')
        named=[dict(a,name=a['name']+'_turn_1') for a in answers()]
        self.assertEqual(admitted_action(named,1)['view'],'maps')
        with self.assertRaisesRegex(Held,'voice_decision_turn'):admitted_action(named,2)
        for bad in [answers('candidate_ranking'),answers('measure'),answers()+[answers()[0]],[]]:
            with self.assertRaises(Held):admitted_action(bad)

    def test_cancelled_or_nonfixture_audio_never_opens_a_live_connection(self):
        loop=PublicSyntheticVoiceLoop(object())
        cancel=threading.Event();cancel.set()
        pcm=bytes(2400)
        fixture={'kind':'synthetic_public_question','pcm':pcm,'sha256':hashlib.sha256(pcm).hexdigest()}
        with self.assertRaisesRegex(Held,'cancelled'):
            asyncio.run(loop.run([fixture],cancel,lambda *_:None,lambda *_:None))
        for bad in [dict(fixture,kind='human_microphone'),dict(fixture,sha256='forged')]:
            with self.assertRaisesRegex(Held,'synthetic_fixture_required'):
                asyncio.run(loop.run([bad],threading.Event(),lambda *_:None,lambda *_:None))

    def test_entire_native_audio_segment_and_final_usage_are_required_before_completion(self):
        # Regression: previously0.05s was checked while0.15s was emitted.
        # One protocol-owner proof, no provider/client/media/file operations.
        expected='The complete official wording is available with its source on screen.'
        pcm=struct.pack('<h',1000)*1200
        fixture={'kind':'synthetic_public_question','pcm':pcm,'sha256':hashlib.sha256(pcm).hexdigest()}
        for fault in ('none','during_asr','on_close','missing_usage'):
            class Socket:
                def __init__(self):self.queue=asyncio.Queue();self.routed=False
                async def __aenter__(self):self.loop=asyncio.get_running_loop();return self
                async def __aexit__(self,*_):pass
                def __aiter__(self):return self
                async def __anext__(self):return json.dumps(await self.queue.get())
                async def audio(self):await self.queue.put({'type':'session.output_audio.delta','delta':base64.b64encode(pcm).decode()})
                async def send(self,raw):
                    event=json.loads(raw);kind=event['type']
                    if kind=='session.start':await self.queue.put({'type':'session.started'})
                    elif kind=='session.input_audio.append' and not self.routed:
                        self.routed=True
                        await self.queue.put({'type':'session.delegation.created','delegation':{'target':'decisions','id':'fixture_delegation'}})
                        answers=[{'type':'choice','name':name+'_turn_1','choice':value} for name,value in [('view','source'),('map_focus','unchanged'),('delivery','brief')]]
                        await self.queue.put({'type':'decision.event','delegation_id':'fixture_delegation','event':{'type':'decision.completed','decision':{'answers':answers}}})
                    elif kind=='session.commentary.append':
                        await self.queue.put({'type':'session.output_transcript.delta','delta':expected});await self.audio()
                    elif kind=='session.close':
                        if fault=='on_close':await self.audio()
                        await self.queue.put({'type':'session.closed','reason':'close_requested',**({'usage':{'seconds':2}} if fault!='missing_usage' else {})})
            socket=Socket()
            class Provider:
                _headers={}
                def transcribe(self,wav,cancel):
                    if fault=='during_asr':
                        asyncio.run_coroutine_threadsafe(socket.audio(),socket.loop).result(timeout=1);time.sleep(.03)
                    return {'text':expected,'languages':[{'code':'en'}]}
            async def run():
                with patch.dict(sys.modules,{'websockets':SimpleNamespace(connect=lambda *a,**k:socket)}):
                    return await PublicSyntheticVoiceLoop(Provider(),seconds=15).run([fixture],threading.Event(),lambda *_:None,lambda *_:None)
            with self.subTest(fault=fault):
                result=asyncio.run(run())
                self.assertEqual(result['all_turns_checked'],fault=='none')
                if fault=='during_asr':self.assertIn('voice_audio_changed_during_asr',result['errors'])
                if fault=='on_close':self.assertIn('voice_after_segment',result['errors'])
                if fault=='missing_usage':self.assertIn('voice_usage_unconfirmed',result['errors'])
