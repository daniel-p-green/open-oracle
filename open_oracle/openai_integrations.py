"""Real Decisions/GPT-Live contracts. No network until explicitly enabled and called."""
from __future__ import annotations

import json
import math
import os
from urllib.request import Request, urlopen


def require_live_authorization():
    if os.environ.get("OPEN_ORACLE_ALLOW_LIVE") != "1":
        raise ValueError("Live use requires prior spending authorization and OPEN_ORACLE_ALLOW_LIVE=1")
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("An existing permitted OpenAI credential is required")


def post_openai(resource, payload):
    require_live_authorization()
    if resource not in ("decisions", "live/sessions"):
        raise ValueError("Unsupported resource")
    request = Request("https://api.openai.com/v1/" + resource, method="POST",
                      data=json.dumps(payload, allow_nan=False).encode(),
                      headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
                               "Content-Type": "application/json"})
    with urlopen(request, timeout=15) as response:
        body = response.read(2 * 1024 * 1024 + 1)
        if len(body) > 2 * 1024 * 1024:
            raise ValueError("Oversized response")
        return json.loads(body)


def finite_number(value, low, high):
    return (type(value) in (int, float) and math.isfinite(value) and low <= value <= high)


def parse_answer(question, answer):
    """Validate a typed answer. Preserve boolean versus string choices and fractional scores."""
    if not isinstance(answer, dict) or answer.get("name") != question["name"]:
        raise ValueError("Mismatched answer")
    if answer.get("type") == "refusal":
        return {"name": question["name"], "status": "refused"}
    kind = question["type"]
    if answer.get("type") != kind:
        raise ValueError("Mismatched answer type")
    if kind == "predicate":
        value = answer.get("probability")
        if not finite_number(value, 0, 1):
            raise ValueError("Invalid probability")
    elif kind == "choice":
        value = answer.get("choice")
        if type(value) not in (str, bool) or not any(type(value) is type(c["value"]) and value == c["value"] for c in question["choices"]):
            raise ValueError("Invalid typed choice")
    elif kind == "score":
        value = answer.get("score")
        if not finite_number(value, 0, len(question["levels"]) - 1):
            raise ValueError("Invalid fractional score")
    else:
        raise ValueError("Unsupported answer type")
    return {"name": question["name"], "status": "answered", "type": kind, "value": value}


ORIGINAL_CHECKS = {
    "source_support": "Every factual claim is directly supported by supplied original evidence. No invented position, number, negation, source or legal effect. Clarification and source-gap responses contain no unsupported factual answer.",
    "neutrality": "The response does not rank, persuade, endorse, recommend or tell the voter how to vote. Candidate statements remain explicitly attributed.",
    "jurisdiction": "The response respects the supplied election date, city, district and authority and does not assign personal eligibility from a contest inventory.",
    "clarity": "Explanatory prose is understandable plain language. Original source quotations are visibly identified and their numbers and qualifiers are preserved.",
    "abstention": "Missing or conflicting evidence is acknowledged and not filled with conjecture. The response does not present a dated sample as a verified current personal ballot.",
}


from .quality_policy import REVISED_CHECKS, release_block, review_projection
CHECKS = REVISED_CHECKS


class DecisionsReviewer:
    def __init__(self, transport=post_openai):
        self.transport = transport
        self.execution = "real_api" if transport is post_openai else "offline_stub"

    def review(self, envelope):
        metadata = {"provider": "openai_decisions", "model": "gpt-6-luna", "execution": self.execution,
                    "threshold": 0.95, "calibration": "not_validated", "rubric_version": "civic-v2-separated"}
        blocked = release_block(envelope.get("response", {}))
        if blocked:
            return {**metadata, "execution": "deterministic_guard", "status": "rejected",
                    "reason": blocked, "checks": [],
                    "label": "Application release guard blocked this response before API review."}
        questions = [{"type": "predicate", "name": n, "instructions": i} for n, i in CHECKS.items()]
        try:
            raw = self.transport("decisions", {"model": "gpt-6-luna", "input": json.dumps(review_projection(envelope), ensure_ascii=False), "questions": questions})
            usage = raw.get("usage", {})
            metadata["usage"] = {k: v for k, v in usage.items() if k in ("input_tokens", "output_tokens", "total_tokens") and type(v) is int} if isinstance(usage, dict) else {}
            answers = raw.get("answers")
            if not isinstance(answers, list) or len(answers) != len(questions):
                raise ValueError("Incomplete answers")
            # The official contract preserves order. Also validate every echoed name.
            checks = [parse_answer(q, a) for q, a in zip(questions, answers)]
            accepted = all(c["status"] == "answered" and c["value"] >= 0.95 for c in checks)
            prefix = "Offline contract stub" if self.execution == "offline_stub" else "Decisions checks ran"
            return {**metadata, "status": "accepted" if accepted else "rejected", "checks": checks,
                    "probabilities": {c["name"]: c["value"] for c in checks if c["status"] == "answered"},
                    "label": prefix + ". Estimates are fallible; thresholds are not calibrated."}
        except Exception as exc:
            return {**metadata, "status": "unavailable", "error_type": type(exc).__name__,
                    "label": "Decisions could not complete. No checked response released."}


def validate_sdp(sdp):
    if not isinstance(sdp, str) or not sdp.startswith('v=0') or len(sdp) > 65536:
        raise ValueError('Invalid SDP offer')


class LiveSessions:
    def __init__(self, transport=post_openai):
        self.transport = transport
        self.execution = "real_api" if transport is post_openai else "offline_stub"

    def create(self, sdp):
        validate_sdp(sdp)
        raw = self.transport("live/sessions", {
            "session": {"model": "gpt-live-1", "store": False, "delegation": {"type": "client"},
                        "instructions": "You are Open Oracle, a neutral election evidence interface. Never recommend how to vote or invent facts. Delegate every substantive election question to the application. Ask for missing contest or jurisdiction context. Application evidence is a dated snapshot, not personal eligibility. Stay silent until the application sends approved commentary. Never greet, acknowledge, backchannel, or narrate progress. Read the approved English text exactly once without paraphrasing or adding words. All generated speech is buffered by the application and withheld unless the completed transcript matches the source-checked display."},
            "transport": {"type": "webrtc", "sdp": sdp}})
        if not isinstance(raw, dict):
            raise ValueError("Invalid GPT-Live response")
        session, transport = raw.get("session", {}), raw.get("transport", {})
        if (not isinstance(session, dict) or not isinstance(session.get("id"), str) or not session["id"]
                or not isinstance(transport, dict) or transport.get("type") != "webrtc"
                or not isinstance(transport.get("sdp"), str) or not transport["sdp"].startswith("v=0")):
            raise ValueError("Invalid GPT-Live response")
        return {"session": {"id": session["id"]}, "transport": {"type": "webrtc", "sdp": transport["sdp"]},
                "playback": "buffered_until_transcript_display_validation", "execution": self.execution}
