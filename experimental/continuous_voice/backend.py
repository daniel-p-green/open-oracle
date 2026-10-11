"""Isolated volatile conversation gate. No endpoints, providers or media devices.

Import into core only after its transport, consent and budget adapters are reviewed.
All input finality is adapter supplied; GPT-Live deltas/delegations are not finals.
"""
from copy import deepcopy
from dataclasses import dataclass
import base64
import math
import threading
import time
import unicodedata
from uuid import uuid4

from open_oracle.session_control import accepted_speech, operation


BASE_KEYS = ('epoch', 'generation', 'turn_id', 'transcript_id', 'request_id')
RELEASE_KEYS = BASE_KEYS + ('release_id', 'speech_id', 'playback_id')


def transcript_matches(expected, actual):
    # Reuse the stricter current language fence. Never erase numeric signs/units.
    from open_oracle.language_speech import canonical_transcript
    try:
        return canonical_transcript(expected) == canonical_transcript(actual)
    except (ValueError, TypeError):
        return False


def valid_wav(encoded):
    if not isinstance(encoded, str) or not 0 < len(encoded) <= 6 * 1024 * 1024:
        return False
    try:
        wav = base64.b64decode(encoded, validate=True)
    except ValueError:
        return False
    # The existing SpeechBuffer produces precisely PCM16 / mono / 24kHz WAV.
    return (44 < len(wav) <= 4320044 and len(wav) % 2 == 0
            and wav[:4] == b'RIFF' and wav[8:16] == b'WAVEfmt '
            and int.from_bytes(wav[4:8], 'little') == len(wav) - 8
            and int.from_bytes(wav[16:20], 'little') == 16
            and int.from_bytes(wav[20:22], 'little') == 1
            and int.from_bytes(wav[22:24], 'little') == 1
            and int.from_bytes(wav[24:28], 'little') == 24000
            and int.from_bytes(wav[28:32], 'little') == 48000
            and int.from_bytes(wav[32:34], 'little') == 2
            and int.from_bytes(wav[34:36], 'little') == 16
            and wav[36:40] == b'data'
            and int.from_bytes(wav[40:44], 'little') == len(wav) - 44)


@dataclass
class Work:
    ticket: dict
    cancel: threading.Event
    deadline: float
    result: dict | None = None
    contract: dict | None = None


