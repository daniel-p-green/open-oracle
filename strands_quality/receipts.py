"""Request-owned Strands 1.59 hooks. Serialize metadata, never model content.

No exporter, file sink, provider constructor or global environment changes.
Application release checks remain authoritative; receipts describe execution.
"""
from __future__ import annotations

from copy import deepcopy
from importlib.metadata import version
import math
import re
from threading import Lock
from time import monotonic
from uuid import UUID, uuid4

from strands.hooks import (HookProvider, BeforeModelCallEvent, AfterModelCallEvent,
                          BeforeToolCallEvent, AfterToolCallEvent, AfterInvocationEvent)

EXECUTIONS = {"synthetic_sdk", "exact_source", "real_api"}
STOP_REASONS = {"end_turn", "tool_use", "max_tokens", "stop_sequence", "guardrail_intervened",
                "content_filtered", "limit_turns", "limit_output_tokens", "limit_total_tokens",
                "cancelled", "interrupt", "checkpoint"}
STATUSES = {"answered", "insufficient_evidence", "unavailable", "clarification", "conflict",
            "neutrality_boundary", "official_links"}
TOOLS = {"resolve_contest", "search_evidence", "read_evidence", "test_ballot_readability", "plan_evidence",
         "search_official_sources", "acquire_official_source", "search_indexed_evidence",
         "read_evidence_chunk", "lookup_legal_reference", "record_source_gap", "request_clarification", "CitedAnswer",
         "define_completion_plan", "search_completion_ballot", "read_completion_ballot",
         "inspect_completion_gaps", "expand_approved_context", "read_completion_context"}
STAGES = {"strands", "source_guards", "decisions", "release", "voice"}


