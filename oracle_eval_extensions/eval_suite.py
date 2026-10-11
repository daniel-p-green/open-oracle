"""Authored contract cases; no live inference, calibration or runtime promotion."""
from copy import deepcopy
from .claim_packs import build_pack, deterministic_check
from .review_contract import CLAIM_CHECKS, request, parse_review

TEXTS = {
    'measure.rate': 'The printed COMBAT rate is one-quarter of one cent.',
    'measure.duration': 'The printed COMBAT continuation period is ten years.',
    'measure.jurisdiction': 'The printed COMBAT question names Jackson County.',
    'measure.name': 'The printed tax is commonly known as COMBAT.',
    'election.date': 'The retained notice header gives the election date as November 3, 2026.'
}


def synthetic_answers(payload, probability=0.99):
    return {'model': payload['model'], 'answers': [
        {'name': q['name'], 'type': 'predicate', 'probability': probability} for q in payload['questions']]}


def run_case(corpus, case):
    from open_oracle.engine import EvidenceLoop
    from open_oracle.claim_bindings import validate_factual_display
    from open_oracle.quality_policy import recommendation_block
    op = case['operation']
    if op in ('typed', 'pack_binding'):
        key = case.get('key', 'measure.rate')
        pack = build_pack(corpus, 'combat:jceb-sample', key, TEXTS[key])
        if op == 'typed':
            pack['typed_claim'].update(case.get('changes', {}))
        else:
            for field, value in case['changes'].items():
                if field.startswith('context.'):
                    pack['source_context'][field.removeprefix('context.')] = value
                else:
                    pack[field] = value
        observed = deterministic_check(corpus, pack)['status']
    elif op == 'display':
        response = EvidenceLoop(corpus).answer('Explain COMBAT')
        if 'answer' in case: response['answer'] = case['answer']
        if case.get('remove_fund'):
            response['card']['facets'] = response['card']['facets'][:-1]
        if 'election_date' in case: response['election_date'] = case['election_date']
        observed = validate_factual_display(response, corpus)['status']
    elif op == 'neutrality':
        response = EvidenceLoop(corpus).answer('Explain COMBAT')
        response['answer'] = case['answer']
        observed = 'blocked' if recommendation_block(response) else 'permitted_by_bounded_guard'
    else:
        raise ValueError('Unknown authored operation')
    # The model reports .99 for every case: a deliberately false-accept stub.
    payload = request({'scripted_case_id': case['id']}, CLAIM_CHECKS)
    stub = parse_review(payload, synthetic_answers(payload))
    return {'id': case['id'], 'operation': op, 'expected': case['expected'], 'observed': observed,
            'pass': observed == case['expected'], 'simulated_decisions': stub['status'],
            'execution': 'offline_authored_model_response', 'external_calls': 0,
            'human_adjudicated': False, 'production_release_authorized': False}


def confusion(labels, predictions):
    """Bookkeeping only; not calibration. Missing/refused review is kept separate."""
    if set(labels) != set(predictions): raise ValueError('Incomplete labeled predictions')
    counts = dict(true_accept=0, false_accept=0, true_hold=0, false_refusal=0, unavailable=0)
    for ident, supported in labels.items():
        if type(supported) is not bool: raise ValueError('Labels must be adjudicated booleans')
        outcome = predictions[ident]
        if outcome in ('unavailable', 'refused'): counts['unavailable'] += 1
        elif outcome not in ('criteria_met', 'criteria_not_met'): raise ValueError('Unknown prediction')
        elif supported and outcome == 'criteria_met': counts['true_accept'] += 1
        elif supported: counts['false_refusal'] += 1
        elif outcome == 'criteria_met': counts['false_accept'] += 1
        else: counts['true_hold'] += 1
    return {'counts': counts, 'threshold': 0.95, 'calibration': 'not_validated',
            'meaning': 'Counts alone do not establish probability calibration or human comprehension.'}
