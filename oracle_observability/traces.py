"""Independent OTel scope that emits only an allowlisted operational projection.

Never installs a global tracer/provider, SDK message processor, environment flag,
or collector. Raw Strands spans cannot enter this private provider. Callers must
separately audit externally configured global SDK telemetry and logging.
"""
from __future__ import annotations

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.trace import Status, StatusCode
from opentelemetry.context import Context
import os
from threading import Lock
from urllib.parse import urlparse
from uuid import UUID

from .monitor import COMPONENTS, STATUS, EXECUTION, BINDING, REVIEW, ERROR, TOOL_ERROR, TOOL, STAGE, STOP, ROUTES, count, digest, enum, mapping, number
from .schema import validate_schema_event

SCOPE = "open_oracle.safe_operations"


def trace_attributes(row):
    """Re-project even if an emitter is accidentally handed arbitrary metadata."""
    row = mapping(row)
    attrs = {"oracle.request_id": str(UUID(row["request_id"])), "oracle.run_id": str(UUID(row["run_id"]))}
    for key in ("deployment_sha256", "source_catalog_sha256", "runtime_config_sha256", "rubric_sha256", "experiment_sha256"):
        if row.get(key) is not None:
            attrs["oracle." + key] = digest(row[key])
    for key, allowed, fallback in (("status", STATUS, "other"), ("execution", EXECUTION, "synthetic_sdk"),
                                  ("binding", BINDING, "not_run"), ("review", REVIEW, "not_run"),
                                  ("error_category", ERROR, "none"), ("coverage", {"sdk_receipt", "boundary_only"}, "boundary_only"),
                                  ("release_outcome", {"released", "held", "no_answer"}, "no_answer")):
        attrs["oracle." + key] = enum(row.get(key), allowed, fallback)
    attrs["oracle.route"] = enum(row.get("route"), ROUTES, "other")
    attrs["oracle.stop_reason"] = enum(row.get("stop_reason"), STOP, "not_recorded")
    for key in ("elapsed_ms", "pipeline_elapsed_ms", "estimated_cost_usd"):
        value = number(row.get(key))
        if value is not None:
            attrs["oracle." + key] = value
    for key in ("model_attempts", "dropped_events"):
        value = count(row.get(key))
        if value is not None:
            attrs["oracle." + key] = value
    attrs["oracle.refusal"] = row.get("refusal") is True
    attrs["oracle.cost_is_invoice"] = False
    for component in COMPONENTS:
        for key in ("input_tokens", "output_tokens", "total_tokens", "calls"):
            value = count(mapping(mapping(row.get("usage")).get(component)).get(key))
            if value is not None:
                attrs[f"oracle.usage.{component}.{key}"] = value
    # Only source version hashes; source IDs remain in the transient application
    # projection and do not appear as dashboard dimensions or cloud attributes.
    sources = row.get("released_sources", [])
    if isinstance(sources, list) and len(sources) <= 8:
        hashes = [digest(mapping(s)["version_sha256"]) for s in sources]
        if hashes:
            attrs["oracle.released_source_versions"] = tuple(sorted(set(hashes)))
    return attrs


class _MeasuredExporter(SpanExporter):
    """No payload/error logging. Export status is measurable, never inferred."""
    def __init__(self, inner):
        self.inner, self._lock = inner, Lock()
        self.attempted, self.succeeded, self.failed = 0, 0, 0

    def export(self, spans):
        try:
            result = self.inner.export(spans)
        except Exception:
            result = SpanExportResult.FAILURE
        with self._lock:
            self.attempted += len(spans)
            if result == SpanExportResult.SUCCESS:
                self.succeeded += len(spans)
            else:
                self.failed += len(spans)
        return result

    def snapshot(self):
        with self._lock:
            return {"span_export_attempts": self.attempted, "span_export_successes": self.succeeded, "span_export_failures": self.failed}

    def shutdown(self):
        self.inner.shutdown()


