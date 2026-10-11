"""Trusted application receipts -> bounded metadata -> volatile aggregates.

The input boundary is application-owned code, never a client telemetry endpoint.
Unknown fields are discarded. Missing instrumentation remains explicitly unknown.
No logging, disk writes, provider calls, environment changes or global OTel setup.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
import math
import re
from threading import Lock
from time import monotonic
from types import MappingProxyType
from uuid import UUID, uuid4
from .schema import validate_schema_event

STATUS = {"answered", "insufficient_evidence", "unavailable", "clarification", "conflict",
          "neutrality_boundary", "official_links", "cancelled", "error", "other"}
EXECUTION = {"exact_source", "synthetic_sdk", "real_api"}
BINDING = {"supported", "unsupported", "contradictory", "not_run", "not_applicable"}
REVIEW = {"accepted", "rejected", "unavailable", "not_run"}
ERROR = {"timeout_or_budget", "contract_error", "transport_error", "execution_error", "cancelled"}
TOOL_ERROR = ERROR | {"tool_result_error", "unknown_error"}
TOOL = {"resolve_contest", "search_evidence", "read_evidence", "test_ballot_readability", "plan_evidence",
        "search_official_sources", "acquire_official_source", "search_indexed_evidence", "read_evidence_chunk",
        "lookup_legal_reference", "record_source_gap", "request_clarification", "CitedAnswer", "other_tool"}
STAGE = {"strands", "source_guards", "decisions", "release", "voice"}
STOP = {"end_turn", "tool_use", "max_tokens", "stop_sequence", "guardrail_intervened", "content_filtered",
        "limit_turns", "limit_output_tokens", "limit_total_tokens", "cancelled", "interrupt", "checkpoint", "other_stop"}
ROUTES = {"exact_source", "live_strands", "reviewed_strands_research", "other"}
COMPONENTS = ("strands", "decisions", "embeddings")


def digest(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("Invalid configuration digest")
    return value


def canonical_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def number(value):
    return value if type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1e12 else None


def count(value):
    return value if type(value) is int and 0 <= value <= 10**12 else None


def enum(value, allowed, fallback):
    return value if isinstance(value, str) and value in allowed else fallback


def mapping(value):
    return value if isinstance(value, dict) else {}


def usage(raw=None, *, calls=None, zero=False):
    """One component's counters; never infer missing paid usage as zero."""
    raw = mapping(raw)
    fields = {key: count(raw.get(key)) for key in ("input_tokens", "output_tokens", "total_tokens")}
    if zero:
        fields = dict.fromkeys(fields, 0)
    # A malformed total is unknown, not silently corrected into measured usage.
    if all(fields[k] is not None for k in fields) and fields["total_tokens"] != fields["input_tokens"] + fields["output_tokens"]:
        fields["total_tokens"] = None
    return {**fields, "calls": count(calls)}


@dataclass(frozen=True)
class TrustedVersions:
    """Construct once from deployed code and retained public sources, never visitor input.

    deployment_sha256 is distinct from each runtime receipt's config_sha256 and
    from a frozen experiment config. No hash is substituted to satisfy a gate.
    """
    deployment_sha256: str
    source_catalog: dict[str, str]
    execution: str = "exact_source"
    sdk_version: str = "1.59.0"
    rubric_sha256: str | None = None
    experiment_sha256: str | None = None
    embeddings_enabled: bool = False

    def __post_init__(self):
        digest(self.deployment_sha256)
        if self.execution not in EXECUTION or type(self.embeddings_enabled) is not bool:
            raise ValueError("Invalid trusted execution")
        if not re.fullmatch(r"\d+\.\d+\.\d+", self.sdk_version):
            raise ValueError("Invalid SDK version")
        if len(self.source_catalog) > 10000:
            raise ValueError("Unbounded public catalog")
        for ident, value in self.source_catalog.items():
            if not re.fullmatch(r"[a-z0-9][a-z0-9:._-]{0,179}", ident):
                raise ValueError("Invalid public source identity")
            digest(value)
        object.__setattr__(self, "source_catalog", MappingProxyType(dict(self.source_catalog)))
        for value in (self.rubric_sha256, self.experiment_sha256):
            if value is not None:
                digest(value)

    @property
    def sources_sha256(self):
        return canonical_hash(dict(self.source_catalog))


