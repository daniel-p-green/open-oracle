"""Promptfoo result contract for the application pipeline, not an LLM judge.

Engines and public live cases are explicit injected dependencies. This module
never constructs a paid provider, reserves budget, or promotes a configuration.
"""
from __future__ import annotations

import json
from time import monotonic

from .monitor import OperationalMonitor, mapping


class EvaluationAdapter:
    def __init__(self, engine, versions, *, public_cases=None, before_paid_case=None, measured_usage=None, clock=monotonic):
        self.engine, self.monitor, self._clock = engine, OperationalMonitor(versions), clock
        self.public_cases = dict(public_cases or {})
        self.before_paid_case = before_paid_case
        self.measured_usage = measured_usage

    def call_api(self, prompt, options, context):
        variables = mapping(mapping(context).get("vars"))
        if self.monitor.versions.execution == "real_api":
            # Live mode cannot be activated by a visitor/context variable. The
            # public fixture manifest and budget reservation are owner-injected.
            case_id = variables.get("case_id")
            case = self.public_cases.get(case_id) if isinstance(case_id, str) else None
            if not isinstance(case, dict) or prompt != case.get("prompt") or self.before_paid_case is None:
                return {"error": "Live evaluation requires an approved public fixture and a reserved budget.", "tokenUsage": {"numRequests": 0}}
            variables = case  # Ignore client-supplied scope/model/config metadata.
            try:
                reserved = self.before_paid_case(case_id) is True
            except Exception:
                return {"error": "Live evaluation reservation failed.", "tokenUsage": {"numRequests": 0}}
            if not reserved:
                return {"error": "Live evaluation reservation declined.", "tokenUsage": {"numRequests": 0}}
        started = self._clock()
        response, error = None, None
        try:
            response = self.engine.answer(prompt, variables.get("scope", {}), contest_id=variables.get("contest_id"))
        except Exception as exc:
            error = exc
        elapsed = max(0, (self._clock()-started)*1000)
        measurement_failed = False
        try:
            extra = mapping(self.measured_usage()) if self.measured_usage is not None else {}
        except Exception:
            extra, measurement_failed = {}, True
        row = self.monitor.record(response, error=error, elapsed_ms=elapsed,
                                  embedding_usage=extra.get("embeddings"), estimated_cost_usd=extra.get("estimated_cost_usd"))
        parts = row["usage"]
        # Synthetic SDK attempts are not paid/provider requests. Missing live
        # counts cannot be represented as a measured zero.
        paid = row["execution"] == "real_api"
        calls_known = all(v["calls"] is not None for v in parts.values())
        token_known = all(v["total_tokens"] is not None for v in parts.values())
        token_usage = {}
        if not paid:
            token_usage = {"prompt": 0, "completion": 0, "total": 0, "numRequests": 0}
        else:
            # Promptfoo defaults absent numRequests to one wrapper invocation.
            # Provide an explicitly labelled observed lower bound instead.
            token_usage["numRequests"] = sum(v["calls"] for v in parts.values() if v["calls"] is not None)
            if token_known:
                token_usage["total"] = sum(v["total_tokens"] for v in parts.values())
            if all(v["input_tokens"] is not None for v in parts.values()):
                token_usage["prompt"] = sum(v["input_tokens"] for v in parts.values())
            if all(v["output_tokens"] is not None for v in parts.values()):
                token_usage["completion"] = sum(v["output_tokens"] for v in parts.values())
        metadata = {"execution": row["execution"], "coverage": row["coverage"],
                    "run_id": row["run_id"], "request_id": row["request_id"],
                    "runtime_config_sha256": row["runtime_config_sha256"],
                    "deployment_sha256": row["deployment_sha256"], "experiment_sha256": row["experiment_sha256"],
                    "source_catalog_sha256": row["source_catalog_sha256"], "rubric_sha256": row["rubric_sha256"],
                    "release_outcome": row["release_outcome"], "source_binding": row["binding"],
                    "decisions_status": row["review"], "component_usage": row["usage"],
                    "usage_complete": calls_known and token_known, "cost_basis": row["cost_basis"],
                    "measurement_callback_failed": measurement_failed,
                    "provider_request_count_basis": "complete" if calls_known else "observed_lower_bound",
                    "unknown_component_call_counts": [k for k, v in parts.items() if v["calls"] is None],
                    "ai_judge": False, "generic_ai_judge": False,
                    "decisions_role": "application_predicate_review" if row["review_execution"] == "real_api" else "not_run",
                    "config_promotion": "disabled"}
        result = {"latencyMs": elapsed, "metadata": metadata}
        if token_usage:
            result["tokenUsage"] = token_usage
        if row["estimated_cost_usd"] is not None:
            result["cost"] = row["estimated_cost_usd"]
        if error is not None:
            result["error"] = "Application execution failed: " + (row["error_category"] or "execution_error")
        else:
            # Only authored public evaluation inputs belong in Promptfoo. A
            # held answer remains an output; assertions evaluate its abstention.
            try:
                result["output"] = json.dumps(response, ensure_ascii=False, allow_nan=False)
            except (ValueError, TypeError):
                result["error"] = "Application output contract failed."
        # No default cost/rates, no fallible score converted to a truth label.
        return result
