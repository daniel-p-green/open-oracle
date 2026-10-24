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

    def test_unknown_owner_cannot_start_read_or_cancel(self):
        for action in [self.jobs.start, self.jobs.public, self.jobs.cancel]:
            with self.assertRaises(Held): action('not_the_owner', self.request)
        self.assertEqual(json.loads(self.path.read_text())['runs'], [])

    def test_cancel_before_start_is_a_tombstone_not_a_late_paid_request(self):
        self.jobs.cancel(self.token, self.request)
        with self.assertRaises(Held): self.jobs.start(self.token, self.request)
        self.assertEqual(self.jobs.runs, 0)

    def test_cancelling_ready_result_discards_server_audio_and_citations(self):
        self.jobs.start(self.token, self.request); self.wait_terminal(); self.jobs.cancel(self.token, self.request)
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
