"""Loopback review server. Providers require an explicit, bounded server flag."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import re
import importlib.metadata
from providers import Held, OpenAIProvider, Pipeline, admitted_corpus
from jobs import Budget, Jobs

ROOT = Path(__file__).resolve().parent
FILES = {
    '/': (ROOT / 'web/index.html', 'text/html; charset=utf-8'),
    '/app.mjs': (ROOT / 'web/app.mjs', 'text/javascript; charset=utf-8'),
    '/core.mjs': (ROOT / 'web/core.mjs', 'text/javascript; charset=utf-8'),
    '/conversation.mjs': (ROOT / 'web/conversation.mjs', 'text/javascript; charset=utf-8'),
    '/live-client.mjs': (ROOT / 'web/live-client.mjs', 'text/javascript; charset=utf-8'),
    '/style.css': (ROOT / 'web/style.css', 'text/css; charset=utf-8'),
    '/fixture.json': (ROOT / 'fixtures/combat.json', 'application/json'),
    '/logo.svg': (ROOT.parents[1] / 'brand/logos/open-oracle-vote.svg', 'image/svg+xml'),
}
REQUEST_ID = re.compile(r'[a-zA-Z0-9_-]{16,64}\Z')


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError('duplicate')
        result[key] = value
    return result


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, data, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Permissions-Policy', 'microphone=(), camera=(), geolocation=()')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; media-src 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.end_headers()
        try: self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError): pass

    def json_reply(self, status, value):
        self.reply(status, json.dumps(value, allow_nan=False).encode())

    def local(self):
        port = self.server.server_port
        return self.headers.get('Host') in {f'127.0.0.1:{port}', f'localhost:{port}'}

    def do_GET(self):
        if not self.local():
            self.json_reply(403, {'error': 'loopback_only'}); return
        try:
            if self.path == '/api/capabilities':
                caps = self.server.jobs.capabilities() if self.server.jobs else {'mode': 'fixture', 'providers': 'disabled', 'credentials_read': False, 'microphone': 'disabled', 'playback': 'disabled', 'visitor_persistence': False}
                self.json_reply(200, caps)
            elif self.path.startswith('/api/provider/job/') and self.server.jobs:
                request = self.path.removeprefix('/api/provider/job/')
                if not REQUEST_ID.fullmatch(request): raise Held('request_invalid')
                self.json_reply(200, self.server.jobs.public(self.headers.get('X-Session-Token'), request))
            elif self.path in FILES:
                path, mime = FILES[self.path]
                self.reply(200, path.read_bytes(), mime)
            else: self.json_reply(404, {'error': 'not_found'})
        except Held:
            self.json_reply(403, {'error': 'request_unavailable'})

    def do_POST(self):
        self.close_connection = True
        if not self.server.jobs:
            self.json_reply(405, {'error': 'provider_and_intake_routes_disabled'}); return
        if not self.local() or self.headers.get('Origin') != 'http://' + self.headers.get('Host', ''):
            self.json_reply(403, {'error': 'unexpected_origin'}); return
        if self.path not in {'/api/provider/start', '/api/provider/cancel'}:
            self.json_reply(404, {'error': 'not_found'}); return
        lengths = self.headers.get_all('Content-Length', [])
        if (len(lengths) != 1 or not lengths[0].isdigit() or not 0 < int(lengths[0]) <= 1024
                or self.headers.get('Transfer-Encoding') or self.headers.get('Content-Encoding')
                or self.headers.get('Content-Type') != 'application/json'):
            self.json_reply(400, {'error': 'request_invalid'}); return
        self.connection.settimeout(3)
        try:
            body = json.loads(self.rfile.read(int(lengths[0])), object_pairs_hook=strict_object,
                              parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
            keys = {'request_id', 'question_id'} if self.path.endswith('/start') else {'request_id'}
            if type(body) is not dict or set(body) != keys or type(body['request_id']) is not str or not REQUEST_ID.fullmatch(body['request_id']):
                raise ValueError()
            if self.path.endswith('/start') and body['question_id'] != 'rate': raise ValueError()
        except Exception:
            self.json_reply(400, {'error': 'request_invalid'}); return
        try:
            token = self.headers.get('X-Session-Token')
            result = (self.server.jobs.start(token, body['request_id']) if self.path.endswith('/start')
                      else self.server.jobs.cancel(token, body['request_id']))
            self.json_reply(202, result)
        except Held as error:
            self.json_reply(409, {'error': str(error)})


def make_server(port=8894, jobs=None):
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    server.jobs = jobs
    return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8894)
    parser.add_argument('--enable-openai', action='store_true')
    parser.add_argument('--organization')
    parser.add_argument('--project')
    parser.add_argument('--ledger', type=Path)
    parser.add_argument('--max-runs', type=int, default=1)
    args = parser.parse_args()
    jobs = None
    if args.enable_openai:
        try:
            if importlib.metadata.version('websockets') != '15.0.1': raise ValueError()
        except Exception: parser.error('Install the pinned optional provider requirements before enabling providers.')
        if args.ledger is None: parser.error('A private existing authorized ledger is required.')
        ledger = args.ledger.resolve()
        repository = ROOT.parents[1]
        if ledger.is_relative_to(repository) and '.local' not in ledger.parts:
            parser.error('Keep the operational ledger outside Git or under ignored .local/.')
        jobs = Jobs(Pipeline(admitted_corpus(ROOT / 'fixtures/combat.json'), OpenAIProvider(args.organization, args.project)), Budget(ledger), args.max_runs)
    server = make_server(args.port, jobs)
    print(f'OpenOracle local review: http://127.0.0.1:{server.server_port} ({"providers enabled; no capture/playback" if jobs else "fixtures only"})', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        if jobs: jobs.close()
        server.server_close()
