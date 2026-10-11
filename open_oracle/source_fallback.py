"""Independently bound original wording; no generated explanation inherits a source fallback."""
from copy import deepcopy
from .claim_bindings import fingerprint


def make_fallback(response, corpus):
    sources = response.get('evidence') or []
    if not sources:
        return None
    contest_id = (response.get('contest') or {}).get('id')
    scope = response.get('scope') or {}
    if corpus.contest_fingerprints.get(contest_id) != fingerprint(response.get('contest')):
        return None
    if scope.get('election_date', '2026-11-03') != '2026-11-03':
        return None
    for source in sources:
        if (corpus.evidence_fingerprints.get(source.get('id')) != fingerprint(source)
                or source.get('contest_id') != contest_id or source.get('status') != 'current_snapshot'
                or not corpus.allowed(corpus.contests[contest_id], scope)):
            return None
    # Includes source attribution and exact original wording, never answer/card/claims/provider text.
    return {'type': 'verified_originals', 'request_id': response['request_id'], 'contest_id': contest_id,
            'election_date': '2026-11-03', 'scope': deepcopy(scope), 'sources': deepcopy(sources),
            'source_bindings': {s['id']: fingerprint(s) for s in sources},
            'label': 'Retained original wording. The explanation was withheld; independent AI review is not claimed for these quotations.',
            'candidate_statement_limit': 'Candidate statements remain attributed and are not independently verified outcomes.'}


def validate_fallback(fallback, response, corpus):
    if corpus is None or not isinstance(fallback, dict):
        return False
    allowed = {'type', 'request_id', 'contest_id', 'election_date', 'scope', 'sources', 'source_bindings', 'label', 'candidate_statement_limit'}
    if set(fallback) != allowed or fallback.get('type') != 'verified_originals':
        return False
    if fallback.get('request_id') != response.get('request_id') or fallback.get('contest_id') != (response.get('contest') or {}).get('id'):
        return False
    shell = {'request_id': response['request_id'], 'contest': response['contest'], 'scope': response.get('scope', {}), 'evidence': fallback.get('sources')}
    expected = make_fallback(shell, corpus)
    return expected is not None and fallback == expected
