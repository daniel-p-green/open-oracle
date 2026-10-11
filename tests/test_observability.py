import json
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from uuid import uuid4

import unittest
from unittest.mock import patch
from contextlib import redirect_stdout, redirect_stderr
from functools import wraps
from io import StringIO

raises = unittest.TestCase().assertRaises

def parameterized(name, values):
    def decorate(fn):
        @wraps(fn)
        def run():
            for value in values:
                fn(value)
        return run
    return decorate
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry import trace

from oracle_observability.monitor import OperationalMonitor, InstrumentedEngine, TrustedVersions
from oracle_observability.evaluation import EvaluationAdapter
from oracle_observability.readout import render_dashboard
from oracle_observability.traces import SafeTraceEmitter, approved_otlp_emitter

CANARY = "PRIVATE-VISITOR-QUESTION-AUDIO-IDENTITY-sk-secret-canary"
CONFIG, SOURCE = "a" * 64, "b" * 64


def versions(execution="exact_source", **kw):
    return TrustedVersions(CONFIG, {"public-source": SOURCE}, execution=execution, **kw)


def receipt(execution="exact_source"):
    return {"request_id": str(uuid4()), "config_sha256": CONFIG, "execution": execution,
            "sdk_version": "1.59.0", "finalized": True, "elapsed_ms": 10,
            "model_attempts_started": 2 if execution != "exact_source" else 0,
            "model_events": [{"status": "completed", "duration_ms": 5, "payload": CANARY}],
            "tool_events": [{"name": "read_evidence_chunk", "status": "success", "duration_ms": 3,
                             "toolUseId": CANARY, "arguments": CANARY, "result": CANARY}],
            "dropped_event_count": 0, "stages_ms": {"strands": 6, CANARY: CANARY},
            "usage": {"inputTokens": 100, "outputTokens": 20, "totalTokens": 120},
            "release": {"status": "answered", "binding": "supported", "review": "accepted" if execution == "real_api" else "not_run",
                        "review_execution": "real_api" if execution == "real_api" else "not_run", "reason": CANARY},
            "released_sources": [{"id": "public-source", "version_sha256": SOURCE, "text": CANARY}],
            "error_category": None, "transcript": CANARY, "network_address": CANARY, "provider_id": CANARY}


def answer(execution="exact_source"):
    review = {"provider": "openai_decisions", "execution": "real_api", "status": "accepted",
              "usage": {"input_tokens": 30, "output_tokens": 2, "total_tokens": 32}, "label": CANARY} if execution == "real_api" else {"status": "not_run"}
    return {"status": "answered", "answer": CANARY, "question": CANARY,
            "review": review, "operational_receipt": receipt(execution), "request_id": CANARY,
            "scope": {"identity": CANARY}, "public_display": True}


def test_projection_and_aggregates_exclude_content_and_history():
    monitor = OperationalMonitor(versions())
    source = answer()
    row = monitor.record(source, elapsed_ms=20)
    assert CANARY not in json.dumps(row)
    aggregate = monitor.snapshot()
    serialized = json.dumps(aggregate)
    assert CANARY not in serialized
    assert row["request_id"] not in serialized and monitor.run_id not in serialized
    assert "public-source" not in serialized
    assert aggregate["totals"]["completed_operations"] == 1
    assert row["usage"]["strands"]["total_tokens"] == 0
    assert aggregate["p95_latency_ms"] is None
    source["operational_receipt"]["tool_events"][0]["name"] = CANARY
    assert row["tools"][0]["name"] == "read_evidence_chunk"


@parameterized("mutate", [
    lambda r: r.update(finalized=False), lambda r: r.update(sdk_version="9.9.9"),
    lambda r: r.update(request_id=CANARY), lambda r: r.update(config_sha256=CANARY),
    lambda r: r.update(execution="real_api"),
    lambda r: r["released_sources"][0].update(version_sha256="c"*64),
    lambda r: r.update(tool_events=[{}]*257),
])
def test_invalid_receipts_are_counted_as_boundary_unknown(mutate):
    response = answer()
    mutate(response["operational_receipt"])
    monitor = OperationalMonitor(versions())
    row = monitor.record(response, elapsed_ms=12)
    assert row["coverage"] == "boundary_only" and row["runtime_config_sha256"] is None
    assert row["model_attempts"] is None and row["usage"]["strands"]["total_tokens"] is None
    assert monitor.snapshot()["totals"]["invalid_receipts"] == 1
    assert CANARY not in json.dumps(row)


