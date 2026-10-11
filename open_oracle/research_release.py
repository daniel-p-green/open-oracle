"""Small reviewed research release contract; arbitrary/legal prose remains private.

The actual Strands agent plans, searches, acquires and reads evidence per part.
This adapter accepts only source-bound COMBAT rate/duration forms and an explicit
prediction gap. It never turns citation presence or a Decisions score into proof
of arbitrary prose entailment. The opt-in browser engine uses a separate validated display projection; speech remains off.
"""
from __future__ import annotations
from dataclasses import asdict
from copy import deepcopy
import re
from hashlib import sha256
from pathlib import Path
from .quality_policy import REVISED_CHECKS
from time import monotonic

from .quality_policy import release_block
from .session_control import check_cancel, current_cancel
from .corpus import Corpus
from strands_quality.research_corpus import Scope, load_verified_corpus
from strands_quality.research_agent import ResearchRequest

FORMS = {
    'rate': 'If approved, the COMBAT sales tax would continue at one-quarter of one cent.',
    'duration': 'If approved, the COMBAT sales tax would continue for ten years.',
}
GAP = 'The retained ballot wording does not establish whether COMBAT would reduce crime or by how much. I cannot support that prediction from this evidence.'
LIMIT = 'Saved November 3, 2026 sample ballot. Samples can change. This is not your personal ballot.'

def source_limit(authority):
    issuer = {'JCEB': 'Jackson County Election Board', 'KCEB': 'Kansas City Election Board'}[authority]
    return issuer + ': ' + LIMIT


def requested_parts(question):
    """Intentionally narrow intake, independent of an agent dropping a requested part."""
    q = question.casefold()
    if 'combat' not in q or len(q) > 2000:
        raise ValueError('Outside reviewed COMBAT research release contract')
    if re.search(r'\bquestion\s*(?:#\s*)?\d+', q):
        raise ValueError('Numbered subquestion requires separate scoped retrieval')
    words=set(re.findall(r'\w+',q))
    allowed=set('what is the combat tax rate and how long would it continue for does last duration will reduce reduction crime by percent percentage fall drop prevent a of its this question printed proposed could much whether give me at as says say wording'.split())
    if any(w not in allowed and not w.isdecimal() for w in words):
        raise ValueError('Outside reviewed COMBAT research release contract')
    out = set()
    if re.search(r'\brate\b', q): out.add('rate')
    if re.search(r'how long|\bduration\b', q): out.add('duration')
    if re.search(r'(?:reduce|reduction|fall|drop|prevent).*\bcrime\b|\bcrime\b.*(?:reduce|reduction|fall|drop|prevent)', q): out.add('prediction')
    # Percent attached to a prediction is an explicit gap, not a tax conversion.
    tax_text = re.split(r'\b(?:will|would|could|whether)\b[^?]*\b(?:reduce|reduction|fall|drop|prevent)\b[^?]*\bcrime\b', q, maxsplit=1)[0] if 'prediction' in out else q
    if re.search(r'\bpercent(?:age)?\b|%', tax_text):
        raise ValueError('Outside reviewed COMBAT tax unit contract')
    # No unrelated request may ride along with a reviewed rate/duration answer.
    if not out or re.search(r'\b(?:candidate|vote|law|ordinance|legal|dollars?|effect|effective|budget|cost|amendment|proposition)\b', q):
        # A numeric crime prediction is allowed only as an explicit refusal.
        if out != {'prediction'}: raise ValueError('Outside reviewed COMBAT research release contract')
    return out


