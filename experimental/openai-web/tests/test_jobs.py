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
    def wait_terminal(self):
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            result = self.jobs.public(self.token, self.request)
            if result['state'] in {'ready', 'held', 'cancelled', 'expired'}: return result
            time.sleep(.005)
        self.fail('local fixture did not complete')

    def test_idempotent_request_and_global_run_cap(self):
        self.jobs.start(self.token, self.request); self.assertEqual(self.wait_terminal()['state'], 'ready')
        self.jobs.start(self.token, self.request)
        with self.assertRaises(Held): self.jobs.start(self.token, 'public_request_0002')
        self.assertEqual(len(json.loads(self.path.read_text())['runs']), 1)

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

    def test_missing_usage_holds_and_retains_reservation(self):
        class MissingUsage:
            def run(self, cancel, progress, meter): meter('text', None)
        self.jobs.pipeline = MissingUsage(); self.jobs.start(self.token, self.request)
        self.assertEqual(self.wait_terminal()['state'], 'held')
        row = json.loads(self.path.read_text())['runs'][0]
        self.assertEqual(row['reserved_usd'], .10); self.assertNotIn('raw', row)


if __name__ == '__main__': unittest.main()