def test_paid_components_not_double_counted_or_invoice_claimed():
    monitor = OperationalMonitor(versions("real_api", embeddings_enabled=True))
    row = monitor.record(answer("real_api"), elapsed_ms=25,
                         embedding_usage={"calls": 1, "input_tokens": 7, "output_tokens": 0, "total_tokens": 7, "text": CANARY},
                         estimated_cost_usd=.01)
    assert row["usage"]["strands"]["total_tokens"] == 120
    assert row["usage"]["decisions"]["total_tokens"] == 32
    assert row["usage"]["embeddings"]["total_tokens"] == 7
    assert row["cost_basis"] == "caller_estimate_not_invoice"
    assert CANARY not in json.dumps(row)


def test_missing_embedding_and_failed_usage_remain_unknown():
    monitor = OperationalMonitor(versions("real_api", embeddings_enabled=True))
    row = monitor.record(error=TimeoutError(CANARY), elapsed_ms=35)
    assert row["status"] == "error" and row["error_category"] == "timeout_or_budget"
    assert all(v["total_tokens"] is None for v in row["usage"].values())
    assert all(v["calls"] is None for v in row["usage"].values())


def test_tool_result_error_has_fixed_category_without_schema_guess():
    response = answer()
    response["operational_receipt"]["tool_events"] = [{"name": "CitedAnswer", "status": "error", "error_category": CANARY, "result": CANARY}]
    row = OperationalMonitor(versions()).record(response)
    assert row["tools"][0]["error_category"] == "tool_result_error"
    assert CANARY not in json.dumps(row)


def test_finally_counts_failure_and_preserves_exception():
    exc = TimeoutError(CANARY)
    class Engine:
        def answer(self, *args, **kw):
            raise exc
    monitor = OperationalMonitor(versions("real_api"))
    with raises(TimeoutError) as caught:
        InstrumentedEngine(Engine(), monitor).answer(CANARY)
    assert caught.exception is exc
    assert monitor.snapshot()["counts"]["errors"] == {"timeout_or_budget": 1}
    assert CANARY not in json.dumps(monitor.snapshot())


def test_finally_counts_cancel_and_preserves_exception():
    from open_oracle.session_control import SessionCancelled
    class Engine:
        def answer(self, *args, **kw):
            raise SessionCancelled(CANARY)
    monitor = OperationalMonitor(versions("real_api"))
    with raises(SessionCancelled):
        InstrumentedEngine(Engine(), monitor).answer(CANARY)
    assert monitor.snapshot()["counts"]["status"] == {"cancelled": 1}


def test_held_clarification_and_refusal_counts_with_no_retained_rows():
    monitor = OperationalMonitor(versions("real_api"))
    held = answer("real_api")
    held["status"] = "unavailable"
    held["review"]["status"] = "rejected"
    held["operational_receipt"]["release"].update(status="unavailable", review="rejected")
    held["operational_receipt"]["released_sources"] = []
    monitor.record(held)
    monitor.record({"status": "clarification", "review": {"status": "not_run"}, "answer": CANARY})
    monitor.record({"status": "neutrality_boundary", "review": {"status": "not_run"}, "answer": CANARY})
    assert monitor.snapshot()["totals"]["held"] == 1
    assert monitor.snapshot()["totals"]["refusals"] == 1
    assert not hasattr(monitor, "rows")


def test_parallel_counts_bounded_and_identifiers_absent():
    monitor = OperationalMonitor(versions())
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda _: monitor.record(answer(), elapsed_ms=20), range(80)))
    assert monitor.snapshot()["totals"]["completed_operations"] == 80
    assert len(monitor.snapshot()["counts"]["tools"]) == 1


def test_helpfulness_aggregate_only_and_bool_required():
    monitor = OperationalMonitor(versions())
    monitor.helpfulness(True)
    monitor.helpfulness(False)
    with raises(ValueError): monitor.helpfulness(CANARY)
    assert monitor.snapshot()["totals"] == {"helpful": 1, "not_helpful": 1}


