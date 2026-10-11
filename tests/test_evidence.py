import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from open_oracle.corpus import Corpus, ELECTION
from open_oracle.engine import EvidenceLoop
from open_oracle.server import make_server


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus()
        cls.loop = EvidenceLoop(cls.corpus)

    def test_complete_inventory_and_original_spans(self):
        c = self.corpus
        self.assertEqual(c.counts(), dict(contests=55, candidates=62, retentions=11, measures=10))
        official = [e for e in c.evidence.values() if e['source_category'] == 'Official election sample']
        self.assertEqual(len(official), 55 + int(c.amendment7_ready))
        self.assertTrue(all(c.integrity.values()))
        self.assertEqual({e['contest_id'] for e in c.evidence.values()}, set(c.contests))
        for e in official:
            parent = c.jceb if e['source_id'] == 'jceb-sample' else c.kceb
            self.assertEqual(parent[e['start_offset']:e['start_offset'] + len(e['text'])], e['text'])
            self.assertTrue(e['sha256'] and e['original_route'] and e['page'])

    def test_all_contests_answer_with_scoped_exact_evidence(self):
        for c in self.corpus.contests.values():
            with self.subTest(contest=c['id']):
                scope = {'authority': 'JCEB'}
                if c['required_location']:
                    scope['district' if c['scope'] == 'district' else 'municipality'] = c['required_location']
                answer = self.loop.answer('Show the original wording', scope, contest_id=c['id'])
                self.assertEqual(answer['status'], 'answered')
                self.assertTrue(all(e['contest_id'] == c['id'] for e in answer['evidence']))
                self.assertEqual(answer['review']['status'], 'not_run')

    def test_scope_applies_to_search_and_read(self):
        for ident in ('blue-springs', 'independence-bonds', 'lees-summit', 'sni-valley'):
            evidence_id = ident + ':jceb-sample'
            for scope in ({}, {'authority': 'KCEB'}, {'municipality': 'Other city'}, {'election_date': '2024-11-05'}):
                self.assertEqual(self.corpus.search(ident, scope), [])
                self.assertIsNone(self.corpus.read(evidence_id, scope))
        self.assertEqual(self.loop.answer('Blue Springs tax')['status'], 'clarification')

    def test_names_are_not_silently_disambiguated(self):
        self.assertGreater(len(self.corpus.resolve('Wilson')), 1)
        self.assertEqual(len(self.corpus.resolve('Quentin Wilson')), 1)
        self.assertEqual(self.loop.answer('Wilson')['status'], 'clarification')

    def test_gaps_and_boundaries(self):
        cases = [('Who should I vote for?', 'neutrality_boundary'),
                 ('Explain Amendment 3 in 2024', 'insufficient_evidence'),
                 ('Who are the declared write-in candidates?', 'insufficient_evidence'),
                 ('Compare Scott Fitzpatrick and Quentin Wilson positions', 'insufficient_evidence'),
                 ('Which contests are on my ballot?', 'clarification'),
                 ('Where can I vote?', 'official_links')]
        for question, expected in cases:
            with self.subTest(question=question):
                r = self.loop.answer(question)
                self.assertEqual(r['status'], expected)
                self.assertEqual(r['claims'], [])
        self.assertIn('source gap', self.loop.answer('Compare Scott Fitzpatrick and Quentin Wilson positions')['answer'])

    def test_fiscal_numbers_and_qualifiers_are_retained(self):
        expectations = {'combat': ['one-quarter', 'ten years'],
                        'independence-bonds': ['$19,900,000', '20-year'],
                        'blue-springs': ['2.5'], 'sni-valley': ['fifty percent', "previous year's"]}
        for ident, phrases in expectations.items():
            text = self.corpus.evidence[ident + ':jceb-sample']['text']
            for phrase in phrases:
                self.assertIn(phrase, text)

    def test_foreign_selection_and_provider_errors_do_not_release(self):
        wrong = EvidenceLoop(self.corpus, lambda *a: (['amendment-3:jceb-sample'], []))
        r = wrong.answer('COMBAT')
        self.assertEqual(r['status'], 'insufficient_evidence')
        self.assertEqual(r['evidence'], [])
        def fail(*args):
            raise RuntimeError('private provider diagnostic MUST_NOT_LEAK')
        r = EvidenceLoop(self.corpus, fail).answer('COMBAT')
        self.assertEqual(r['status'], 'unavailable')
        self.assertNotIn('MUST_NOT_LEAK', json.dumps(r))

    def test_tampered_reading_copy_blocks_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            pack = Path(temp) / 'OpenOracle-JacksonCounty-2026-Research'
            files = ['jceb/2026-11-03-notice-sample-ballot.pdf', 'raw/kceb-sample.pdf',
                     'jceb/2026-11-03-notice-sample-ballot.md', 'markdown/kceb-sample.md', 'COUNTYWIDE-INVENTORY.md']
            for rel in files:
                target = pack / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((self.corpus.pack / rel).read_bytes())
            copy = pack / files[2]
            copy.write_text(copy.read_text() + '\nChanged reading copy\n')
            changed = Corpus(Path(temp))
            self.assertFalse(changed.integrity['jceb-sample'])
            self.assertEqual(EvidenceLoop(changed).answer('COMBAT')['status'], 'conflict')


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        conn.request(method, path, body, headers or {})
        response = conn.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        conn.close()
        return result

    def test_browser_inventory_original_and_ask(self):
        for path in ('/', '/app.js', '/live.js', '/styles.css', '/api/health', '/api/inventory', '/api/original/jceb-sample', '/api/candidate-original/judge-2026-paul-wilson-lawyer'):
            status, headers, body = self.request('GET', path)
            self.assertEqual(status, 200, path)
            self.assertIn('no-store', headers['Cache-Control'])
        status, _, body = self.request('POST', '/api/ask', json.dumps({'question': 'COMBAT', 'request_id': 'test-request'}), {'Content-Type': 'application/json'})
        r = json.loads(body)
        self.assertEqual((status, r['status'], r['request_id']), (200, 'answered', 'test-request'))

    def test_invalid_requests_and_no_live_default(self):
        for body in ('not-json', '[]', json.dumps({'question': 5}), json.dumps({'question': 'COMBAT', 'scope': {'address': 'private'}})):
            self.assertEqual(self.request('POST', '/api/ask', body, {'Content-Type': 'application/json'})[0], 400)
        self.assertEqual(self.request('GET', '/', headers={'Host': 'untrusted.example'})[0], 403)
        self.assertEqual(self.request('POST', '/api/ask', '{}', {'Content-Type': 'application/json', 'Origin': 'https://untrusted.example'})[0], 403)
        self.assertEqual(self.request('GET', '/../../.env')[0], 404)
        self.assertEqual(self.request('GET', '/api/original/../../.env')[0], 404)
        self.assertEqual(self.request('GET', '/api/candidate-original/../../.env')[0], 404)
        self.assertEqual(self.request('GET', '/api/candidate-original/congress-alford')[0], 404)
        self.assertEqual(self.request('POST', '/api/live/session', '{}', {'Content-Type': 'application/json'})[0], 503)

    def test_malformed_inputs_fail_before_workflow(self):
        for body in (json.dumps({'question':'COMBAT','request_id':'\\ud800'}).replace('\\\\ud800','\\ud800'),
                     '{"question":"COMBAT","extra":' + '[' * 1200 + '0' + ']' * 1200 + '}'):
            self.assertEqual(self.request('POST','/api/ask',body,{'Content-Type':'application/json'})[0],400)
        self.assertEqual(self.request('GET','/',headers={'Host':'[::1'})[0],400)
        self.assertIn(self.request('GET','//[')[0], (400, 404))
        self.assertEqual(self.request('GET','/api/health')[0],200)

    def test_original_hash_is_rechecked_on_every_serve(self):
        import hashlib
        from open_oracle.corpus import KCEB_HASH
        corpus = Corpus()
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'sample.pdf'
            target.write_bytes(corpus.originals['jceb-sample'].read_bytes())
            corpus.originals['jceb-sample'] = target
            server = make_server(port=0,corpus=corpus)
            thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
            def get(path):
                conn=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=3)
                conn.request('GET',path); response=conn.getresponse()
                result=response.status,response.read(); conn.close(); return result
            try:
                self.assertEqual(get('/api/original/jceb-sample')[0],200)
                target.write_bytes(target.read_bytes()+b'altered')
                self.assertEqual(get('/api/original/jceb-sample')[0],404)
                target.unlink()
                self.assertEqual(get('/api/original/jceb-sample')[0],404)
                status, body = get('/api/original/kceb-sample')
                self.assertEqual(status,200)
                self.assertEqual(hashlib.sha256(body).hexdigest(),KCEB_HASH)
            finally:
                server.shutdown(); server.server_close(); thread.join()

    def test_live_route_validates_before_single_session_budget(self):
        # Actual handler/adapter, explicitly stubbed transport and auth guard. No credentials or network.
        from open_oracle.openai_integrations import LiveSessions
        calls = []
        def transport(resource, body):
            calls.append(body)
            return {'session': {'id': 'offline-route-session'}, 'transport': {'type': 'webrtc', 'sdp': 'v=0'}}
        with patch('open_oracle.orchestration.build_selector', return_value=lambda *a: ([], [])), \
             patch('open_oracle.openai_integrations.require_live_authorization'), \
             patch('open_oracle.openai_integrations.LiveSessions', return_value=LiveSessions(transport)):
            server = make_server(port=0, live=True, live_voice=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        def create(payload, origin=True):
            conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=3)
            headers = {'Content-Type': 'application/json'}
            if origin: headers['Origin'] = 'http://127.0.0.1:' + str(server.server_port)
            conn.request('POST', '/api/live/session', json.dumps(payload), headers)
            response = conn.getresponse(); body = response.read(); status = response.status; conn.close()
            return status, json.loads(body)
        try:
            self.assertEqual(create({'sdp': 'v=0'}, origin=False)[0], 403)
            self.assertEqual(create({'sdp': 'bad'})[0], 400)
            self.assertEqual(create({'sdp': None})[0], 400)
            self.assertEqual(calls, [])
            status, result = create({'sdp': 'v=0'})
            self.assertEqual((status, result['execution']), (201, 'offline_stub'))
            self.assertEqual(create({'sdp': 'v=0'})[0], 429)
            self.assertEqual(len(calls), 1)
        finally:
            server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__':
    unittest.main()