def project_receipt(snapshot, versions):
    """Project a server-generated EvidenceReceipt snapshot, not browser JSON."""
    snapshot = mapping(snapshot)
    if snapshot.get("finalized") is not True or snapshot.get("sdk_version") != versions.sdk_version:
        raise ValueError("Expected finalized matching-SDK receipt")
    request_id = str(UUID(snapshot["request_id"]))
    execution = enum(snapshot.get("execution"), EXECUTION, None)
    if execution != versions.execution:
        raise ValueError("Receipt execution does not match the deployed mode")
    release = mapping(snapshot.get("release"))
    sources = []
    raw_sources = snapshot.get("released_sources", [])
    if not isinstance(raw_sources, list) or len(raw_sources) > 8:
        raise ValueError("Invalid released sources")
    for source in raw_sources:
        source = mapping(source)
        ident = source.get("id")
        if not isinstance(ident, str) or versions.source_catalog.get(ident) != source.get("version_sha256"):
            raise ValueError("Source is not bound to the retained public catalog")
        sources.append({"id": ident, "version_sha256": versions.source_catalog[ident]})
    tool_events = snapshot.get("tool_events", [])
    if not isinstance(tool_events, list) or len(tool_events) > 256:
        raise ValueError("Unbounded receipt events")
    tools = [{"name": enum(mapping(t).get("name"), TOOL, "other_tool"),
              "status": enum(mapping(t).get("status"), {"started", "success", "error", "cancelled"}, "error"),
              "error_category": enum(mapping(t).get("error_category"), TOOL_ERROR,
                                     "tool_result_error" if mapping(t).get("status") == "error" else None),
              "duration_ms": number(mapping(t).get("duration_ms"))} for t in tool_events]
    model_events = snapshot.get("model_events", [])
    if not isinstance(model_events, list) or len(model_events) > 256:
        raise ValueError("Unbounded model events")
    models = [{"status": enum(mapping(m).get("status"), {"completed", "error"}, "error"),
               "error_category": enum(mapping(m).get("error_category"), ERROR,
                                      "unknown_error" if mapping(m).get("status") == "error" else None),
               "duration_ms": number(mapping(m).get("duration_ms"))} for m in model_events]
    raw_usage = mapping(snapshot.get("usage"))
    calls = count(snapshot.get("model_attempts_started"))
    schema_events, invalid_schema = [], 0
    raw_schema = snapshot.get("schema_events", [])
    if not isinstance(raw_schema, list):
        raw_schema, invalid_schema = [], 1
    for event in raw_schema[:32]:
        try:
            schema_events.append(validate_schema_event(event))
        except (ValueError, TypeError):
            invalid_schema += 1
    invalid_schema += max(0, len(raw_schema)-32)
    return {"schema_version": 1, "request_id": request_id,
            "runtime_config_sha256": digest(snapshot["config_sha256"]),
            "execution": execution, "coverage": "sdk_receipt", "elapsed_ms": number(snapshot.get("elapsed_ms")),
            "status": enum(release.get("status"), STATUS, "other"),
            "binding": enum(release.get("binding"), BINDING, "not_run"),
            "review": enum(release.get("review"), REVIEW, "not_run"),
            "review_execution": enum(release.get("review_execution"), EXECUTION | {"not_run", "deterministic_guard"}, "not_run"),
            "error_category": enum(snapshot.get("error_category"), ERROR, None),
            "tools": tools, "models": models, "model_attempts": calls,
            "dropped_events": count(snapshot.get("dropped_event_count")),
            "stop_reason": enum(snapshot.get("stop_reason"), STOP, "not_recorded"),
            "stages_ms": {k: number(v) for k, v in mapping(snapshot.get("stages_ms")).items() if k in STAGE},
            "released_sources": sources,
            "schema_events": schema_events, "invalid_schema_events": invalid_schema,
            "schema_dropped_event_count": count(snapshot.get("schema_dropped_event_count", 0)),
            "usage": {"strands": usage({"input_tokens": raw_usage.get("inputTokens"),
                                       "output_tokens": raw_usage.get("outputTokens"), "total_tokens": raw_usage.get("totalTokens")},
                                      calls=calls, zero=execution == "exact_source" and calls == 0)}}


def boundary_error(exc):
    # Never serialize a class name, message, traceback or provider request ID.
    try:
        from open_oracle.session_control import SessionCancelled
        if isinstance(exc, SessionCancelled):
            return "cancelled"
    except ImportError:
        pass
    if isinstance(exc, TimeoutError):
        return "timeout_or_budget"
    if isinstance(exc, ConnectionError):
        return "transport_error"
    if isinstance(exc, (ValueError, TypeError)):
        return "contract_error"
    return "execution_error"