@patch.dict("os.environ", {"OTEL_SDK_DISABLED": "false"})
def test_otel_serialized_spans_are_content_free_and_correlated():
    global_provider = trace.get_tracer_provider()
    exporter = InMemorySpanExporter()
    emitter = SafeTraceEmitter(exporter)
    monitor = OperationalMonitor(versions("real_api"), emitter=emitter)
    row = monitor.record(answer("real_api"), elapsed_ms=20)
    spans = exporter.get_finished_spans()
    serialized = json.dumps([json.loads(s.to_json()) for s in spans])
    assert CANARY not in serialized
    assert len(spans) == 4  # Stage, tool, model event, one root.
    assert len({s.context.trace_id for s in spans}) == 1
    roots = [s for s in spans if s.parent is None]
    assert len(roots) == 1 and roots[0].attributes["oracle.request_id"] == row["request_id"]
    assert all(not s.events for s in spans)
    assert trace.get_tracer_provider() is global_provider
    assert monitor.snapshot()["export_status"]["span_export_successes"] == 4
    emitter.close()


@patch.dict("os.environ", {"OTEL_SDK_DISABLED": "false"})
def test_export_failure_does_not_change_return_or_log_exception():
    class Failing(SpanExporter):
        def export(self, spans): raise RuntimeError(CANARY)
    response = answer()
    class Engine:
        def answer(self, *args, **kw): return response
    emitter = SafeTraceEmitter(Failing())
    monitor = OperationalMonitor(versions(), emitter=emitter)
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        assert InstrumentedEngine(Engine(), monitor).answer(CANARY) is response
    assert monitor.snapshot()["export_status"]["span_export_failures"] == 4
    assert CANARY not in out.getvalue() + err.getvalue()
    emitter.close()


@parameterized("endpoint", ["http://example.com/v1/traces", "https://u:p@example.com/v1/traces", "https://example.com/v1/traces?secret=x"])
def test_export_destination_rejected_before_network(endpoint):
    with raises(ValueError): approved_otlp_emitter(endpoint, network_export_approved=True)


def test_export_default_off_and_ambient_transport_rejected():
    with raises(ValueError): approved_otlp_emitter("https://example.com/v1/traces")
    with patch.dict("os.environ", {"OTEL_EXPORTER_OTLP_HEADERS": CANARY}):
        with raises(ValueError): approved_otlp_emitter("https://example.com/v1/traces", network_export_approved=True)


def test_readout_uses_aggregates_and_escapes_text():
    monitor = OperationalMonitor(versions())
    row = monitor.record(answer())
    html = render_dashboard(monitor.snapshot())
    assert "<table>" in html and "scope='col'" in html and "<script" not in html
    assert CANARY not in html and row["request_id"] not in html
    altered = monitor.snapshot()
    altered["limitations"] = ["<script>alert(1)</script>"]
    assert "<script>" not in render_dashboard(altered)


def test_promptfoo_offline_real_engine_with_no_provider_calls():
    from open_oracle.corpus import Corpus
    from open_oracle.engine import EvidenceLoop
    corpus = Corpus()
    identity = TrustedVersions(CONFIG, {k: v["sha256"] for k,v in corpus.evidence.items()})
    adapter = EvaluationAdapter(EvidenceLoop(corpus), identity)
    result = adapter.call_api("What is the COMBAT tax rate?", {}, {"vars": {"scope": {"authority": "JCEB"}, "contest_id": "combat"}})
    assert "output" in result and result["latencyMs"] >= 0
    assert result["tokenUsage"] == {"prompt": 0, "completion": 0, "total": 0, "numRequests": 0}
    assert result["metadata"]["coverage"] == "sdk_receipt"
    assert result["metadata"]["ai_judge"] is False and "cost" not in result


def test_live_adapter_requires_frozen_public_case_and_reservation():
    called = []
    class Engine:
        def answer(self, *args, **kw): called.append(kw); return answer("real_api")
    case = {"prompt": "public fixture", "scope": {"authority": "JCEB"}, "contest_id": "combat"}
    adapter = EvaluationAdapter(Engine(), versions("real_api"), public_cases={"case-one": case}, before_paid_case=lambda ident: True)
    assert "error" in adapter.call_api(CANARY, {}, {"vars": {"case_id": "case-one"}})
    assert not called
    result = adapter.call_api("public fixture", {}, {"vars": {"case_id": "case-one", "scope": {"identity": CANARY}}})
    assert called == [{"contest_id": "combat"}]
    assert result["tokenUsage"] == {"numRequests": 3, "total": 152, "prompt": 130, "completion": 22}
    assert "cost" not in result and result["metadata"]["usage_complete"] is True


