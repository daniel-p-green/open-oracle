"""Loopback-first local browser host. No writes, authentication stores, or telemetry exports."""
from __future__ import annotations

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlparse, parse_qs, parse_qs

from .corpus import Corpus, ELECTION, JCEB_HASH, KCEB_HASH, SNAPSHOT
from .engine import EvidenceLoop

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BRAND_ASSETS = {
    '/brand/fonts/libre-baskerville.ttf': ('brand/fonts/LibreBaskerville[wght].ttf', 'font/ttf'),
    '/brand/fonts/libre-franklin.ttf': ('brand/fonts/LibreFranklin[wght].ttf', 'font/ttf'),
    **{'/icons/phosphor/' + name + '.svg': ('web/icons/phosphor/' + name + '.svg', 'image/svg+xml')
       for name in ('microphone', 'stop', 'eraser', 'arrow-left', 'arrow-right', 'arrow-up-right', 'play', 'phone')},
}


def public_brand_asset(path):
    definition = PUBLIC_BRAND_ASSETS.get(path)
    if definition is None:
        return None
    try:
        file = (ROOT / definition[0]).resolve(strict=True)
        if not file.is_relative_to(ROOT.resolve()) or not file.is_file():
            return None
        return file.read_bytes(), definition[1]
    except OSError:
        return None


def station_context(config, supplied):
    """Admin scope cannot be replaced by a visitor request."""
    allowed = {'election_date', 'authority', 'municipality', 'district'}
    if not isinstance(supplied, dict) or set(supplied) - allowed or any(not isinstance(v, str) or len(v) > 100 for v in supplied.values()):
        raise ValueError('Invalid source context')
    if config is None:
        return dict(supplied)
    if any(key not in config or value != config[key] for key, value in supplied.items()):
        raise ValueError('Use this station context')
    return dict(config)


def configured_station(config):
    if config is None:
        return None
    config = station_context(None, config)
    if config.get('election_date') != ELECTION or config.get('authority') not in ('KCEB', 'JCEB') or ('municipality' in config and 'district' in config) or any(not v or any(ord(c) < 32 for c in v) for v in config.values()):
        raise ValueError('Invalid admin station context')
    return config


