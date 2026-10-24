import importlib.util
import json
from pathlib import Path
import threading
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from urllib.request import Request, urlopen
from urllib.error import HTTPError

spec = importlib.util.spec_from_file_location('review_server', Path(__file__).resolve().parents[1] / 'server.py')
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = server_module.make_server(0, review_tools=True)
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_served_build_has_every_dependency_and_no_store_policy(self):
        for route in server_module.FILES:
            with urlopen(self.url + route) as r:
                self.assertEqual(r.status, 200)
                self.assertTrue(r.read())
                self.assertEqual(r.headers['Cache-Control'], 'no-store')
                self.assertIn("connect-src 'self'", r.headers['Content-Security-Policy'])
                self.assertIn('microphone=()', r.headers['Permissions-Policy'])

    def test_capabilities_are_honest(self):
        with urlopen(self.url + '/api/capabilities') as r:
            result = json.load(r)
            self.assertEqual(result['providers'], 'disabled')
            self.assertFalse(result['credentials_read'])
            self.assertFalse(result['visitor_persistence'])

    def test_no_file_or_secret_paths_are_served(self):
        for path in ['/../README.md', '/.env.local', '/server.py', '/api/original/private', '/fixture.json?private=data']:
            with self.assertRaises(HTTPError) as e:
                urlopen(self.url + path)
            self.assertEqual(e.exception.code, 404)
            e.exception.close()

    def test_no_provider_or_intake_post_can_execute(self):
        for path in ['/api/session', '/api/ask', '/api/intake', '/api/decisions']:
            with self.assertRaises(HTTPError) as e:
                urlopen(Request(self.url + path, data=b'{}', headers={'Content-Type': 'application/json'}))
            self.assertEqual(e.exception.code, 405)
            e.exception.close()

    def test_unexpected_host_is_rejected(self):
        with self.assertRaises(HTTPError) as e:
            urlopen(Request(self.url, headers={'Host': 'attacker.example'}))
        self.assertEqual(e.exception.code, 403)
        e.exception.close()



# Provider HTTP contract uses fake work only; no API credential is read.
import tempfile
from jobs import Budget, Jobs
from test_jobs import ImmediatePipeline


class EnabledServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        ledger = Path(cls.temp.name) / 'ledger.json'
        ledger.write_text(json.dumps({'authorization_usd_max': 200, 'runs': []}))
        cls.jobs = Jobs(ImmediatePipeline(), Budget(ledger))
        cls.server = server_module.make_server(0, cls.jobs)
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()
        with urlopen(cls.url + '/api/capabilities') as r: cls.token = json.load(r)['session_token']
    @classmethod
    def tearDownClass(cls):
        cls.jobs.close(); cls.server.shutdown(); cls.server.server_close(); cls.thread.join(); cls.temp.cleanup()
    def post(self, path, body, token=None, origin=None):
        headers = {'Content-Type': 'application/json', 'X-Session-Token': token or self.token, 'Origin': origin or self.url}
        return urlopen(Request(self.url + path, data=body, headers=headers))

    def test_rejects_raw_visitor_input_unknown_question_duplicate_fields_and_cross_origin(self):
        for body in [b'{"request_id":"public_request_0001","question_id":"rate","text":"private visitor words"}',
                     b'{"request_id":"public_request_0001","question_id":"other"}',
                     b'{"request_id":"public_request_0001","request_id":"public_request_0002","question_id":"rate"}']:
            with self.assertRaises(HTTPError) as e: self.post('/api/provider/start', body)
            self.assertEqual(e.exception.code, 400); e.exception.close()
        body = b'{"request_id":"public_request_0001","question_id":"rate"}'
        with self.assertRaises(HTTPError) as e: self.post('/api/provider/start', body, origin='https://attacker.invalid')
        self.assertEqual(e.exception.code, 403); e.exception.close()

    def test_owner_binding_and_audio_routes_remain_closed(self):
        with self.assertRaises(HTTPError) as e: self.post('/api/provider/start', b'{"request_id":"public_request_0001","question_id":"rate"}', token='wrong-owner')
        self.assertEqual(e.exception.code, 409); e.exception.close()
        for route in ['/api/provider/audio/public_request_0001','/api/session','/.env.local']:
            with self.assertRaises(HTTPError) as e: urlopen(self.url + route)
            self.assertEqual(e.exception.code, 404); e.exception.close()

    def test_cancel_before_start_tombstone_prevents_paid_work(self):
        request = b'{"request_id":"public_cancel_0001"}'
        with self.post('/api/provider/cancel', request) as r: self.assertEqual(r.status, 202)
        with self.assertRaises(HTTPError) as e: self.post('/api/provider/start', b'{"request_id":"public_cancel_0001","question_id":"rate"}')
        self.assertEqual(e.exception.code, 409); e.exception.close()
        self.assertEqual(self.jobs.runs, 0)

if __name__ == '__main__': unittest.main()

class ProductSurfaceTests(unittest.TestCase):
    def test_unheard_voice_is_excluded_outside_explicit_local_review(self):
        with tempfile.TemporaryDirectory() as folder:
            approved=json.loads((server_module.ROOT.parents[1]/'docs/rebuild/EXPERIENCE-ASSET-PIN.json').read_text())
            (Path(folder)/'manifest.json').write_text(json.dumps(approved))
            routes=server_module.load_experience(folder,review_tools=False)
            self.assertEqual(json.loads(routes['/experience/manifest.json'][0])['audio'],[])
            self.assertFalse(any('/audio/' in route for route in routes))
