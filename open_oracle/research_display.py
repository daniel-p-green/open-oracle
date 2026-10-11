"""Explicit browser projection of reviewed finite research; no arbitrary prose release.

The registry remains distinct from the legacy contest inventory. Every visible
source is rebuilt from its own authority's retained original, including context
beyond a cited sentence. Revalidation does not trust model/reviewer metadata.
"""
from copy import deepcopy
from dataclasses import asdict
from .research_release import FORMS, GAP, source_limit
from strands_quality.research_corpus import Scope, load_verified_corpus

CONTRACT = 'source_bound_research_browser_v1'


def evidence_for(registry, source_id, scope):
    source = registry.sources[source_id]
    registry.acquire(source_id)  # Fresh original and extraction hashes.
    chunks = [c for c in registry.chunks.values() if c.source_id == source_id
              and registry.eligible(c, scope, 'combat', 'ballot_fact')]
    if not chunks or source.role != 'ballot_proposal' or source.authority != scope.authority:
        raise ValueError('Unbound research source authority')
    start, end = min(c.start for c in chunks), max(c.end for c in chunks)
    return {'id': 'combat:' + source.id + ':research', 'source_id': source.id,
            'contest_id': 'combat', 'title': source.title, 'url': source.url,
            'issuer': source.issuer, 'source_category': 'official sample ballot',
            'authority': source.authority, 'role': source.role,
            'election_date': source.election_date, 'retrieved_date': source.retrieved_date,
            'snapshot_date': scope.as_of, 'version': 'Retained sample; subject to change',
            'sha256': source.original_sha256, 'extraction_sha256': source.extraction_sha256,
            'quality': source.quality, 'status': 'current_snapshot',
            'extraction': source.extraction, 'text': source.text[start:end],
            'start_offset': start, 'end_offset': end,
            'page': chunks[0].page, 'column': chunks[0].column,
            'original_route': '/api/original/' + source.id}


def project_display(request, response):
    """Called before Decisions and again after it; not a post-review decoration."""
    value = deepcopy(response)
    ids = sorted({c['source_id'] for claim in value['claims'] for c in claim['citations']})
    value['evidence'] = [evidence_for(request.registry, sid, request.scope) for sid in ids]
    value['display_contract'] = CONTRACT
    # No unreviewed legacy inventory title/roster or inferred personal eligibility.
    value['choices'] = []; value['links'] = []; value['candidate_sources'] = []
    return value


def validate_display(response, corpus):
    """Independent second release boundary, including every public prose field."""
    try:
        if response.get('display_contract') != CONTRACT:
            raise ValueError('No research display contract')
        raw_scope = response['scope']
        scope = Scope(authority=raw_scope['authority'])
        import json
        if json.dumps(raw_scope, sort_keys=True) != json.dumps(asdict(scope), sort_keys=True):
            raise ValueError('Changed research scope')
        if response.get('mode') != 'reviewed_strands_research' or response.get('language') != 'en' or response.get('translation_status') != 'not_requested':
            raise ValueError('Changed research mode/language')
        if response.get('election_date') != scope.election_date or response.get('snapshot_date') != scope.as_of:
            raise ValueError('Changed election/version')
        if response.get('card') is not None or response.get('view_plan') or response.get('contest') or response.get('readability') or response.get('source_fallback') or response.get('translation_review') or response.get('speech'):
            raise ValueError('Unregistered research display surface')
        if response.get('limitations') != [source_limit(scope.authority)] or any(response.get(k) for k in ('choices', 'links', 'candidate_sources')):
            raise ValueError('Unregistered research prose')
        covered = response['fact_validation']['covered_parts']
        if not isinstance(covered, list) or sorted(set(covered)) != covered or not covered or set(covered) - {'rate', 'duration', 'prediction'}:
            raise ValueError('Invalid coverage')
        registry = load_verified_corpus(corpus)
        seen, ids, texts = set(), set(), []
        part_ids = set()
        for claim in response['claims']:
            if set(claim) != {'part_id', 'text', 'citations'} or claim['part_id'] in part_ids:
                raise ValueError('Changed claim schema')
            part_ids.add(claim['part_id'])
            kind = next((k for k, text in FORMS.items() if text == claim['text']), None)
            if kind is None or kind in seen or not 1 <= len(claim['citations']) <= 3:
                raise ValueError('Unregistered research explanation')
            for citation in claim['citations']:
                chunk = registry.chunks[citation['chunk_id']]
                if registry.citation(chunk.id, citation['quote']) != citation or not registry.eligible(chunk, scope, 'combat', 'ballot_fact'):
                    raise ValueError('Changed citation')
                import re
                text = ' '.join(citation['quote'].split())
                if not re.search(r'Shall Jackson County continue its anti-crime sales tax,\s+commonly known as COMBAT,', text) or 'at the rate of one-quarter of one cent for a period of ten years' not in text:
                    raise ValueError('Unbound proposal/rate/duration')
                ids.add(chunk.source_id)
            texts.append(claim['text']); seen.add(kind)
        if 'prediction' in covered:
            texts.append(GAP); seen.add('prediction')
        if seen != set(covered) or response['answer'] != ' '.join(texts):
            raise ValueError('Changed explanation/coverage')
        if response['status'] != ('answered' if response['claims'] else 'insufficient_evidence'):
            raise ValueError('Changed result status')
        expected = [evidence_for(registry, sid, scope) for sid in sorted(ids)]
        if response['evidence'] != expected:
            raise ValueError('Changed retained original context')
        return {'status': 'supported', 'method': CONTRACT}
    except (KeyError, ValueError, TypeError, AttributeError, OSError):
        return {'status': 'unsupported', 'reason': 'research_display_unbound'}
