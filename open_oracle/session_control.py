"""Bounded volatile visitor operations and accepted receipts; no persistence or telemetry."""
from contextvars import ContextVar
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import threading
import time
from uuid import UUID

current_cancel = ContextVar('open_oracle_cancel', default=None)

class SessionCancelled(Exception):
    pass

def check_cancel():
    signal = current_cancel.get()
    if signal is not None and signal.is_set():
        raise SessionCancelled('Visitor session stopped')

@contextmanager
def operation(signal):
    token = current_cancel.set(signal)
    try:
        check_cancel()
        yield
        check_cancel()
    finally:
        current_cancel.reset(token)

def valid_session(value):
    if not isinstance(value, str) or len(value) != 36:
        return False
    try:
        return str(UUID(value)) == value.lower()
    except ValueError:
        return False

def accepted_speech(result, corpus):
    from .quality_policy import release_block
    from .claim_bindings import validate_factual_display
    if (not isinstance(result, dict) or result.get('status') != 'answered'
            or result.get('review', {}).get('execution') != 'real_api'
            or result['review'].get('status') != 'accepted'
            or result.get('fact_validation', {}).get('status') != 'supported'
            or result.get('language') != 'en' or result.get('translation_status') != 'not_requested'):
        return None
    speech = result.get('speech')
    if (not isinstance(speech, dict) or speech.get('request_id') != result.get('request_id')
            or speech.get('text') != result.get('answer') or speech.get('language') != 'en'
            or not 0 < len(speech.get('text', '')) <= 1800 or not speech.get('evidence_bindings')):
        return None
    if release_block(result, corpus) or validate_factual_display(result, corpus).get('status') != 'supported':
        return None
    for binding in speech['evidence_bindings']:
        source = next((e for e in result['evidence'] if e['id'] == binding.get('id')), None)
        if not source or any(binding.get(k) != source[k] for k in ('sha256', 'text')):
            return None
        # Corpus construction checks are insufficient if a retained original changed later.
        original = corpus.originals.get(source.get('source_id'))
        if original is None:
            original_bytes = corpus.candidate_sources.original(source.get('source_id'))
        else:
            try:
                original_bytes = original.read_bytes()
            except OSError:
                return None
        if not original_bytes or hashlib.sha256(original_bytes).hexdigest() != source['sha256']:
            return None
    return deepcopy(speech)

class VisitorSessions:
    def __init__(self, now=time.monotonic, capacity=32, ttl=600):
        self.now, self.capacity, self.ttl = now, capacity, ttl
        self.lock = threading.RLock()
        self.entries = {}

    def _prune(self):
        for key, item in list(self.entries.items()):
            if self.now() - item['touched'] > self.ttl and not item['active']:
                del self.entries[key]

    def begin(self, session_id):
        if session_id is None:
            return threading.Event()
        if not valid_session(session_id):
            raise ValueError('Invalid session identity')
        with self.lock:
            self._prune()
            item = self.entries.get(session_id)
            if item is None:
                if len(self.entries) >= self.capacity:
                    raise ValueError('Session capacity reached')
                item = {'cancel': threading.Event(), 'receipt': None, 'touched': self.now(), 'active': 0}
                self.entries[session_id] = item
            if item['cancel'].is_set():
                raise SessionCancelled('Session was erased')
            item['active'] += 1
            item['touched'] = self.now()
            return item['cancel']

    def end(self, session_id):
        with self.lock:
            item = self.entries.get(session_id)
            if item:
                item['active'] = max(0, item['active'] - 1)

    def retain(self, session_id, result, corpus):
        if not session_id:
            return
        contract = accepted_speech(result, corpus)
        with self.lock:
            item = self.entries.get(session_id)
            if item and not item['cancel'].is_set():
                item['receipt'] = deepcopy(result) if contract else None
                contest = result.get('contest') or {}
                from .claim_bindings import fingerprint, validate_factual_display
                if result.get('status') == 'answered' and corpus.contest_fingerprints.get(contest.get('id')) == fingerprint(contest) and validate_factual_display(result, corpus).get('status') == 'supported':
                    item['context'] = {'contest_id': contest['id'], 'scope': deepcopy(result.get('scope',{}))}
                item['touched'] = self.now()


    def contextual_contest(self, session_id, question, scope, explicit, corpus):
        """Volatile verified contest ID only; no transcript history or eligibility."""
        import re
        if explicit is not None or corpus.resolve(question): return explicit
        if not re.search(r'^(?:and\b|what about\b|how do (?:their|they)\b)|\b(?:their|they|them)\b', question.strip(), re.I): return None
        with self.lock:
            item = self.entries.get(session_id)
            if not item or item['cancel'].is_set() or self.now()-item['touched'] > self.ttl: return None
            context = item.get('context')
            if not context or any(context['scope'].get(k) != scope.get(k) for k in ('authority','municipality','district')): return None
            if scope.get('election_date','2026-11-03') != context['scope'].get('election_date','2026-11-03'): return None
            return context['contest_id']

    def speech(self, session_id, request_id, corpus):
        with self.lock:
            item = self.entries.get(session_id)
            if not item or item['cancel'].is_set() or self.now() - item['touched'] > 180:
                return None
            result = item['receipt']
            if not result or result['request_id'] != request_id:
                return None
            return accepted_speech(result, corpus)

    def erase(self, session_id):
        if not valid_session(session_id):
            raise ValueError('Invalid session identity')
        with self.lock:
            self._prune()
            item = self.entries.get(session_id)
            if item is None:
                if len(self.entries) >= self.capacity:
                    raise ValueError('Session capacity reached')
                item = {'cancel': threading.Event(), 'receipt': None, 'touched': self.now(), 'active': 0}
                self.entries[session_id] = item
            item['cancel'].set()
            item['receipt'] = None
            item.pop('context',None)
            item['touched'] = self.now()

