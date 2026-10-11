"""Independent strict validation of core's already-sanitized schema event.

Does not accept Pydantic exceptions, arbitrary locations or extra keys. Core's
normalizer maps numeric indices to '*' and unknown paths to unrecognized_field.
"""
import re

CATEGORIES = {"missing", "list_type", "model_type", "string_type", "string_too_short", "string_too_long",
              "string_pattern_mismatch", "literal_error", "extra_forbidden", "too_short", "too_long",
              "value_error", "dict_type", "validation_other"}
PATHS = {"root", "unrecognized_field", "claims", "gaps", "clarification", "claims.*", "claims.*.part_id",
         "claims.*.text", "claims.*.citations", "claims.*.citations.*", "claims.*.citations.*.chunk_id",
         "claims.*.citations.*.exact_quote", "claims.*.citations.*.citation_span_id", "gaps.*",
         "gaps.*.part_id", "gaps.*.reason"}


def validate_schema_event(event):
    if not isinstance(event, dict) or set(event) != {"schema", "schema_sha256", "category", "field_path"}:
        raise ValueError("Invalid schema metadata shape")
    if event["schema"] != "cited_answer_v1" or not isinstance(event["schema_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", event["schema_sha256"]):
        raise ValueError("Invalid schema metadata identity")
    if not isinstance(event["category"], str) or event["category"] not in CATEGORIES:
        raise ValueError("Invalid schema category")
    if not isinstance(event["field_path"], str) or event["field_path"] not in PATHS:
        raise ValueError("Invalid normalized schema path")
    return {k: event[k] for k in ("schema", "schema_sha256", "category", "field_path")}
