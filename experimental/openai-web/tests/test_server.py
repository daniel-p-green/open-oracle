import importlib.util
import json
from pathlib import Path
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

spec = importlib.util.spec_from_file_location('review_server', Path(__file__).resolve().parents[1] / 'server.py')
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = server_module.make_server(0)
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


if __name__ == '__main__':
    unittest.main()