def validate_draft(request, draft, question):
    """Rebind every planned part/citation; keep exact units and proposal qualifiers."""
    request.check()
    wanted = requested_parts(question)
    if request.plan is None or draft.get('plan') != request.plan.model_dump() or request.plan.contest_id != 'combat':
        raise ValueError('Research plan binding failed')
    expected = request.finalize(request.result)
    if draft != expected: raise ValueError('Research draft changed after source finalization')
    covered = set()
    sources = {}
    for claim in draft['claims']:
        kind = next((k for k,v in FORMS.items() if claim['text'] == v), None)
        if kind is None or kind not in wanted or kind in covered:
            raise ValueError('Unregistered or duplicate research explanation')
        part = request.part(claim['part_id'])
        if part.purpose != 'ballot_fact': raise ValueError('Research claim purpose binding failed')
        # Bind the model's planned question to the requested semantic role as well.
        if not re.search(r'\brate\b' if kind == 'rate' else r'how long|\bduration\b|\byears\b|\bcontinue\b', part.question, re.I):
            raise ValueError('Research claim part binding failed')
        for citation in claim['citations']:
            chunk = request.registry.chunks[citation['chunk_id']]
            actual = request.registry.citation(chunk.id, citation['quote'])
            if actual != citation or chunk.id not in request.read_by_part[part.id] or not request.registry.eligible(chunk,request.scope,'combat',part.purpose):
                raise ValueError('Research original/part citation binding failed')
            text = ' '.join(citation['quote'].split())
            # Preserve conditional continuation and printed units. This is a finite
            # source grammar, not a token-overlap or numerical-entailment proxy.
            if not re.search(r'Shall Jackson County continue its anti-crime sales tax,\s+commonly known as COMBAT,', text):
                raise ValueError('Research proposal qualification missing')
            if not re.search(r'at the rate of one-quarter of one cent for a period of ten years', text):
                raise ValueError('Research rate/duration source grammar failed')
            source = request.registry.sources[chunk.source_id]
            if source.role != 'ballot_proposal' or source.authority != request.scope.authority:
                raise ValueError('Research authority/role binding failed')
            sources[source.id] = {'id':source.id, 'title':source.title,'url':source.url,'issuer':source.issuer,
                'authority':source.authority,'role':source.role,'election_date':source.election_date,
                'retrieved_date':source.retrieved_date,'original_sha256':source.original_sha256,
                'extraction_sha256':source.extraction_sha256,'quality':source.quality,'text':source.text[chunk.start:chunk.end]}
        covered.add(kind)
    for gap in draft['gaps']:
        part = request.part(gap['part_id'])
        if part.purpose != 'prediction' or gap['reason'] != 'unsupported_prediction' or 'prediction' not in wanted or 'prediction' in covered:
            raise ValueError('Outside reviewed research refusal contract')
        covered.add('prediction')
    if covered != wanted: raise ValueError('Research answer dropped a requested part')
    response = {'status':'answered' if draft['claims'] else 'insufficient_evidence',
        'answer':' '.join([c['text'] for c in draft['claims']] + ([GAP] if draft['gaps'] else [])),
        'card':None,'evidence':list(sources.values()),'claims':deepcopy(draft['claims']),
        'scope':asdict(request.scope),'election_date':request.scope.election_date,
        'snapshot_date':request.scope.as_of,'language':'en','translation_status':'not_requested',
        'mode':'reviewed_strands_research','limitations':[source_limit(request.scope.authority)],
        'fact_validation':{'status':'supported','method':'finite_source_bound_combat_research_v1',
            'arbitrary_prose_entailment_claimed':False,'covered_parts':sorted(covered)},
        'public_display':False,'speech':False}
    if release_block(response): raise ValueError('Application release guard rejected research')
    request.check()
    return response


def research_reviewed(question, *, authority, model, execution, reviewer, corpus=None,
                      is_current=lambda: True, max_turns=12, timeout_seconds=45, max_total_tokens=24000, display_adapter=None):
    """Dependency-injected text-only service. Review and cancellation precede final receipt."""
    check_cancel()
    requested_parts(question)
    if authority not in {'KCEB','JCEB'}: raise ValueError('Research requires explicit election authority')
    if execution == 'real_api':
        from .openai_integrations import require_live_authorization
        require_live_authorization()
    elif execution != 'synthetic_sdk': raise ValueError('Explicit execution required')
    if reviewer is None: raise ValueError('Independent reviewer required')
    request = ResearchRequest(load_verified_corpus(corpus or Corpus()), scope=Scope(authority=authority),
        model=model,execution=execution,cancel=current_cancel.get(),is_current=is_current,
        max_turns=max_turns,timeout_seconds=timeout_seconds,max_total_tokens=max_total_tokens,
        release_config={'adapter_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'display_sha256': sha256(Path(__file__).with_name('research_display.py').read_bytes()).hexdigest() if display_adapter else None,
            'checks':REVISED_CHECKS,'threshold':0.95,'contract':'finite_source_bound_combat_research_v1'})
    def release(r,draft):
        start=monotonic();response=validate_draft(r,draft,question)
        if display_adapter: response=display_adapter(r,response)
        r.receipt.stage('source_guards',monotonic()-start)
        start=monotonic();review=reviewer.review({'question':question,'response':deepcopy(response)})
        r.receipt.stage('decisions',monotonic()-start)
        r.check();check_cancel()
        # Rebind after the fallible review, including source-file/cancellation changes.
        fresh=validate_draft(r,draft,question)
        if display_adapter: fresh=display_adapter(r,fresh)
        if fresh != response: raise ValueError('Research envelope changed during review')
        accepted = review.get('status') == 'accepted' and (execution != 'real_api' or review.get('execution') == 'real_api')
        status=response['status'] if accepted else 'unavailable'
        response['review']=review
        response['public_display']=accepted
        response['release_state']='released' if accepted else 'held'
        if not accepted:
            response['answer']='Quality checks did not accept this research answer. Retained original wording remains available through the exact-source interface.'
            response['claims']=[];response['evidence']=[]
        r.receipt.release(status=status,binding='supported',review=review.get('status','unavailable'),
            review_execution='real_api' if review.get('execution')=='real_api' else 'synthetic_sdk',
            evidence_ids=[s.get('source_id',s['id']) for s in response['evidence']])
        response['status']=status
        return response
    return request._run(question,release_adapter=release)
