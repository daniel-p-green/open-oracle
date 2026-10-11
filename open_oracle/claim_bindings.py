"""Finite factual contracts, bound to retained source spans; not a prose entailment model."""
from __future__ import annotations
import hashlib
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from fractions import Fraction


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def normalized(value):
    return ' '.join(str(value).casefold().split())


def canonical_value(kind, value):
    if kind == 'number':
        try:
            if type(value) not in (str, int, float) or len(str(value)) > 80 or not re.fullmatch(r'[-+]?\d+(?:\.\d+|/\d+)?', str(value)):
                raise ValueError('Invalid numeric value')
            fraction = Fraction(str(value))
            return format((Decimal(fraction.numerator) / Decimal(fraction.denominator)).normalize(), 'f')
        except (ValueError, ZeroDivisionError, InvalidOperation):
            raise ValueError('Invalid numeric value') from None
    if kind == 'date':
        return date.fromisoformat(value).isoformat()
    if kind == 'entity':
        return normalized(value)
    raise ValueError('Unsupported fact kind')


def span_fact(source, key, kind, value, unit, phrase):
    pattern = r'\s+'.join(re.escape(w) for w in phrase.split())
    match = re.search(pattern, source['text'], re.I)
    if not match:
        return None
    return {'key': key, 'kind': kind, 'value': canonical_value(kind, value), 'unit': unit,
            'evidence_id': source['id'], 'source_sha256': source['sha256'],
            'text_sha256': hashlib.sha256(source['text'].encode()).hexdigest(),
            'start': match.start(), 'end': match.end(), 'quote': match.group(), 'binding': 'retrieved_passage'}


def fact_catalog(corpus, evidence, contest_id):
    """Known contracts only. A keyword or matching number never proves an arbitrary sentence."""
    facts = {}
    for source in evidence:
        if source['contest_id'] != contest_id or corpus.evidence_fingerprints.get(source['id']) != fingerprint(source):
            continue
        if contest_id == 'combat' and source['id'] == 'combat:jceb-sample':
            from .cards import EXPECTED
            if ' '.join(source['text'].split()) != EXPECTED:
                continue
            specs = [('measure.rate', 'number', '1/4', 'cent', 'at the rate of one-quarter of one cent'),
                     ('measure.duration', 'number', '10', 'year', 'for a period of ten years'),
                     ('measure.jurisdiction', 'entity', 'Jackson County', None, 'Jackson County'),
                     ('measure.name', 'entity', 'COMBAT', None, 'COMBAT')]
            for key, kind, value, unit, phrase in specs:
                item = span_fact(source, key, kind, value, unit, phrase)
                if item:
                    facts[key] = item
        for candidate in corpus.contests[contest_id].get('candidates', []):
            item = span_fact(source, 'candidate.' + candidate['name'], 'entity', candidate['name'], None, candidate['name'])
            if item:
                facts[item['key']] = item
    # The election date is bound to the printed document header, not invented offsets in a question.
    for source in evidence:
        if source.get('source_id') not in ('jceb-sample', 'kceb-sample'):
            continue
        text = corpus.jceb if source['source_id'] == 'jceb-sample' else corpus.kceb
        match = re.search(r'^NOVEMBER\s+3,?\s+2026', text, re.M)
        if match and corpus.integrity.get(source['source_id']):
            facts['election.date'] = {'key': 'election.date', 'kind': 'date', 'value': '2026-11-03', 'unit': None,
                'evidence_id': source['id'], 'source_sha256': source['sha256'],
                'text_sha256': hashlib.sha256(text.encode()).hexdigest(), 'start': match.start(), 'end': match.end(),
                'quote': match.group(), 'binding': 'printed_document_header', 'text_reference': source['source_id']}
            break
    return facts


