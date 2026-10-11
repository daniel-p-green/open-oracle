"""Private, dependency-injected research service; no default provider or UI route."""
from .corpus import Corpus
from .session_control import check_cancel, current_cancel
from strands_quality.research_corpus import Scope, load_verified_corpus
from strands_quality.research_agent import ResearchRequest


def research_private(question, *, authority, model, execution, corpus=None,
                     municipality=None, district=None, is_current=lambda: True,
                     max_turns=12, timeout_seconds=45, max_total_tokens=40000):
    """Return a bounded private draft. Independent claim/review adaptation remains required."""
    check_cancel()
    if authority not in {"KCEB", "JCEB"}:
        raise ValueError("Research requires an explicit election authority")
    if not isinstance(question, str) or not 0 < len(question.strip()) <= 2000:
        raise ValueError("A public-source question of up to 2,000 characters is required")
    if execution == "real_api":
        from .openai_integrations import require_live_authorization
        require_live_authorization()
    elif execution != "synthetic_sdk":
        raise ValueError("Explicit real or synthetic execution required")
    request = ResearchRequest(load_verified_corpus(corpus or Corpus()),
        scope=Scope(authority=authority, municipality=municipality, district=district),
        model=model, execution=execution, cancel=current_cancel.get(), is_current=is_current,
        max_turns=max_turns, timeout_seconds=timeout_seconds, max_total_tokens=max_total_tokens)
    draft = request.run(question)
    check_cancel()
    if not is_current():
        raise TimeoutError("Research delivery was superseded")
    assert draft["public_display"] is False and draft["speech"] is False
    return draft