def digest(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("Expected SHA256 digest")
    return value


def error_category(error: BaseException | None) -> str | None:
    """Do not serialize error messages/class names from providers or tools."""
    if error is None:
        return None
    # SDK EventLoopException preserves the provider cause; inspect type only.
    seen = set()
    while error.__cause__ is not None and id(error) not in seen and len(seen) < 5:
        seen.add(id(error))
        error = error.__cause__
    if isinstance(error, TimeoutError):
        return "timeout_or_budget"
    if isinstance(error, (ValueError, TypeError)):
        return "contract_error"
    if isinstance(error, ConnectionError):
        return "transport_error"
    return "execution_error"


def milliseconds(seconds: float) -> float | None:
    return round(seconds * 1000, 3) if math.isfinite(seconds) and seconds >= 0 else None


class EvidenceReceipt(HookProvider):
    """One instance per request. Thread-safe for concurrent tool callbacks.

    Only fixed field names and enums, trusted public source catalog metadata,
    hashes, UUIDs and numeric metrics can reach `snapshot()`. Tool args/results,
    messages, question hashes, invocation state and exception text never do.
    """
    def __init__(self, *, config_hash: str, execution: str,
                 source_catalog: dict[str, str], request_id: str | None = None,
                 max_events: int = 64, clock=monotonic):
        if execution not in EXECUTIONS or type(max_events) is not int or not 1 <= max_events <= 256:
            raise ValueError("Invalid receipt configuration")
        self.request_id = str(UUID(request_id)) if request_id else str(uuid4())
        self.config_hash = digest(config_hash)
        self.execution = execution
        # The catalog must be application-owned, not derived from client text.
        self._catalog = {}
        for ident, source_version in source_catalog.items():
            if not re.fullmatch(r"[a-z0-9][a-z0-9:._-]{0,179}", ident):
                raise ValueError("Invalid public source ID")
            self._catalog[ident] = digest(source_version)
        self._clock, self._start = clock, clock()
        self._max_events, self._lock = max_events, Lock()
        self._tools, self._active_tools, self._models = [], {}, []
        self._schema_events, self._schema_dropped = [], 0
        self._model_start = None
        self._attempts, self._dropped = 0, 0
        self._usage, self._stop = None, None
        self._stages, self._sources = {}, []
        self._release = {"status": "not_finalized", "binding": "not_run", "review": "not_run",
                         "review_execution": "not_run"}
        self._error, self._finished, self._elapsed = None, False, None

    def register_hooks(self, registry):
        registry.add_callback(BeforeModelCallEvent, self.before_model)
        registry.add_callback(AfterModelCallEvent, self.after_model)
        registry.add_callback(BeforeToolCallEvent, self.before_tool)
        registry.add_callback(AfterToolCallEvent, self.after_tool)
        registry.add_callback(AfterInvocationEvent, self.after_invocation)

    def before_model(self, event):
        with self._lock:
            if self._finished:
                return
            self._attempts += 1
            self._model_start = self._clock()

    def after_model(self, event):
        with self._lock:
            if self._finished:
                return
            if len(self._models) < self._max_events:
                elapsed = self._clock() - self._model_start if self._model_start is not None else None
                self._models.append({"attempt": self._attempts,
                                     "duration_ms": milliseconds(elapsed) if elapsed is not None else None,
                                     "status": "error" if event.exception else "completed",
                                     "error_category": error_category(event.exception)})
            else:
                self._dropped += 1
            self._model_start = None

    @staticmethod
    def _tool_name(name):
        return name if name in TOOLS else "other_tool"

    def before_tool(self, event):
        with self._lock:
            if self._finished:
                return
            if len(self._tools) >= self._max_events:
                self._dropped += 1
                return
            index = len(self._tools)
            self._tools.append({"sequence": index + 1, "name": self._tool_name(event.tool_use.get("name")),
                                "status": "started", "duration_ms": None, "error_category": None})
            # Native ID is private correlation only, never exported.
            self._active_tools[event.tool_use.get("toolUseId")] = index

    def after_tool(self, event):
        with self._lock:
            if self._finished:
                return
            index = self._active_tools.pop(event.tool_use.get("toolUseId"), None)
            if index is None:
                return
            entry = self._tools[index]
            entry["status"] = "cancelled" if event.cancel_message else (
                "success" if event.result.get("status") == "success" and not event.exception else "error")
            entry["duration_ms"] = milliseconds(event.duration) if event.duration is not None else None
            entry["error_category"] = error_category(event.exception)

    def after_invocation(self, event):
        if event.result is not None:
            self.observe_result(event.result)

    def observe_result(self, result):
        """Overwrite one aggregate slot; duplicate observation never adds tokens."""
        usage = result.metrics.accumulated_usage
        with self._lock:
            if self._finished:
                return
            self._usage = {key: usage[key] for key in ("inputTokens", "outputTokens", "totalTokens")
                           if key in usage and type(usage[key]) is int and usage[key] >= 0}
            self._stop = result.stop_reason if result.stop_reason in STOP_REASONS else "other_stop"

    def schema_validation(self, **event):
        """Already normalized schema metadata only; independently revalidate."""
        from .schema_validation import SCHEMA_NAME, CATEGORIES, FIELD_PATHS
        if set(event) != {"schema", "schema_sha256", "category", "field_path"} or event["schema"] != SCHEMA_NAME:
            raise ValueError("Invalid schema metadata shape")
        digest(event["schema_sha256"])
        if not isinstance(event["category"], str) or event["category"] not in CATEGORIES:
            raise ValueError("Invalid schema category")
        if not isinstance(event["field_path"], str) or event["field_path"] not in FIELD_PATHS:
            raise ValueError("Invalid normalized schema path")
        projected = {k: event[k] for k in ("schema", "schema_sha256", "category", "field_path")}
        with self._lock:
            if self._finished:
                return
            if len(self._schema_events) < min(self._max_events, 32):
                self._schema_events.append(projected)
            else:
                self._schema_dropped += 1

    def stage(self, name: str, seconds: float):
        if name not in STAGES or type(seconds) not in (int, float) or milliseconds(seconds) is None:
            raise ValueError("Invalid operational stage")
        with self._lock:
            if self._finished:
                raise ValueError("Receipt already finalized")
            self._stages[name] = milliseconds(seconds)

    def release(self, *, status: str, binding: str, review: str, review_execution: str,
                evidence_ids: list[str] = ()):
        if status not in STATUSES or binding not in {"supported", "unsupported", "contradictory", "not_run", "not_applicable"}:
            raise ValueError("Invalid release status")
        if review not in {"accepted", "rejected", "unavailable", "not_run"} or review_execution not in {
                "real_api", "synthetic_sdk", "deterministic_guard", "not_run"}:
            raise ValueError("Invalid review status")
        if status == "answered" and (binding != "supported" or (self.execution == "real_api" and
                (review != "accepted" or review_execution != "real_api"))):
            raise ValueError("Unaccepted answer cannot be recorded as released")
        if review in {"rejected", "unavailable"} and evidence_ids:
            raise ValueError("Withheld content cannot have released sources")
        unique = sorted(set(evidence_ids))
        if len(unique) > 8 or any(ident not in self._catalog for ident in unique):
            raise ValueError("Unknown or excessive released sources")
        with self._lock:
            if self._finished:
                raise ValueError("Receipt already finalized")
            self._release = {"status": status, "binding": binding, "review": review,
                             "review_execution": review_execution}
            self._sources = [{"id": ident, "version_sha256": self._catalog[ident]} for ident in unique]

    def finish(self, error: BaseException | None = None):
        """Call from the application's outer finally, including validation errors."""
        with self._lock:
            if not self._finished:
                self._error = error_category(error)
                self._elapsed = milliseconds(self._clock() - self._start)
                self._finished = True
        return self.snapshot()

    def snapshot(self):
        with self._lock:
            return deepcopy({"version": 1, "request_id": self.request_id, "config_sha256": self.config_hash,
                "execution": self.execution, "sdk_version": version("strands-agents"),
                "finalized": self._finished, "elapsed_ms": self._elapsed,
                "schema_events": self._schema_events, "schema_dropped_event_count": self._schema_dropped,
                "model_attempts_started": self._attempts, "model_events": self._models,
                "tool_events": self._tools, "dropped_event_count": self._dropped,
                "usage": self._usage, "stop_reason": self._stop, "stages_ms": self._stages,
                "released_sources": self._sources, "release": self._release, "error_category": self._error})