def assess_claim(claim, facts):
    """Supported: equal typed fact and exact anchor. Contradictory: known slot disagrees.
    Unsupported: missing contract/anchor/invalid type. These are bounded contracts, not all truth.
    """
    expected = facts.get(claim.get('key')) if isinstance(claim, dict) else None
    if not expected:
        return {'status': 'unsupported', 'reason': 'no_retained_fact_contract'}
    try:
        value = canonical_value(claim.get('kind'), claim.get('value'))
    except (ValueError, TypeError):
        return {'status': 'unsupported', 'reason': 'invalid_typed_value'}
    if claim.get('kind') != expected['kind'] or value != expected['value'] or claim.get('unit') != expected['unit']:
        return {'status': 'contradictory', 'key': expected['key'], 'reason': 'disagrees_with_bound_source_value',
                'expected_value': expected['value'], 'expected_unit': expected['unit']}
    if type(claim.get('start')) is not int or type(claim.get('end')) is not int:
        return {'status': 'unsupported', 'reason': 'invalid_source_offsets'}
    keys = ('evidence_id', 'source_sha256', 'text_sha256', 'start', 'end', 'quote', 'binding')
    if any(claim.get(k) != expected.get(k) for k in keys):
        return {'status': 'unsupported', 'key': expected['key'], 'reason': 'source_span_binding_failed'}
    return {'status': 'supported', 'key': expected['key'], 'binding': expected}


COMBAT_ANSWERS = (
    'A NO vote rejects the proposal to continue the COMBAT sales tax. The sample does not explain what happens if the proposal fails.',
    'This question asks whether Jackson County should continue the COMBAT sales tax for ten years. You can read one part at a time below.',
)
SOURCE_ANSWER = 'The official sample asks the question below. Its wording is evidence of the printed question; it is not an endorsement or a prediction of every legal effect. Read the original document alongside it.'
CANDIDATE_ANSWER = 'The retained official sample shows the printed roster below. The names also appear in the inventory. Position comparisons need additional original, attributed sources.'
RETENTION_ANSWER = 'This is a judicial retention question: whether the named judge stays in office. The official question is below. This slice does not assess the judge or recommend a response.'
COMPARISON_ANSWER = 'Read how both candidates answered the same question. This compares their stated priorities or proposals; it does not rate the candidates or establish that their claims are true.'


def comparison_answer(parts):
    """Finite attributed-source framing; never a generated position comparison."""
    if not isinstance(parts, dict) or set(parts) != {'topics', 'gaps', 'unclassified'}:
        raise ValueError('Invalid comparison request')
    topics, gaps = parts['topics'], parts['gaps']
    known_gaps = {'climate', 'crime', 'abortion', 'immigration', 'records and experience',
                  'stadiums and sports', 'sales taxes', 'endorsements', 'other_requested_topic'}
    if topics not in (['issues'], ['property'], ['issues', 'property']) or not isinstance(gaps,list) or len(set(gaps)) != len(gaps) or set(gaps)-known_gaps or type(parts['unclassified']) is not bool:
        raise ValueError('Invalid comparison coverage')
    text = COMPARISON_ANSWER
    if len(topics) == 2:
        text += ' Both retained questionnaire topics are included in Sources: priorities and property-tax fairness.'
    if gaps:
        labels = [g.replace('other_requested_topic', 'the other requested topic') for g in gaps]
        text += ' The retained answers do not establish their positions on ' + ', '.join(labels) + '. That part remains unanswered. Missing coverage is not a candidate position.'
    return text


def combat_parts_answer(parts):
    from .cards import FACETS
    from .research_release import GAP
    if not isinstance(parts,list) or parts != sorted(set(parts)) or not parts or set(parts)-{'rate','duration','prediction'} or set(parts)=={'prediction'}:
        raise ValueError('Invalid COMBAT coverage')
    return ' '.join(([FACETS[1][1]] if 'rate' in parts else []) +
                    ([FACETS[2][1]] if 'duration' in parts else []) + ([GAP] if 'prediction' in parts else []))