class Conversation:
    """Single worker, bounded attempts; caller owns HTTP/auth/session registries.

    finalize must validate a trusted adapter's snapshot AND its identity binding.
    Missing finalize deliberately disables automatic voice submission.
    """
    def __init__(self, corpus, *, finalize=None, max_turns=2, now=time.monotonic,
                 timeout=75, epoch=None):
        if type(max_turns) is not int or not 2 <= max_turns <= 8:
            raise ValueError('Turn allowance must be 2..8')
        if not 0 < timeout <= 75:
            raise ValueError('Invalid deadline')
        self.corpus, self.finalize, self.max_turns = corpus, finalize, max_turns
        self.now, self.timeout = now, timeout
        self.epoch = epoch or str(uuid4())
        self.generation, self.attempts = 0, 0
        self.state, self.active = 'idle', None
        self.session_deadline = None
        self.document_ref, self.accepted_result = None, None
        self.lock = threading.RLock()
        self.seen = set()
        self.counts = {k: 0 for k in ('submitted', 'released', 'rendered', 'completed',
                                      'cancelled', 'withheld', 'stale', 'erased')}

    def identity(self):
        return {'epoch': self.epoch, 'generation': self.generation}

    def _speech(self, result):
        try:
            return accepted_speech(result, self.corpus)
        except Exception:
            return None  # Malformed receipts fail closed without logging content.

    def start(self):
        with self.lock:
            if self.state != 'idle' or self.finalize is None:
                return None
            self.generation += 1
            self.session_deadline = self.now() + 180
            self.state = 'listening'
            return self.identity()

    def listen(self, context):
        """Acknowledge a serialized client control envelope before opening capture.

        Identities are correlation, not authorization. Core must authenticate the
        caller, bind epoch to VisitorSessions and authorize deliberate Start/Resume.
        """
        with self.lock:
            if (not isinstance(context, dict) or context.get('epoch') != self.epoch
                    or type(context.get('generation')) is not int or self.finalize is None
                    or self.active is not None or self.state not in ('idle', 'paused', 'listening')
                    or self.attempts >= self.max_turns
                    or (self.session_deadline is not None and self.now() >= self.session_deadline)
                    or context['generation'] not in (self.generation, self.generation + 1)
                    or (context['generation'] == self.generation and self.state != 'listening')):
                return None
            self.generation = context['generation']
            if self.session_deadline is None:
                self.session_deadline = self.now() + 180
            self.state = 'listening'
            return self.identity()

    def invalidate(self, context, state='paused'):
        """Ordered cancellation control; duplicate same-generation cancels are safe."""
        with self.lock:
            if (not isinstance(context, dict) or context.get('epoch') != self.epoch
                    or type(context.get('generation')) is not int
                    or context['generation'] not in (self.generation, self.generation + 1)
                    or state not in ('paused', 'idle', 'exhausted')
                    or (context['generation'] == self.generation and self.active is not None)):
                return None
            generation = context['generation']
            self._invalidate(state)
            self.generation = generation
            return self.identity()

    def begin(self, ticket, snapshot):
        with self.lock:
            if (self.state != 'listening' or self.attempts >= self.max_turns
                    or self.session_deadline is None or self.now() >= self.session_deadline
                    or not isinstance(ticket, dict) or ticket.get('epoch') != self.epoch
                    or type(ticket.get('generation')) is not int
                    or ticket['generation'] != self.generation
                    or any(not isinstance(ticket.get(k), str) or not 0 < len(ticket[k]) <= 128
                           for k in BASE_KEYS if k != 'generation')
                    or any(ticket[k] in self.seen for k in ('turn_id', 'transcript_id', 'request_id'))
                    or len({ticket.get(k) for k in ('turn_id', 'transcript_id', 'request_id')}) != 3
                    or not isinstance(snapshot, dict) or not isinstance(snapshot.get('text'), str)
                    or not 0 < len(snapshot['text'].strip()) <= 2000):
                return None
            try:
                finalized = self.finalize(snapshot, ticket) is True
            except Exception:
                finalized = False
            if not finalized:
                self.counts['withheld'] += 1
                return None
            self.seen.update(ticket[k] for k in ('turn_id', 'transcript_id', 'request_id'))
            self.attempts += 1
            self.counts['submitted'] += 1
            self.active = Work({k: ticket[k] for k in BASE_KEYS}, threading.Event(),
                               self.now() + self.timeout)
            self.state = 'researching'
            # Caller dispatches the finalized question once, under operation(work.cancel).
            return self.active

    def _current(self, ticket, *, released=False):
        keys = RELEASE_KEYS if released else BASE_KEYS
        return (self.active is not None and isinstance(ticket, dict)
                and not self.active.cancel.is_set() and self.now() < self.active.deadline
                and self.session_deadline is not None and self.now() < self.session_deadline
                and all(ticket.get(k) == self.active.ticket.get(k) for k in keys))

    def release(self, ticket, result):
        with self.lock:
            if not self._current(ticket) or self.state != 'researching':
                self.counts['stale'] += 1
                return None
            contract = self._speech(result)
            if not contract or contract['request_id'] != ticket['request_id']:
                self._invalidate('paused')
                self.counts['withheld'] += 1
                return None
            self.active.ticket.update({k: str(uuid4()) for k in RELEASE_KEYS[5:]})
            self.active.result, self.active.contract = deepcopy(result), contract
            self.accepted_result = deepcopy(result)  # Preserve accepted text on Stop.
            self.state = 'released'
            self.counts['released'] += 1
            return {'ticket': deepcopy(self.active.ticket), 'result': deepcopy(result)}

    def render(self, ticket, renderer):
        """renderer is explicitly injected. No default import/call to paid transport."""
        with self.lock:
            if not self._current(ticket, released=True) or self.state != 'released':
                self.counts['stale'] += 1
                return None
            work = self.active
            contract = self._speech(work.result)
            if not contract or contract != work.contract:
                self._invalidate('paused')
                self.counts['withheld'] += 1
                return None
            self.state = 'rendering'
        try:
            with operation(work.cancel):
                output = renderer(deepcopy(contract), work.cancel)
        except Exception:
            with self.lock:
                if self.active is work:
                    self._invalidate('paused')
                    self.counts['withheld'] += 1
            return None
        with self.lock:
            current_contract = self._speech(work.result)
            if (self.active is not work or self.state != 'rendering'
                    or not self._current(ticket, released=True)
                    or current_contract != contract):
                if isinstance(output, dict):
                    output.clear()
                if self.active is work:
                    self._invalidate('paused')
                self.counts['stale'] += 1
                return None
            report = output.get('report') if isinstance(output, dict) else None
            report = report if isinstance(report, dict) else {}
            usage = output.get('usage') if isinstance(output, dict) else None
            seconds = usage.get('seconds') if isinstance(usage, dict) else None
            valid = (isinstance(output, dict) and output.get('accepted') is True
                     and output.get('request_id') == contract['request_id']
                     and output.get('text') == contract['text']
                     and output.get('language') == contract['language']
                     and isinstance(output.get('transcript'), str)
                     and transcript_matches(contract['text'], output['transcript'])
                     and report.get('acknowledged') is True
                     and report.get('transcript_matches') is True
                     and report.get('invalid_output') is False
                     and report.get('final_usage_confirmed') is True
                     and report.get('close_reason') == 'close_requested'
                     and type(seconds) in (float, int) and math.isfinite(seconds) and seconds >= 0
                     and valid_wav(output.get('wav_base64')))
            if not valid:
                if isinstance(output, dict):
                    output.clear()
                self._invalidate('paused')
                self.counts['withheld'] += 1
                return None
            self.state = 'ready'
            self.counts['rendered'] += 1
            # No provider snapshots/IDs in this envelope; audio is ephemeral.
            return {'ticket': deepcopy(work.ticket), 'request_id': contract['request_id'],
                    'text': contract['text'], 'language': contract['language'],
                    'transcript': output['transcript'], 'wav_base64': output['wav_base64'],
                    'report': {k: report[k] for k in ('acknowledged', 'transcript_matches',
                              'invalid_output', 'final_usage_confirmed', 'close_reason')},
                    'usage': {'seconds': seconds}}

    def complete(self, ticket):
        with self.lock:
            if not self._current(ticket, released=True) or self.state != 'ready':
                return False
            self.active = None
            self.counts['completed'] += 1
            self.state = 'exhausted' if self.attempts >= self.max_turns else 'listening'
            return True

    def _invalidate(self, state):
        if self.active:
            self.active.cancel.set()
            self.active.result = self.active.contract = None
            self.active = None
            self.counts['cancelled'] += 1
        self.generation += 1
        self.state = state

    def stop(self):
        with self.lock:
            self._invalidate('paused')
            return self.identity()

    def resume(self):
        with self.lock:
            if (self.state != 'paused' or self.attempts >= self.max_turns or self.finalize is None
                    or self.session_deadline is None or self.now() >= self.session_deadline):
                return None
            self.generation += 1
            self.state = 'listening'
            return self.identity()

    def interrupt(self):
        with self.lock:
            if self.state not in ('researching', 'released', 'rendering', 'ready'):
                return None
            self._invalidate('exhausted' if self.attempts >= self.max_turns else 'listening')
            return self.identity()

    def erase(self, next_context=None):
        with self.lock:
            if next_context is not None and (not isinstance(next_context, dict)
                    or not isinstance(next_context.get('epoch'), str)
                    or not 0 < len(next_context['epoch']) <= 128
                    or next_context['epoch'] == self.epoch
                    or next_context.get('generation') != self.generation):
                return None
            self._invalidate('idle')
            self.epoch = next_context['epoch'] if next_context else str(uuid4())
            if next_context:
                self.generation = next_context['generation']
            self.attempts = 0
            self.session_deadline = None
            self.seen.clear()
            self.document_ref = self.accepted_result = None
            self.counts['erased'] += 1
            return self.identity()

    def tick(self):
        with self.lock:
            if ((self.active and self.now() >= self.active.deadline)
                    or (self.state not in ('idle', 'paused', 'exhausted')
                        and self.session_deadline is not None and self.now() >= self.session_deadline)):
                self._invalidate('paused')
                return True
            return False

    def metrics(self):
        with self.lock:
            return dict(self.counts)  # No text, documents, identities or audio.
