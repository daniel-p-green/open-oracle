"""Single-run local ownership, cancellation, conservative spend reservation and TTL."""
import copy
import fcntl
import json
import math
import os
import secrets
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from providers import Held, check_cancel

TOKEN_TTL = 600
JOB_TTL = 120


class Budget:
    def __init__(self, path, per_run=.10):
        self.path = Path(path).resolve()
        self.per_run = per_run
        if not 0 < per_run <= .10 or not self.path.is_file(): raise Held('budget_configuration')

    @contextmanager
    def locked(self):
        with open(str(self.path) + '.lock', 'a') as lock:
            os.chmod(lock.name, 0o600)
            fcntl.flock(lock, fcntl.LOCK_EX)
            data = json.loads(self.path.read_text())
            yield data
            descriptor, name = tempfile.mkstemp(dir=self.path.parent)
            try:
                with os.fdopen(descriptor, 'w') as target:
                    json.dump(data, target, indent=2); target.write('\n')
                os.replace(name, self.path)
            finally:
                if os.path.exists(name): os.unlink(name)

    def reserve(self, run):
        with self.locked() as data:
            maximum = data.get('authorization_usd_max')
            runs = data.get('runs')
            if type(maximum) not in (int, float) or not math.isfinite(maximum) or not 0 < maximum <= 200 or not isinstance(runs, list):
                raise Held('budget_invalid')
            amounts = [r.get('reserved_usd') for r in runs]
            if any(type(n) not in (int, float) or not math.isfinite(n) or n < 0 for n in amounts): raise Held('budget_invalid')
            if sum(amounts) + self.per_run > maximum: raise Held('budget_exhausted')
            runs.append({'id': run, 'kind': 'integrated_public_rate', 'state': 'reserved',
                         'reserved_usd': self.per_run, 'retry': False, 'requests_max': 4, 'stages': []})
            data['conservative_reservations_usd'] = sum(amounts) + self.per_run
            data['state'] = 'integrated public-provider test in flight'

    def record(self, run, stage, usage):
        if not isinstance(usage, dict): raise Held('usage_unconfirmed')
        if stage == 'audio':
            seconds = usage.get('seconds')
            if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0 <= seconds <= 40: raise Held('usage_unconfirmed')
            safe = {'seconds': seconds}
            estimate = seconds * .05 / 60
        else:
            incoming, outgoing = usage.get('input_tokens'), usage.get('output_tokens')
            details = usage.get('input_tokens_details', {})
            cached, written = details.get('cached_tokens', 0), details.get('cache_write_tokens', 0)
            if any(type(n) is not int or not 0 <= n <= 20000 for n in (incoming, outgoing, cached, written)) or cached + written > incoming:
                raise Held('usage_unconfirmed')
            if stage == 'text' and outgoing > 128: raise Held('usage_bound')
            safe = {'input_tokens': incoming, 'output_tokens': outgoing, 'cached_tokens': cached, 'cache_write_tokens': written}
            estimate = ((incoming - cached - written) * .10 + cached * .01 + written * .125 + (outgoing * .50 if stage == 'text' else 0)) / 1_000_000
        with self.locked() as data:
            row = next(r for r in data['runs'] if r['id'] == run)
            row['stages'].append({'stage': stage, 'usage': safe, 'price_estimate_usd': estimate})
            row['direct_usage_price_estimate_usd'] = sum(s['price_estimate_usd'] for s in row['stages'])
            row['invoice_confirmed'] = False

    def finish(self, run, state):
        with self.locked() as data:
            next(r for r in data['runs'] if r['id'] == run)['state'] = state
            data['state'] = 'latest integrated run ' + state
            data['direct_usage_price_estimate_usd'] = sum(r.get('price_estimate_usd', r.get('direct_usage_price_estimate_usd', 0)) for r in data['runs'])