def diagnose_unbound_text(text, facts):
    """Conservative diagnostics for demonstrated numeric/date failures; never acceptance by token overlap."""
    candidates = []
    rate = re.search(r'\b(?:tax(?:\s+rate)?|rate)\s*(?:is|of|at|:|equals|would\s+be|will\s+be|remains|=)\s*(\d+(?:\.\d+)?)\s*(percent\b|%)', text, re.I)
    if rate:
        candidates.append({'key': 'measure.rate', 'kind': 'number', 'value': rate[1], 'unit': 'percent'})
    duration = re.search(r'\b(?:continuation|tax|proposal|measure)\s+(?:lasts?|continues?\s+for|runs?\s+for|is\s+for|would\s+last|will\s+last)\s+(?:a\s+period\s+of\s+)?(\d+|twenty|ten)\s+years?\b', text, re.I)
    if duration:
        candidates.append({'key': 'measure.duration', 'kind': 'number', 'value': {'twenty': '20', 'ten': '10'}.get(duration[1].lower(), duration[1]), 'unit': 'year'})
    when = re.search(r'\belection(?:\s+date)?\s*(?:is|:|on|takes\s+place\s+on|scheduled\s+for)?\s*(\d{4}-\d{2}-\d{2})\b', text, re.I)
    if when:
        candidates.append({'key': 'election.date', 'kind': 'date', 'value': when[1], 'unit': None})
    for claim in candidates:
        result = assess_claim(claim, facts)
        if result['status'] == 'contradictory':
            return result
    return {'status': 'unsupported', 'reason': 'unregistered_display_text'}


