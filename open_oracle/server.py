"""Loopback-first local browser host. No writes, authentication stores, or telemetry exports."""
from __future__ import annotations

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlparse, parse_qs

from .corpus import Corpus, ELECTION, JCEB_HASH, KCEB_HASH, SNAPSHOT
from .engine import EvidenceLoop

ROOT = Path(__file__).resolve().parents[1]


def make_server(host="127.0.0.1", port=8765, live=False, corpus=None, allowed_hosts=(), decisions=False, live_voice=False, bedrock=False, max_live_requests=None, input_events=None, operator_name=None, live_ws=False, research=False, triage=False):
    if operator_name is not None and (not isinstance(operator_name, str) or not 1 <= len(operator_name.strip()) <= 100 or any(ord(c) < 32 for c in operator_name)):
        raise ValueError('Operator name must be short, readable text')
    if research and (not live or bedrock or live_voice or live_ws or host not in ('127.0.0.1', 'localhost', '::1') or max_live_requests is None):
        raise ValueError('Research requires capped loopback OpenAI live text mode; voice remains off')
    if live and bedrock:
        raise ValueError("Choose one Strands model provider")
    if input_events is not None and host not in ('127.0.0.1', 'localhost', '::1'):
        raise ValueError('Input metadata requires loopback-only app hosting')
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
    budget_lock = threading.Lock()
    remaining_requests = max_live_requests
    if research:
        from .research_engine import build_research_engine
        engine = build_research_engine(corpus, reviewer)
    else:
        engine = EvidenceLoop(corpus, selector, reviewer)
    if triage:
        # Opt-in Decisions input triage ahead of the engine; requires the same paid-review authorization.
        if reviewer is None:
            raise ValueError('Triage requires enabled Decisions review')
        from .triage import DecisionsTriage, TriagedEngine
        engine = TriagedEngine(engine, DecisionsTriage(), corpus)
    slots = threading.BoundedSemaphore(4)
    voice_slot = threading.BoundedSemaphore(1)
    voice_requested = False
    if live_ws and not live_voice:
        raise ValueError('WebSocket speech requires explicitly enabled live voice')
    from .session_control import VisitorSessions, SessionCancelled, operation, valid_session
    sessions = VisitorSessions()
    safe_hosts = {"127.0.0.1", "localhost", "::1", *allowed_hosts}
    if host not in ("0.0.0.0", "::"):
        safe_hosts.add(host)

    class Handler(BaseHTTPRequestHandler):
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
                                "voice_session_available": bool(voice and not voice_requested),
                                "speech_transport": "websocket" if live_ws else "webrtc" if voice else None,
                                "input_events": {"enabled": input_events is not None},
                                "operator_name": operator_name})
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
            elif path in ("/", "/devices", "/devices.js", "/copilot", "/copilot.js", "/app.js", "/interaction.js", "/input-bridge.js", "/live.js", "/styles.css", "/orb.js", "/orb.css", "/orb-noise.png", "/intelligent.js"):
                filename = "index.html" if path == "/" else "devices.html" if path == "/devices" else "copilot.html" if path == "/copilot" else path[1:]
                types = {"devices.html": "text/html; charset=utf-8", "devices.js": "text/javascript; charset=utf-8", "copilot.html": "text/html; charset=utf-8", "copilot.js": "text/javascript; charset=utf-8", "index.html": "text/html; charset=utf-8", "app.js": "text/javascript; charset=utf-8", "interaction.js": "text/javascript; charset=utf-8", "input-bridge.js": "text/javascript; charset=utf-8", "live.js": "text/javascript; charset=utf-8", "styles.css": "text/css; charset=utf-8",
                         "orb.js": "text/javascript; charset=utf-8", "orb.css": "text/css; charset=utf-8",
                         "orb-noise.png": "image/png", "intelligent.js": "text/javascript; charset=utf-8"}
                self.send(200, (ROOT / "web" / filename).read_bytes(), types[filename])
            else:
                self.send(404, {"error": "Not found"})

        def do_POST(self):
            nonlocal voice_requested
            if not self.trusted():
                return
            path = urlparse(self.path).path
            session_id = self.headers.get('X-Oracle-Session')
            if session_id is not None and not valid_session(session_id):
                self.send(400, {'error': 'Invalid visitor session identity'})
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
                try:
                    contract = sessions.speech(session_id, data['request_id'], corpus)
                    if not contract:
                        self.send(409, {'error': 'No current server-accepted speech receipt'})
                        return
                    if not voice_slot.acquire(blocking=False):
                        self.send(429, {'error': 'The voice-session allowance is used'})
                        return
                    voice_requested = True
                    from .ws_speech import render_speech
                    with operation(cancel):
                        result = render_speech(contract, cancel)
                        if sessions.speech(session_id, data['request_id'], corpus) != contract:
                            self.send(409, {'error': 'Accepted answer or sources changed; speech withheld'})
                            return
                        self.send(200, result)
                except SessionCancelled:
                    self.send(410, {'error': 'Session erased; speech discarded'})
                except Exception:
                    self.send(502, {'error': 'Speech did not finish; usage may have occurred. Read the accepted answer.'})
                finally:
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
                # One billable session creation per server run. Restart explicitly to retry.
                if not voice_slot.acquire(blocking=False):
                    self.send(429, {"error": "A GPT-Live session was already requested. Restart the server to create another."})
                    return
                voice_requested = True
                try:
                    self.send(201, voice.create(data["sdp"]))
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
                        sessions.retain(session_id, answer, corpus)
                        events = release_events(answer, data["threadId"], data["runId"], corpus=engine.corpus)
                        self.send(200, encode_events(events), "text/event-stream; charset=utf-8")
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
                scope = data.get("scope", {})
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
                    sessions.retain(session_id, answer, corpus)
                    self.send(200, answer)
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
    parser.add_argument('--sensor-stdin', action='store_true', help='Opt-in bounded metadata from an approved producer over stdin; no HTTP injection endpoint')
    parser.add_argument('--sensor-presence', action='store_true', help='Declare externally verified presence/departure support; does not install a detector')
    parser.add_argument('--sensor-wave', action='store_true', help='Declare externally verified deliberate wave support; not motion-only staging')
    parser.add_argument('--sensor-local-wake', action='store_true', help='Declare separately authorized and verified local wake detector; installs no microphone listener')
    parser.add_argument('--operator-name', help='Confirmed supervisor/operator display name; no government affiliation implied')
    args = parser.parse_args()
    if (args.sensor_presence or args.sensor_wave or args.sensor_local_wake) and not args.sensor_stdin:
        parser.error('Sensor capabilities require --sensor-stdin')
    inbox = None
    if args.sensor_stdin:
        import sys
        from .input_events import InputEvents
        inbox = InputEvents(presence=args.sensor_presence, wave=args.sensor_wave, local_wake=args.sensor_local_wake)

    server = make_server(args.host, args.port, args.live, allowed_hosts=args.allowed_host,
                         decisions=args.decisions, live_voice=args.live_voice, bedrock=args.bedrock, max_live_requests=args.max_live_requests, input_events=inbox, operator_name=args.operator_name, live_ws=args.live_ws, research=args.research, triage=args.triage)
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
