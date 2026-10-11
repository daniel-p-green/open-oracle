"""Opt-in browser research engine. Legacy typed fallback remains separately available."""
from uuid import uuid4
from time import monotonic
from .research_release import requested_parts, research_reviewed
from .research_display import project_display, validate_display
from .session_control import check_cancel, SessionCancelled


class ResearchEvidenceLoop:
    def __init__(self, corpus, model_factory, reviewer, execution='real_api'):
        self.corpus, self.model_factory, self.reviewer, self.execution = corpus, model_factory, reviewer, execution

    def answer(self, question, scope=None, request_id=None, contest_id=None):
        check_cancel(); scope = dict(scope or {}); started = monotonic()
        base = {'request_id': request_id or str(uuid4()), 'mode': 'reviewed_strands_research',
                'status': 'insufficient_evidence', 'answer': '', 'card': None,
                'evidence': [], 'claims': [], 'choices': [], 'links': [], 'candidate_sources': [],
                'scope': scope, 'election_date': '2026-11-03', 'snapshot_date': '2026-10-11',
                'language': 'en', 'translation_status': 'not_requested', 'speech': False,
                'review': {'status': 'not_run'}, 'public_display': False, 'limitations': []}
        if scope.get('election_date', '2026-11-03') != '2026-11-03':
            return {**base, 'answer': 'This research route covers retained November 3, 2026 sources only.'}
        if scope.get('authority') not in {'JCEB', 'KCEB'}:
            return {**base, 'status': 'clarification', 'answer': 'Choose KCEB or JCEB in election context before research. This does not determine your personal ballot.'}
        try:
            requested_parts(question)
            if contest_id not in (None, 'combat'):
                raise ValueError('Different contest')
        except ValueError:
            return {**base, 'answer': 'This reviewed research route currently supports only the COMBAT printed tax rate, duration, and a refusal to predict crime reduction. Your full question is outside that contract; no part was answered. Use the retained-source interface for other contests or wording.'}
        try:
            result = research_reviewed(question, authority=scope['authority'], model=self.model_factory(),
                execution=self.execution, reviewer=self.reviewer, corpus=self.corpus, display_adapter=project_display, timeout_seconds=35)
            check_cancel()
            if result['public_display'] and validate_display(result, self.corpus)['status'] != 'supported':
                raise ValueError('Second research display boundary failed')
            return {**base, **result, 'request_id': base['request_id'],
                    'elapsed_ms': round((monotonic() - started) * 1000),
                    'operational_receipt': result['receipt']}
        except SessionCancelled:
            raise
        except Exception:
            check_cancel()
            return {**base, 'status': 'unavailable',
                    'answer': 'Research could not finish its source and quality checks. No draft was released. Retained original wording remains available in the exact-source interface.'}


def build_research_engine(corpus, reviewer):
    import os
    from .openai_integrations import require_live_authorization
    require_live_authorization()
    if not os.environ.get('OPEN_ORACLE_MODEL'):
        raise ValueError('Research requires an explicitly selected model')
    from strands.models.openai import OpenAIModel
    def factory():
        return OpenAIModel(model_id=os.environ['OPEN_ORACLE_MODEL'],
            client_args={'timeout': 10, 'max_retries': 0},
            params={'reasoning_effort': 'none', 'max_completion_tokens': 600, 'store': False})
    return ResearchEvidenceLoop(corpus, factory, reviewer)
