"""Replay public native routing/caption events through the actual local web UI.

No provider instance, credential read, remote connection, real budget or media.
This does NOT turn a held trace into success. The banner and status identify the
replay; checked text/speech from older contracts is deliberately not replayed.
Run with --trace /absolute/public-synthetic-receipt.json --map-review-dir ... .
"""
import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from jobs import Budget, Jobs
from providers import Held
from journey import QUESTION_PIN

spec = importlib.util.spec_from_file_location('voice_replay_server', ROOT / 'server.py')
web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web)


def public_events(path):
    if path.stat().st_size > 262144:
        raise ValueError('trace_bound')
    trace = json.loads(path.read_text())
    receipt = trace.get('receipt', {})
    if (receipt.get('mode') != 'native_live_public_synthetic' or
            receipt.get('human_capture') is not False or receipt.get('speaker_playback') is not False or
            receipt.get('source_version') != QUESTION_PIN or receipt.get('language') != 'en' or
            receipt.get('all_turns_checked') is not False):
        raise ValueError('held_public_synthetic_trace_required')
    # Historical reviewed text no longer meets the new brief bound. Never mint
    # a current successful review/audio receipt from these historical events.
    events = [row for row in trace['events']
              if row.get('stage') in {'listening', 'input_partial', 'routing'}]
    if len(events) > 100 or not any(row.get('view') == 'maps' for row in events):
        raise ValueError('captured_map_route_required')
    return events


class Replay:
    voice_fixtures = 'held_public_trace_replay_only'
    voice_languages = ['en']

    def __init__(self, events):
        self.events = events

    def run_task(self, task, cancel, progress, meter):
        if task != 'voice:synthetic:en':
            raise Held('replay_language_unavailable')
        for event in self.events:
            delay = 8 if event['stage'] == 'listening' and event['turn'] == 2 else .15
            if cancel.wait(delay):
                raise Held('cancelled')
            progress('audio', event)
        if cancel.wait(15):
            raise Held('cancelled')
        raise Held('captured_run_held')


class ReplayJobs(Jobs):
    def capabilities(self):
        result = super().capabilities()
        result.update(mode='offline_public_trace_replay', providers='disabled', credentials_read=False)
        return result


class ReplayHandler(web.Handler):
    def reply(self, status, data, content_type='application/json'):
        if status == 200 and self.path in {'/', '/voice'}:
            banner = (b'<aside role="note"><strong>OFFLINE PUBLIC TRACE REPLAY / EVENTOS SIN CONEXION</strong>'
                      b'<p>No API calls, charges or audio. Historical model routes and provisional captions only; '
                      b'the recorded failure is preserved. This is UI testing, not live-conversation evidence.</p></aside>')
            data = data.replace(b'<body>', b'<body>' + banner, 1)
        super().reply(status, data, content_type)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace', type=Path, required=True)
    parser.add_argument('--map-review-dir', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8925)
    args = parser.parse_args()
    events = public_events(args.trace)
    with tempfile.TemporaryDirectory(prefix='openoracle-replay-') as temporary:
        ledger = Path(temporary) / 'fixture-ledger.json'
        ledger.write_text(json.dumps({'authorization_usd_max': 200, 'runs': []}))
        jobs = ReplayJobs(Replay(events), Budget(ledger), max_runs=8)
        server = web.make_server(args.port, jobs, args.map_review_dir, review_tools=True)
        server.RequestHandlerClass = ReplayHandler
        print(f'OFFLINE PUBLIC TRACE REPLAY http://127.0.0.1:{server.server_port}/; no API, credential or audio', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            jobs.close()
            server.server_close()


if __name__ == '__main__':
    main()