class Jobs:
    def __init__(self, pipeline, budget, max_runs=1, clock=time.monotonic):
        if type(max_runs) is not int or not 1 <= max_runs <= 2: raise Held('run_limit')
        self.pipeline, self.budget, self.max_runs, self.clock = pipeline, budget, max_runs, clock
        self.lock = threading.RLock()
        self.owners = {}
        self.runs = 0
        self.workers = []
        self.stopping = threading.Event()
        self.janitor = threading.Thread(target=self._sweep, daemon=True, name='openoracle-expiry')
        self.janitor.start()

    def _sweep(self):
        while not self.stopping.wait(1):
            with self.lock: self._expire()

    def _expire(self):
        now = self.clock()
        for owner in self.owners.values():
            for row in owner['jobs'].values():
                if now - row['created'] >= JOB_TTL:
                    row['cancel'].set(); row['result'] = row['audio'] = None; row['state'] = 'expired'
        self.owners = {token: value for token, value in self.owners.items()
                       if now - value['created'] < TOKEN_TTL}

    def capabilities(self):
        with self.lock:
            self._expire()
            if len(self.owners) >= 8: raise Held('owner_capacity')
            token = secrets.token_urlsafe(32)
            self.owners[token] = {'created': self.clock(), 'jobs': {}, 'cancelled': set()}
            return {'mode': 'public_provider_pilot', 'providers': 'enabled', 'microphone': 'disabled',
                    'playback': 'disabled', 'visitor_persistence': False, 'credentials_read': True,
                    'session_token': token, 'remaining_runs': max(0, self.max_runs - self.runs)}

    def _owner(self, token):
        self._expire()
        owner = self.owners.get(token)
        if owner is None: raise Held('owner_unavailable')
        return owner

    def start(self, token, request):
        with self.lock:
            owner = self._owner(token)
            if request in owner['cancelled']: raise Held('cancelled')
            if request in owner['jobs']: return self.public(token, request)
            if self.runs >= self.max_runs: raise Held('run_limit')
            if any(r['state'] not in {'ready', 'held', 'cancelled', 'expired'} for o in self.owners.values() for r in o['jobs'].values()):
                raise Held('busy')
            run = secrets.token_hex(12)
            self.budget.reserve(run)
            self.runs += 1
            row = {'created': self.clock(), 'state': 'queued', 'cancel': threading.Event(),
                   'result': None, 'audio': None, 'run': run, 'reason': None}
            owner['jobs'][request] = row
            worker = threading.Thread(target=self._run, args=(row,), daemon=True, name='openoracle-public-run')
            self.workers.append(worker); worker.start()
            return self.public(token, request)

    def _run(self, row):
        def progress(stage):
            with self.lock:
                check_cancel(row['cancel']); row['state'] = stage
        def meter(stage, usage): self.budget.record(row['run'], stage, usage)
        try:
            result, pcm = self.pipeline.run(row['cancel'], progress, meter)
            check_cancel(row['cancel'])
            self.budget.finish(row['run'], 'ready')
            with self.lock:
                check_cancel(row['cancel'])
                if self.clock() - row['created'] >= JOB_TTL: raise Held('expired')
                row.update(state='ready', result=copy.deepcopy(result), audio=bytes(pcm))
        except Held as error:
            with self.lock:
                row.update(state='cancelled' if row['cancel'].is_set() else 'held', reason=str(error), result=None, audio=None)
        except Exception:
            with self.lock: row.update(state='held', reason='provider_failure', result=None, audio=None)
        finally:
            try:
                if row['state'] != 'ready': self.budget.finish(row['run'], row['state'])
            except Exception:
                with self.lock: row.update(state='held', reason='ledger_unavailable', result=None, audio=None)

    def public(self, token, request):
        with self.lock:
            owner = self._owner(token)
            row = owner['jobs'].get(request)
            if row is None: raise Held('job_unavailable')
            return copy.deepcopy({'request_id': request, 'state': row['state'], 'reason': row['reason'],
                                  'result': row['result'], 'playback_enabled': False,
                                  'expires_in_seconds': max(0, JOB_TTL - (self.clock() - row['created']))})

    def cancel(self, token, request):
        with self.lock:
            owner = self._owner(token)
            if len(owner['cancelled']) >= 16 and request not in owner['cancelled']: raise Held('cancel_capacity')
            owner['cancelled'].add(request)  # Tombstone rejects a delayed Start arriving after reset.
            row = owner['jobs'].get(request)
            if row:
                row['cancel'].set(); row['result'] = row['audio'] = None
                row['state'] = 'cancelled' if row['state'] in {'ready', 'held', 'cancelled', 'expired'} else 'cancel_requested'
            return {'request_id': request, 'state': 'cancel_requested', 'result': None, 'playback_enabled': False}

    def close(self):
        self.stopping.set()
        with self.lock:
            for owner in self.owners.values():
                for row in owner['jobs'].values():
                    row['cancel'].set(); row['result'] = row['audio'] = None

        for worker in self.workers: worker.join(timeout=17)
