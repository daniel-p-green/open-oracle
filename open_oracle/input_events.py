"""Bounded metadata-only input from an operator-selected stdin pipe. Disabled by default."""
from collections import deque
import json
import math
import re
import threading
import time

SCHEMA = 'open-oracle-input/v1'
PAIRS = {
    ('ready', 'camera'), ('frame_acquired', 'camera'), ('error', 'camera'), ('stopped', 'camera'),
    ('presence_detected', 'camera'), ('presence_lost', 'camera'), ('departure_confirmed', 'camera'),
    ('start_requested', 'camera_wave'), ('start_requested', 'spoken_initiation'),
    ('start_requested', 'presenter_key'), ('start_requested', 'presenter_click'),
    ('reset_requested', 'presenter_key'), ('reset_requested', 'presenter_click'),
    ('hand_observed', 'camera'), ('navigate_requested', 'presenter_key'),
}
SESSION = re.compile(r'[A-Za-z0-9_-]{8,128}\Z')
HAND_LABELS = {'None', 'Open_Palm', 'Closed_Fist', 'Thumb_Up', 'Thumb_Down', 'Pointing_Up', 'Victory', 'ILoveYou'}


def hand_summary(raw):
    """Allowlisted scalar summary, never pixels, raw landmarks or identity."""
    count, stable, hand = raw.get('hand_count'), raw.get('scene_stable'), raw.get('hand')
    if type(count) is not int or count not in (0, 1, 2) or type(stable) is not bool:
        return None
    if count != 1:
        return {'hand_count': count, 'scene_stable': stable, 'hand': None} if hand is None else None
    if not isinstance(hand, dict):
        return None
    for key in ('x', 'y', 'palm_width', 'score'):
        value = hand.get(key)
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
            return None
    if hand['palm_width'] <= 0 or not isinstance(hand.get('label'), str) or hand['label'] not in HAND_LABELS or hand.get('side') not in ('Left', 'Right'):
        return None
    return {'hand_count': count, 'scene_stable': stable,
            'hand': {key: hand[key] for key in ('x', 'y', 'palm_width', 'score', 'label', 'side')}}


class InputEvents:
    def __init__(self, *, presence=False, wave=False, local_wake=False, hand_gestures=False, clock=time.monotonic, lease_seconds=3):
        if type(lease_seconds) not in (int, float) or not math.isfinite(lease_seconds) or not 1 <= lease_seconds <= 10:
            raise ValueError('Input lease must be 1–10 seconds')
        self.clock, self.lease_seconds = clock, lease_seconds
        self.capabilities = {'presence': presence is True, 'wave': wave is True, 'localWake': local_wake is True, 'handGestures': hand_gestures is True}
        self.lock = threading.Lock()
        self.events = deque(maxlen=64)
        self.cursor, self.sequence = 0, -1
        self.session_id, self.anchor, self.last_frame, self.active = None, None, None, False
        self.seen_sessions = set()
        self.ended = True

    def accept(self, raw):
        if not isinstance(raw, dict) or raw.get('schema') != SCHEMA or raw.get('synthetic') is not False:
            return False
        session, sequence, timestamp = raw.get('session_id'), raw.get('sequence'), raw.get('monotonic_ms')
        pair = (raw.get('type'), raw.get('source'))
        if not isinstance(pair[0], str) or not isinstance(pair[1], str) or not isinstance(session, str) or not SESSION.fullmatch(session) or type(sequence) is not int or not 0 <= sequence <= 2**53-1 or type(timestamp) not in (int, float) or not math.isfinite(timestamp) or timestamp < 0 or pair not in PAIRS:
            return False
        extra = {}
        if pair == ('hand_observed', 'camera'):
            extra = hand_summary(raw)
            if not self.capabilities['handGestures'] or extra is None:
                return False
        elif pair == ('navigate_requested', 'presenter_key'):
            if raw.get('direction') not in ('previous', 'next'):
                return False
            extra = {'direction': raw['direction']}
        now = self.clock()
        with self.lock:
            if session != self.session_id:
                if pair != ('ready', 'camera') or session in self.seen_sessions or len(self.seen_sessions) >= 32:
                    return False
                self.seen_sessions.add(session)
                self.session_id, self.sequence = session, -1
                self.anchor, self.last_frame, self.active = now - timestamp / 1000, None, True
                self.events.clear()
                self.ended = False
            if self.ended:
                return False
            if sequence <= self.sequence or not -0.25 <= now - self.anchor - timestamp / 1000 <= 2:
                return False
            self.sequence = sequence
            if pair == ('frame_acquired', 'camera'):
                # A camera-ready claim alone never establishes actual frame flow.
                self.last_frame, self.active = now, True
            if pair in {('error', 'camera'), ('stopped', 'camera')}:
                self.active = False
                self.ended = True
            if pair[0] in {'ready', 'frame_acquired'}:
                return True
            # Drop all other payload fields, including accidental image/audio/text data.
            self.cursor += 1
            event = {k: raw[k] for k in ('schema', 'type', 'source', 'session_id', 'sequence', 'monotonic_ms', 'synthetic')}
            event.update(extra)
            self.events.append((self.cursor, event))
            return True

    def stopped(self):
        with self.lock:
            self.active = False
            self.ended = True

    def snapshot(self, after=0):
        if type(after) is not int or not 0 <= after <= 2**53-1:
            raise ValueError('Invalid input cursor')
        now = self.clock()
        with self.lock:
            available = self.active and self.last_frame is not None and now - self.last_frame <= self.lease_seconds
            return {'schema': SCHEMA, 'enabled': True, 'available': available, 'cursor': self.cursor,
                    'session_id': self.session_id if available else None,
                    'producer_monotonic_ms': max(0, (now - self.anchor) * 1000) if available else None,
                    'capabilities': dict(self.capabilities) if available else {key: False for key in self.capabilities},
                    'events': [dict(event) for cursor, event in self.events if cursor > after] if available else [],
                    'discontinuity': bool(self.events and after < self.events[0][0] - 1)}

    def consume(self, stream):
        try:
            while True:
                line = stream.readline(8193)
                if not line:
                    break
                if len(line) > 8192:
                    break  # Stop rather than parse a split/oversized record as a new event.
                try:
                    raw = json.loads(line)
                except (ValueError, UnicodeError, RecursionError):
                    continue
                self.accept(raw)
        finally:
            self.stopped()

    def start(self, stream):
        thread = threading.Thread(target=self.consume, args=(stream,), daemon=True, name='oracle-input-metadata')
        thread.start()
        return thread
