"""Promptfoo evaluates the same EvidenceLoop used by the browser; no model calls here."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop

_engine = None


def call_api(prompt, options, context):
    global _engine
    if _engine is None:
        _engine = EvidenceLoop(Corpus())
    variables = context.get("vars", {})
    answer = _engine.answer(prompt, variables.get("scope", {}), contest_id=variables.get("contest_id"))
    return {"output": json.dumps(answer, ensure_ascii=False)}