def test_provider_failure_sanitized_unknown_usage_reported():
    class Engine:
        def answer(self, *args, **kw): raise ConnectionError(CANARY)
    adapter = EvaluationAdapter(Engine(), versions("real_api", embeddings_enabled=True),
        public_cases={"public": {"prompt": "public"}}, before_paid_case=lambda ident: True)
    result = adapter.call_api("public", {}, {"vars": {"case_id": "public"}})
    assert CANARY not in json.dumps(result)
    assert result["metadata"]["coverage"] == "boundary_only"
    assert result["metadata"]["usage_complete"] is False
    assert result["metadata"]["provider_request_count_basis"] == "observed_lower_bound"
    assert result["metadata"]["unknown_component_call_counts"] == ["strands", "decisions", "embeddings"]


def test_config_ids_distinct_no_automatic_promotion_or_fabricated_cost():
    class Engine:
        def answer(self, *args, **kw): return answer()
    adapter = EvaluationAdapter(Engine(), versions(experiment_sha256="c"*64))
    result = adapter.call_api("public", {}, {})
    assert result["metadata"]["runtime_config_sha256"] == CONFIG
    assert result["metadata"]["experiment_sha256"] == "c"*64
    assert result["metadata"]["config_promotion"] == "disabled"
    assert result["metadata"]["cost_basis"] == "unknown"


@patch.dict("os.environ", {"OTEL_SDK_DISABLED": "false"})
def test_schema_events_are_revalidated_bounded_and_content_free():
    from oracle_observability.schema import validate_schema_event
    good = {"schema": "cited_answer_v1", "schema_sha256": CONFIG, "category": "list_type", "field_path": "claims"}
    with raises(ValueError): validate_schema_event({**good, "input": CANARY})
    with raises(ValueError): validate_schema_event({**good, "field_path": "claims." + CANARY})
    with raises(ValueError): validate_schema_event({**good, "category": CANARY})
    response = answer()
    response["operational_receipt"]["schema_events"] = [good]*31 + [{**good, "field_path": CANARY}] + [good]*4
    exporter = InMemorySpanExporter()
    emitter = SafeTraceEmitter(exporter)
    monitor = OperationalMonitor(versions(), emitter=emitter)
    row = monitor.record(response)
    assert len(row["schema_events"]) == 31 and row["invalid_schema_events"] == 5
    assert monitor.snapshot()["counts"]["schema_categories"] == {"list_type": 31}
    assert monitor.snapshot()["counts"]["schema_paths"] == {"claims": 31}
    assert CANARY not in json.dumps([json.loads(s.to_json()) for s in exporter.get_finished_spans()])
    emitter.close()


def test_evaluation_callback_failures_never_expose_exception_text():
    def broken(*args): raise ValueError(CANARY)
    class Engine:
        def answer(self, *args, **kw): return answer("real_api")
    fixture = {"public": {"prompt": "public"}}
    adapter = EvaluationAdapter(Engine(), versions("real_api"), public_cases=fixture, before_paid_case=broken)
    result = adapter.call_api("public", {}, {"vars": {"case_id": "public"}})
    assert CANARY not in json.dumps(result) and "error" in result
    adapter = EvaluationAdapter(Engine(), versions("real_api"), public_cases=fixture,
                                before_paid_case=lambda ident: True, measured_usage=broken)
    result = adapter.call_api("public", {}, {"vars": {"case_id": "public"}})
    assert result["metadata"]["measurement_callback_failed"] is True
    assert CANARY not in json.dumps(result["metadata"])


def test_frozen_receipt_hunk_has_independent_schema_bounds_and_copy():
    import types
    from pathlib import Path
    module = types.ModuleType("strands_quality.staged_receipts")
    module.__package__ = "strands_quality"
    file = Path(__file__).resolve().parents[1] / "proof/staged-receipts.py"
    if file.exists():
        exec(compile(file.read_text(), str(file), "exec"), module.__dict__)
    else:
        import strands_quality.receipts as module
    r = module.EvidenceReceipt(config_hash=CONFIG, execution="synthetic_sdk", source_catalog={}, max_events=3)
    event = {"schema": "cited_answer_v1", "schema_sha256": CONFIG, "category": "list_type", "field_path": "claims"}
    for _ in range(5): r.schema_validation(**event)
    with raises(ValueError): r.schema_validation(**{**event, "msg": CANARY})
    with raises(ValueError): r.schema_validation(**{**event, "field_path": CANARY})
    r.finish()
    r.schema_validation(**event)
    projected = r.snapshot()
    assert len(projected["schema_events"]) == 3 and projected["schema_dropped_event_count"] == 2
    projected["schema_events"][0]["field_path"] = CANARY
    assert CANARY not in json.dumps(r.snapshot())