def validate_factual_display(response, corpus):
    """Every explanation is a fixed contract. Unknown prose is withheld, even with matching tokens."""
    if response.get('display_contract') == 'source_bound_research_browser_v1':
        from .research_display import validate_display
        return validate_display(response, corpus)
    evidence = response.get('evidence') or []
    if not isinstance(evidence, list) or any(not isinstance(e, dict) or not {'id', 'contest_id', 'text', 'sha256'} <= e.keys() for e in evidence):
        return {'status': 'unsupported', 'reason': 'invalid_source_shape', 'claims': []}
    contest = response.get('contest') or {}
    facts = fact_catalog(corpus, evidence, contest.get('id')) if evidence else {}
    if response.get('status') != 'answered':
        return {'status': 'not_applicable', 'reason': 'no_substantive_answer', 'claims': []}
    if not isinstance(response.get('answer'), str) or not response['answer'].strip():
        return {'status': 'unsupported', 'reason': 'unregistered_display_text', 'claims': []}
    if corpus.contest_fingerprints.get(contest.get('id')) != fingerprint(contest):
        return {'status': 'unsupported', 'reason': 'contest_entity_binding_failed', 'claims': []}
    if any(corpus.evidence_fingerprints.get(s['id']) != fingerprint(s) for s in evidence):
        return {'status': 'unsupported', 'reason': 'retained_source_binding_failed', 'claims': []}
    if response.get('election_date') != '2026-11-03' or response.get('scope', {}).get('election_date', '2026-11-03') != '2026-11-03':
        return {'status': 'contradictory', 'reason': 'election_date_disagrees_with_snapshot', 'claims': []}
    if response.get('claims') != [{'quote': source['text'], 'evidence_id': source['id']} for source in evidence]:
        return {'status': 'unsupported', 'reason': 'quoted_claim_binding_failed', 'claims': []}
    from .readability import diagnostic_answer, verify_diagnostic
    data = response.get('readability') or {}
    if not isinstance(data, dict):
        return {'status': 'unsupported', 'reason': 'computed_diagnostic_unbound', 'claims': []}
    diagnostic = diagnostic_answer(data)
    if data.get('reports') and not verify_diagnostic(response, corpus):
        return {'status': 'unsupported', 'reason': 'computed_diagnostic_unbound', 'claims': []}
    card = response.get('card') or {}
    if card and card.get('type') not in ('measure_explanation', 'candidate_comparison'):
        return {'status': 'unsupported', 'reason': 'unregistered_component_data', 'claims': []}
    if card.get('type') == 'measure_explanation' and contest.get('id') == 'amendment-7':
        from .amendment7 import validate
        return validate(response, corpus)
    if card.get('type') == 'measure_explanation':
        from .cards import FACETS, measure_card
        statements = [(f.get('title'), f.get('statement')) for f in card.get('facets', [])]
        expected = [(title, statement) for title, statement, quote in FACETS]
        question = 'What does NO mean?' if card.get('presentation') == 'choice_focus' else "I still don't understand" if card.get('presentation') == 'step_by_step' else 'Explain COMBAT'
        expected_card = measure_card(question, contest, evidence)
        if card.get('election_date') != '2026-11-03':
            return {'status': 'contradictory', 'reason': 'card_election_date_disagrees_with_source', 'claims': []}
        if card.get('jurisdiction') != 'Jackson County, Missouri':
            return {'status': 'contradictory', 'reason': 'card_jurisdiction_disagrees_with_source', 'claims': []}
        try:
            parts_answer = combat_parts_answer(response['requested_parts']) if response.get('requested_parts') else None
        except (ValueError, TypeError):
            return {'status': 'unsupported', 'reason': 'measure_coverage_unbound', 'claims': []}
        if response['answer'] not in (*COMBAT_ANSWERS, *((parts_answer,) if parts_answer else ()), *(item[1] for item in FACETS), *((diagnostic,) if diagnostic else ())) or statements != expected or card != expected_card:
            text = response.get('answer', '') + ' ' + ' '.join(f.get('statement', '') for f in card.get('facets', []))
            return {**diagnose_unbound_text(text, facts), 'claims': []}
        if not {'measure.rate', 'measure.duration', 'measure.jurisdiction', 'measure.name', 'election.date'}.issubset(facts):
            return {'status': 'unsupported', 'reason': 'required_fact_binding_missing', 'claims': []}
    elif card.get('type') == 'candidate_comparison':
        from .demo_sources import CONTEST, QUESTIONS
        from .cards import candidate_card
        parts = response.get('comparison_request')
        try:
            expected_answer = comparison_answer(parts) if parts is not None else COMPARISON_ANSWER
        except (ValueError, TypeError, KeyError):
            return {'status': 'unsupported', 'reason': 'comparison_coverage_unbound', 'claims': []}
        if parts and (card.get('topic') != parts['topics'][0] or sorted({s.get('topic') for s in evidence}) != sorted(parts['topics']) or any(sum(s.get('topic') == topic for s in evidence) != 2 for topic in parts['topics'])):
            return {'status': 'unsupported', 'reason': 'comparison_coverage_unbound', 'claims': []}
        if contest.get('id') != CONTEST or card.get('title') != QUESTIONS.get(card.get('topic')) or response['answer'] != expected_answer or card != candidate_card(contest, evidence, card.get('topic')):
            return {'status': 'unsupported', 'reason': 'unregistered_attributed_display', 'claims': []}
    else:
        expected = CANDIDATE_ANSWER if contest.get('kind') == 'candidate' else RETENTION_ANSWER if contest.get('kind') == 'retention' else SOURCE_ANSWER
        if response['answer'] != (diagnostic or expected):
            return {**diagnose_unbound_text(response.get('answer', ''), facts), 'claims': []}
    checks = [assess_claim(item, facts) for item in facts.values()]
    return {'status': 'supported', 'method': 'finite_source_span_contracts', 'claims': checks,
            'prose_entailment_claimed': False, 'calibrated_probability_used': False,
            'computed_diagnostic': 'recomputed_exact_match' if diagnostic else 'not_requested'}
