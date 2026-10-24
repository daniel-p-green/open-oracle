"""Public-fixture-only provider diagnostics; never imported by the web server.

Keeps generated drafts/predicate scores for failed synthetic tests without
putting raw payloads into production Held errors, jobs, or operational ledgers.
"""
import json
from providers import Held, OpenAIProvider


class PublicDiagnosticProvider(OpenAIProvider):
    def __init__(self, organization, project, *, fixture_kind):
        if fixture_kind != 'synthetic_public_questions_no_human_recording':
            raise Held('public_diagnostics_role')
        super().__init__(organization, project)
        self.public_drafts = []
        self.predicate_reviews = []

    def post(self, path, body, cancel):
        result = super().post(path, body, cancel)
        public = next((part.get('content') for part in body.get('input', []) if type(part) is dict and part.get('role') == 'user'), '{}') if path == 'responses' else body.get('input', '{}')
        try:
            context = json.loads(public)
        except (TypeError, ValueError):
            context = {}
        operation = (body.get('text', {}).get('format', {}).get('schema', {}).get('properties', {}).get('operation', {}).get('enum', [None])[0]
                     if path == 'responses' else context.get('draft', {}).get('operation'))
        tags = {'operation': operation, 'language': context.get('language'),
                'has_previous': context.get('previous_checked_public_unit') is not None}
        if path == 'responses':
            text = ''.join(part.get('text', '') for message in result.get('output', [])
                           if message.get('type') == 'message' for part in message.get('content', [])
                           if part.get('type') == 'output_text')
            if len(text) > 8192:
                raise Held('public_diagnostics_bound')
            self.public_drafts.append({**tags, 'model': body.get('model'), 'text': text})
        elif path == 'decisions':
            self.predicate_reviews.append({**tags, 'answers': [
                {key: answer.get(key) for key in ('type', 'name', 'probability')}
                for answer in result.get('answers', [])
            ]})
        return result
