"""Same-origin finite rendering definitions; never an answer/review authority."""
from copy import deepcopy
import hashlib
from .claim_bindings import fingerprint
from .corpus import ELECTION

class CatalogUnavailable(ValueError):
    pass

def rendering_catalog(corpus, scope=None):
    scope = dict(scope or {})
    if (set(scope) - {'election_date', 'authority', 'municipality', 'district'}
            or any(not isinstance(v, str) or not 0 < len(v) <= 100 for v in scope.values())
            or scope.get('election_date', ELECTION) != ELECTION
            or scope.get('authority', 'KCEB') not in ('KCEB', 'JCEB', 'unknown')):
        raise ValueError('Invalid catalog scope')
    scope.setdefault('election_date', ELECTION)
    for ident, original in corpus.originals.items():
        try:
            expected = next(e['sha256'] for e in corpus.evidence.values() if e['source_id'] == ident)
            if not corpus.integrity.get(ident) or hashlib.sha256(original.read_bytes()).hexdigest() != expected:
                raise CatalogUnavailable('Original changed')
        except (OSError, StopIteration):
            raise CatalogUnavailable('Original unavailable') from None
    if corpus.amendment7_ready:
        from .amendment7 import original_pdf, fair_original
        if not original_pdf(corpus) or not fair_original(corpus):
            raise CatalogUnavailable('Proposal changed')
    if corpus.prepared_sources_ready:
        from .demo_sources import original_text
        if not original_text():
            raise CatalogUnavailable('Attributed original changed')
    sources = {}
    for ident, source in corpus.evidence.items():
        if corpus.evidence_fingerprints.get(ident) != fingerprint(source):
            raise CatalogUnavailable('Source record changed')
        read_scope = {**scope, **({'_comparison_topic':source['topic']} if 'topic' in source else {})}
        if corpus.read(ident, read_scope) is not None:
            sources[ident] = deepcopy(source)
    contests = {ident:{k:deepcopy(v) for k,v in contest.items() if k != 'aliases'}
                for ident,contest in corpus.contests.items()}
    if any(corpus.contest_fingerprints.get(ident) != fingerprint(contest) for ident,contest in contests.items()):
        raise CatalogUnavailable('Contest record changed')
    from .cards import measure_card, candidate_card
    from .demo_sources import CONTEST, QUESTIONS
    cards = {}
    for ident in ('combat', 'amendment-7'):
        evidence = [e for e in sources.values() if e['contest_id'] == ident and 'topic' not in e]
        card = measure_card('Explain the proposal', contests[ident], evidence)
        if card:
            cards[card['id']] = card
    for topic in QUESTIONS:
        evidence = [e for e in sources.values() if e['contest_id'] == CONTEST and e.get('topic') == topic]
        card = candidate_card(contests[CONTEST], evidence, topic)
        if card:
            cards[card['id']] = card
    people = {}
    for contest in corpus.contests.values():
        if contest['kind'] in ('candidate','retention'):
            for person in corpus.candidate_sources.lookup(contest, '', scope)['people']:
                people[person['candidate_id']] = person
    from .engine import OFFICIAL_LINKS
    links = deepcopy(OFFICIAL_LINKS) + [
        {'title':'Official KCEB sample','url':'https://kceb.org/elections/ballot/'},
        {'title':'Official JCEB sample','url':'https://jcebmo.org/election-information/on-the-ballot/'}]
    for source in sources.values():
        link = {'title':'Retained official wording','url':source['original_route']}
        if link not in links:
            links.append(link)
    return deepcopy({'sources':sources,'contests':contests,'cards':cards,
        'source_bindings':{ident:corpus.evidence_fingerprints[ident] for ident in sources},
        'official_links':links,'candidate_sources':people})