class SafeTraceEmitter:
    """Private provider, fixed resource/name, no span events or exception payloads.

    Provider work is already completed: child span elapsed time is a numeric
    attribute, not fabricated start/end timing or claims of SDK auto-instrumentation.
    Root and children share trace ID; request/run/config hashes correlate receipts.
    Exporter injection is explicitly opt-in. Default application monitor has none.
    """
    def __init__(self, exporter, *, asynchronous=False):
        self.provider = TracerProvider(resource=Resource({"service.name": "open-oracle", "oracle.telemetry.schema": 1}))
        self.exporter = _MeasuredExporter(exporter)
        processor = BatchSpanProcessor(self.exporter, max_queue_size=256, max_export_batch_size=128, schedule_delay_millis=5000, export_timeout_millis=2000) if asynchronous else SimpleSpanProcessor(self.exporter)
        self.provider.add_span_processor(processor)
        self.tracer = self.provider.get_tracer(SCOPE, "1.0.0")

    def emit(self, row):
        attrs = trace_attributes(row)
        with self.tracer.start_as_current_span("oracle.completed_operation", context=Context(), attributes=attrs,
                                               record_exception=False, set_status_on_exception=False) as root:
            if attrs["oracle.error_category"] != "none":
                root.set_status(Status(StatusCode.ERROR))  # No description/exception text.
            for key, value in mapping(row.get("stages_ms")).items():
                if key in STAGE and number(value) is not None:
                    with self.tracer.start_as_current_span("oracle.stage." + key, attributes={"oracle.measured_duration_ms": value}, record_exception=False, set_status_on_exception=False):
                        pass
            for raw in (row.get("tools") or [])[:256]:
                tool = mapping(raw)
                name = enum(tool.get("name"), TOOL, "other_tool")
                child = {"oracle.tool_name": name, "oracle.tool_status": enum(tool.get("status"), {"started", "success", "error", "cancelled"}, "error")}
                child["oracle.tool_error_category"] = enum(tool.get("error_category"), TOOL_ERROR, "none")
                if number(tool.get("duration_ms")) is not None:
                    child["oracle.measured_duration_ms"] = tool["duration_ms"]
                with self.tracer.start_as_current_span("oracle.tool." + name, attributes=child, record_exception=False, set_status_on_exception=False):
                    pass
            for raw in (row.get("models") or [])[:256]:
                model = mapping(raw)
                child = {"oracle.model_status": enum(model.get("status"), {"completed", "error"}, "error")}
                child["oracle.model_error_category"] = enum(model.get("error_category"), ERROR | {"unknown_error"}, "none")
                if number(model.get("duration_ms")) is not None:
                    child["oracle.measured_duration_ms"] = model["duration_ms"]
                with self.tracer.start_as_current_span("oracle.model_attempt", attributes=child, record_exception=False, set_status_on_exception=False):
                    pass
            for raw in (row.get("schema_events") or [])[:32]:
                try:
                    event = validate_schema_event(raw)
                except (ValueError, TypeError):
                    continue
                with self.tracer.start_as_current_span("oracle.schema_validation",
                    attributes={"oracle.schema": event["schema"], "oracle.schema_sha256": event["schema_sha256"],
                                "oracle.schema_category": event["category"], "oracle.schema_field_path": event["field_path"]},
                    record_exception=False, set_status_on_exception=False):
                    pass

    def close(self):
        self.provider.shutdown()

    def snapshot(self):
        return self.exporter.snapshot()

    def flush(self):
        return self.provider.force_flush(timeout_millis=2000)


def approved_otlp_emitter(endpoint, *, network_export_approved=False, headers=None):
    """Explicit generic HTTP OTLP seam, not an AgentCore/CloudWatch setup claim.

    Core must verify destination permission, retention and costs before opting in.
    No ambient OTEL_* endpoint or credential is inherited. Supplied headers are
    transport-only and never part of spans. ADOT/SigV4 AWS ingestion is separate.
    """
    if network_export_approved is not True:
        raise ValueError("Explicit network export approval is required")
    parsed = urlparse(endpoint)
    if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Invalid explicit export destination")
    if parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}):
        raise ValueError("Exporter requires HTTPS or loopback HTTP")
    if any(k.startswith("OTEL_EXPORTER_OTLP_") or "OTLP_HTTP_TRACES_CREDENTIAL_PROVIDER" in k for k in os.environ):
        raise ValueError("Ambient OTLP transport configuration must be audited separately")
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from requests import Session
    from opentelemetry.sdk.metrics import MeterProvider
    exporter = OTLPSpanExporter(endpoint=endpoint, headers=dict(headers or {}), timeout=2, session=Session(),
                                max_request_size=262144, meter_provider=MeterProvider())
    return SafeTraceEmitter(exporter, asynchronous=True)
