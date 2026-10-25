"""Public-fixture-only provider diagnostics; never imported by the web server.

Keeps generated drafts/predicate scores for failed synthetic tests without
putting raw payloads into production Held errors, jobs, or operational ledgers.
"""
import json
import math
from providers import Held, OpenAIProvider


class PublicDiagnosticProvider(OpenAIProvider):
    def __init__(self, organization, project, *, fixture_kind, before_dispatch=None):
        if fixture_kind != 'synthetic_public_questions_no_human_recording':
            raise Held('public_diagnostics_role')
        super().__init__(organization, project, before_dispatch=before_dispatch)
        self.public_drafts = []
        self.predicate_reviews = []
        self.public_voice_outputs = []

    def observe_public_voice(self, turn, expected, observed, *, start_ms=None, end_ms=None):
        # Only this explicitly synthetic-public provider retains model prose.
        # The production provider/operational receipt has no such observer.
        if (type(turn) is not int or not 1<=turn<=3 or type(expected) is not str
                or not 1<=len(expected)<=700 or type(observed) is not str or len(observed)>2000):
            raise Held('public_voice_diagnostics_bound')
        row=next((x for x in self.public_voice_outputs if x['turn']==turn),None)
        if row is None:
            row={'turn':turn,'expected':expected,'observed':'','fragments':0,'deltas':[],'delta_history_truncated':False}
            self.public_voice_outputs.append(row)
        if row['expected'] != expected: raise Held('public_voice_diagnostics_binding')
        if not observed.startswith(row['observed']): raise Held('public_voice_diagnostics_binding')
        delta=observed[len(row['observed']):]
        valid_window=(type(start_ms) in (int,float) and type(end_ms) in (int,float)
                      and math.isfinite(start_ms) and math.isfinite(end_ms) and 0<=start_ms<=end_ms<=120000)
        if len(row['deltas'])<128:
            row['deltas'].append({'delta':delta,'start_ms':start_ms if valid_window else None,
                                  'end_ms':end_ms if valid_window else None})
        else: row['delta_history_truncated']=True
        row['observed']=observed
        row['fragments']+=1

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