class OperationalMonitor:
    """No completed request objects retained; counts are lifetime process aggregates.

    A private optional emitter receives projected metadata synchronously, without
    adding a persistent local buffer. Emitters stay absent by default.
    """
    def __init__(self, versions: TrustedVersions, *, emitter=None):
        self.versions, self.run_id = versions, str(uuid4())
        self._emitter, self._lock = emitter, Lock()
        self._counts = {k: Counter() for k in ("status", "execution", "route", "coverage", "review", "binding", "errors", "latency", "stage_latency", "stop_reasons", "tools", "tool_outcomes", "tool_error_categories", "model_error_categories", "schema_categories", "schema_paths")}
        self._totals = Counter()
        self._usage = {k: Counter() for k in COMPONENTS}

    def record(self, response=None, *, error=None, elapsed_ms=None, embedding_usage=None, estimated_cost_usd=None):
        """Response must come directly from an application engine, never a route body.

        No prompt, client/session identifiers, answer, provider ID, review label,
        exception text or custom metadata survive this projection.
        """
        response = mapping(response)
        invalid = False
        raw = response.get("operational_receipt")
        try:
            row = project_receipt(raw, self.versions)
        except (ValueError, TypeError, KeyError, AttributeError):
            invalid = raw is not None
            row = {"schema_version": 1, "request_id": str(uuid4()), "runtime_config_sha256": None,
                   "execution": self.versions.execution, "coverage": "boundary_only", "elapsed_ms": number(elapsed_ms),
                   "status": enum(response.get("status"), STATUS, "error" if error else "other"),
                   "binding": "not_run", "review": "not_run", "review_execution": "not_run", "error_category": None,
                   "tools": [], "models": [], "model_attempts": None, "dropped_events": None,
                   "stop_reason": "not_recorded",
                   "stages_ms": {}, "released_sources": [], "schema_events": [], "invalid_schema_events": 0,
                   "schema_dropped_event_count": None, "usage": {"strands": usage()}}
        row["pipeline_elapsed_ms"] = number(elapsed_ms)
        row["route"] = enum(response.get("mode"), ROUTES, "other")
        if error is not None:
            row["error_category"] = boundary_error(error)
            row["status"] = "cancelled" if row["error_category"] == "cancelled" else "error"
        review = mapping(response.get("review"))
        # API-attempt inference is possible only for the known application reviewer.
        review_exec = enum(review.get("execution"), {"real_api", "offline_stub", "synthetic_sdk", "deterministic_guard", "not_run"}, "not_run")
        reviewed = enum(review.get("status"), REVIEW, "not_run")
        row["review"] = reviewed
        row["review_execution"] = review_exec
        known_real_review = review.get("provider") == "openai_decisions" and review_exec == "real_api" and reviewed != "not_run"
        no_review_call = ("review" in response and reviewed == "not_run" and not review.get("execution")) or review_exec in {"offline_stub", "synthetic_sdk", "deterministic_guard"}
        row["usage"]["decisions"] = usage(review.get("usage"), calls=1 if known_real_review else 0 if no_review_call else None, zero=no_review_call)
        row["usage"]["embeddings"] = usage(embedding_usage, calls=mapping(embedding_usage).get("calls"), zero=False) if self.versions.embeddings_enabled else usage(calls=0, zero=True)
        row["estimated_cost_usd"] = number(estimated_cost_usd)
        row["cost_basis"] = "caller_estimate_not_invoice" if row["estimated_cost_usd"] is not None else "unknown"
        parts = mapping(response.get("fact_validation")).get("covered_parts", [])
        row["refusal"] = row["status"] in {"neutrality_boundary", "insufficient_evidence"} or (isinstance(parts, list) and "prediction" in parts)
        row["release_outcome"] = "held" if reviewed in {"rejected", "unavailable"} or (row["status"] == "answered" and response.get("public_display") is False) else "released" if row["status"] == "answered" else "no_answer"
        row.update({"run_id": self.run_id, "deployment_sha256": self.versions.deployment_sha256,
                    "source_catalog_sha256": self.versions.sources_sha256, "rubric_sha256": self.versions.rubric_sha256,
                    "experiment_sha256": self.versions.experiment_sha256, "sdk_version": self.versions.sdk_version})
        elapsed = row["pipeline_elapsed_ms"]
        bucket = "unknown" if elapsed is None else next((f"le_{b}_ms" for b in (100, 1000, 5000, 10000, 30000) if elapsed <= b), "over_30000_ms")
        with self._lock:
            for key, value in (("status", row["status"]), ("execution", row["execution"]), ("coverage", row["coverage"]),
                               ("review", row["review"]), ("route", row["route"]), ("stop_reasons", row["stop_reason"]),
                               ("binding", row["binding"]), ("errors", row["error_category"] or "none"), ("latency", bucket)):
                self._counts[key][value] += 1
            self._totals["completed_operations"] += 1
            self._totals[row["release_outcome"]] += 1
            self._totals["refusals"] += int(row["refusal"])
            self._totals["invalid_receipts"] += int(invalid)
            self._totals["observed_tool_events"] += len(row["tools"])
            self._totals["released_source_events"] += len(row["released_sources"])
            for stage, value in row["stages_ms"].items():
                b = "unknown" if value is None else next((f"le_{bound}_ms" for bound in (100,1000,5000,10000,30000) if value <= bound), "over_30000_ms")
                self._counts["stage_latency"][stage+":"+b] += 1
            self._totals["dropped_events"] += row["dropped_events"] or 0
            self._totals["schema_event_count"] += len(row["schema_events"])
            self._totals["invalid_schema_events"] += row["invalid_schema_events"]
            self._totals["schema_dropped_events"] += row["schema_dropped_event_count"] or 0
            for event in row["schema_events"]:
                self._counts["schema_categories"][event["category"]] += 1
                self._counts["schema_paths"][event["field_path"]] += 1
            for tool in row["tools"]:
                self._counts["tools"][tool["name"]] += 1
                self._counts["tool_outcomes"][tool["status"]] += 1
                self._counts["tool_error_categories"][tool["error_category"] or "none"] += 1
            for model in row["models"]:
                self._counts["model_error_categories"][model["error_category"] or "none"] += 1
            for component, counters in row["usage"].items():
                for key, value in counters.items():
                    self._usage[component]["unknown_" + key if value is None else key] += 1 if value is None else value
            if row["estimated_cost_usd"] is not None:
                self._totals["estimated_cost_usd"] += row["estimated_cost_usd"]
            else:
                self._totals["cost_unknown_operations"] += 1
        if self._emitter is not None:
            try:
                self._emitter.emit(row)
            except Exception:
                with self._lock:
                    self._totals["export_failures"] += 1
        return row

    def helpfulness(self, helpful: bool):
        """Optional aggregate-only signal; no identifier, text or outcome linkage."""
        if type(helpful) is not bool:
            raise ValueError("Expected boolean helpfulness")
        with self._lock:
            self._totals["helpful" if helpful else "not_helpful"] += 1

    def snapshot(self):
        with self._lock:
            return {"schema_version": 1, "collection": "volatile_aggregate_only", "export_enabled": self._emitter is not None,
                    "export_status": self._emitter.snapshot() if self._emitter is not None and hasattr(self._emitter, "snapshot") else None,
                    "deployment_sha256": self.versions.deployment_sha256, "source_catalog_sha256": self.versions.sources_sha256,
                    "rubric_sha256": self.versions.rubric_sha256, "experiment_sha256": self.versions.experiment_sha256,
                    "sdk_version": self.versions.sdk_version, "counts": {k: dict(v) for k, v in self._counts.items()},
                    "totals": dict(self._totals), "observed_usage_lower_bound": {k: dict(v) for k, v in self._usage.items()},
                    "unique_visitors": None, "p95_latency_ms": None,
                    "limitations": ["Counts describe operations, not people.", "Missing instrumentation and usage remain unknown.",
                                    "No request or source history retained in aggregates.", "Estimates are not invoices.",
                                    "Lifetime counters reset with the process; erase clears visitor content separately."]}


class InstrumentedEngine:
    """Outer finally covers intake, held responses, exceptions and cancellation.

    No retries, provider construction or pipeline behavior changes. No response
    mutation. Record immediately and discard projected per-request metadata.
    """
    def __init__(self, engine, monitor, *, clock=monotonic):
        self.engine, self.monitor, self._clock = engine, monitor, clock

    def __getattr__(self, name):
        return getattr(self.engine, name)

    def answer(self, *args, **kwargs):
        started = self._clock()
        response, error = None, None
        try:
            response = self.engine.answer(*args, **kwargs)
            return response
        except BaseException as exc:
            error = exc
            raise
        finally:
            try:
                self.monitor.record(response, error=error, elapsed_ms=max(0, (self._clock()-started)*1000))
            except Exception:
                # Observability must not change source/release/cancellation behavior.
                with self.monitor._lock:
                    self.monitor._totals["collection_failures"] += 1
