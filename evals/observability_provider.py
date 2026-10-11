"""Offline default Promptfoo provider with full pipeline numeric metadata.

Copy beside evals/provider.py; replacing its config target is a core-owned hunk.
No environment switch to construct a paid provider. Live targets must explicitly
inject EvaluationAdapter with a public fixture manifest and reservation callback.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from oracle_observability.evaluation import EvaluationAdapter
from oracle_observability.monitor import TrustedVersions, canonical_hash

_adapter = None


def call_api(prompt, options, context):
    global _adapter
    if (options or {}).get("config", {}).get("execution", "exact_source") != "exact_source":
        return {"error": "This target is offline exact_source; live adapters require explicit owner injection.",
                "tokenUsage": {"numRequests": 0}}
    if _adapter is None:
        from open_oracle.corpus import Corpus
        import open_oracle.engine as engine_module
        from open_oracle.engine import EvidenceLoop
        from open_oracle.quality_policy import REVISED_CHECKS
        from importlib.metadata import version
        from hashlib import sha256
        corpus = Corpus()
        root = Path(engine_module.__file__).resolve().parents[1]
        package = Path(__file__).resolve().parents[1] / "oracle_observability"
        files = {"open_oracle/" + p: root / "open_oracle" / p for p in ("engine.py", "quality_policy.py", "operational_receipts.py")}
        files.update({"oracle_observability/" + p: package / p for p in ("monitor.py", "evaluation.py")})
        files["evals/observability_provider.py"] = Path(__file__)
        versions = TrustedVersions(deployment_sha256=canonical_hash({name: sha256(p.read_bytes()).hexdigest() for name, p in files.items()}),
            source_catalog={ident: e["sha256"] for ident, e in corpus.evidence.items()},
            sdk_version=version("strands-agents"), rubric_sha256=canonical_hash(REVISED_CHECKS))
        _adapter = EvaluationAdapter(EvidenceLoop(corpus), versions)
    return _adapter.call_api(prompt, options, context)
