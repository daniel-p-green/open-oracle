"""Memory-only numeric stage timings; never request/content/identity telemetry."""
import time

STAGES = frozenset({'queued', 'routing', 'retrieval', 'text', 'validation',
                    'review', 'audio', 'transcription', 'ready', 'held',
                    'cancelled', 'expired'})


class StageTiming:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.started = clock()
        self.last = self.started
        self.stage = 'queued'
        self.durations = {}
        self.finished = None

    def advance(self, stage, terminal=False):
        if stage not in STAGES or self.finished is not None:
            return
        now = max(self.last, self.clock())
        self.durations[self.stage] = self.durations.get(self.stage, 0) + now - self.last
        self.last, self.stage = now, stage
        if terminal:
            self.finished = now

    def snapshot(self):
        now = self.finished if self.finished is not None else max(self.last, self.clock())
        durations = dict(self.durations)
        if self.finished is None:
            durations[self.stage] = durations.get(self.stage, 0) + now - self.last
        return {'basis': 'server_monotonic_job_not_user_playback',
                'elapsed_ms': round((now - self.started) * 1000, 3),
                'stages_ms': {name: round(seconds * 1000, 3)
                              for name, seconds in durations.items()}}
