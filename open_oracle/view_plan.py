"""Constrained adaptive component catalog: references only, no generated display prose or code."""
import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

FACET_KEYS = ('decision', 'rate', 'time', 'purpose', 'fund')

class EvidenceViewPlan(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    version: Literal[1] = 1
    request_id: str = Field(min_length=1, max_length=120)
    component: Literal['measure_parts', 'measure_focus', 'candidate_quotes', 'source_quotes']
    evidence_ids: list[str] = Field(min_length=1, max_length=4)
    facet_keys: list[Literal['decision', 'rate', 'time', 'purpose', 'fund']] = Field(max_length=5)
    initial_part: int = Field(ge=0, le=4)
    language: Literal['en'] = 'en'


def make_view_plan(response, question):
    card = response.get('card') or {}
    sources = response.get('evidence') or []
    if response.get('source_fallback'):
        sources = response['source_fallback']['sources']
        component, keys, initial = 'source_quotes', [], 0
    elif response.get('status') != 'answered' or not sources:
        return None
    elif card.get('type') == 'candidate_comparison':
        component, keys, initial = 'candidate_quotes', [], 0
    elif card.get('type') == 'measure_explanation':
        focus = ('rate' if re.search(r'\brate\b|how much.*tax', question, re.I) else
                 'time' if re.search(r'how long|duration|years|length', question, re.I) else
                 'fund' if re.search(r'money go|trust fund|general fund', question, re.I) else
                 'purpose' if re.search(r'purpose|what.*fund|what.*pay for', question, re.I) else
                 'decision' if card.get('presentation') == 'choice_focus' else None)
        if re.search(r"still.*(?:understand|confused)|one (?:thing|step).*time|break.*down", question, re.I):
            focus = None
        component = 'measure_focus' if focus else 'measure_parts'
        keys = [focus] if focus else list(FACET_KEYS)
        initial = FACET_KEYS.index(focus) if focus else 0
    else:
        component, keys, initial = 'source_quotes', [], 0
    return EvidenceViewPlan(request_id=response['request_id'], component=component,
                            evidence_ids=[s['id'] for s in sources], facet_keys=keys, initial_part=initial).model_dump()


def validate_view_plan(plan, response):
    try:
        parsed = EvidenceViewPlan.model_validate(plan)
        if parsed.request_id != response.get('request_id'):
            return False
        sources = response.get('evidence') or (response.get('source_fallback') or {}).get('sources') or []
        if parsed.evidence_ids != [s['id'] for s in sources] or len(set(parsed.evidence_ids)) != len(parsed.evidence_ids):
            return False
        card = response.get('card') or {}
        if parsed.component == 'source_quotes':
            return not parsed.facet_keys and parsed.initial_part == 0
        if response.get('status') != 'answered' or response.get('fact_validation', {}).get('status') != 'supported':
            return False
        if parsed.component == 'candidate_quotes':
            return card.get('type') == 'candidate_comparison' and not parsed.facet_keys and parsed.initial_part == 0
        if card.get('type') != 'measure_explanation':
            return False
        if parsed.component == 'measure_parts':
            return parsed.facet_keys == list(FACET_KEYS) and parsed.initial_part == 0
        return len(parsed.facet_keys) == 1 and parsed.initial_part == FACET_KEYS.index(parsed.facet_keys[0])
    except (ValueError, TypeError, KeyError):
        return False
