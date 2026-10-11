"""Capture-free adapter for the hardware owner's existing, supervised camera loop.

No imports of OpenCV/MediaPipe, device access, downloads, network or persistence.
The caller supplies MediaPipe results and the acquisition timestamp of a new frame.
No presence/departure claims are inferred from hands. All scene ownership is supplied
by a separately validated, ephemeral occupancy gate (never facial identity).
"""
import math
import uuid

LABELS = {'None', 'Open_Palm', 'Closed_Fist', 'Thumb_Up', 'Thumb_Down', 'Pointing_Up', 'Victory', 'ILoveYou'}


def summarize(result, *, scene_stable=False, mirror_x=False):
    """Map a recognizer result to bounded scalars; ambiguity suppresses actions."""
    if type(scene_stable) is not bool or type(mirror_x) is not bool:
        raise ValueError('Scene and mirror flags must be explicit booleans')
    hands = result.hand_landmarks
    count = min(2, len(hands))
    summary = {'hand_count': count, 'scene_stable': scene_stable, 'hand': None}
    if count != 1:
        return summary
    try:
        points = hands[0]
        if len(points) != 21:
            raise ValueError('Expected 21 landmarks')
        x = sum(points[i].x for i in (0, 5, 9, 13, 17)) / 5
        y = sum(points[i].y for i in (0, 5, 9, 13, 17)) / 5
        width = math.hypot(points[5].x - points[17].x, points[5].y - points[17].y)
        side = result.handedness[0][0].category_name
        category = result.gestures[0][0] if result.gestures[0] else None
        label, score = (category.category_name, category.score) if category else ('None', 0.)
        if side not in ('Left', 'Right') or label not in LABELS or any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in (x, y, width, score)) or width <= 0:
            raise ValueError('Invalid hand metadata')
        summary['hand'] = {'x': 1-x if mirror_x else x, 'y': y, 'palm_width': width, 'score': score, 'label': label, 'side': side}
        return summary
    except (IndexError, TypeError, AttributeError, ValueError):
        # Not an absence claim: unstable immediately clears motion history.
        return {'hand_count': 0, 'scene_stable': False, 'hand': None}


class HandObservationProducer:
    """Bounded v1 metadata envelopes, usable without a camera in authored tests.

    Authorization flags are integration preconditions, not an access-control system.
    Synthetic mode always marks events synthetic, and production transport rejects
    them. Operator supervision/capture shutdown remain the hardware owner's job.
    """
    def __init__(self, *, synthetic=True, camera_authorized=False, foreground_user_ready=False, mirror_x=False):
        if type(synthetic) is not bool or type(mirror_x) is not bool:
            raise ValueError('Flags must be booleans')
        if not synthetic and not (camera_authorized is True and foreground_user_ready is True):
            raise ValueError('Real metadata requires explicit camera authorization and a ready foreground participant')
        self.synthetic, self.mirror_x = synthetic, mirror_x
        self.session_id = uuid.uuid4().hex
        self.sequence, self.last_frame, self.ended = 0, -1, False
        self.started = False

    def envelope(self, type, at, source='camera', **fields):
        if self.ended or type not in ('ready', 'frame_acquired', 'hand_observed', 'error', 'stopped', 'navigate_requested') or source not in ('camera', 'presenter_key') or not isinstance(at, (int, float)) or isinstance(at, bool) or not math.isfinite(at) or at < 0:
            raise ValueError('Invalid producer event')
        expected = {'hand_count', 'scene_stable', 'hand'} if type == 'hand_observed' else {'direction'} if type == 'navigate_requested' else set()
        if set(fields) != expected:
            raise ValueError('Only allowlisted event metadata may be emitted')
        self.sequence += 1
        return {'schema': 'open-oracle-input/v1', 'type': type, 'source': source, 'session_id': self.session_id, 'sequence': self.sequence, 'monotonic_ms': at, 'synthetic': self.synthetic, **fields}

    def observe(self, result, frame_monotonic_ms, *, scene_stable=False):
        at = frame_monotonic_ms
        if type(at) not in (int, float) or not math.isfinite(at) or at <= self.last_frame or self.ended:
            raise ValueError('A fresh acquired-frame timestamp is required; frozen/repeated frames are not proof')
        summary = summarize(result, scene_stable=scene_stable, mirror_x=self.mirror_x)
        events = []
        if not self.started:
            events.append(self.envelope('ready', at)); self.started = True
        events.append(self.envelope('frame_acquired', at))
        events.append(self.envelope('hand_observed', at, **summary))
        self.last_frame = at
        return events

    def presenter(self, direction, at):
        if not self.started or direction not in ('previous', 'next'):
            raise ValueError('Presenter navigation requires an active producer and a valid direction')
        return self.envelope('navigate_requested', at, 'presenter_key', direction=direction)

    def stop(self, at, *, failed=False):
        event = self.envelope('error' if failed else 'stopped', at)
        self.ended = True
        return event
