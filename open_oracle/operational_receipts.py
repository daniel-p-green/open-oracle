"""Request metadata only; no exporter, visitor transcript or persistent sink."""
from contextvars import ContextVar
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path

from strands_quality.receipts import EvidenceReceipt

current_receipt = ContextVar("oracle_operational_receipt", default=None)


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def new_receipt(loop):
    catalog = {ident: item["sha256"] for ident, item in loop.corpus.evidence.items()}
    root = Path(__file__).parent
    # Version actual policy/code, provider identity, public source versions and limits.
    # The hash never includes question, request identity or visitor jurisdiction.
    config = {
        "implementation": {name: sha256((root / name).read_bytes()).hexdigest() for name in
                           ("engine.py", "orchestration.py", "readability.py", "operational_receipts.py", "claim_bindings.py", "quality_policy.py", "openai_integrations.py")},
        "sources": catalog, "sdk": version("strands-agents"),
        "provider_model": getattr(loop.selector, "receipt_model", "unverified_selector") if loop.selector else "none",
        "reviewer": type(loop.reviewer).__module__ + "." + type(loop.reviewer).__name__ if loop.reviewer else "none",
        "limits": {"model_calls": 5, "tool_calls": 8, "seconds": 25, "message_bytes": 90000, "retries": 0},
    }
    execution = getattr(loop.selector, "receipt_execution", "synthetic_sdk") if loop.selector else "exact_source"
    return EvidenceReceipt(config_hash=fingerprint(config), execution=execution, source_catalog=catalog)


def bind_agent_configuration(receipt, provider, tools, prompt, schema):
    """Bind the actual registered schemas and prompt without serializing contents."""
    receipt.config_hash = fingerprint({
        "application_config": receipt.config_hash,
        "model_id": provider.get_config().get("model_id", "unknown"),
        "tools": [t.tool_spec for t in tools], "output_schema": schema,
        "system_prompt_sha256": sha256(prompt.encode()).hexdigest(),
    })


def record_release(receipt, response):
    for key, stage in (("resolve_retrieve_construct", "strands"), ("source_guards", "source_guards"),
                       ("decisions", "decisions")):
        if stage == "strands" and response.get("mode") != "live_strands":
            continue
        value = response.get("stage_ms", {}).get(key)
        if type(value) in (int, float):
            receipt.stage(stage, value / 1000)
    review = response.get("review", {})
    review_execution = review.get("execution", "not_run")
    if review_execution in ("offline_stub", "unverified_provider"):
        review_execution = "synthetic_sdk"
    elif review_execution not in {"real_api", "synthetic_sdk", "deterministic_guard", "not_run"}:
        review_execution = "not_run"
    receipt.release(status=response["status"], binding=response.get("fact_validation", {}).get("status", "not_run"),
                    review=review.get("status", "not_run"), review_execution=review_execution,
                    evidence_ids=[e["id"] for e in response.get("evidence", [])])
