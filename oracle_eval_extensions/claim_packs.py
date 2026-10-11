"""Exact per-claim evidence packs for offline tests, never an arbitrary-prose gate."""
from copy import deepcopy
import hashlib
from open_oracle.claim_bindings import fact_catalog, assess_claim, fingerprint
from .review_contract import CLAIM_CHECKS, request


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def build_pack(corpus, evidence_id, fact_key, claim_text=''):
    """Trusted corpus owns metadata. Keep both short anchor and full passage context."""
    if not isinstance(claim_text, str) or len(claim_text) > 20000:
        raise ValueError('Invalid claim text')
    source = corpus.read(evidence_id, {'election_date': '2026-11-03'})
    if not source or corpus.evidence_fingerprints.get(evidence_id) != fingerprint(source):
        raise ValueError('Unbound source')
    if not corpus.integrity.get(source['source_id']):
        raise ValueError('Original integrity unavailable')
    original = corpus.originals.get(source['source_id'])
    if original is None or hashlib.sha256(original.read_bytes()).hexdigest() != source['sha256']:
        raise ValueError('Original bytes changed')
    facts = fact_catalog(corpus, [source], source['contest_id'])
    if fact_key not in facts:
        raise ValueError('No retained fact contract')
    fact = deepcopy(facts[fact_key])
    anchor_text = ({'jceb-sample': corpus.jceb, 'kceb-sample': corpus.kceb}.get(fact.get('text_reference'))
                   if fact['binding'] == 'printed_document_header' else source['text'])
    if (not isinstance(anchor_text, str) or digest(anchor_text) != fact['text_sha256'] or
            anchor_text[fact['start']:fact['end']] != fact['quote']):
        raise ValueError('Invalid exact anchor')
    contest = corpus.contests[source['contest_id']]
    context = {k: source.get(k) for k in ('source_id', 'url', 'title', 'issuer', 'source_category',
        'election_date', 'retrieved_date', 'snapshot_date', 'version', 'page', 'status', 'extraction')}
    context.update(contest_id=source['contest_id'],
                   jurisdiction=facts.get('measure.jurisdiction', {}).get('value', contest.get('jurisdiction')),
                   source_role='official_sample_ballot', personal_applicability='not_established',
                   current_law='not_established_by_sample', legal_failure_consequences='not_established_by_sample')
    return {'contract': 'claim_evidence_eval_v1', 'claim_id': fact_key, 'claim_text': claim_text,
            'typed_claim': fact, 'source_context': context,
            'original_sha256': source['sha256'], 'passage_text_sha256': digest(source['text']),
            'source_fingerprint': fingerprint(source), 'exact_anchor': deepcopy(fact),
            'complete_passage': source['text'], 'production_release_authorized': False}


def deterministic_check(corpus, pack):
    """Rebuild trusted context; assess typed facts only, not arbitrary claim_text."""
    try:
        claim = pack['typed_claim']
        expected = build_pack(corpus, claim['evidence_id'], pack['claim_id'], pack['claim_text'])
        if set(pack) != set(expected) or set(claim) != set(expected['typed_claim']):
            return {'status': 'unsupported', 'reason': 'invalid_evidence_pack'}
        binding_fields = ('contract', 'claim_id', 'source_context', 'original_sha256',
                          'passage_text_sha256', 'source_fingerprint', 'exact_anchor', 'complete_passage')
        if any(pack.get(k) != expected[k] for k in binding_fields):
            return {'status': 'unsupported', 'reason': 'evidence_pack_binding_failed'}
        return assess_claim(claim, {expected['claim_id']: expected['typed_claim']})
    except (ValueError, TypeError, KeyError, AttributeError):
        return {'status': 'unsupported', 'reason': 'invalid_evidence_pack'}


def decisions_draft(corpus, pack):
    if deterministic_check(corpus, pack)['status'] != 'supported':
        raise ValueError('Deterministic check holds pack before optional model review')
    # Expected labels/splits are deliberately absent. No provider ID or visitor content.
    return request({'claim_id': pack['claim_id'], 'claim_text': pack['claim_text'],
                    'exact_evidence_pack': {k: v for k, v in pack.items()
                                            if k not in ('production_release_authorized',)}}, CLAIM_CHECKS)
