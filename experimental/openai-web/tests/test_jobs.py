import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jobs import Budget, Jobs
from providers import Held


class ImmediatePipeline:
    def run(self, cancel, progress, meter):
        progress('text'); meter('text', {'input_tokens': 20, 'output_tokens': 10})
        return {'playback_enabled': False}, b'public audio fixture'


class JobsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.path = Path(self.temp.name) / 'ledger.json'
        self.path.write_text(json.dumps({'authorization_usd_max': 200, 'runs': []}))
        self.jobs = Jobs(ImmediatePipeline(), Budget(self.path))
        self.token = self.jobs.capabilities()['session_token']
        self.request = 'public_request_0001'
    def tearDown(self): self.jobs.close(); self.temp.cleanup()

    def test_unknown_usage_stage_cannot_fall_back_to_decisions_pricing(self):
        budget=Budget(self.path);budget.reserve('pricing')
        before=self.path.read_bytes()
        with self.assertRaisesRegex(Held,'usage_stage'):
            budget.record('pricing','unrecognized_audio_renderer',{'input_tokens':1000,'output_tokens':500})
        self.assertEqual(self.path.read_bytes(),before)
    def wait_terminal(self):
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            result = self.jobs.public(self.token, self.request)
            if result['state'] in {'ready', 'held', 'cancelled', 'expired'}: return result
            time.sleep(.005)
        self.fail('local fixture did not complete')

    def test_latency_stages_are_numeric_frozen_and_do_not_retain_input(self):
        from latency import StageTiming
        now = [0.0]
        timing = StageTiming(lambda: now[0])
        for at, stage in [(0.1, 'routing'), (0.3, 'retrieval'), (0.35, 'text'),
                          (1.55, 'validation'), (1.6, 'review'), (1.8, 'validation')]:
            now[0] = at
            timing.advance(stage)
        now[0] = 1.85
        timing.advance('ready', terminal=True)
        measured = timing.snapshot()
        self.assertEqual(measured['elapsed_ms'], 1850)
        self.assertEqual(measured['stages_ms'], {'queued': 100, 'routing': 200,
                         'retrieval': 50, 'text': 1200, 'validation': 100, 'review': 200})
        now[0] = 50
        timing.advance('private words cannot become a metric')
        self.assertEqual(timing.snapshot(), measured)

    def test_idempotent_request_and_global_run_cap(self):
        self.jobs.start(self.token, self.request); self.assertEqual(self.wait_terminal()['state'], 'ready')
        self.jobs.start(self.token, self.request)
        with self.assertRaises(Held): self.jobs.start(self.token, 'public_request_0002')
        self.assertEqual(len(json.loads(self.path.read_text())['runs']), 1)

    def test_slow_voice_poll_preserves_checked_turns_and_cancel_removes_captions(self):
        class PublicVoice:
            def run_task(self,task,cancel,progress,meter):
                progress('audio',{'stage':'checked_text','turn':1,'text':'public checked wording'})
                for number in range(100):
                    progress('audio',{'stage':'input_partial','turn':2,'text':str(number)})
                progress('audio',{'stage':'input_unavailable','turn':2})
                progress('audio',{'stage':'input_final','turn':2,'text':'public final input'})
                return {'public_fixture':True},b''
        self.jobs.pipeline=PublicVoice()
        self.jobs.start(self.token,self.request,'voice:synthetic:en')
        row=self.wait_terminal()
        self.assertEqual(row['state'],'ready')
        self.assertEqual([(item['stage'],item['text']) for item in row['updates']],
                         [('checked_text','public checked wording'),('input_final','public final input')])
        self.assertEqual([item['revision'] for item in row['updates']],[1,103])
        self.jobs.cancel(self.token,self.request)
        self.assertNotIn('updates',self.jobs.public(self.token,self.request))

    def test_adaptation_uses_only_ready_same_owner_public_unit_and_erase_revokes_it(self):
        class PublicJourney:
            def __init__(self): self.parents=[]
            def run_task(self,task,cancel,progress,meter,prior=None):
                self.parents.append(prior)
                return {'mode':'fresh_grounded_generation','unit':{'public':'checked'}},b''
        self.jobs.close();pipeline=PublicJourney();now=[0.0];self.jobs=Jobs(pipeline,Budget(self.path),max_runs=3,clock=lambda:now[0])
        self.token=self.jobs.capabilities()['session_token']
        self.jobs.start(self.token,self.request,'journey:overview:en');self.wait_terminal()
        now[0]=121
        self.assertEqual(self.jobs.public(self.token,self.request)['state'],'ready')
        other=self.jobs.capabilities()['session_token']
        with self.assertRaisesRegex(Held,'parent_unavailable'):
            self.jobs.start(other,'cross_owner_context','journey:simpler:en',parent_request=self.request)
        child='public_followup_0002';self.jobs.start(self.token,child,'journey:simpler:en',parent_request=self.request)
        self.jobs.workers[-1].join(1)
        self.assertEqual(pipeline.parents[-1],{'mode':'fresh_grounded_generation','unit':{'public':'checked'}})
        self.jobs.cancel(self.token,self.request)
        with self.assertRaisesRegex(Held,'parent_unavailable'):
            self.jobs.start(self.token,'erased_context_0003','journey:simpler:en',parent_request=self.request)
        self.assertEqual(self.jobs.runs,2)
        now[0]=601
        with self.assertRaisesRegex(Held,'owner_unavailable'):self.jobs.public(self.token,child)

    def test_rehearsal_refresh_evicts_inactive_owner_without_displacing_active_work(self):
        entered, gate=threading.Event(),threading.Event()
        class Delayed:
            def run(self,cancel,progress,meter):
                entered.set();gate.wait(2);return {'checked':True},b''
        self.jobs.pipeline=Delayed();self.jobs.start(self.token,self.request)
        self.assertTrue(entered.wait(1))
        tokens=[self.jobs.capabilities()['session_token'] for _ in range(12)]
        self.assertEqual(len(self.jobs.owners),8)
        self.assertIn(tokens[-1],self.jobs.owners);self.assertIn(self.token,self.jobs.owners)
        gate.set();self.assertEqual(self.wait_terminal()['state'],'ready')

    def test_unknown_owner_cannot_start_read_or_cancel(self):
        for action in [self.jobs.start, self.jobs.public, self.jobs.cancel]:
            with self.assertRaises(Held): action('not_the_owner', self.request)
        self.assertEqual(json.loads(self.path.read_text())['runs'], [])

    def test_cancel_before_start_is_a_tombstone_not_a_late_paid_request(self):
        self.jobs.cancel(self.token, self.request)
        with self.assertRaises(Held): self.jobs.start(self.token, self.request)
        self.assertEqual(self.jobs.runs, 0)
        for i in range(17):self.jobs.cancel(self.token,'unused_cancel_'+str(i))
        with self.assertRaisesRegex(Held,'owner_unavailable'):self.jobs.start(self.token,'delayed_after_overflow')
        self.assertEqual(self.jobs.runs,0)

    def test_cancelling_ready_result_discards_server_audio_and_citations(self):
        self.jobs.start(self.token, self.request); self.wait_terminal()
        for i in range(16):self.jobs.cancel(self.token,'unused_cancel_'+str(i))
        self.jobs.cancel(self.token, self.request)
        row = self.jobs.public(self.token, self.request)
        self.assertEqual(row['state'], 'cancelled'); self.assertIsNone(row['result'])
        self.assertIsNone(self.jobs.owners[self.token]['jobs'][self.request]['audio'])

    def test_pending_cancellation_prevents_late_ready_publish(self):
        gate, entered = threading.Event(), threading.Event()
        class Delayed:
            def run(self, cancel, progress, meter):
                entered.set(); gate.wait(2); return {'unsafe_late': True}, b'audio'
        self.jobs.pipeline = Delayed(); self.jobs.start(self.token, self.request); self.assertTrue(entered.wait(1))
        self.jobs.cancel(self.token, self.request); gate.set()
        self.assertEqual(self.wait_terminal()['state'], 'cancelled')
        self.assertIsNone(self.jobs.public(self.token, self.request)['result'])

    def test_expiry_discards_prepared_audio_without_releasing_it(self):
        self.jobs.start(self.token, self.request); self.wait_terminal()
        self.jobs.clock = lambda: time.monotonic() + 121
        row = self.jobs.public(self.token, self.request)
        self.assertEqual(row['state'], 'expired'); self.assertIsNone(row['result'])
        self.assertIsNone(self.jobs.owners[self.token]['jobs'][self.request]['audio'])

    def test_token_expiry_cancels_and_retains_draining_job_ownership(self):
        self.jobs.close();now=[0.0];entered,gate=threading.Event(),threading.Event()
        class Draining:
            def run(self,cancel,progress,meter):
                entered.set();gate.wait(2);return {'late':True},b'audio'
        self.jobs=Jobs(Draining(),Budget(self.path),max_runs=2,clock=lambda:now[0])
        token=self.jobs.capabilities()['session_token'];now[0]=590
        self.jobs.start(token,self.request);self.assertTrue(entered.wait(1))
        row=self.jobs.owners[token]['jobs'][self.request];now[0]=601
        other=self.jobs.capabilities()['session_token']
        self.assertTrue(row['cancel'].is_set());self.assertIn(token,self.jobs.owners)
        with self.assertRaisesRegex(Held,'busy'):self.jobs.start(other,'another_request_01')
        with self.assertRaises(Held):self.jobs.public(token,self.request)
        gate.set();self.jobs.workers[0].join(1)
        self.assertFalse(row['in_flight']);self.assertIsNone(row['result'])
        self.jobs.capabilities();self.assertNotIn(token,self.jobs.owners)

    def test_conservative_reservations_enforce_authorized_cap(self):
        self.path.write_text(json.dumps({'authorization_usd_max': 200, 'runs': [{'id': 'prior', 'reserved_usd': 199.95}]}))
        with self.assertRaises(Held): self.jobs.start(self.token, self.request)
        self.assertEqual(self.jobs.runs, 0)

    def test_four_trial_package_is_atomic_bounded_and_never_retries_a_purpose(self):
        from jobs import VOICE_TRIAL_PACKAGE, VOICE_TRIAL_PURPOSES
        budget=Budget(self.path)
        for number,purpose in enumerate(sorted(VOICE_TRIAL_PURPOSES)):
            budget.reserve('fixture_'+str(number),'voice:synthetic:en',
                           trial_package=VOICE_TRIAL_PACKAGE,trial_purpose=purpose)
            if number == 0:
                with self.assertRaisesRegex(Held,'trial_package_outcome_unconfirmed'):
                    budget.reserve('overlap','voice:synthetic:en',trial_package=VOICE_TRIAL_PACKAGE,trial_purpose='recovery')
            budget.record('fixture_'+str(number),'fresh_audio',{'seconds':2})
            budget.finish('fixture_'+str(number),'held')
            if number == 0:
                with self.assertRaisesRegex(Held,'trial_package_outcome_unconfirmed'):
                    budget.reserve('unclosed','voice:synthetic:en',trial_package=VOICE_TRIAL_PACKAGE,trial_purpose='recovery')
            budget.finish('fixture_'+str(number),'held',voice_receipt={'finalized':True,'close_reason':'close_requested','usage':{'seconds':2},'errors':[],'asr_outcome_confirmed':True,'native_usage_confirmed':True})
            budget.finish('fixture_'+str(number),'held')  # bookkeeping cannot erase established confirmation
        with self.assertRaisesRegex(Held,'trial_package_exhausted'):
            budget.reserve('extra','voice:synthetic:en',trial_package=VOICE_TRIAL_PACKAGE,trial_purpose='english_diagnostic')
        rows=json.loads(self.path.read_text())['runs']
        self.assertEqual(len(rows),4)
        self.assertAlmostEqual(sum(row['reserved_usd'] for row in rows),.40)

    def test_staged_package_keeps_old_trials_closed_and_blocks_unknown_dispatch(self):
        from jobs import STAGED_TRIAL_PACKAGE as package
        budget=Budget(self.path,per_run=.01)
        with self.assertRaisesRegex(Held,'trial_prerequisite'):
            budget.reserve('premature','voice:synthetic:en',trial_package=package,trial_purpose='english')
        budget.reserve('text',trial_package=package,trial_purpose='text_initial')
        budget.attempt('text')
        budget.finish('text','held')  # HTTP attempt without metered response is uncertain.
        with self.assertRaisesRegex(Held,'outcome_unconfirmed'):
            budget.reserve('repair',trial_package=package,trial_purpose='text_repair',repair_basis='named offline repair')
        budget.record('text','journey_text',{'input_tokens':10,'output_tokens':10})
        budget.finish('text','held')
        with self.assertRaisesRegex(Held,'trial_prerequisite'):
            budget.reserve('skip','voice:synthetic:en',trial_package=package,trial_purpose='english')
        budget.reserve('repair',trial_package=package,trial_purpose='text_repair',repair_basis='named offline repair')
        for _ in range(4):
            budget.attempt('repair');budget.record('repair','review',{'input_tokens':10,'output_tokens':0})
        with self.assertRaisesRegex(Held,'trial_attempt_limit'): budget.attempt('repair')
        budget.finish('repair','ready')
        budget.reserve('en','voice:synthetic:en',trial_package=package,trial_purpose='english')
        with self.assertRaisesRegex(Held,'outcome_unconfirmed'):
            budget.reserve('es','voice:synthetic:es',trial_package=package,trial_purpose='spanish')
        budget.attempt('en');budget.record('en','fresh_audio',{'seconds':2})
        budget.finish('en','ready',voice_receipt={'finalized':True,'close_reason':'close_requested','usage':{'seconds':2},'errors':[],'asr_outcome_confirmed':True,'native_usage_confirmed':True})
        budget.finish('en','held',voice_receipt={'finalized':True,'close_reason':'close_requested','usage':{'seconds':2},'errors':['usage_unconfirmed'],'asr_outcome_confirmed':True,'native_usage_confirmed':True})
        with self.assertRaisesRegex(Held,'outcome_unconfirmed'):
            budget.reserve('blocked','voice:synthetic:es',trial_package=package,trial_purpose='spanish')
        budget.finish('en','held',voice_receipt={'finalized':True,'close_reason':'close_requested','usage':{'seconds':2},'errors':[],'asr_outcome_confirmed':False})
        with self.assertRaisesRegex(Held,'outcome_unconfirmed'):
            budget.reserve('blocked','voice:synthetic:es',trial_package=package,trial_purpose='spanish')
        budget.finish('en','ready',voice_receipt={'finalized':True,'close_reason':'close_requested','usage':{'seconds':2},'errors':[],'asr_outcome_confirmed':True,'native_usage_confirmed':True})
        for purpose in ('spanish','native_repair','recovery'):
            budget.reserve(purpose,'voice:synthetic:es' if purpose=='spanish' else 'voice:synthetic:en',trial_package=package,trial_purpose=purpose,repair_basis='named offline repair' if purpose=='native_repair' else None)
            budget.attempt(purpose);budget.record(purpose,'fresh_audio',{'seconds':2})
            budget.finish(purpose,'ready',voice_receipt={'finalized':True,'close_reason':'close_requested','usage':{'seconds':2},'errors':[],'asr_outcome_confirmed':True,'native_usage_confirmed':True})
        with self.assertRaisesRegex(Held,'trial_package_exhausted'):
            budget.reserve('extra',trial_package=package,trial_purpose='text_initial')
        rows=json.loads(self.path.read_text())['runs']
        self.assertAlmostEqual(sum(r['reserved_usd'] for r in rows),.42)
        self.assertEqual(sum(r['requests_max'] for r in rows),52)

    def test_bilingual_batch_preserves_history_caps_repair_and_unknown_settlement(self):
        from jobs import BILINGUAL_TRIAL_PACKAGE as package
        budget=Budget(self.path)
        def reserve(name,purpose,language='en',**kwargs):
            budget.reserve(name,'voice:synthetic:'+language,trial_package=package,trial_purpose=purpose,**kwargs)
        with self.assertRaisesRegex(Held,'trial_prerequisite'):reserve('skip','roundtrip')
        reserve('en','english')
        budget.attempt('en');budget.record('en','fresh_audio',{'seconds':2})
        receipt={'finalized':True,'close_reason':'close_requested','usage':{'seconds':2},'errors':[],
                 'asr_outcome_confirmed':True,'native_usage_confirmed':False}
        budget.finish('en','held',voice_receipt=receipt)
        with self.assertRaisesRegex(Held,'outcome_unconfirmed'):reserve('repair','conditional_repair',repair_basis='named offline accounting repair')
        receipt['native_usage_confirmed']=True
        budget.finish('en','held',voice_receipt=receipt)
        with self.assertRaisesRegex(Held,'trial_repair_required'):reserve('es','spanish','es')
        with self.assertRaisesRegex(Held,'trial_repair_scope'):
            reserve('wrong','conditional_repair',repair_basis='named offline checked speech repair',trial_scenario='roundtrip',repair_of='en')
        reserve('repair','conditional_repair',repair_basis='named offline checked speech repair',trial_scenario='english',repair_of='en')
        for number in range(16):
            budget.attempt('repair')
            budget.record('repair','fresh_audio' if number==15 else 'review',{'seconds':2} if number==15 else {'input_tokens':10,'output_tokens':0})
        with self.assertRaisesRegex(Held,'trial_attempt_limit'):budget.attempt('repair')
        budget.finish('repair','ready',voice_receipt=receipt)
        for purpose,language in [('spanish','es'),('roundtrip','en'),('cancellation','en')]:
            reserve(purpose,purpose,language)
            budget.attempt(purpose);budget.record(purpose,'fresh_audio',{'seconds':2})
            budget.finish(purpose,'ready',voice_receipt=receipt)
        with self.assertRaisesRegex(Held,'trial_package_exhausted'):reserve('retry','conditional_repair',repair_basis='second repair is forbidden')
        rows=json.loads(self.path.read_text())['runs']
        self.assertAlmostEqual(sum(r['reserved_usd'] for r in rows),.65)
        self.assertEqual(sum(r['requests_max'] for r in rows),70)

    def test_partial_text_language_proof_does_not_release_an_unverified_language(self):
        from jobs import STAGED_TRIAL_PACKAGE as package
        from journey import QUESTION_PIN
        budget=Budget(self.path,per_run=.01)
        budget.reserve('partial',trial_package=package,trial_purpose='text_initial')
        for stage in ('journey_text','review','journey_text'):
            budget.attempt('partial');budget.record('partial',stage,{'input_tokens':10,'output_tokens':10 if stage=='journey_text' else 0})
        budget.finish('partial','held','journey_time_drift')
        result={'source_version':QUESTION_PIN,'mode':'fresh_grounded_generation','request_fit':'confirmed',
                'review':'uncalibrated_model_check','raw_visitor_input_sent':False,
                'unit':{'operation':'brief','language':'en','sections':[{'source_id':'question','text':'The question asks whether to approve the legislature’s act replacing the congressional plan.'}]}}
        budget.record_checked_text('partial',result,held_language='es')
        with self.assertRaisesRegex(Held,'trial_prerequisite'):
            budget.reserve('es','voice:synthetic:es',trial_package=package,trial_purpose='spanish')
        budget.reserve('en','voice:synthetic:en',trial_package=package,trial_purpose='english')
        with self.assertRaisesRegex(Held,'outcome_unconfirmed'):
            budget.reserve('recovery','voice:synthetic:en',trial_package=package,trial_purpose='recovery')
        row=json.loads(self.path.read_text())['runs'][0]
        self.assertEqual(row['checked_text_languages'],['en']);self.assertNotIn('unit',row)

    def test_internal_voice_deadline_is_held_without_disguising_it_as_operator_cancel(self):
        class Deadline:
            def run(self,cancel,progress,meter):
                cancel.set()  # Stops further provider dispatch after timeout.
                raise Held('voice_deadline')
        self.jobs.pipeline=Deadline();self.jobs.start(self.token,self.request)
        row=self.wait_terminal()
        self.assertEqual(row['state'],'held');self.assertEqual(row['reason'],'voice_deadline')
        class Uncertain:
            def run(self,cancel,progress,meter):
                cancel.set();raise Held('voice_native_usage_unconfirmed')
        self.jobs.close();self.jobs=Jobs(Uncertain(),Budget(self.path))
        self.token=self.jobs.capabilities()['session_token']
        self.jobs.start(self.token,'native_uncertainty_0002')
        self.jobs.workers[-1].join(1)
        row=self.jobs.public(self.token,'native_uncertainty_0002')
        self.assertEqual(row['state'],'held');self.assertEqual(row['reason'],'voice_native_usage_unconfirmed')

    def test_missing_usage_holds_and_retains_reservation(self):
        class MissingUsage:
            def run(self, cancel, progress, meter): meter('text', None)
        self.jobs.pipeline = MissingUsage(); self.jobs.start(self.token, self.request)
        self.assertEqual(self.wait_terminal()['state'], 'held')
        row = json.loads(self.path.read_text())['runs'][0]
        self.assertEqual(row['reserved_usd'], .10); self.assertNotIn('raw', row)


if __name__ == '__main__': unittest.main()
