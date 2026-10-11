"""Privacy-safe report contract. Evidence tiers are independent, never promoted."""
import math

LANGUAGES = ('en', 'es', 'vi', 'ar', 'zh-Hans', 'fil')
TIERS = ('synthetic', 'live_provider', 'browser', 'physical_device')
STAGES = ('delegation', 'evidence', 'deterministic_guards', 'decisions',
          'language_identification', 'translation', 'speech_fidelity', 'playback',
          'lifecycle', 'privacy', 'accessibility')
COMPONENTS = ('gpt_live', 'strands', 'embedding', 'decisions_output',
              'decisions_classifier', 'decisions_language', 'decisions_translation')
STATUSES = ('pass', 'fail', 'unrun', 'blocked')
OUTCOMES = frozenset({'answered', 'insufficient_evidence', 'neutrality_boundary', 'clarification',
    'contradictory', 'held', 'released', 'accepted', 'rejected', 'unavailable', 'guarded_without_dispatch',
    'unsafe_dispatch', 'unexpected_dispatch_count', 'cleared', 'retained', 'stale_session_accepted',
    'owner_adapter_unavailable', 'owner_fixture_unavailable', 'suggested', 'mixed_input', 'uncertain',
    'short_input', 'unsafe_identification', 'inactive_or_stale', 'refused', 'stale_rejected', 'stale_accepted',
    'retained_visitor_text', 'rtl', 'ltr', 'fixture_validated', 'translation_not_verified',
    'translation_contract_mismatch', 'source_binding_mismatch', 'invalid_translation_claim',
    'accepted_contract', 'held_contract', 'comparator_parity_failed', 'single_frozen_review',
    'unsafe_delegation', 'allowlisted', 'leaked', 'bound_fixture', 'finite_simplest_no_fact_loss', 'retained_original',
    'sdk_contract_pass', 'sdk_contract_fail', 'owner_sdk_tests_unavailable'})


def finite(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def measurement(calls=None, input_tokens=None, output_tokens=None, cost_usd=None):
    """Unknown stays null; estimates are explicitly distinct from invoice data."""
    for value in (calls, input_tokens, output_tokens):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError('invalid_counter')
    if cost_usd is not None and not finite(cost_usd):
        raise ValueError('invalid_cost')
    return dict(calls=calls, input_tokens=input_tokens, output_tokens=output_tokens,
                cost_usd=cost_usd, cost_basis='unknown' if cost_usd is None else 'caller_estimate')


def project_result(result, case):
    """Case ID/stage/language belong to the fixed authored catalog, not visitors."""
    if (result.get('status') not in STATUSES or not finite(result.get('elapsed_ms'))
            or result.get('actual') not in OUTCOMES or case.get('expected') not in OUTCOMES
            or case.get('language') not in LANGUAGES or case.get('stage') not in STAGES):
        raise ValueError('invalid_result')
    row = {'case_id': case['id'], 'language': case['language'], 'stage': case['stage'],
            'evidence_tier': 'synthetic', 'status': result['status'],
            'elapsed_ms': result['elapsed_ms'], 'expected': case['expected'],
            'actual': result['actual'], 'human_adjudicated': False,
            'measurement_scope': 'offline_contract_execution',
            'external_components': {name: measurement(0, 0, 0, 0) for name in COMPONENTS}}
    if case['adapter'] == 'sdk' and isinstance(result.get('synthetic_sdk'), dict):
        values = result['synthetic_sdk']
        row['synthetic_sdk'] = {key: values.get(key) if type(values.get(key)) is int and 0 <= values[key] <= 1000 else None
                                for key in ('model_dispatches', 'tool_events', 'requests')}
    return row


def release_matrix(results):
    """Fresh report only: no inferred cross-tier/language/provider acceptance."""
    rows = []
    for language in LANGUAGES:
        cells = {}
        for stage in STAGES:
            selected = [r for r in results if r['language'] == language and r['stage'] == stage]
            executed = [r for r in selected if r['status'] in ('pass', 'fail')]
            status = ('fail' if any(r['status'] == 'fail' for r in selected)
                      else 'pass' if executed and len(executed) == len(selected)
                      else 'blocked' if any(r['status'] == 'blocked' for r in selected) else 'unrun')
            cells[stage] = {'synthetic': {'status': status, 'cases': len(selected)},
                            **{tier: {'status': 'unrun', 'cases': 0} for tier in TIERS[1:]}}
        rows.append({'language': language, 'stages': cells, 'production_readiness': 'not_established',
                     'spoken_ready': False})
    return rows
