import asyncio
import base64
import hashlib
import sys
import json
import struct
import time
import threading
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from voice_agent import admitted_action,PublicSyntheticVoiceLoop,map_navigation_text,reading_prefix_possible,public_wave
from providers import Held,NotDispatched


class NativeVoiceAdmissionTests(unittest.TestCase):
    def test_rejected_cancelled_and_drained_native_work_is_settled_before_admission(self):
        from jobs import Budget, STAGED_TRIAL_PACKAGE
        pcm=struct.pack('<h',1000)*1200
        fixture={'kind':'synthetic_public_question','pcm':pcm,'sha256':hashlib.sha256(pcm).hexdigest()}
        for fault in ('second_delegation','after_cancel','error_drain','duplicate','conflicting_duplicate','missing_usage','attempt_limit','completion_burst','created_only','created_after_cancel','created_in_drain','malformed_completion','transport_drain'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'ledger.json'
                path.write_text(json.dumps({'authorization_usd_max':200,'runs':[{
                    'id':'run','state':'reserved','trial_package':STAGED_TRIAL_PACKAGE,'trial_purpose':'english',
                    'requests_attempted':0,'requests_max':2 if fault=='attempt_limit' else 11,'reserved_usd':.10,'stages':[]}]}))
                budget=Budget(path);cancel=threading.Event()
                class Socket:
                    def __init__(self):self.queue=asyncio.Queue();self.routed=False
                    async def __aenter__(self):return self
                    async def __aexit__(self,*_):pass
                    def __aiter__(self):return self
                    async def __anext__(self):return json.dumps(await self.queue.get())
                    async def completion(self,delegation,usage=True):
                        await self.queue.put({'type':'session.delegation.created','delegation':{'target':'decisions','id':delegation}})
                        await self.queue.put({'type':'decision.event','delegation_id':delegation,'event':{'type':'decision.completed','decision':{
                            'answers':[{'type':'choice','name':name+'_turn_1','choice':value} for name,value in
                                [('view','source'),('map_focus','unchanged'),('delivery','brief'),('language','en')]],
                            **({'usage':{'input_tokens':200,'output_tokens':0}} if usage else {})}}})
                    async def send(self,raw):
                        kind=json.loads(raw)['type']
                        if kind=='session.start':await self.queue.put({'type':'session.started'})
                        elif kind=='session.input_audio.append' and not self.routed:
                            self.routed=True;await self.completion('d1')
                        elif kind=='session.commentary.append':
                            if fault in {'after_cancel','created_after_cancel'}:cancel.set()
                            if fault=='transport_drain':await self.queue.put({'type':'session.output_audio.delta','delta':'not-base64!'})
                            elif fault in {'error_drain','completion_burst','created_in_drain'}:await self.queue.put({'type':'error'})
                            elif fault in {'created_only','created_after_cancel'}:
                                await self.queue.put({'type':'session.delegation.created','delegation':{'target':'decisions','id':'d2'}})
                                await self.queue.put({'type':'error'})
                            elif fault=='malformed_completion':
                                await self.queue.put({'type':'decision.event','delegation_id':'d2','event':{'type':'decision.completed','decision':None}})
                            elif fault in {'duplicate','conflicting_duplicate'}:
                                await self.queue.put({'type':'decision.event','delegation_id':'d1','event':{'type':'decision.completed','decision':{
                                    'usage':{'input_tokens':201 if fault=='conflicting_duplicate' else 200,'output_tokens':0}}}})
                                await self.queue.put({'type':'error'})
                            else:await self.completion('d2',usage=fault!='missing_usage')
                        elif kind=='session.close':
                            if fault in {'error_drain','transport_drain'}:await self.completion('d2')
                            if fault=='created_in_drain':await self.queue.put({'type':'session.delegation.created','delegation':{'target':'decisions','id':'d2'}})
                            if fault=='completion_burst':
                                for number in range(2,25):await self.completion('d'+str(number))
                            await self.queue.put({'type':'session.closed','reason':'close_requested','usage':{'seconds':2}})
                socket=Socket()
                class Provider:
                    _headers={}
                    def account_attempt(self):budget.attempt('run')
                with patch.dict(sys.modules,{'websockets':SimpleNamespace(connect=lambda *a,**k:socket)}):
                    receipt=asyncio.run(PublicSyntheticVoiceLoop(Provider(),seconds=15).run([fixture],cancel,
                        lambda stage,usage:budget.record('run',stage,usage),lambda *_:None))
                budget.finish('run','held',voice_receipt=receipt)
                row=json.loads(path.read_text())['runs'][0]
                self.assertFalse(receipt['all_turns_checked']);self.assertFalse(receipt['turns'])
                expected=16 if fault=='completion_burst' else 1 if fault in {'duplicate','conflicting_duplicate','missing_usage','created_only','created_after_cancel','created_in_drain','malformed_completion'} else 2
                self.assertEqual(len([s for s in row['stages'] if s['stage']=='review']),expected)
                self.assertEqual(row['requests_attempted'],11 if fault=='completion_burst' else 2 if fault in {'duplicate','conflicting_duplicate','attempt_limit'} else 3)
                # A rejected distinct delegation is charged, but still holds the
                # workflow; missing/conflicting usage must never allow progression.
                self.assertEqual(row['trial_closure_confirmed'],fault in {'second_delegation','after_cancel','error_drain','transport_drain','duplicate'})
                if fault in {'missing_usage','conflicting_duplicate','attempt_limit','completion_burst','created_only','created_after_cancel','created_in_drain','malformed_completion'}:
                    self.assertIn('voice_native_usage_unconfirmed',receipt['errors'])
                if fault=='completion_burst':
                    self.assertTrue(receipt['native_completion_overflow']);self.assertEqual(receipt['native_completions'],16)

    def test_native_choices_cannot_add_rankings_or_apply_geography_to_a_nonmap_action(self):
        def answers(view='maps',focus='kansas_city'):
            return [{'type':'choice','name':'view','choice':view},
                {'type':'choice','name':'map_focus','choice':focus},
                {'type':'choice','name':'delivery','choice':'brief'},
                {'type':'choice','name':'language','choice':'en'}]
        self.assertEqual(admitted_action(answers())['map_focus'],'kansas_city')
        named=[dict(a,name=a['name']+'_turn_1') for a in answers()]
        self.assertEqual(admitted_action(named,1)['view'],'maps')
        with self.assertRaisesRegex(Held,'voice_decision_turn'):admitted_action(named,2)
        for bad in [answers('candidate_ranking'),answers('measure'),answers()+[answers()[0]],[]]:
            with self.assertRaises(Held):admitted_action(bad)

    def test_prefix_check_defers_partial_words_and_closed_year_normalization(self):
        expected='The question describes House Bill No. 1 (2025 Second Extraordinary Session) and the congressional plan.'
        observed='The question describes House Bill number one, two thousand and twenty five Second Extraordinary Session and the congressional plan.'
        for end in range(len(observed)+1):self.assertTrue(reading_prefix_possible(observed[:end],expected))
        self.assertFalse(reading_prefix_possible('The question says vote yes because this proposal is best and should be adopted by every voter.',expected))

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
        for fault in ('none','during_asr','on_close','missing_usage','deadline','repeat','cancel','repeat_empty','maps','map_repeat','maps_unchanged','captions','caption_language','caption_cancel','missing_native_usage','caption_deadline','switch_es','switch_en','diverged','switch_roundtrip','repeated_reading','cancel_switch','stale_language','late_native_usage','short_tail','caption_not_dispatched'):
            expected=(map_navigation_text('en','statewide') if fault=='maps_unchanged' else map_navigation_text('en','kansas_city') if fault in {'maps','map_repeat'} else 'Please name the public election question you want to understand.' if fault=='repeat_empty' else 'The question asks whether to approve the legislature’s act replacing the congressional plan.' if fault=='repeat' else 'The complete official wording is available with its source on screen.')
            switching=fault in {'switch_es','switch_en','switch_roundtrip','cancel_switch','stale_language'}
            turn_count=3 if fault=='switch_roundtrip' else 2 if fault in {'repeat','map_repeat','switch_es','switch_en','cancel_switch','stale_language','late_native_usage'} else 1
            initial_language='es' if fault=='switch_en' else 'en'
            def response_language(turn):
                return ('es' if initial_language=='en' else 'en') if switching and turn==2 else initial_language
            input_languages=[initial_language]+(['en','es'][:turn_count-1] if initial_language=='en' else ['es']*(turn_count-1))
            clips=[dict(fixture,language=language,pcm=struct.pack('<h',1100+i)*1200,
                        sha256=hashlib.sha256(struct.pack('<h',1100+i)*1200).hexdigest())
                   for i,language in enumerate(input_languages)] if switching else [fixture]*turn_count
            switch_text={'en':'The question asks whether to approve the legislature’s act replacing the congressional plan.',
                         'es':'La pregunta indica si los votantes aprueban la ley de la legislatura que reemplaza el plan congresional.'}
            class Socket:
                def __init__(self):self.queue=asyncio.Queue();self.routed=False;self.turn=1;self.commentaries=0;self.last_text=''
                async def __aenter__(self):self.loop=asyncio.get_running_loop();self.operation=asyncio.current_task();return self
                async def __aexit__(self,*_):pass
                def __aiter__(self):return self
                async def __anext__(self):return json.dumps(await self.queue.get())
                async def audio(self):await self.queue.put({'type':'session.output_audio.delta','delta':base64.b64encode(pcm).decode()})
                async def send(self,raw):
                    event=json.loads(raw);kind=event['type']
                    if kind=='session.start':await self.queue.put({'type':'session.started'})
                    elif kind=='session.update':
                        self.turn+=1;self.routed=False
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
                        answers=[{'type':'choice','name':name+'_turn_'+str(self.turn),'choice':value} for name,value in [('view','maps' if fault in {'maps','map_repeat','maps_unchanged'} else 'measure' if fault=='repeat' or switching else 'source'),('map_focus','kansas_city' if fault in {'maps','map_repeat'} else 'unchanged'),('delivery','simpler' if fault=='switch_roundtrip' and self.turn==2 else 'repeat' if self.turn==2 or fault=='repeat_empty' else 'brief'),('language',response_language(self.turn))]]
                        if fault=='stale_language' and self.turn==2:
                            old=[dict(a,name=a['name'].replace('_turn_2','_turn_1'),choice='en' if a['name'].startswith('language_') else a['choice']) for a in answers]
                            await self.queue.put({'type':'decision.event','delegation_id':'fixture_delegation_1','event':{'type':'decision.completed','decision':{'answers':old,'usage':{'input_tokens':200,'output_tokens':0}}}})
                        await self.queue.put({'type':'decision.event','delegation_id':'fixture_delegation_'+str(self.turn),'event':{'type':'decision.completed','decision':{'answers':answers,**({'usage':{'input_tokens':200,'output_tokens':0}} if fault!='missing_native_usage' else {})}}})
                    elif kind=='session.commentary.append':
                        self.commentaries+=1;self.last_text=(event['content']+' Let me know.' if fault=='short_tail' else event['content']+' '+event['content'] if fault=='repeated_reading' else 'The question recommends voting yes because this is the best map for everyone and you should approve it immediately.' if fault=='diverged' else event['content'])
                        await self.queue.put({'type':'session.output_transcript.delta','delta':self.last_text if switching or fault in {'diverged','repeated_reading','short_tail'} else expected});await self.audio()
                        if fault=='deadline': self.loop.call_later(.01,self.operation.cancel)
                    elif kind=='session.close':
                        if fault=='on_close':await self.audio()
                        await self.queue.put({'type':'session.closed','reason':'close_requested',**({'usage':{'seconds':2}} if fault!='missing_usage' else {})})
            socket=Socket()
            class Provider:
                _headers={}
                def __init__(self):self.posts=[];self.transcriptions=0;self.attempts=0;self.contexts=[];self.voice_observed=[]
                def account_attempt(self):self.attempts+=1
                def observe_public_voice(self,turn,expected,observed,**timing):self.voice_observed.append((turn,expected,observed))
                def post(self,path,body,cancel):
                    self.posts.append(path)
                    usage={'input_tokens':200,'output_tokens':80 if path=='responses' else 0}
                    if path=='responses':
                        context=json.loads(body['input'][1]['content']);self.contexts.append(context)
                        draft={'operation':body['text']['format']['schema']['properties']['operation']['enum'][0],'language':context['language'] if switching else 'en','sections':[{'source_id':'question','text':switch_text[context['language']] if switching else expected}],
                               'components':['explanation','original','uncertainty']}
                        return {'status':'completed','usage':usage,'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(draft)}]}]}
                    return {'usage':usage,'answers':[{'name':name,'type':'predicate','probability':.99} for name in ['entailed','no_additions','attributed','request_fit','language_match','polarity_safe']]}
                def transcribe(self,wav,cancel):
                    self.transcriptions+=1
                    if fault=='caption_not_dispatched':cancel.set();raise NotDispatched('cancelled')
                    if switching:
                        for clip in clips:
                            if wav==public_wave(clip['pcm']):
                                return {'text':'public input','languages':[{'code':clip['language']}]}
                    if fault in {'captions','caption_language','caption_cancel','caption_deadline'} and self.transcriptions==1:
                        if fault=='caption_cancel':cancel.set()
                        if fault=='caption_deadline':
                            socket.loop.call_soon_threadsafe(socket.operation.cancel);time.sleep(.04)
                        return {'text':'Could you show the official source?', 'languages':[{'code':'es' if fault=='caption_language' else 'en'}]}
                    if fault=='late_native_usage':
                        asyncio.run_coroutine_threadsafe(socket.queue.put({'type':'decision.event','delegation_id':'fixture_delegation_1',
                            'event':{'type':'decision.completed','decision':{'usage':{'input_tokens':201,'output_tokens':0}}}}),socket.loop).result(timeout=1)
                        time.sleep(.03)
                    if fault=='during_asr':
                        asyncio.run_coroutine_threadsafe(socket.audio(),socket.loop).result(timeout=1);time.sleep(.03)
                    return {'text':socket.last_text if switching else expected,'languages':[{'code':response_language(socket.turn)}]}
            metered=[]
            async def run():
                updates=[];cancel=threading.Event();cancel_at=[]
                def notify(value):
                    updates.append(value)
                    if (fault=='cancel' or fault=='cancel_switch' and value['turn']==2) and value['stage']=='checked_text':
                        cancel_at.append(value['at_ms']);cancel.set()
                provider=Provider()
                with patch.dict(sys.modules,{'websockets':SimpleNamespace(connect=lambda *a,**k:socket)}):
                    result=await PublicSyntheticVoiceLoop(provider,seconds=15,language=initial_language,input_captions=fault in {'captions','caption_language','caption_cancel','caption_deadline','switch_es','switch_en','switch_roundtrip','cancel_switch','stale_language','caption_not_dispatched'}).run(clips,cancel,lambda stage,usage:metered.append((stage,usage)),notify)
                routed_turns=1 if fault=='late_native_usage' else turn_count
                self.assertEqual([e['text'] for e in updates if e['stage']=='input_partial'],['public input']*routed_turns)
                self.assertEqual(len([e for e in updates if e['stage']=='input_unavailable']),routed_turns)
                self.assertEqual([e['stage'] for e in updates if e['stage'] in {'input_partial','input_unavailable'}],
                                 ['input_partial','input_unavailable'] if fault=='none' else ['input_unavailable','input_partial']*routed_turns)
                finals=[e for e in updates if e['stage']=='input_final']
                if fault=='captions':
                    self.assertEqual([(e['turn'],e['text'],e['input_audio_sha256']) for e in finals],[(1,'Could you show the official source?',fixture['sha256'])])
                    self.assertEqual(result['inputs'][0]['text'],finals[0]['text'])
                    self.assertEqual(provider.transcriptions,2)
                elif switching:
                    if fault=='cancel_switch':
                        self.assertTrue(any(e['turn']==1 for e in finals))
                        self.assertTrue(all(e['language']==initial_language and e['at_ms']<=cancel_at[0] for e in finals))
                        self.assertFalse(any(e['stage']=='speech_checked' and e['turn']==2 for e in updates))
                    else:self.assertEqual([(e['turn'],e['language']) for e in finals],list(enumerate(input_languages,1)))
                    self.assertEqual([e['language'] for e in updates if e['stage']=='input_partial'],input_languages)
                else:self.assertFalse(finals)
                self.assertGreaterEqual(result['diagnostics']['discarded_chunks_with_energy_bytes'],len(pcm))
                if fault in {'diverged','repeated_reading'}:
                    self.assertTrue(provider.voice_observed)
                    self.assertFalse(result['turns'])
                    self.assertNotEqual(provider.voice_observed[-1][1],provider.voice_observed[-1][2])
                self.assertEqual(provider.posts,['responses','decisions']*turn_count if switching else ['responses','decisions'] if fault=='repeat' else [])
                if switching:
                    self.assertEqual(provider.contexts[1]['previous_checked_public_unit']['language'],initial_language)
                    self.assertTrue(all(c['sources']==provider.contexts[0]['sources'] for c in provider.contexts))
                    if turn_count==3:
                        self.assertEqual(provider.contexts[2]['previous_checked_public_unit']['language'],'es')
                        self.assertEqual(result['turns'][1]['checked']['result']['unit']['operation'],'simpler')
                        self.assertEqual(result['turns'][1]['checked']['result']['request_fit'],'confirmed')
                    self.assertEqual([t['language'] for t in result['turns']],[response_language(i) for i in range(1,2 if fault=='cancel_switch' else turn_count+1)])
                    if fault=='cancel_switch':self.assertIn('voice_cancelled',result['errors'])
                    if fault=='stale_language':self.assertEqual(result['native_decisions'],2)
                    self.assertTrue(all(e['session_language']==initial_language for e in updates))
                return result
            with self.subTest(fault=fault):
                result=asyncio.run(run())
                self.assertEqual(result['all_turns_checked'],fault in {'none','repeat','repeat_empty','maps','map_repeat','maps_unchanged','captions','switch_es','switch_en','switch_roundtrip','stale_language'})
                if fault=='caption_deadline':
                    self.assertIn('voice_asr_outcome_unconfirmed',result['errors'])
                    self.assertIn('transcription',[stage for stage,_ in metered])  # Settles even after awaiting coroutine was cancelled.
                if fault=='short_tail':
                    self.assertIn('voice_output_mismatch',result['errors']);self.assertNotIn('voice_deadline',result['errors'])
                if fault=='caption_not_dispatched':
                    self.assertTrue(result['asr_outcome_confirmed']);self.assertEqual(result['asr_attempted'],0);self.assertEqual(result['asr_not_dispatched'],1)
                    self.assertFalse(result['turns'])
                if fault=='caption_language':self.assertIn('voice_input_asr_language',result['errors'])
                if fault=='caption_cancel':self.assertFalse(result['inputs']);self.assertFalse(result['turns'])
                if fault in {'diverged','repeated_reading'}:self.assertIn('voice_output_diverged',result['errors']);self.assertNotIn('voice_deadline',result['errors'])
                if fault=='late_native_usage':
                    self.assertFalse(result['native_usage_confirmed']);self.assertEqual(result['native_decisions'],1)
                    self.assertIn('voice_native_usage_unconfirmed',result['errors']);self.assertFalse(result['turns'])
                if fault=='during_asr':self.assertIn('voice_audio_changed_during_asr',result['errors'])
                if fault=='on_close':self.assertIn('voice_after_segment',result['errors'])
                if fault=='missing_native_usage':self.assertIn('voice_native_usage_unconfirmed',result['errors'])
                if fault=='missing_usage':self.assertIn('voice_usage_unconfirmed',result['errors'])
                if fault in {'repeat','map_repeat'}:self.assertEqual(socket.commentaries,2);self.assertEqual(len(result['turns']),2);self.assertEqual(result['turns'][1]['checked'],result['turns'][0]['checked'])
                if fault=='cancel':self.assertIn('voice_cancelled',result['errors']);self.assertFalse(result['turns']);self.assertTrue(result['finalized'])
                if fault=='deadline':self.assertIn('voice_deadline',result['errors']);self.assertTrue(result['finalized'])
