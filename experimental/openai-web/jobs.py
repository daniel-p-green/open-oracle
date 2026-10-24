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
from fresh_speech import speech_preflight
from latency import StageTiming

TOKEN_TTL = 600
JOB_TTL = 120
VOICE_TRIAL_PACKAGE = 'native_voice_four_trials_20261024'
VOICE_TRIAL_PURPOSES = {'english_diagnostic', 'repair_verification', 'spanish', 'recovery'}
STAGED_TRIAL_PACKAGE = 'native_voice_staged_six_20261024'
STAGED_TRIAL_LIMITS = {'text_initial': (.01, 4), 'text_repair': (.01, 4),
                       'english': (.10, 11), 'spanish': (.10, 11),
                       'native_repair': (.10, 11), 'recovery': (.10, 11)}


class Budget:
    def __init__(self, path, per_run=.10, journey_reserve=.01):
        self.path = Path(path).resolve()
        self.per_run = per_run
        self.journey_reserve = journey_reserve
        if journey_reserve not in {.01,.10}: raise Held('budget_configuration')
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

    def reserve(self, run, task=None, *, trial_package=None, trial_purpose=None, repair_basis=None):
        speech=bool(task and task.startswith('speech:'))
        voice=bool(task and task.startswith('voice:synthetic:'))
        amount = .10 if speech or voice else self.journey_reserve if task and task.startswith('journey:') else min(self.per_run, .01) if task else self.per_run
        with self.locked() as data:
            maximum = data.get('authorization_usd_max')
            runs = data.get('runs')
            if type(maximum) not in (int, float) or not math.isfinite(maximum) or not 0 < maximum <= 200 or not isinstance(runs, list):
                raise Held('budget_invalid')
            amounts = [r.get('reserved_usd') for r in runs]
            if any(type(n) not in (int, float) or not math.isfinite(n) or n < 0 for n in amounts): raise Held('budget_invalid')
            if sum(amounts) + amount > maximum: raise Held('budget_exhausted')
            if trial_package == STAGED_TRIAL_PACKAGE:
                if trial_purpose not in STAGED_TRIAL_LIMITS: raise Held('trial_package_invalid')
                expected, attempts = STAGED_TRIAL_LIMITS[trial_purpose]
                text_trial = trial_purpose.startswith('text_')
                if amount != expected or (text_trial and task is not None) or (not text_trial and not voice):
                    raise Held('trial_package_invalid')
                if 'repair' in trial_purpose and (type(repair_basis) is not str or not 10 <= len(repair_basis) <= 200):
                    raise Held('trial_repair_basis_required')
                previous = [r for r in runs if r.get('trial_package') == trial_package]
                if (len(previous) >= 6 or sum(r['reserved_usd'] for r in previous) + amount > .420001
                        or sum(r['requests_max'] for r in previous) + attempts > 52
                        or any(r.get('trial_purpose') == trial_purpose for r in previous)):
                    raise Held('trial_package_exhausted')
                if any(r.get('state') == 'reserved' or r.get('trial_closure_confirmed') is not True for r in previous):
                    raise Held('trial_package_outcome_unconfirmed')
                if trial_purpose != 'text_initial' and not previous: raise Held('trial_prerequisite')
                if not text_trial and not any(r.get('trial_purpose') in {'text_initial','text_repair'} and r.get('state') == 'ready' for r in previous):
                    raise Held('trial_prerequisite')
                # A semantic hold requires diagnosis and its allocated repair,
                # never another unchanged-language run merely to get a pass.
                if previous and previous[-1].get('state') == 'held' and 'repair' not in trial_purpose:
                    raise Held('trial_repair_required')
            elif trial_package is not None or trial_purpose is not None:
                if trial_package != VOICE_TRIAL_PACKAGE or trial_purpose not in VOICE_TRIAL_PURPOSES or not voice:
                    raise Held('trial_package_invalid')
                previous = [r for r in runs if r.get('trial_package') == trial_package]
                if (len(previous) >= 4 or sum(r['reserved_usd'] for r in previous) + amount > .400001
                        or any(r.get('trial_purpose') == trial_purpose for r in previous)):
                    raise Held('trial_package_exhausted')
                if any(r.get('state') == 'reserved' or r.get('trial_closure_confirmed') is not True or not any(s.get('stage') == 'fresh_audio' for s in r.get('stages',[])) for r in previous):
                    raise Held('trial_package_outcome_unconfirmed')
            journey = bool(task and task.startswith('journey:'))
            runs.append({'id': run, 'kind': 'native_live_synthetic_loop' if voice else 'fresh_public_speech' if speech else 'fresh_public_journey' if journey else 'bounded_ui_composition' if task else 'integrated_public_rate', 'state': 'reserved',
                         'reserved_usd': amount, 'retry': False, 'requests_max': 9 if voice else 2 if journey or speech else 1 if task else 4, 'stages': []})
            if trial_package:
                runs[-1].update(trial_package=trial_package, trial_purpose=trial_purpose)
                if trial_package == STAGED_TRIAL_PACKAGE:
                    runs[-1].update(requests_max=attempts, requests_attempted=0)
                    if repair_basis: runs[-1]['repair_basis'] = repair_basis
            data['conservative_reservations_usd'] = sum(amounts) + amount
            data['state'] = 'integrated public-provider test in flight'

    def attempt(self, run):
        """Atomic pre-dispatch counter for the staged public test transport."""
        with self.locked() as data:
            row = next(r for r in data['runs'] if r['id'] == run)
            if row.get('trial_package') != STAGED_TRIAL_PACKAGE or row['state'] != 'reserved':
                raise Held('trial_package_invalid')
            if row['requests_attempted'] >= row['requests_max']: raise Held('trial_attempt_limit')
            row['requests_attempted'] += 1

    def record(self, run, stage, usage):
        if not isinstance(usage, dict): raise Held('usage_unconfirmed')
        if stage in {'audio','fresh_audio','transcription'}:
            seconds = usage.get('seconds')
            maximum=75 if stage=='fresh_audio' else 60 if stage=='transcription' else 40
            if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0 <= seconds <= maximum: raise Held('usage_unconfirmed')
            safe = {'seconds': seconds}
            if stage=='transcription': safe['basis']='submitted_waveform_duration_not_invoice'
            estimate = seconds * (.0045 if stage=='transcription' else .05) / 60
        else:
            incoming, outgoing = usage.get('input_tokens'), usage.get('output_tokens')
            details = usage.get('input_tokens_details', {})
            cached, written = details.get('cached_tokens', 0), details.get('cache_write_tokens', 0)
            if any(type(n) is not int or not 0 <= n <= 20000 for n in (incoming, outgoing, cached, written)) or cached + written > incoming:
                raise Held('usage_unconfirmed')
            if stage == 'text' and outgoing > 128: raise Held('usage_bound')
            if stage == 'journey_text' and outgoing > 512: raise Held('usage_bound')
            if stage == 'sol_text' and outgoing > 1536: raise Held('usage_bound')
            safe = {'input_tokens': incoming, 'output_tokens': outgoing, 'cached_tokens': cached, 'cache_write_tokens': written}
            estimate = (((incoming-cached-written)*2 + cached*.10 + written*5 + outgoing*10) if stage == 'sol_text' else
                        ((incoming - cached - written) * .10 + cached * .01 + written * .125 + (outgoing * .50 if stage in {'text', 'journey_text'} else 0))) / 1_000_000
        with self.locked() as data:
            row = next(r for r in data['runs'] if r['id'] == run)
            row['stages'].append({'stage': stage, 'usage': safe, 'price_estimate_usd': estimate})
            row['direct_usage_price_estimate_usd'] = sum(s['price_estimate_usd'] for s in row['stages'])
            row['invoice_confirmed'] = False

    def finish(self, run, state, reason=None, *, voice_receipt=None):
        with self.locked() as data:
            row = next(r for r in data['runs'] if r['id'] == run)
            row['state'] = state
            if row.get('trial_package') == STAGED_TRIAL_PACKAGE and row['trial_purpose'].startswith('text_'):
                row['trial_closure_confirmed'] = (0 < row['requests_attempted'] <= row['requests_max']
                    and len(row['stages']) == row['requests_attempted'])
            if row.get('trial_package') and voice_receipt is not None:
                usage=voice_receipt.get('usage',{}) if type(voice_receipt) is dict else {}
                seconds=usage.get('seconds') if type(usage) is dict else None
                final_usage=[s['usage']['seconds'] for s in row['stages'] if s['stage']=='fresh_audio']
                confirmed=(voice_receipt.get('finalized') is True and voice_receipt.get('close_reason')=='close_requested'
                           and type(seconds) in (int,float) and 0<seconds<=75 and final_usage==[seconds]
                           and not set(voice_receipt.get('errors',[])) & {'voice_usage_unconfirmed','voice_close_unconfirmed','voice_closure_unconfirmed'}) if type(voice_receipt) is dict else False
                row['trial_closure_confirmed']=confirmed
                row['voice_closure']={'finalized':voice_receipt.get('finalized') is True,
                                      'close_reason':'close_requested' if voice_receipt.get('close_reason')=='close_requested' else 'unconfirmed',
                                      'metered_usage_match':confirmed} if type(voice_receipt) is dict else {'finalized':False,'close_reason':'unconfirmed','metered_usage_match':False}
            if reason is not None: row['outcome_reason'] = reason
            data['state'] = 'latest integrated run ' + state
            data['direct_usage_price_estimate_usd'] = sum(r.get('price_estimate_usd', r.get('direct_usage_price_estimate_usd', 0)) for r in data['runs'])


