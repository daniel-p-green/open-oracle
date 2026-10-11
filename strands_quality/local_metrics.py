"""Aggregate operations and opt-in, short-lived debug memory. No disk sink."""
from collections import Counter
from threading import Lock
from time import monotonic
from .receipts import EvidenceReceipt


class AggregateMetrics:
    """No request/person identifiers, questions or source history retained.

    Application must call record once per finished request. Counts describe
    operations, not unique visitors; this class does not deduplicate people.
    """
    def __init__(self):
        self._lock = Lock()
        self._counts, self._errors, self._latency = Counter(), Counter(), Counter()
    def record(self, receipt: EvidenceReceipt):
        snapshot = receipt.snapshot()
        if not snapshot['finalized']:
            raise ValueError('Only completed requests may be aggregated')
        elapsed = snapshot['elapsed_ms']
        bucket = 'unknown' if elapsed is None else next(
            (f'le_{bound}_ms' for bound in (100,1000,5000,10000) if elapsed <= bound), 'over_10000_ms')
        with self._lock:
            self._counts[snapshot['release']['status']] += 1
            self._errors[snapshot['error_category'] or 'none'] += 1
            self._latency[bucket] += 1
    def snapshot(self):
        with self._lock:
            return {'completed_operation_counts':dict(self._counts), 'error_counts':dict(self._errors),
                    'latency_histogram':dict(self._latency), 'unique_visitor_count':None}


class DebugReceiptBuffer:
    """Disabled by default. Pseudonymous request UUIDs, not anonymous data.

    TTL is measured from insertion, never extended by reads. The buffer has no
    persistence/export facility; wire clear() to operator stop/visitor reset.
    UI opt-out/stop wiring remains an application integration responsibility.
    """
    def __init__(self, *, enabled=False, ttl_seconds=60, max_entries=32, clock=monotonic):
        if type(enabled) is not bool or type(ttl_seconds) not in (int,float) or not 0 < ttl_seconds <= 300:
            raise ValueError('Invalid bounded debug retention')
        if type(max_entries) is not int or not 1 <= max_entries <= 64:
            raise ValueError('Invalid buffer bound')
        self.enabled, self.ttl_seconds, self.max_entries, self._clock = enabled, ttl_seconds, max_entries, clock
        self._entries, self._lock = [], Lock()
    def _expire(self):
        now = self._clock()
        self._entries = [(created,value) for created,value in self._entries if now-created < self.ttl_seconds]
    def put(self, receipt: EvidenceReceipt):
        if not isinstance(receipt, EvidenceReceipt):
            raise TypeError('Only projected operational receipts accepted')
        with self._lock:
            self._expire()
            if self.enabled:
                self._entries.append((self._clock(),receipt.snapshot()))
                self._entries = self._entries[-self.max_entries:]
    def snapshots(self):
        from copy import deepcopy
        with self._lock:
            self._expire()
            return deepcopy([value for _,value in self._entries])
    def clear(self):
        with self._lock:
            self._entries.clear()
    def stop(self):
        with self._lock:
            self.enabled = False
            self._entries.clear()