def test_proposed_server_hunks_collect_and_render_actual_local_http():
    import types, threading, urllib.request
    from pathlib import Path
    import open_oracle.server as canonical
    module = types.ModuleType("open_oracle.staged_telemetry_server")
    module.__package__ = "open_oracle"
    module.__file__ = canonical.__file__
    stage = Path(__file__).resolve().parents[1] / "proof/staged-server.py"
    if stage.exists():
        exec(compile(stage.read_text(), str(stage), "exec"), module.__dict__)
    else:
        module = canonical
    with raises(ValueError): module.make_server(operations=True, allowed_hosts=("tunnel.example",))
    server = module.make_server(port=0, operations=True)
    worker = threading.Thread(target=server.serve_forever, daemon=True); worker.start()
    url = "http://127.0.0.1:" + str(server.server_port)
    session = str(uuid4())
    headers = {"Content-Type": "application/json", "Origin": url, "X-Oracle-Session": session}
    def request(path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        return urllib.request.urlopen(urllib.request.Request(url+path, data=data, headers=headers), timeout=3)
    try:
        for prompt in ("What does COMBAT say?", "Tell me about Wilson", "Who should I vote for?"):
            with request("/api/ask", {"question": prompt, "request_id": CANARY}) as response:
                assert response.status == 200
        with request("/api/operations") as response: aggregate = json.load(response)
        assert aggregate["totals"]["completed_operations"] == 3
        assert aggregate["counts"]["status"] == {"answered": 1, "clarification": 1, "neutrality_boundary": 1}
        assert aggregate["counts"]["coverage"] == {"sdk_receipt": 3}
        assert aggregate["collection"] == "volatile_aggregate_only" and aggregate["export_enabled"] is False
        assert CANARY not in json.dumps(aggregate) and session not in json.dumps(aggregate)
        with request("/operations") as response:
            html = response.read().decode()
            assert "Operation totals" in html and CANARY not in html and session not in html
        with request("/api/erase", {}) as response: assert response.status == 200
        with raises(urllib.error.HTTPError) as caught:
            request("/api/ask", {"question": "What does COMBAT say?"})
        assert caught.exception.code == 410
        caught.exception.close()
        with request("/api/operations") as response: after = json.load(response)
        assert after["totals"]["completed_operations"] == 3
        # Only process aggregate remains; there is no per-session telemetry history.
        with request("/api/health") as response: health = json.load(response)
        assert health["mode"] == "exact_source" and health["provider"] is None
        assert health["voice"] == "not_connected" and health["input_events"]["enabled"] is False
        proof = {"execution": "isolated_virtual_server_hunks_real_http", "primary_app_changed": False,
                 "paid_calls": 0, "operations": aggregate["totals"], "coverage": aggregate["counts"]["coverage"],
                 "privacy_canary_absent": True, "erase_status": 200, "old_session_status": 410,
                 "health": {k: health[k] for k in ("mode", "provider", "voice", "input_events")}}
        if stage.exists():
            (stage.parent / "server-integration.json").write_text(json.dumps(proof, indent=2)+"\n")
            (stage.parent / "operations-readout.html").write_text(html)
    finally:
        server.shutdown(); server.server_close(); worker.join(timeout=2)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn))


@patch.dict("os.environ", {"OTEL_SDK_DISABLED": "true"})
def test_private_provider_honors_global_sdk_disable():
    exporter = InMemorySpanExporter()
    emitter = SafeTraceEmitter(exporter)
    try:
        monitor = OperationalMonitor(versions(), emitter=emitter)
        monitor.record(answer(), elapsed_ms=20)
        assert not exporter.get_finished_spans()
        assert emitter.snapshot()["span_export_attempts"] == 0
        assert monitor.snapshot()["totals"]["completed_operations"] == 1
    finally:
        emitter.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
