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
from voice_agent import admitted_action,PublicSyntheticVoiceLoop,map_navigation_text
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
        for fault in ('none','during_asr','on_close','missing_usage','deadline','repeat','cancel','repeat_empty','maps','map_repeat','maps_unchanged','captions','caption_language','caption_cancel','missing_native_usage','caption_deadline'):
            expected=(map_navigation_text('en','statewide') if fault=='maps_unchanged' else map_navigation_text('en','kansas_city') if fault in {'maps','map_repeat'} else 'Please name the public election question you want to understand.' if fault=='repeat_empty' else 'The question asks whether to approve the legislature’s act replacing the congressional plan.' if fault=='repeat' else 'The complete official wording is available with its source on screen.')
            class Socket:
                def __init__(self):self.queue=asyncio.Queue();self.routed=False;self.turn=1;self.commentaries=0
                async def __aenter__(self):self.loop=asyncio.get_running_loop();self.operation=asyncio.current_task();return self
                async def __aexit__(self,*_):pass
                def __aiter__(self):return self
                async def __anext__(self):return json.dumps(await self.queue.get())
                async def audio(self):await self.queue.put({'type':'session.output_audio.delta','delta':base64.b64encode(pcm).decode()})
                async def send(self,raw):
                    event=json.loads(raw);kind=event['type']
                    if kind=='session.start':await self.queue.put({'type':'session.started'})
                    elif kind=='session.update':
                        self.turn=2;self.routed=False
                        await self.queue.put({'type':'session.updated','session':event['session']})
                    elif kind=='session.input_audio.append' and not self.routed:
                        self.routed=True
                        # Same-session timing is not a sent-PCM byte offset.
                        # Unknown commands with plausible timing stay withheld;
                        # an owned command can bind even when clocks differ.
                        fragments=([(event['event_id'],'public input',40000),(event['event_id'],'omitted',None)] if fault=='none'
                                   else [('foreign','incorrect',0),(event['event_id'],'public input',40000)])
                        for command,delta,start in fragments:
                            await self.queue.put({'type':'session.input_transcript.delta','client_event_id':command,
                                'delta':delta,**({'start_ms':start,'end_ms':start+200} if start is not None else {})})
                        await self.audio()  # Pre-approval energy is discarded, never admitted.
                        await self.queue.put({'type':'session.delegation.created','delegation':{'target':'decisions','id':'fixture_delegation_'+str(self.turn)}})
                        answers=[{'type':'choice','name':name+'_turn_'+str(self.turn),'choice':value} for name,value in [('view','maps' if fault in {'maps','map_repeat','maps_unchanged'} else 'measure' if fault=='repeat' else 'source'),('map_focus','kansas_city' if fault in {'maps','map_repeat'} else 'unchanged'),('delivery','repeat' if self.turn==2 or fault=='repeat_empty' else 'brief')]]
                        await self.queue.put({'type':'decision.event','delegation_id':'fixture_delegation_'+str(self.turn),'event':{'type':'decision.completed','decision':{'answers':answers,**({'usage':{'input_tokens':200,'output_tokens':0}} if fault!='missing_native_usage' else {})}}})
                    elif kind=='session.commentary.append':
                        self.commentaries+=1
                        await self.queue.put({'type':'session.output_transcript.delta','delta':expected});await self.audio()
                        if fault=='deadline': self.loop.call_later(.01,self.operation.cancel)
                    elif kind=='session.close':
                        if fault=='on_close':await self.audio()
                        await self.queue.put({'type':'session.closed','reason':'close_requested',**({'usage':{'seconds':2}} if fault!='missing_usage' else {})})
            socket=Socket()
            class Provider:
                _headers={}
                def __init__(self):self.posts=[];self.transcriptions=0;self.attempts=0
                def account_attempt(self):self.attempts+=1
                def post(self,path,body,cancel):
                    self.posts.append(path)
                    usage={'input_tokens':200,'output_tokens':80 if path=='responses' else 0}
                    if path=='responses':
                        draft={'operation':'brief','language':'en','sections':[{'source_id':'question','text':expected}],
                               'components':['explanation','original','uncertainty']}
                        return {'status':'completed','usage':usage,'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(draft)}]}]}
                    return {'usage':usage,'answers':[{'name':name,'type':'predicate','probability':.99} for name in ['entailed','no_additions','attributed','request_fit','language_match','polarity_safe']]}
                def transcribe(self,wav,cancel):
                    self.transcriptions+=1
                    if fault in {'captions','caption_language','caption_cancel','caption_deadline'} and self.transcriptions==1:
                        if fault=='caption_cancel':cancel.set()
                        if fault=='caption_deadline':
                            socket.loop.call_soon_threadsafe(socket.operation.cancel);time.sleep(.04)
                        return {'text':'Could you show the official source?', 'languages':[{'code':'es' if fault=='caption_language' else 'en'}]}
                    if fault=='during_asr':
                        asyncio.run_coroutine_threadsafe(socket.audio(),socket.loop).result(timeout=1);time.sleep(.03)
                    return {'text':expected,'languages':[{'code':'en'}]}
            metered=[]
            async def run():
                updates=[];cancel=threading.Event()
                def notify(value):
                    updates.append(value)
                    if fault=='cancel' and value['stage']=='checked_text':cancel.set()
                provider=Provider()
                with patch.dict(sys.modules,{'websockets':SimpleNamespace(connect=lambda *a,**k:socket)}):
                    result=await PublicSyntheticVoiceLoop(provider,seconds=15,input_captions=fault in {'captions','caption_language','caption_cancel','caption_deadline'}).run([fixture,fixture] if fault in {'repeat','map_repeat'} else [fixture],cancel,lambda stage,usage:metered.append((stage,usage)),notify)
                self.assertEqual([e['text'] for e in updates if e['stage']=='input_partial'],['public input']*(2 if fault in {'repeat','map_repeat'} else 1))
                self.assertEqual(len([e for e in updates if e['stage']=='input_unavailable']),2 if fault in {'repeat','map_repeat'} else 1)
                self.assertEqual([e['stage'] for e in updates if e['stage'] in {'input_partial','input_unavailable'}],
                                 ['input_partial','input_unavailable'] if fault=='none' else ['input_unavailable','input_partial']*(2 if fault in {'repeat','map_repeat'} else 1))
                finals=[e for e in updates if e['stage']=='input_final']
                if fault=='captions':
                    self.assertEqual([(e['turn'],e['text'],e['input_audio_sha256']) for e in finals],[(1,'Could you show the official source?',fixture['sha256'])])
                    self.assertEqual(result['inputs'][0]['text'],finals[0]['text'])
                    self.assertEqual(provider.transcriptions,2)
                else:self.assertFalse(finals)
                self.assertGreaterEqual(result['diagnostics']['discarded_chunks_with_energy_bytes'],len(pcm))
                self.assertEqual(provider.posts,['responses','decisions'] if fault=='repeat' else [])
                return result
            with self.subTest(fault=fault):
                result=asyncio.run(run())
                self.assertEqual(result['all_turns_checked'],fault in {'none','repeat','repeat_empty','maps','map_repeat','maps_unchanged','captions'})
                if fault=='caption_deadline':
                    self.assertIn('voice_asr_outcome_unconfirmed',result['errors'])
                    self.assertIn('transcription',[stage for stage,_ in metered])  # Settles even after awaiting coroutine was cancelled.
                if fault=='caption_language':self.assertIn('voice_input_asr_language',result['errors'])
                if fault=='caption_cancel':self.assertFalse(result['inputs']);self.assertFalse(result['turns'])
                if fault=='during_asr':self.assertIn('voice_audio_changed_during_asr',result['errors'])
                if fault=='on_close':self.assertIn('voice_after_segment',result['errors'])
                if fault=='missing_native_usage':self.assertIn('voice_native_usage_unconfirmed',result['errors'])
                if fault=='missing_usage':self.assertIn('voice_usage_unconfirmed',result['errors'])
                if fault in {'repeat','map_repeat'}:self.assertEqual(socket.commentaries,2);self.assertEqual(len(result['turns']),2);self.assertEqual(result['turns'][1]['checked'],result['turns'][0]['checked'])
                if fault=='cancel':self.assertIn('voice_cancelled',result['errors']);self.assertFalse(result['turns']);self.assertTrue(result['finalized'])
                if fault=='deadline':self.assertIn('voice_deadline',result['errors']);self.assertTrue(result['finalized'])
