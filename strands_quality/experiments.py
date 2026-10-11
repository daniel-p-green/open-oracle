"""Frozen local experiments, honest execution labels, review-only promotion.

The runner is an explicit dependency: this module never builds a paid provider.
Raw synthetic/curated cases remain in local fixtures; reports omit inputs/output.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from importlib.metadata import version
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import median
from typing import Callable
from uuid import uuid4

from .receipts import digest, STATUSES

QUALITY = ("source_support", "no_vote_advice", "viewpoint_neutrality", "jurisdiction",
           "clarity", "abstention", "translation")
CRITICAL = ("source_binding", "scope_date", "no_vote_advice", "translation", "reset_isolation")
EXECUTIONS = {"exact_source", "synthetic_sdk", "real_api"}


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def fingerprint(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def identifier(value: str):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9_.:-]{0,119}", value):
        raise ValueError("Invalid controlled identifier")
    return value


@dataclass(frozen=True)
class Configuration:
    name: str
    execution: str
    provider: str
    model_id: str
    prompt_sha256: str
    tools_sha256: str
    schema_sha256: str
    corpus_sha256: str
    rubric_sha256: str
    sdk_version: str = "1.59.0"
    max_turns: int = 5
    max_total_tokens: int = 12000
    max_tool_records: int = 8
    timeout_seconds: int = 25
    retry_attempts: int = 1

    def __post_init__(self):
        identifier(self.name)
        if self.execution not in EXECUTIONS or self.provider not in {"none", "synthetic", "openai", "bedrock"}:
            raise ValueError("Invalid execution/provider")
        if ((self.execution == "exact_source" and self.provider != "none") or
                (self.execution == "synthetic_sdk" and self.provider != "synthetic") or
                (self.execution == "real_api" and self.provider not in {"openai", "bedrock"})):
            raise ValueError("Execution/provider mismatch")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}", self.model_id) or self.model_id.startswith("sk-"):
            raise ValueError("Invalid trusted model identity")
        if not re.fullmatch(r"\d+\.\d+\.\d+", self.sdk_version):
            raise ValueError("Invalid SDK version")
        for value in (self.prompt_sha256, self.tools_sha256, self.schema_sha256,
                      self.corpus_sha256, self.rubric_sha256):
            digest(value)
        for value in (self.max_turns, self.max_total_tokens, self.max_tool_records, self.timeout_seconds):
            if type(value) is not int or value <= 0:
                raise ValueError("Limits must be positive integers")
        if self.retry_attempts != 1:
            raise ValueError("Tonight's trials must preserve no-retry policy")

    @property
    def sha256(self):
        return fingerprint(asdict(self))


@dataclass(frozen=True)
class Case:
    name: str
    split: str
    group: str
    prompt: str
    expected_status: str
    expected_facets: tuple[str, ...] = ()
    expected_evidence: tuple[str, ...] = ()
    scope: dict = field(default_factory=dict)
    label_origin: str = "agent_authored"
    heldout_prior_exposure: bool = False

    def __post_init__(self):
        identifier(self.name)
        identifier(self.group)
        if self.split not in {"regression", "heldout"} or self.label_origin not in {
                "agent_authored", "human_reviewed", "synthetic_contract"}:
            raise ValueError("Invalid case labels")
        if self.split == "heldout" and self.heldout_prior_exposure:
            raise ValueError("Consumed historical cases belong in regression")
        if not isinstance(self.prompt, str) or not 0 < len(self.prompt) <= 2000:
            raise ValueError("Invalid curated input")
        if self.expected_status not in STATUSES:
            raise ValueError("Invalid expected response")
        if not isinstance(self.scope, dict) or set(self.scope) - {"election_date", "authority", "municipality", "district"}:
            raise ValueError("Invalid scope fixture")
        if any(not isinstance(v, str) or len(v) > 100 for v in self.scope.values()):
            raise ValueError("Invalid scope values")
        for value in (*self.expected_facets, *self.expected_evidence):
            identifier(value)

    @property
    def sha256(self):
        return fingerprint(asdict(self))


@dataclass(frozen=True)
class Observation:
    execution: str
    status: str
    facets: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    critical: dict[str, bool | None] = field(default_factory=dict)
    quality: dict[str, bool | None] = field(default_factory=dict)
    latency_ms: float | None = None
    estimated_cost_usd: float | None = None
    receipt: dict | None = None

    def __post_init__(self):
        if self.execution not in EXECUTIONS or self.status not in STATUSES:
            raise ValueError("Invalid observation")
        for observed, allowed in ((self.critical, CRITICAL), (self.quality, QUALITY)):
            if set(observed) - set(allowed) or any(v is not None and type(v) is not bool for v in observed.values()):
                raise ValueError("Checks must be booleans or explicitly unknown")
        for value in (self.latency_ms, self.estimated_cost_usd):
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                raise ValueError("Invalid measured metric")


def freeze(path: Path, configurations: list[Configuration], cases: list[Case]) -> dict:
    if not configurations or not cases or len({c.name for c in configurations}) != len(configurations):
        raise ValueError("Nonempty uniquely named configurations required")
    if len({c.name for c in cases}) != len(cases):
        raise ValueError("Case IDs must be unique")
    regression = {c.group for c in cases if c.split == "regression"}
    heldout = {c.group for c in cases if c.split == "heldout"}
    if not heldout or regression & heldout:
        raise ValueError("Held-out groups required and must not overlap regression")
    if len({(c.prompt_sha256, c.tools_sha256, c.schema_sha256, c.corpus_sha256, c.rubric_sha256,
             c.provider, c.model_id, c.execution, c.max_turns, c.max_total_tokens,
             c.max_tool_records, c.timeout_seconds, c.retry_attempts) for c in configurations}) != len(configurations):
        raise ValueError("Differently named identical configurations are not distinct trials")
    body = {"version": 1, "configurations": [asdict(c) for c in configurations],
            "cases": [asdict(c) for c in cases]}
    manifest = {**body, "manifest_sha256": fingerprint(body)}
    # Exclusive creation prevents silently rewriting a consumed/frozen experiment.
    with path.open("x") as stream:
        stream.write(json.dumps(manifest, indent=2) + "\n")
    return manifest


def load_frozen(path: Path):
    manifest = json.loads(path.read_text())
    if set(manifest) != {"version", "configurations", "cases", "manifest_sha256"} or manifest["version"] != 1:
        raise ValueError("Invalid manifest")
    body = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    if fingerprint(body) != digest(manifest["manifest_sha256"]):
        raise ValueError("Frozen manifest changed")
    configs = [Configuration(**c) for c in manifest["configurations"]]
    cases = [Case(**{**c, "expected_facets": tuple(c["expected_facets"]),
                    "expected_evidence": tuple(c["expected_evidence"])}) for c in manifest["cases"]]
    if len({c.name for c in configs}) != len(configs) or len({c.name for c in cases}) != len(cases):
        raise ValueError("Duplicate frozen identity")
    groups = {s: {c.group for c in cases if c.split == s} for s in ("regression", "heldout")}
    if not configs or not groups["heldout"] or groups["regression"] & groups["heldout"]:
        raise ValueError("Invalid frozen split")
    return manifest, configs, cases


def run_frozen(path: Path, runner: Callable[[Configuration, Case], Observation]) -> dict:
    """Run all precommitted configurations once; reserve heldout before execution.

    The .consumed.json ledger is permanent even after failure: do not retry the
    same heldout after seeing partial results. A new reviewed split is required.
    """
    manifest, configs, cases = load_frozen(path)
    if any(c.sdk_version != version("strands-agents") for c in configs):
        raise ValueError("Installed SDK differs from frozen configuration")
    run_id = str(uuid4())
    ledger_path = path.with_suffix(".consumed.json")
    with ledger_path.open("x") as stream:
        stream.write(canonical({"run_id": run_id, "manifest_sha256": manifest["manifest_sha256"],
                                "state": "reserved_before_execution"}) + "\n")
    reports = []
    for config in configs:
        rows = []
        for case in cases:
            original_case_hash = case.sha256
            observation = runner(config, case)
            if case.sha256 != original_case_hash:
                raise ValueError("Runner mutated a frozen case")
            if observation.execution != config.execution:
                raise ValueError("Fallback/synthetic execution cannot count as live")
            receipt = observation.receipt
            if receipt is not None and (receipt.get("config_sha256") != config.sha256 or
                    receipt.get("execution") != observation.execution or not receipt.get("finalized")):
                raise ValueError("Receipt does not match completed trial")
            # No raw observation.receipt copied: it belongs to the request sink.
            rows.append({"case": case.name, "case_sha256": case.sha256, "split": case.split,
                "label_origin": case.label_origin, "execution": observation.execution,
                "status_matches": observation.status == case.expected_status,
                "facets_complete": set(case.expected_facets) <= set(observation.facets),
                "evidence_complete": set(case.expected_evidence) <= set(observation.evidence_ids),
                "critical": {k: observation.critical.get(k) for k in CRITICAL},
                "quality": {k: observation.quality.get(k) for k in QUALITY},
                "latency_ms": observation.latency_ms, "estimated_cost_usd": observation.estimated_cost_usd,
                "receipt_present": receipt is not None})
        timing = [r["latency_ms"] for r in rows if r["latency_ms"] is not None]
        reports.append({"config_sha256": config.sha256, "name": config.name, "execution": config.execution,
            "cases": rows, "n": len(rows), "latency_median_ms": median(timing) if timing else None,
            # A tiny suite does not support a useful tail percentile.
            "latency_p95_ms": sorted(timing)[math.ceil(.95 * len(timing)) - 1] if len(timing) >= 20 else None,
            "estimated_cost_usd": sum(r["estimated_cost_usd"] for r in rows)
                if all(r["estimated_cost_usd"] is not None for r in rows) else None})
    result = {"version": 1, "run_id": run_id, "manifest_sha256": manifest["manifest_sha256"],
              "heldout_consumed": True, "population_reliability_claim": False, "reports": reports}
    result['report_sha256'] = fingerprint(result)
    # Final report never contains prompts, output prose, tool args or reviewer reasoning.
    path.with_suffix(".report.json").write_text(json.dumps(result, indent=2) + "\n")
    ledger_path.write_text(canonical({"run_id": run_id, "manifest_sha256": manifest["manifest_sha256"],
                                    "report_sha256": result['report_sha256'], "state": "completed"}) + "\n")
    return result


def promotion_gate(path: Path, result: dict, candidate_hash: str, *, max_case_latency_ms: float,
                   max_total_estimated_cost_usd: float, baseline_hash: str | None = None) -> dict:
    """Recommendation only. Never updates config or relaxes reviewer thresholds."""
    manifest, configs, cases = load_frozen(path)
    for bound in (max_case_latency_ms, max_total_estimated_cost_usd):
        if type(bound) not in (int, float) or not math.isfinite(bound) or bound < 0:
            raise ValueError("Promotion bounds must be finite and nonnegative")
    reasons = []
    ledger = json.loads(path.with_suffix(".consumed.json").read_text())
    if (result.get("manifest_sha256") != manifest["manifest_sha256"] or not result.get("heldout_consumed") or
            ledger.get("state") != "completed" or ledger.get("run_id") != result.get("run_id") or
            ledger.get("manifest_sha256") != manifest["manifest_sha256"] or
            ledger.get('report_sha256') != result.get('report_sha256') or
            fingerprint({k:v for k,v in result.items() if k != 'report_sha256'}) != result.get('report_sha256')):
        reasons.append("unverified_frozen_run")
    expected_configs = {c.sha256 for c in configs}
    report_hashes = [r.get("config_sha256") for r in result.get("reports", [])]
    if set(report_hashes) != expected_configs or len(report_hashes) != len(expected_configs):
        reasons.append("configuration_set_mismatch")
    candidates = [r for r in result.get("reports", []) if r.get("config_sha256") == candidate_hash]
    if len(candidates) != 1 or candidate_hash not in expected_configs:
        return {"eligible": False, "reasons": sorted(set(reasons + ["unknown_candidate"]))}
    report = candidates[0]
    baselines = [r for r in result.get('reports', []) if r.get('config_sha256') == baseline_hash]
    if baseline_hash == candidate_hash or len(baselines) != 1 or baseline_hash not in expected_configs:
        reasons.append('baseline_comparison_required')
    else:
        baseline = baselines[0]
        config_by_hash = {c.sha256:c for c in configs}
        if any(getattr(config_by_hash[candidate_hash], key) != getattr(config_by_hash[baseline_hash], key)
               for key in ('corpus_sha256','rubric_sha256','sdk_version')):
            reasons.append('baseline_source_rubric_version_mismatch')
        def task_passes(r):
            return sum(all(row.get(k) is True for k in ('status_matches','facets_complete','evidence_complete'))
                       for row in r.get('cases', []))
        improvements = task_passes(report) > task_passes(baseline)
        for metric in ('latency_median_ms', 'estimated_cost_usd'):
            old, new = baseline.get(metric), report.get(metric)
            improvements |= type(old) in (int,float) and type(new) in (int,float) and new < old
        if not improvements:
            reasons.append('no_measured_improvement')
    if report.get("execution") != "real_api":
        reasons.append("real_api_evidence_required")
    expected_cases = {c.name: c for c in cases}
    rows = report.get("cases", [])
    if {r.get("case") for r in rows} != set(expected_cases) or len(rows) != len(cases):
        reasons.append("case_set_mismatch")
    for row in rows:
        case = expected_cases.get(row.get("case"))
        if not case or row.get("case_sha256") != case.sha256 or row.get("split") != case.split:
            reasons.append("case_identity_mismatch")
            continue
        if case.label_origin != "human_reviewed" or row.get("label_origin") != "human_reviewed":
            reasons.append("human_review_required")
        if row.get("execution") != "real_api" or not row.get("receipt_present"):
            reasons.append("real_receipt_required")
        if any(row.get(k) is not True for k in ("status_matches", "facets_complete", "evidence_complete")):
            reasons.append("task_coverage_failed")
        if any(row.get("critical", {}).get(k) is not True for k in CRITICAL):
            reasons.append("critical_boundary_failed_or_unknown")
        if any(row.get("quality", {}).get(k) is not True for k in QUALITY):
            reasons.append("quality_failed_or_unknown")
        latency = row.get("latency_ms")
        if type(latency) not in (int, float) or not math.isfinite(latency) or latency > max_case_latency_ms:
            reasons.append("latency_missing_or_over_bound")
    cost = report.get("estimated_cost_usd")
    if type(cost) not in (int, float) or not math.isfinite(cost) or cost > max_total_estimated_cost_usd:
        reasons.append("estimated_cost_missing_or_over_bound")
    return {"eligible": not reasons, "reasons": sorted(set(reasons)),
            "candidate_sha256": candidate_hash, "baseline_sha256": baseline_hash, "automatic_promotion": False}


def promote(registry_path: Path, *, candidate_hash: str, decision: dict,
            reviewer_approved: bool, expected_current_hash: str):
    """Local registry, explicit human approval, stale-write check; not live tuning."""
    candidate_hash, expected_current_hash = digest(candidate_hash), digest(expected_current_hash)
    if (not decision.get("eligible") or decision.get("candidate_sha256") != candidate_hash or
            decision.get('baseline_sha256') != expected_current_hash or reviewer_approved is not True):
        raise ValueError("Eligible reviewed candidate required")
    registry = json.loads(registry_path.read_text())
    if registry.get("current") != expected_current_hash:
        raise ValueError("Current configuration changed")
    registry_path.write_text(canonical({"version": 1, "current": candidate_hash,
                                       "previous": expected_current_hash}) + "\n")


def rollback(registry_path: Path, *, expected_current_hash: str):
    registry = json.loads(registry_path.read_text())
    if registry.get("current") != digest(expected_current_hash) or not registry.get("previous"):
        raise ValueError("No matching rollback available")
    previous = digest(registry["previous"])
    registry_path.write_text(canonical({"version": 1, "current": previous,
                                       "previous": registry["current"]}) + "\n")