def make_server(host="127.0.0.1", port=8765, live=False, corpus=None, allowed_hosts=(), decisions=False, live_voice=False, bedrock=False, max_live_requests=None, input_events=None, operator_name=None, live_ws=False, research=False, triage=False, semantic_backend_factory=None, operations=False, max_voice_sessions=1, intake=False, station_scope=None):
    station_scope = configured_station(station_scope)
    if operator_name is not None and (not isinstance(operator_name, str) or not 1 <= len(operator_name.strip()) <= 100 or any(ord(c) < 32 for c in operator_name)):
        raise ValueError('Operator name must be short, readable text')
    if semantic_backend_factory is not None and not research:
        raise ValueError('Semantic factory requires explicitly capped research mode')
    if research and (not live or bedrock or live_voice or live_ws or host not in ('127.0.0.1', 'localhost', '::1') or max_live_requests is None):
        raise ValueError('Research requires capped loopback OpenAI live text mode; voice remains off')
    if live and bedrock:
        raise ValueError("Choose one Strands model provider")
    if input_events is not None and host not in ('127.0.0.1', 'localhost', '::1'):
        raise ValueError('Input metadata requires loopback-only app hosting')
    if operations and (host not in ("127.0.0.1", "localhost", "::1") or allowed_hosts):
        raise ValueError("Operator operations readout requires untunneled loopback hosting")
    if intake and (host not in ('127.0.0.1', 'localhost', '::1') or allowed_hosts):
        raise ValueError('Private intake requires untunneled loopback hosting')
    corpus = corpus or Corpus()
    selector = None
    if live and not research:
        from .orchestration import build_selector
        selector = build_selector()
    elif bedrock:
        from .orchestration import build_bedrock_selector
        selector = build_bedrock_selector()
    reviewer, voice = None, None
    if decisions or live or bedrock or live_voice:
        from .openai_integrations import DecisionsReviewer, LiveSessions, require_live_authorization
        require_live_authorization()
        reviewer = DecisionsReviewer()
        if live_voice:
            if not (live or bedrock) or host not in ("127.0.0.1", "localhost", "::1"):
                raise ValueError("GPT-Live requires live Strands and a loopback-only host")
            voice = LiveSessions()
    if max_live_requests is not None and (type(max_live_requests) is not int or max_live_requests < 1):
        raise ValueError('max_live_requests must be a positive integer')
    if type(max_voice_sessions) is not int or not 1 <= max_voice_sessions <= 24:
        raise ValueError('max_voice_sessions must be an integer from 1 to 24')
    budget_lock = threading.Lock()
    remaining_requests = max_live_requests
    if research:
        from .research_engine import build_research_engine
        engine = build_research_engine(corpus, reviewer, semantic_backend_factory=semantic_backend_factory)
    else:
        engine = EvidenceLoop(corpus, selector, reviewer)
    if triage:
        # Opt-in Decisions input triage ahead of the engine; requires the same paid-review authorization.
        if reviewer is None:
            raise ValueError('Triage requires enabled Decisions review')
        from .triage import DecisionsTriage, TriagedEngine
        engine = TriagedEngine(engine, DecisionsTriage(), corpus)
    operations_monitor = None
    if operations:
        from oracle_observability import OperationalMonitor, InstrumentedEngine, TrustedVersions
        from oracle_observability.monitor import canonical_hash
        from .quality_policy import REVISED_CHECKS
        from importlib.metadata import version
        source_catalog = {ident: item["sha256"] for ident, item in corpus.evidence.items()}
        if research:
            from strands_quality.research_corpus import load_verified_corpus
            source_catalog = {s.id: s.original_sha256 for s in load_verified_corpus(corpus).sources.values()}
        code_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for folder in ("open_oracle", "strands_quality", "oracle_observability")
                       for p in sorted((ROOT / folder).glob("*.py"))}
        versions = TrustedVersions(deployment_sha256=canonical_hash(code_hashes), source_catalog=source_catalog,
            execution="real_api" if (live or bedrock) else "exact_source", sdk_version=version("strands-agents"),
            rubric_sha256=canonical_hash(REVISED_CHECKS), embeddings_enabled=semantic_backend_factory is not None)
        operations_monitor = OperationalMonitor(versions)
        engine = InstrumentedEngine(engine, operations_monitor)
    slots = threading.BoundedSemaphore(4)
    voice_slot = threading.BoundedSemaphore(1)
    remaining_voice_sessions = max_voice_sessions
    if live_ws and not live_voice:
        raise ValueError('WebSocket speech requires explicitly enabled live voice')
    from .session_control import VisitorSessions, SessionCancelled, operation, valid_session
    sessions = VisitorSessions()
    from .private_intake import PrivateIntake, IntakeFailure
    private_intake = PrivateIntake(sessions) if intake else None
    safe_hosts = {"127.0.0.1", "localhost", "::1", *allowed_hosts}
    if host not in ("0.0.0.0", "::"):
        safe_hosts.add(host)

    class Handler(BaseHTTPRequestHandler):
        def reserve_voice(self):
            nonlocal remaining_voice_sessions
            with budget_lock:
                if remaining_voice_sessions <= 0:
                    self.send(429, {'error': 'The approved voice allowance is used. You can read existing answers and sources.', 'voice_sessions_remaining': 0})
                    return False
                remaining_voice_sessions -= 1
                return True

        def reserve_request(self):
            nonlocal remaining_requests
            with budget_lock:
                if remaining_requests is None or not reviewer:
                    return True
                if remaining_requests <= 0:
                    self.send(429, {'error': 'The approved live-test allowance is used. Existing answers and original documents remain readable. New questions require exact-source mode or another approved allowance.'})
                    return False
                remaining_requests -= 1
                return True

        def log_message(self, *args):
            pass  # Do not retain visitor questions or IP addresses.

        def send(self, status, body, content_type="application/json; charset=utf-8"):
            if isinstance(body, (dict, list)):
                body = json.dumps(body, ensure_ascii=False).encode()
            elif isinstance(body, str):
                body = body.encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; style-src-attr 'unsafe-inline'; connect-src 'self'; media-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def trusted(self):
            raw_host = self.headers.get("Host", "")
            try:
                hostname = urlparse("http://" + raw_host).hostname
                urlparse(self.path)
            except ValueError:
                self.send(400, {"error": "Malformed request"})
                return False
            if hostname not in safe_hosts:
                self.send(403, {"error": "Host is not allowed"})
                return False
            origin = self.headers.get("Origin")
            if origin and origin not in ("http://" + raw_host, "https://" + raw_host):
                self.send(403, {"error": "Cross-origin requests are not allowed"})
                return False
            return True

        def do_GET(self):
            if not self.trusted():
                return
            path = urlparse(self.path).path
            if path == "/api/health":
                self.send(200, {"status": "ready", "mode": "reviewed_strands_research" if research else "live_strands" if selector else "exact_source", "counts": corpus.counts(),
                                "provider": "bedrock" if bedrock else "openai" if live else None,
                                "prepared_candidate_answers": corpus.prepared_sources_ready,
                                "snapshot_date": SNAPSHOT, "election_date": ELECTION, "source_integrity": corpus.integrity,
                                "independent_review": "openai_decisions_enabled" if reviewer else "not_run",
                                "input_triage": "openai_decisions_enabled" if triage else "not_run",
                                "voice": "gpt_live_buffered" if voice else "not_connected",
                                "voice_playback": "buffered_until_transcript_display_validation",
                                "voice_session_available": bool(voice and remaining_voice_sessions > 0),
                                "voice_sessions_remaining": remaining_voice_sessions if voice else 0,
                                "live_requests_remaining": remaining_requests,
                                "station_scope": station_scope,
                                "speech_transport": "websocket" if live_ws else "webrtc" if voice else None,
                                "input_events": {"enabled": input_events is not None},
                                "operator_name": operator_name,
                                "intake": {"enabled": intake, "schema": "open-oracle-private-intake/v1" if intake else None,
                                           "source_admission": "not_implemented", "translation": "blocked",
                                           "readability": "explicit_english_formula_assumption" if intake else "unavailable"}})
            elif path == '/api/data-use':
                from .privacy_faq import data_use_faq
                self.send(200, data_use_faq(live=live, bedrock=bedrock, reviewer=reviewer is not None, voice=voice is not None, websocket=live_ws))
            elif path == '/api/input-events' and input_events is not None:
                try:
                    query = parse_qs(urlparse(self.path).query)
                    if set(query) - {'after'} or len(query.get('after', ['0'])) != 1:
                        raise ValueError('Invalid cursor')
                    cursor = int(query.get('after', ['0'])[0])
                    self.send(200, input_events.snapshot(cursor))
                except (ValueError, TypeError):
                    self.send(400, {'error': 'Invalid input cursor'})
            elif path == "/api/operations" and operations_monitor is not None:
                self.send(200, operations_monitor.snapshot())
            elif path == "/operations" and operations_monitor is not None:
                from oracle_observability.readout import render_dashboard
                self.send(200, render_dashboard(operations_monitor.snapshot()), "text/html; charset=utf-8")
            elif path == "/api/render-catalog":
                from .render_catalog import rendering_catalog, CatalogUnavailable
                try:
                    query = urlparse(self.path).query
                    if len(query) > 1024:
                        raise ValueError('Catalog scope too large')
                    fields = parse_qs(query, keep_blank_values=True, strict_parsing=True, max_num_fields=4)
                    if any(len(values) != 1 for values in fields.values()):
                        raise ValueError('Repeated scope field')
                    catalog = rendering_catalog(corpus, station_context(station_scope, {key:values[0] for key,values in fields.items()}))
                except CatalogUnavailable:
                    self.send(503, {'error':'Rendering definitions unavailable; source version must be reconciled.'})
                    return
                except ValueError:
                    self.send(400, {'error':'Use current election, authority and city or district scope only.'})
                    return
                self.send(200, catalog)
            elif path == "/api/inventory":
                self.send(200, [{k: v for k, v in c.items() if k not in ("aliases", "heading")} for c in corpus.contests.values()])
            elif path == "/api/prepared-source/beacon-atlarge":
                from .demo_sources import original_text
                body = original_text()
                if body:
                    self.send(200, body, "text/plain; charset=utf-8")
                else:
                    self.send(404, {"error": "Prepared source missing or changed"})
            elif path.startswith("/api/candidate-original/"):
                ident = path.removeprefix("/api/candidate-original/")
                body = corpus.candidate_sources.original(ident)
                if body:
                    self.send(200, body, "application/pdf")
                else:
                    self.send(404, {"error": "Retained candidate document unavailable or version changed"})
            elif path == '/api/prepared-source/amendment-7-fair.pdf':
                from .amendment7 import fair_original
                body = fair_original(corpus)
                if body:
                    self.send(200, body, 'application/pdf')
                else:
                    self.send(404, {'error': 'Original source unavailable'})
            elif path == '/api/prepared-source/amendment-7.pdf':
                from .amendment7 import original_pdf
                body = original_pdf(corpus)
                if body:
                    self.send(200, body, 'application/pdf')
                else:
                    self.send(404, {'error': 'Original source unavailable'})
            elif path.startswith("/api/original/"):
                ident = path.removeprefix("/api/original/")
                original = corpus.originals.get(ident)
                body = None
                if original and corpus.integrity.get(ident):
                    try:
                        body = original.read_bytes()
                    except OSError:
                        pass
                    if body is not None and hashlib.sha256(body).hexdigest() != {"jceb-sample": JCEB_HASH, "kceb-sample": KCEB_HASH}.get(ident):
                        body = None
                if body:
                    self.send(200, body, "application/pdf")
                else:
                    self.send(404, {"error": "Original source unavailable"})
            elif path in PUBLIC_BRAND_ASSETS:
                asset = public_brand_asset(path)
                if asset is None:
                    self.send(404, {'error': 'Asset unavailable'})
                else:
                    self.send(200, *asset)
            elif path in ("/", "/website", "/website.css", "/website.js", "/intake.js", "/devices", "/devices.js", "/copilot", "/copilot.js", "/app.js", "/release-store.js", "/render-bindings.js", "/interaction.js", "/input-bridge.js", "/live.js", "/styles.css", "/orb.js", "/orb.css", "/orb-noise.png", "/intelligent.js"):
                filename = "index.html" if path == "/" else "website.html" if path == "/website" else "devices.html" if path == "/devices" else "copilot.html" if path == "/copilot" else path[1:]
                types = {"website.html": "text/html; charset=utf-8", "website.css": "text/css; charset=utf-8", "website.js": "text/javascript; charset=utf-8", "intake.js": "text/javascript; charset=utf-8", "devices.html": "text/html; charset=utf-8", "devices.js": "text/javascript; charset=utf-8", "copilot.html": "text/html; charset=utf-8", "copilot.js": "text/javascript; charset=utf-8", "index.html": "text/html; charset=utf-8", "app.js": "text/javascript; charset=utf-8", "release-store.js": "text/javascript; charset=utf-8", "render-bindings.js": "text/javascript; charset=utf-8", "interaction.js": "text/javascript; charset=utf-8", "input-bridge.js": "text/javascript; charset=utf-8", "live.js": "text/javascript; charset=utf-8", "styles.css": "text/css; charset=utf-8",
                         "orb.js": "text/javascript; charset=utf-8", "orb.css": "text/css; charset=utf-8",
                         "orb-noise.png": "image/png", "intelligent.js": "text/javascript; charset=utf-8"}
                self.send(200, (ROOT / "web" / filename).read_bytes(), types[filename])
            else:
                self.send(404, {"error": "Not found"})

        def intake_request(self, path, session_id):
            if private_intake is None:
                self.send(503, {'error': 'Private intake is disabled'})
                return
            if (self.headers.get('Origin') != 'http://' + self.headers.get('Host', '')
                    or session_id is None or len(self.headers.get_all('X-Oracle-Session', [])) != 1):
                self.send(403, {'error': 'Same-origin visitor session required'})
                return
            if path not in ('/api/intake/state', '/api/intake/prepare', '/api/intake/upload',
                            '/api/intake/commit', '/api/intake/discard', '/api/intake/select'):
                self.send(404, {'error': 'Unknown private intake action'})
                return
            if not private_intake.slot.acquire(blocking=False):
                self.send(429, {'error': 'Private intake is busy; no queued parser or retry'})
                return
            started = False
            previous_timeout = self.connection.gettimeout()
            try:
                self.connection.settimeout(5)
                lengths = self.headers.get_all('Content-Length', [])
                types = self.headers.get_all('Content-Type', [])
                if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit() or len(types) != 1 or self.headers.get('Transfer-Encoding'):
                    raise ValueError('strict_framing_required')
                size = int(lengths[0])
                content_type = types[0].split(';')[0].strip().lower()
                cap = 5*1024*1024 if path == '/api/intake/upload' and content_type == 'application/pdf' else 1024*1024 if path == '/api/intake/prepare' else 256*1024 if path == '/api/intake/upload' else 8192
                if not 0 < size <= cap:
                    self.send(413, {'error': 'Private intake body exceeds its fixed limit'})
                    return
                body = self.rfile.read(size)
                if len(body) != size: raise ValueError('incomplete_body')
                def strict_object(pairs):
                    result = {}
                    for key, value in pairs:
                        if key in result: raise ValueError('duplicate_json_key')
                        result[key] = value
                    return result
                def strict_json(raw):
                    if isinstance(raw, bytes): raw = raw.decode('utf-8', errors='strict')
                    value = json.loads(raw, object_pairs_hook=strict_object,
                                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite_json')))
                    json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
                    if not isinstance(value, dict): raise ValueError('object_required')
                    return value
                if path == '/api/intake/upload':
                    metadata = self.headers.get_all('X-Oracle-Intake', [])
                    if len(metadata) != 1 or len(metadata[0]) > 8192 or not metadata[0].isascii():
                        raise ValueError('private_context_header_required')
                    data = strict_json(metadata[0])
                    expected = {'owner_ticket', 'expected_revision'}
                    if content_type not in ('application/pdf', 'text/plain'):
                        self.send(415, {'error': 'Only PDF or strict UTF-8 text is accepted'})
                        return
                else:
                    if content_type != 'application/json': raise ValueError('json_required')
                    data = strict_json(body)
                    expected = {
                        '/api/intake/state': set(), '/api/intake/prepare': {'owner_ticket', 'expected_revision', 'text'},
                        '/api/intake/commit': {'owner_ticket', 'expected_revision', 'prepared_id'},
                        '/api/intake/discard': {'prepared_id'},
                        '/api/intake/select': {'owner_ticket', 'expected_revision', 'document_id', 'block_id',
                                             'confirmed_complete', 'method_language_assumption'},
                    }[path]
                if set(data) != expected: raise ValueError('unknown_or_missing_fields')
                for key in ('prepared_id', 'document_id', 'block_id'):
                    if key in data and (not isinstance(data[key], str) or not 1 <= len(data[key]) <= 80):
                        raise ValueError('invalid_private_identity')
                if 'expected_revision' in data and (type(data['expected_revision']) is not int or not 0 <= data['expected_revision'] < 2**53-1):
                    raise ValueError('invalid_revision')
                signal = sessions.begin(session_id)
                started = True
                if path == '/api/intake/state': result = private_intake.state(session_id, signal)
                elif path == '/api/intake/discard': result = private_intake.discard(session_id, signal, data['prepared_id'])
                elif path in ('/api/intake/prepare', '/api/intake/upload'):
                    result = private_intake.prepare(session_id, signal, data['owner_ticket'], data['expected_revision'],
                        text=data.get('text'), raw=body if path.endswith('/upload') else None,
                        kind=('pdf' if content_type == 'application/pdf' else 'txt') if path.endswith('/upload') else None)
                elif path == '/api/intake/commit':
                    result, signal = private_intake.commit(session_id, signal, data['prepared_id'], data['owner_ticket'], data['expected_revision'])
                else:
                    result, signal = private_intake.select(session_id, signal, data['document_id'], data['block_id'],
                        data['owner_ticket'], data['expected_revision'], data['confirmed_complete'], data['method_language_assumption'])
                sessions.deliver(session_id, signal, lambda: self.send(200, result))
            except SessionCancelled:
                self.send(410, {'error': 'Session erased or expired; private intake discarded'})
            except IntakeFailure as failure:
                self.send(failure.status, {'error': failure.reason})
            except (ValueError, TypeError, UnicodeError, RecursionError):
                self.send(400, {'error': 'Invalid private intake contract; no source accepted'})
            except Exception:
                self.send(503, {'error': 'Private intake unavailable; no source or answer accepted'})
            finally:
                if started: sessions.end(session_id)
                private_intake.slot.release()
                self.connection.settimeout(previous_timeout)

        def do_POST(self):
            if not self.trusted():
                return
            path = urlparse(self.path).path
            session_id = self.headers.get('X-Oracle-Session')
            if session_id is not None and not valid_session(session_id):
                self.send(400, {'error': 'Invalid visitor session identity'})
                return
            if path.startswith('/api/intake/'):
                self.intake_request(path, session_id)
                return
            if path == '/api/erase':
                if self.headers.get('Origin') != 'http://' + self.headers.get('Host', ''):
                    self.send(403, {'error': 'Same-origin browser required'})
                    return
                try:
                    size = int(self.headers.get('Content-Length', '0'))
                    if not 0 < size <= 64 or json.loads(self.rfile.read(size)) != {}:
                        raise ValueError('Empty JSON object required')
                    sessions.erase(session_id)
                except (ValueError, TypeError, UnicodeError):
                    self.send(400, {'error': 'Use a valid session and empty JSON object'})
                    return
                self.send(200, {'status': 'erased_locally', 'provider_erasure_claimed': False})
                return
            if path == '/api/live/speech':
                if not voice or not live_ws:
                    self.send(503, {'error': 'Server-side GPT-Live speech is off'})
                    return
                if self.headers.get('Origin') != 'http://' + self.headers.get('Host', '') or session_id is None:
                    self.send(403, {'error': 'Same-origin visitor session required'})
                    return
                try:
                    size = int(self.headers.get('Content-Length', '0'))
                    if not 0 < size <= 256 or self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                        raise ValueError('Invalid speech request')
                    data = json.loads(self.rfile.read(size))
                    if not isinstance(data, dict) or set(data) != {'request_id'} or not isinstance(data['request_id'], str) or len(data['request_id']) > 120:
                        raise ValueError('Identity only')
                    cancel = sessions.begin(session_id)
                except SessionCancelled:
                    self.send(410, {'error': 'Session was erased'})
                    return
                except (ValueError, TypeError, UnicodeError):
                    self.send(400, {'error': 'Supply only the accepted request identity'})
                    return
                speech_slot_acquired = False
                try:
                    contract = sessions.speech(session_id, data['request_id'], corpus)
                    if not contract:
                        self.send(409, {'error': 'No current server-accepted speech receipt'})
                        return
                    if not voice_slot.acquire(blocking=False):
                        self.send(429, {'error': 'A spoken answer is already being prepared. Wait for it to finish.'})
                        return
                    speech_slot_acquired = True
                    if not self.reserve_voice():
                        return
                    from .ws_speech import render_speech
                    with operation(cancel):
                        result = render_speech(contract, cancel)
                        if sessions.speech(session_id, data['request_id'], corpus) != contract:
                            self.send(409, {'error': 'Accepted answer or sources changed; speech withheld'})
                            return
                        sessions.deliver(session_id, cancel, lambda: self.send(200, {**result, 'voice_sessions_remaining': remaining_voice_sessions}))
                except SessionCancelled:
                    self.send(410, {'error': 'Session erased; speech discarded'})
                except Exception:
                    self.send(502, {'error': 'Speech did not finish; usage may have occurred. Read the accepted answer.'})
                finally:
                    if speech_slot_acquired:
                        voice_slot.release()
                    sessions.end(session_id)
                return
            if path == "/api/live/session":
                if not voice:
                    self.send(503, {"error": "GPT-Live is not enabled. No session created."})
                    return
                if self.headers.get("Origin") != "http://" + self.headers.get("Host", ""):
                    self.send(403, {"error": "A same-origin local browser is required"})
                    return
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    if not 0 < size <= 65536 or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                        raise ValueError("Invalid request")
                    data = json.loads(self.rfile.read(size))
                    if not isinstance(data, dict) or set(data) != {"sdp"}:
                        raise ValueError("Invalid session request")
                    from .openai_integrations import validate_sdp
                    validate_sdp(data["sdp"])
                except (ValueError, TypeError, UnicodeError, RecursionError):
                    self.send(400, {"error": "Use a JSON SDP offer"})
                    return
                # Attempts consume the explicit allowance even when the provider fails.
                if not self.reserve_voice():
                    return
                try:
                    self.send(201, {**voice.create(data["sdp"]), 'voice_sessions_remaining': remaining_voice_sessions})
                except Exception:
                    self.send(502, {"error": "GPT-Live could not connect. No provider details released; session creation may have incurred usage."})
                return
            if path == "/api/ag-ui":
                # The actual EvidenceLoop finishes grounding/review before any event data.
                from .agui import parse_run, release_events, encode_events
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    if not 0 < size <= 32768 or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                        raise ValueError("Invalid run size/type")
                    data = json.loads(self.rfile.read(size))
                    json.dumps(data, ensure_ascii=False).encode()
                    question, scope, contest_id = parse_run(data)
                    scope = station_context(station_scope, scope)
                except (ValueError, TypeError, UnicodeError, RecursionError):
                    self.send(400, {"error": "Send one current text question with valid scope; client tools are disabled."})
                    return
                if not slots.acquire(blocking=False):
                    self.send(429, {"error": "Busy. Please try again shortly."})
                    return
                try:
                    if not self.reserve_request():
                        return
                    cancel = sessions.begin(session_id)
                    with operation(cancel):
                        context_id = sessions.contextual_contest(session_id, question, scope, contest_id, corpus)
                        answer = engine.answer(question, scope, data["runId"], context_id)
                        sessions.retain(session_id, answer, corpus, signal=cancel)
                        events = release_events(answer, data["threadId"], data["runId"], corpus=engine.corpus)
                        sessions.deliver(session_id, cancel, lambda: self.send(200, encode_events(events), "text/event-stream; charset=utf-8"))
                except SessionCancelled:
                    self.send(410, {'error': 'Session erased; answer discarded'})
                except Exception:
                    self.send(500, {"error": "The gated evidence workflow failed. No event content released."})
                finally:
                    sessions.end(session_id)
                    slots.release()
                return
            if path != "/api/ask":
                self.send(404, {"error": "Not found"})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 8192:
                    raise ValueError("Invalid request size")
                if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                    raise ValueError("JSON content type required")
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict) or set(data) - {"question", "scope", "contest_id", "request_id"} or not isinstance(data.get("question"), str):
                    raise ValueError("Question must be text")
                json.dumps(data, ensure_ascii=False).encode()  # Reject lone surrogates before any model work.
                scope = station_context(station_scope, data.get("scope", {}))
                allowed_fields = {"election_date", "authority", "municipality", "district"}
                if not isinstance(scope, dict) or set(scope) - allowed_fields or any(not isinstance(v, str) or len(v) > 100 for v in scope.values()):
                    raise ValueError("Invalid scope")
                for key in ("contest_id", "request_id"):
                    if key in data and (not isinstance(data[key], str) or len(data[key]) > 120):
                        raise ValueError("Invalid identity")
            except (ValueError, TypeError, UnicodeError, RecursionError):
                self.send(400, {"error": "Use a JSON question and valid text scope."})
                return
            # Local privacy commands never enter ballot retrieval or a paid review.
            from .privacy_faq import erase_intent, faq_intent, data_use_faq
            if erase_intent(data['question']):
                try:
                    sessions.erase(session_id)
                except ValueError:
                    self.send(400, {'error': 'A visitor session is required to erase'})
                    return
                self.send(200, {'status': 'erased_locally', 'provider_erasure_claimed': False})
                return
            if faq_intent(data['question']):
                self.send(200, data_use_faq(live=live, bedrock=bedrock, reviewer=reviewer is not None, voice=voice is not None, websocket=live_ws))
                return
            if not slots.acquire(blocking=False):
                self.send(429, {"error": "Busy. Please try again shortly."})
                return
            try:
                cancel = sessions.begin(session_id)
                if not self.reserve_request():
                    return
                with operation(cancel):
                    context_id = sessions.contextual_contest(session_id, data["question"], scope, data.get("contest_id"), corpus)
                    answer = engine.answer(data["question"], scope, data.get("request_id"), context_id)
                    sessions.retain(session_id, answer, corpus, signal=cancel)
                    sessions.deliver(session_id, cancel, lambda: self.send(200, answer))
            except SessionCancelled:
                self.send(410, {'error': 'Session erased; answer discarded'})
            except Exception:
                self.send(500, {"error": "The evidence workflow failed. No answer released."})
            finally:
                sessions.end(session_id)
                slots.release()

    return ThreadingHTTPServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description="Run Open Oracle locally")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--allowed-host", action="append", default=[])
    parser.add_argument("--live", action="store_true", help="Explicitly enabled, previously authorized model use only")
    parser.add_argument("--research", action="store_true", help="Opt-in real Strands research browser route; requires --live and --max-live-requests; text only")
    parser.add_argument("--bedrock", action="store_true", help="Strands with the AWS event profile and an explicitly selected Bedrock model")
    parser.add_argument("--decisions", action="store_true", help="Enable real OpenAI Decisions checks; requires authorized spending")
    parser.add_argument("--live-voice", action="store_true", help="GPT-Live opt-in capture and buffered, transcript-validated playback")
    parser.add_argument('--live-ws', action='store_true', help='Prepare typed accepted answers with server-side GPT-Live WebSocket PCM; no microphone capture')
    parser.add_argument("--triage", action="store_true", help="Opt-in Decisions input triage and view routing before the engine; requires --decisions or --live")
    parser.add_argument("--max-live-requests", type=int, help="Hard cap on evidence requests with paid checks; no automatic retries")
    parser.add_argument('--max-voice-sessions', type=int, default=1, help='Explicit shared capture/speech session cap (1–24); attempts consume allowance, no retries')
    parser.add_argument('--sensor-stdin', action='store_true', help='Opt-in bounded metadata from an approved producer over stdin; no HTTP injection endpoint')
    parser.add_argument('--sensor-presence', action='store_true', help='Declare externally verified presence/departure support; does not install a detector')
    parser.add_argument('--sensor-wave', action='store_true', help='Declare externally verified deliberate wave support; not motion-only staging')
    parser.add_argument('--sensor-local-wake', action='store_true', help='Declare separately authorized and verified local wake detector; installs no microphone listener')
    parser.add_argument('--sensor-hand-gestures', action='store_true', help='Opt-in validated scalar hand summaries; installs no capture or detector')
    parser.add_argument('--operator-name', help='Confirmed supervisor/operator display name; no government affiliation implied')
    parser.add_argument("--operations", action="store_true", help="Local volatile aggregate readout; requires untunneled loopback hosting; no exporter")
    parser.add_argument('--intake', action='store_true', help='Opt-in private PDF/text preview and explicit English-formula diagnostics; untunneled loopback only, no source admission')
    parser.add_argument("--station-authority", choices=("KCEB", "JCEB"), help="Admin-owned station authority; visitors cannot replace it")
    parser.add_argument("--station-municipality", help="Admin-owned station municipality")
    args = parser.parse_args()
    if args.station_municipality and not args.station_authority:
        parser.error("Station municipality requires station authority")
    station_scope = ({"election_date": ELECTION, "authority": args.station_authority, **({"municipality": args.station_municipality} if args.station_municipality else {})} if args.station_authority else None)
    if (args.sensor_presence or args.sensor_wave or args.sensor_local_wake or args.sensor_hand_gestures) and not args.sensor_stdin:
        parser.error('Sensor capabilities require --sensor-stdin')
    inbox = None
    if args.sensor_stdin:
        import sys
        from .input_events import InputEvents
        inbox = InputEvents(presence=args.sensor_presence, wave=args.sensor_wave, local_wake=args.sensor_local_wake, hand_gestures=args.sensor_hand_gestures)

    server = make_server(args.host, args.port, args.live, allowed_hosts=args.allowed_host,
                         decisions=args.decisions, live_voice=args.live_voice, bedrock=args.bedrock, max_live_requests=args.max_live_requests, input_events=inbox, operator_name=args.operator_name, live_ws=args.live_ws, research=args.research, triage=args.triage, operations=args.operations, max_voice_sessions=args.max_voice_sessions, intake=args.intake, station_scope=station_scope)
    if inbox is not None:
        inbox.start(sys.stdin.buffer)
    print(f"Open Oracle ready at http://{args.host}:{server.server_port} — {'live Strands' if args.live or args.bedrock else 'exact-source mode; no model calls'}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if inbox is not None:
            inbox.stopped()
        server.server_close()


if __name__ == "__main__":
    main()
