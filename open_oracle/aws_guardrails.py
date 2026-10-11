"""Request-owned ApplyGuardrail gate. It never grants factual release authority.

No credential loading or network calls happen at import/construction. The live
factory is separately opt-in, config-verified and budget-authorized by core.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Callable


@dataclass(frozen=True)
class GuardrailSpec:
    identifier: str
    version: str
    configuration_sha256: str
    region: str = "us-east-1"
    account: str = "123456789012"
    language: str = "en"
    grounding_required: bool = False

    def __post_init__(self):
        if self.region != "us-east-1" or self.account != "123456789012" or self.language != "en":
            raise ValueError("Unreviewed guardrail scope")
        pattern = rf"arn:aws:bedrock:{self.region}:{self.account}:guardrail/[a-z0-9]+"
        if not re.fullmatch(pattern, self.identifier):
            raise ValueError("Guardrail must use the reviewed account ARN")
        if not re.fullmatch(r"[1-9][0-9]{0,7}", self.version):
            raise ValueError("Immutable guardrail version required")
        if not re.fullmatch(r"[a-f0-9]{64}", self.configuration_sha256):
            raise ValueError("Reviewed configuration hash required")
        if type(self.grounding_required) is not bool:
            raise ValueError("Invalid grounding policy")


@dataclass(frozen=True)
class GroundingContext:
    query: str
    sources: str
    # Core must validate source hashes/roles/spans before supplying this object.


@dataclass(frozen=True)
class GuardrailResult:
    status: str
    reason: str
    surface: str
    execution: str
    guardrail_version: str
    configuration_sha256: str
    guarded_characters: int = 0
    total_characters: int = 0
    usage: tuple = ()

    def metadata(self):
        """No content, content hashes, matches, raw findings or visitor IDs."""
        return {"status": self.status, "reason": self.reason, "surface": self.surface,
                "execution": self.execution, "guardrail_version": self.guardrail_version,
                "configuration_sha256": self.configuration_sha256,
                "guarded_characters": self.guarded_characters,
                "total_characters": self.total_characters, "usage": dict(self.usage)}


def _nonnegative_int(value):
    return type(value) is int and value >= 0


USAGE_KEYS = frozenset({"contentPolicyUnits", "contentPolicyImageUnits", "topicPolicyUnits",
                       "wordPolicyUnits", "sensitiveInformationPolicyUnits",
                       "sensitiveInformationPolicyFreeUnits", "contextualGroundingPolicyUnits",
                       "automatedReasoningPolicyUnits", "automatedReasoningPolicies"})


def _safe_usage(value):
    if (not isinstance(value, dict) or not value.keys() <= USAGE_KEYS
            or any(not _nonnegative_int(v) for v in value.values())):
        return None
    return tuple(sorted(value.items()))


class BedrockGuardrailGate:
    """Use one instance per request; fixed input/text/speech call slots, no retry.

    is_current must check request cancellation/epoch. authorize_call reserves
    each actual billable attempt and checks the private canonical-request hash
    against its approved upload scope. This hash must not enter ordinary logs.
    Application-owned source and Decisions gates remain outside this adapter.
    """
    def __init__(self, spec: GuardrailSpec, client, *, execution: str,
                 is_current: Callable[[], bool], authorize_call: Callable[[str, int, str], None]):
        if execution not in {"synthetic", "real_api"}:
            raise ValueError("Explicit guardrail execution required")
        self.spec, self.client, self.execution = spec, client, execution
        self.is_current, self.authorize_call = is_current, authorize_call
        self._slots = {}  # private content bindings; never serialize/export
        self.attempts = 0
        if execution == "real_api" and client.meta.region_name != spec.region:
            raise ValueError("Client region mismatch")

    def _result(self, status, reason, surface, **values):
        return GuardrailResult(status, reason, surface, self.execution,
                               self.spec.version, self.spec.configuration_sha256, **values)

    def check(self, text: str, *, surface: str, language: str = "en", grounding=None):
        if surface not in {"input", "text", "speech"}:
            raise ValueError("Unknown guardrail surface")
        if not self.is_current():
            return self._result("cancelled", "request_not_current", surface)
        if language != self.spec.language:
            return self._result("unavailable", "language_not_reviewed", surface)
        # Do not truncate: unchecked content cannot become public output.
        if type(text) is not str or not text.strip() or len(text) > 5000:
            return self._result("unavailable", "invalid_or_oversized_content", surface)
        source = "INPUT" if surface == "input" else "OUTPUT"
        content = [{"text": {"text": text, "qualifiers": ["guard_content"]}}]
        if source == "INPUT" and grounding is not None:
            return self._result("unavailable", "grounding_not_input_policy", surface)
        if source == "OUTPUT" and self.spec.grounding_required:
            if (not isinstance(grounding, GroundingContext)
                    or type(grounding.query) is not str or not grounding.query.strip()
                    or type(grounding.sources) is not str or not grounding.sources.strip()
                    or len(grounding.query) > 1000 or len(grounding.sources) > 20000):
                return self._result("unavailable", "grounding_context_missing_or_invalid", surface)
            content = [{"text": {"text": grounding.sources, "qualifiers": ["grounding_source"]}},
                       {"text": {"text": grounding.query, "qualifiers": ["query"]}}] + content
        elif grounding is not None:
            return self._result("unavailable", "grounding_not_configured", surface)
        request = {"guardrailIdentifier": self.spec.identifier,
                   "guardrailVersion": self.spec.version, "source": source,
                   "content": content, "outputScope": "FULL"}
        binding = sha256(json.dumps(request, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if surface in self._slots:
            old_binding, result = self._slots[surface]
            return result if old_binding == binding else self._result("unavailable", "surface_changed", surface)
        # Consume even a denied reservation; never silently retry the stage.
        self._slots[surface] = (binding, self._result("unavailable", "authorization_failed", surface))
        try:
            authorized = self.authorize_call(surface, sum(len(b["text"]["text"]) for b in content), binding)
        except Exception:
            # Reservation errors must remain fail closed without echoing content.
            return self._slots[surface][1]
        if authorized is False:
            return self._slots[surface][1]
        if not self.is_current():
            return self._result("cancelled", "request_not_current", surface)
        self.attempts += 1
        try:
            response = self.client.apply_guardrail(**request)
        except Exception:
            # SDK errors can echo sensitive request/provider fields: omit them.
            result = self._result("unavailable", "provider_error", surface)
        else:
            try:
                result = self._parse(response, surface, len(text))
            except (KeyError, TypeError, ValueError):
                result = self._result("unavailable", "invalid_provider_response", surface)
        # A completed request cannot be unsent. This prevents late release only.
        if not self.is_current():
            result = self._result("cancelled", "request_not_current", surface)
        self._slots[surface] = (binding, result)
        return result

    def _parse(self, response, surface, length):
        if not isinstance(response, dict):
            raise ValueError("Invalid response")
        action = response["action"]
        if action not in {"NONE", "GUARDRAIL_INTERVENED"}:
            raise ValueError("Unknown action")
        safe_usage = _safe_usage(response.get("usage"))
        if action == "GUARDRAIL_INTERVENED":
            return self._result("blocked", "aws_intervention", surface, usage=safe_usage or ())
        coverage = response["guardrailCoverage"]["textCharacters"]
        guarded, total = coverage["guarded"], coverage["total"]
        if not (_nonnegative_int(guarded) and _nonnegative_int(total)
                and guarded == total and guarded >= length):
            return self._result("unavailable", "incomplete_coverage", surface)
        usage = response["usage"]
        if safe_usage is None:
            raise ValueError("Invalid usage")
        # Candidate base configuration enables content + sensitive policies on
        # both directions, and denied topics on output only. This is application
        # strictness, not a claim these fields are mandatory for every AWS config.
        required_units = ["contentPolicyUnits", "sensitiveInformationPolicyUnits"]
        if surface != "input":
            required_units.append("topicPolicyUnits")
        if self.spec.grounding_required and surface != "input":
            required_units.append("contextualGroundingPolicyUnits")
        if any(not _nonnegative_int(usage.get(k)) or usage[k] < 1 for k in required_units):
            return self._result("unavailable", "required_policy_not_assessed", surface)
        assessments = response["assessments"]
        if not isinstance(assessments, list) or not assessments:
            raise ValueError("Missing assessments")
        required_policies = {"contentPolicy", "sensitiveInformationPolicy"}
        if surface != "input":
            required_policies.add("topicPolicy")
        if self.spec.grounding_required and surface != "input":
            required_policies.add("contextualGroundingPolicy")
        seen_policies = set()
        for assessment in assessments:
            if not isinstance(assessment, dict) or "automatedReasoningPolicy" in assessment:
                raise ValueError("Unreviewed assessment policy")
            details = assessment.get("appliedGuardrailDetails")
            if details is not None and (not isinstance(details, dict)
                    or details.get("guardrailVersion") != self.spec.version
                    or details.get("guardrailArn") != self.spec.identifier):
                raise ValueError("Guardrail binding mismatch")
            for name in required_policies & assessment.keys():
                if not isinstance(assessment[name], dict) or not assessment[name]:
                    raise ValueError("Missing policy assessment")
                seen_policies.add(name)
            # Detection-only settings must not accidentally authorize output.
            def walk(value):
                if isinstance(value, dict):
                    if "detected" in value and type(value["detected"]) is not bool:
                        raise ValueError("Invalid detected flag")
                    if value.get("detected") is True or value.get("action") in {"BLOCKED", "ANONYMIZED"}:
                        return True
                    return any(walk(v) for k, v in value.items() if k not in {"match", "text", "regex"})
                if isinstance(value, list):
                    return any(walk(v) for v in value)
                return False
            if walk(assessment):
                return self._result("blocked", "detected_policy_finding", surface, usage=safe_usage)
        if not required_policies <= seen_policies:
            return self._result("unavailable", "required_policy_not_assessed", surface)
        # Never return outputs, actionReason, match text or raw assessments.
        return self._result("approved", "aws_checks_passed", surface,
                            guarded_characters=guarded, total_characters=total,
                            usage=safe_usage)


def build_live_gate(spec, *, configuration_verified=False, is_current, authorize_call):
    """Core-only opt-in after resource config/version and upload scope review."""
    if not configuration_verified:
        raise ValueError("Live guardrail configuration has not been verified")
    import boto3
    from botocore.config import Config
    session = boto3.Session(profile_name="open-oracle-event", region_name=spec.region)
    client = session.client("bedrock-runtime", config=Config(
        retries={"total_max_attempts": 1}, connect_timeout=5, read_timeout=8))
    return BedrockGuardrailGate(spec, client, execution="real_api",
                               is_current=is_current, authorize_call=authorize_call)
