"""Loopback review server. Providers require an explicit, bounded server flag."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import re
import hashlib
import importlib.metadata
import io
import wave
from providers import Held, OpenAIProvider, Pipeline, admitted_corpus
from jobs import Budget, Jobs
from layout import ProductPipeline, RECIPES
from journey import TASKS
from fresh_speech import TASKS as SPEECH_TASKS

ROOT = Path(__file__).resolve().parent
FILES = {
    '/': (ROOT / 'web/index.html', 'text/html; charset=utf-8'),
    '/diagnostics': (ROOT / 'web/diagnostics.html', 'text/html; charset=utf-8'),
    '/experience.mjs': (ROOT / 'web/experience.mjs', 'text/javascript; charset=utf-8'),
    '/experience-core.mjs': (ROOT / 'web/experience-core.mjs', 'text/javascript; charset=utf-8'),
    '/map-status.json': (ROOT / 'fixtures/map-status.json', 'application/json'),
    '/proposition-a.json': (ROOT / 'fixtures/proposition-a.json', 'application/json'),
    '/measure-source.mjs': (ROOT / 'web/measure-source.mjs', 'text/javascript; charset=utf-8'),
    '/view-timing.mjs': (ROOT / 'web/view-timing.mjs', 'text/javascript; charset=utf-8'),
    '/layout-client.mjs': (ROOT / 'web/layout-client.mjs', 'text/javascript; charset=utf-8'),
    '/input-intent.mjs': (ROOT / 'web/input-intent.mjs', 'text/javascript; charset=utf-8'),
    '/journey-core.mjs': (ROOT / 'web/journey-core.mjs', 'text/javascript; charset=utf-8'),
    '/reading-guide.mjs': (ROOT / 'web/reading-guide.mjs', 'text/javascript; charset=utf-8'),
    '/reading-guides.json': (ROOT / 'fixtures/reading-guides.json', 'application/json'),
    '/inventory-view.mjs': (ROOT / 'web/inventory-view.mjs', 'text/javascript; charset=utf-8'),
    '/recap-view.mjs': (ROOT / 'web/recap-view.mjs', 'text/javascript; charset=utf-8'),
    '/office-source.mjs': (ROOT / 'web/office-source.mjs', 'text/javascript; charset=utf-8'),
    '/office-contexts.json': (ROOT / 'fixtures/office-contexts.json', 'application/json'),
    '/house-office.json': (ROOT / 'fixtures/house-office.json', 'application/json'),
    '/contest-inventory.json': (ROOT / 'fixtures/contest-inventory.json', 'application/json'),
    '/kc-public-sample.json': (ROOT / 'fixtures/kc-public-sample.json', 'application/json'),
    '/official-nextsteps.json': (ROOT / 'fixtures/official-nextsteps.json', 'application/json'),
    '/sample-house-contest.json': (ROOT / 'fixtures/sample-house-contest.json', 'application/json'),
    '/readings.mjs': (ROOT / 'web/readings.mjs', 'text/javascript; charset=utf-8'),
    '/speech-output.mjs': (ROOT / 'web/speech-output.mjs', 'text/javascript; charset=utf-8'),
    '/map-view.mjs': (ROOT / 'web/map-view.mjs', 'text/javascript; charset=utf-8'),
    '/experience.css': (ROOT / 'web/experience.css', 'text/css; charset=utf-8'),
    '/app.mjs': (ROOT / 'web/app.mjs', 'text/javascript; charset=utf-8'),
    '/core.mjs': (ROOT / 'web/core.mjs', 'text/javascript; charset=utf-8'),
    '/conversation.mjs': (ROOT / 'web/conversation.mjs', 'text/javascript; charset=utf-8'),
    '/live-client.mjs': (ROOT / 'web/live-client.mjs', 'text/javascript; charset=utf-8'),
    '/style.css': (ROOT / 'web/style.css', 'text/css; charset=utf-8'),
    '/fixture.json': (ROOT / 'fixtures/combat.json', 'application/json'),
    '/logo.svg': (ROOT.parents[1] / 'brand/logos/open-oracle-vote.svg', 'image/svg+xml'),
    '/maps': (ROOT / 'web/maps.html', 'text/html; charset=utf-8'),
    '/maps.css': (ROOT / 'web/maps.css', 'text/css; charset=utf-8'),
    '/maps.mjs': (ROOT / 'web/maps.mjs', 'text/javascript; charset=utf-8'),
    '/map-core.mjs': (ROOT / 'web/map-core.mjs', 'text/javascript; charset=utf-8'),
    '/map-review-pin.json': (ROOT.parents[1] / 'docs/rebuild/MAP-DERIVATIVE-PIN.json', 'application/json'),
    '/map-manifest.json': (ROOT.parents[1] / 'docs/rebuild/MAP-SOURCE-MANIFEST.json', 'application/json'),
}
REVIEW_ROUTES={'/diagnostics','/app.mjs','/conversation.mjs','/live-client.mjs','/style.css','/maps','/maps.mjs'}
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
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; media-src blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
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
                if self.headers.get('Sec-Fetch-Site') not in {None, 'same-origin', 'none'}: raise Held('unexpected_site')
                caps = self.server.jobs.capabilities() if self.server.jobs else {'mode': 'fixture', 'providers': 'disabled', 'credentials_read': False, 'microphone': 'disabled', 'playback': 'disabled', 'visitor_persistence': False}
                caps['review_tools']=self.server.review_tools
                self.json_reply(200, caps)
            elif self.path.startswith('/api/provider/job/') and self.server.jobs:
                request = self.path.removeprefix('/api/provider/job/')
                if not REQUEST_ID.fullmatch(request): raise Held('request_invalid')
                self.json_reply(200, self.server.jobs.public(self.headers.get('X-Session-Token'), request))
            elif self.path.startswith('/api/provider/audio/') and self.server.jobs and self.server.review_tools:
                request=self.path.removeprefix('/api/provider/audio/')
                if not REQUEST_ID.fullmatch(request): raise Held('request_invalid')
                self.reply(200,self.server.jobs.audio(self.headers.get('X-Session-Token'),request),'audio/wav')
            elif self.path in self.server.experience:
                raw, mime = self.server.experience[self.path]
                self.reply(200, raw, mime)
            elif self.path == '/maps.json' and self.server.maps is not None:
                self.reply(200, self.server.maps)
            elif self.path in REVIEW_ROUTES and not self.server.review_tools:
                self.json_reply(404, {'error':'not_found'})
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
            if type(body) is dict and 'parent_request_id' in body and self.path.endswith('/start'):
                keys.add('parent_request_id')
                if type(body['parent_request_id']) is not str or not REQUEST_ID.fullmatch(body['parent_request_id']) or not str(body.get('question_id','')).startswith(('journey:','speech:')): raise ValueError()
            if type(body) is not dict or set(body) != keys or type(body['request_id']) is not str or not REQUEST_ID.fullmatch(body['request_id']):
                raise ValueError()
            if self.path.endswith('/start') and body['question_id'] not in {'rate', *('layout:' + key for key in RECIPES), *TASKS,*SPEECH_TASKS}: raise ValueError()
            if self.path.endswith('/start') and body['question_id'].startswith('speech:') and not self.server.review_tools: raise ValueError()
            if self.path.endswith('/start') and body['question_id'].startswith(('journey:','speech:')) and body['question_id'].endswith(':es') and not self.server.review_tools: raise ValueError()
        except Exception:
            self.json_reply(400, {'error': 'request_invalid'}); return
        try:
            token = self.headers.get('X-Session-Token')
            result = (self.server.jobs.start(token, body['request_id'], body['question_id'] if body['question_id'].startswith(('layout:', 'journey:','speech:')) else None, parent_request=body.get('parent_request_id')) if self.path.endswith('/start')
                      else self.server.jobs.cancel(token, body['request_id']))
            self.json_reply(202, result)
        except Held as error:
            self.json_reply(409, {'error': str(error)})


def load_maps(directory):
    directory = Path(directory).resolve()
    paths = [(directory / name).resolve() for name in ['maps.json', 'receipt.json']]
    if any(p.parent != directory or not p.is_file() for p in paths): raise ValueError('map_paths')
    if paths[0].stat().st_size > 8 * 1024 * 1024 or paths[1].stat().st_size > 16384: raise ValueError('map_bounds')
    raw = paths[0].read_bytes()
    receipt = json.loads(paths[1].read_text())
    approved = json.loads((ROOT.parents[1] / 'docs/rebuild/MAP-DERIVATIVE-PIN.json').read_text())
    actual = hashlib.sha256(raw).hexdigest()
    if actual != approved['sha256'] or len(raw) != approved['bytes'] or actual != receipt.get('sha256'):
        raise ValueError('map_integrity')
    data = json.loads(raw)
    registry = json.loads((ROOT.parents[1] / 'docs/rebuild/MAP-SOURCE-MANIFEST.json').read_text())
    if (data.get('version') != 1 or data.get('projection') != 'EPSG:5070' or data.get('sources') != registry['sources']
            or receipt.get('source_hashes_verified') != 4 or receipt.get('districts_per_plan') != [8, 8]
            or receipt.get('original_and_projected_geometry_valid') is not True): raise ValueError('map_admission')
    # Snapshot bytes once; a later file mutation cannot change this review server.
    return raw


def load_experience(directory, review_tools=False):
    if directory is None: return {'/experience/manifest.json': (b'{"version":1,"audio":[]}', 'application/json')}
    directory = Path(directory).resolve()
    approved = json.loads((ROOT.parents[1] / 'docs/rebuild/EXPERIENCE-ASSET-PIN.json').read_text())
    manifest = directory / 'manifest.json'
    if not manifest.is_file() or manifest.stat().st_size > 32768: raise ValueError('experience_manifest')
    if json.loads(manifest.read_text()) != approved: raise ValueError('experience_pin')
    admitted = dict(approved, audio=[a for a in approved['audio'] if review_tools or a.get('acoustic_human_review') is True])
    routes = {'/experience/manifest.json': (json.dumps(admitted).encode(), 'application/json')}
    for asset in admitted['audio']:
        if not re.fullmatch(r'[a-z]{2,12}-(?:en|es)', asset['id']): raise ValueError('audio_id')
        path = (directory / (asset['id'] + '.wav')).resolve()
        if path.parent != directory or not path.is_file() or not 44 <= path.stat().st_size <= 4 * 1024 * 1024: raise ValueError('audio_path')
        raw = path.read_bytes()
        if len(raw) != asset['bytes'] or hashlib.sha256(raw).hexdigest() != asset['sha256']: raise ValueError('audio_integrity')
        with wave.open(io.BytesIO(raw), 'rb') as audio:
            if audio.getnchannels() != 1 or audio.getsampwidth() != 2 or audio.getframerate() != 24000 or not 0 < audio.getnframes() <= 24000 * 40:
                raise ValueError('audio_format')
        routes['/experience/audio/' + asset['id'] + '.wav'] = (raw, 'audio/wav')
    return routes


def make_server(port=8894, jobs=None, map_review_dir=None, experience_dir=None, review_tools=False):
    maps = load_maps(map_review_dir) if map_review_dir else None
    experience = load_experience(experience_dir, review_tools)
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    server.jobs = jobs
    server.maps = maps
    server.experience = experience
    server.review_tools = review_tools
    return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8894)
    parser.add_argument('--enable-openai', action='store_true')
    parser.add_argument('--organization')
    parser.add_argument('--project')
    parser.add_argument('--ledger', type=Path)
    parser.add_argument('--max-runs', type=int, default=1)
    parser.add_argument('--text-model', choices=['gpt-6-luna','gpt-6.1-sol'], default='gpt-6-luna')
    parser.add_argument('--map-review-dir', type=Path)
    parser.add_argument('--experience-dir', type=Path)
    parser.add_argument('--review-tools', action='store_true')
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
        jobs = Jobs(ProductPipeline(Pipeline(admitted_corpus(ROOT / 'fixtures/combat.json'), OpenAIProvider(args.organization, args.project)), allow_spanish=args.review_tools, text_model=args.text_model), Budget(ledger, journey_reserve=.10 if args.text_model == 'gpt-6.1-sol' else .01), args.max_runs)
    server = make_server(args.port, jobs, args.map_review_dir, args.experience_dir, args.review_tools)
    print(f'OpenOracle local review: http://127.0.0.1:{server.server_port} ({"bounded providers enabled" if jobs else "providers off"}; microphone off; manual speaker consent required)', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        if jobs: jobs.close()
        server.server_close()