class Jobs:
    def __init__(self, pipeline, budget, max_runs=1, clock=time.monotonic):
        if type(max_runs) is not int or not 1 <= max_runs <= 8: raise Held('run_limit')
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
                ready_public_context = row['state'] == 'ready' and str(row.get('task','')).startswith('journey:')
                ready_speech=row['state']=='ready' and str(row.get('task','')).startswith('speech:')
                expired=((now-row.get('ready_at',row['created'])>=JOB_TTL or now-row['created']>=240) if ready_speech
                         else not ready_public_context and now-row['created']>=JOB_TTL)
                if expired or now - owner['created'] >= TOKEN_TTL:
                    row['cancel'].set(); row['result'] = row['audio'] = row['prior'] = None; row['state'] = 'expired'
                    row.pop('updates',None)
            for row in owner['jobs'].values():
                if str(row.get('task','')).startswith('speech:'):
                    parent=owner['jobs'].get(row.get('parent_request'))
                    if not parent or parent['state']!='ready':
                        row['cancel'].set();row['result']=row['audio']=row['prior']=None;row['state']='expired'
        self.owners = {token: value for token, value in self.owners.items()
                       if now - value['created'] < TOKEN_TTL or any(r.get('in_flight') for r in value['jobs'].values())}

    def capabilities(self):
        with self.lock:
            self._expire()
            if len(self.owners) >= 8:
                inactive=[(token,owner) for token,owner in self.owners.items() if all(not r.get('in_flight') for r in owner['jobs'].values())]
                if not inactive: raise Held('owner_capacity')
                del self.owners[min(inactive,key=lambda item:item[1]['created'])[0]]
            token = secrets.token_urlsafe(32)
            self.owners[token] = {'created': self.clock(), 'jobs': {}, 'cancelled': set()}
            return {'mode': 'public_provider_pilot', 'providers': 'enabled', 'microphone': 'disabled',
                    'playback': 'disabled', 'visitor_persistence': False, 'credentials_read': True,
                    'layout_enabled': hasattr(self.pipeline, 'run_task'), 'session_token': token, 'remaining_runs': max(0, self.max_runs - self.runs)}

    def _owner(self, token):
        self._expire()
        owner = self.owners.get(token)
        if owner is None or self.clock()-owner['created']>=TOKEN_TTL: raise Held('owner_unavailable')
        return owner

    def start(self, token, request, task=None, parent_request=None):
        with self.lock:
            owner = self._owner(token)
            if owner.get('blocked'):raise Held('owner_unavailable')
            if request in owner['cancelled']: raise Held('cancelled')
            if request in owner['jobs']:
                if owner['jobs'][request].get('task') != task or owner['jobs'][request].get('parent_request') != parent_request: raise Held('request_conflict')
                return self.public(token, request)
            prior = None
            if parent_request:
                parent = owner['jobs'].get(parent_request)
                if (not task or not task.startswith(('journey:','speech:')) or not parent or parent['state'] != 'ready'
                        or type(parent.get('result')) is not dict or not parent['result'].get('unit') or parent['result'].get('mode') != 'fresh_grounded_generation'):
                    raise Held('parent_unavailable')
                prior = copy.deepcopy(parent['result'])
            if task and task.startswith('speech:') and not prior: raise Held('parent_unavailable')
            if task and task.startswith('speech:'):speech_preflight(prior,task.split(':')[1])
            if self.runs >= self.max_runs: raise Held('run_limit')
            if any(r.get('in_flight') for o in self.owners.values() for r in o['jobs'].values()):
                raise Held('busy')
            run = secrets.token_hex(12)
            self.budget.reserve(run, task) if task else self.budget.reserve(run)
            self.runs += 1
            row = {'created': self.clock(), 'timing': StageTiming(self.clock), 'state': 'queued', 'cancel': threading.Event(),
                   'result': None, 'audio': None, 'run': run, 'reason': None, 'task': task, 'in_flight': True, 'prior': prior, 'parent_request': parent_request}
            owner['jobs'][request] = row
            worker = threading.Thread(target=self._run, args=(row,), daemon=True, name='openoracle-public-run')
            self.workers.append(worker); worker.start()
            return self.public(token, request)

    def _run(self, row):
        def progress(stage, update=None):
            with self.lock:
                self._expire()
                check_cancel(row['cancel']); row['timing'].advance(stage); row['state'] = stage
                if update is not None:
                    if not str(row.get('task','')).startswith('voice:synthetic:') or len(json.dumps(update))>32768:
                        raise Held('voice_update_bound')
                    updates=row.setdefault('updates',[])
                    revision=row.get('update_revision',0)+1
                    if revision>128: raise Held('voice_update_bound')
                    row['update_revision']=revision
                    if update.get('stage')=='input_partial':
                        updates[:]=[item for item in updates if not (item.get('stage')=='input_partial' and item.get('turn')==update.get('turn'))]
                    updates.append(copy.deepcopy(dict(update, revision=revision)))
                    if len(updates)>16: raise Held('voice_update_bound')
        def meter(stage, usage): self.budget.record(row['run'], stage, usage)
        try:
            result, pcm = (self.pipeline.run_task(row['task'], row['cancel'], progress, meter, prior=row['prior']) if row['task'] and row['task'].startswith(('journey:','speech:'))
                           else self.pipeline.run_task(row['task'], row['cancel'], progress, meter) if row['task']
                           else self.pipeline.run(row['cancel'], progress, meter))
            check_cancel(row['cancel'])
            with self.lock:
                self._expire()
                check_cancel(row['cancel'])
                if self.clock() - row['created'] >= JOB_TTL: raise Held('expired')
                self.budget.finish(row['run'], 'ready')
                row.update(state='ready', result=copy.deepcopy(result), audio=bytes(pcm),ready_at=self.clock())
                row['timing'].advance('ready', terminal=True)
        except Held as error:
            with self.lock:
                row.update(state='expired' if row['state']=='expired' or str(error)=='expired' else 'cancelled' if row['state']=='cancel_requested' or row['cancel'].is_set() and str(error)!='voice_deadline' else 'held', reason=str(error), result=None, audio=None)
        except Exception:
            with self.lock: row.update(state='held', reason='provider_failure', result=None, audio=None)
        finally:
            try:
                if row['state'] != 'ready': self.budget.finish(row['run'], row['state'], row['reason'])
            except Exception:
                with self.lock: row.update(state='held', reason='ledger_unavailable', result=None, audio=None)
            finally:
                with self.lock:
                    row['timing'].advance(row['state'], terminal=True)
                    row['in_flight']=False

    def public(self, token, request):
        with self.lock:
            owner = self._owner(token)
            row = owner['jobs'].get(request)
            if row is None: raise Held('job_unavailable')
            lifetime_left = (TOKEN_TTL - (self.clock()-owner['created']) if row['state']=='ready' and str(row.get('task','')).startswith('journey:')
                             else min(JOB_TTL-(self.clock()-row.get('ready_at',row['created'])),240-(self.clock()-row['created']),TOKEN_TTL-(self.clock()-owner['created'])) if row['state']=='ready' and str(row.get('task','')).startswith('speech:')
                             else JOB_TTL-(self.clock()-row['created']))
            return copy.deepcopy({'request_id': request, 'state': row['state'], 'reason': row['reason'],
                                  'result': row['result'], 'playback_enabled': False, 'timing': row['timing'].snapshot(),
                                  **({'updates':row.get('updates',[])} if str(row.get('task','')).startswith('voice:synthetic:') and row['state'] not in {'held','cancelled','cancel_requested','expired'} else {}),
                                  'expires_in_seconds': max(0, lifetime_left)})

    def cancel(self, token, request):
        with self.lock:
            owner = self._owner(token)
            if len(owner['cancelled']) >= 16 and request not in owner['cancelled'] and request not in owner['jobs']:
                # Saturation must never permit a delayed Start after Erase.
                owner['blocked']=True
                for pending in owner['jobs'].values():
                    pending['cancel'].set();pending['result']=pending['audio']=pending['prior']=None;pending['state']='cancel_requested'
            if len(owner['cancelled'])<16:owner['cancelled'].add(request)
            # Existing job rows themselves prevent restarting cancelled work.
            row = owner['jobs'].get(request)
            if row:
                row['cancel'].set(); row['result'] = row['audio'] = None
                row.pop('updates',None)
                row['prior'] = None
                row['state'] = 'cancelled' if row['state'] in {'ready', 'held', 'cancelled', 'expired'} else 'cancel_requested'
            # Revocation reaches dependent speech even after its WAV was prepared.
            for child in owner['jobs'].values():
                if child.get('parent_request')==request and str(child.get('task','')).startswith('speech:'):
                    child['cancel'].set();child['result']=child['audio']=child['prior']=None;child['state']='cancel_requested'
            return {'request_id': request, 'state': 'cancel_requested', 'result': None, 'playback_enabled': False}

    def audio(self, token, request):
        with self.lock:
            owner=self._owner(token);row=owner['jobs'].get(request)
            parent=owner['jobs'].get(row.get('parent_request')) if row else None
            if (not row or not str(row.get('task','')).startswith('speech:') or row['state']!='ready'
                    or not parent or parent['state']!='ready' or type(row.get('audio')) is not bytes
                    or not row['audio'] or row['cancel'].is_set()): raise Held('audio_unavailable')
            return bytes(row['audio'])

    def close(self):
        self.stopping.set()
        with self.lock:
            for owner in self.owners.values():
                for row in owner['jobs'].values():
                    row['cancel'].set(); row['result'] = row['audio'] = None

        for worker in self.workers: worker.join(timeout=17)
