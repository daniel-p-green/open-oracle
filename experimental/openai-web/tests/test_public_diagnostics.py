import json
import os
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests/manual'))
from providers import Held, OpenAIProvider
from journey import JourneyPipeline
from public_diagnostics import PublicDiagnosticProvider


class PublicDiagnosticsTests(unittest.TestCase):
    def test_language_hold_retains_public_draft_and_all_scores_only_in_explicit_test_provider(self):
        draft = {'operation': 'brief', 'language': 'en',
                 'sections': [{'source_id': 'question', 'text': 'The question asks whether to approve the legislature’s act replacing the congressional plan.'}],
                 'components': ['explanation', 'original', 'uncertainty']}
        names = ['entailed', 'no_additions', 'attributed', 'request_fit', 'language_match', 'polarity_safe']
        answers = [{'type': 'predicate', 'name': name, 'probability': .1 if name == 'language_match' else .99}
                   for name in names]
        def response(path, body, cancel):
            usage = {'input_tokens': 200, 'output_tokens': 80 if path == 'responses' else 0}
            if path == 'responses':
                return {'status': 'completed', 'usage': usage, 'private_transport_metadata': 'must-not-retain',
                        'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(draft)}]}]}
            return {'usage': usage, 'answers': answers, 'private_transport_metadata': 'must-not-retain'}
        # Fake key and patched transport: no real credential or network access.
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'fixture-only'}), patch.object(OpenAIProvider, 'post', side_effect=response):
            provider = PublicDiagnosticProvider('fixture-scope', 'fixture-scope',
                fixture_kind='synthetic_public_questions_no_human_recording')
            with self.assertRaisesRegex(Held, 'journey_language_match_held') as held:
                JourneyPipeline(provider).run_task('journey:brief:en', threading.Event(), lambda *_: None, lambda *_: None)
        self.assertEqual(provider.public_drafts[0]['text'], json.dumps(draft))
        self.assertEqual(provider.predicate_reviews, [{'operation': 'brief', 'language': 'en', 'has_previous': False, 'answers': answers}])
        self.assertEqual({k:provider.public_drafts[0][k] for k in ('operation','language','has_previous')},
                         {'operation': 'brief', 'language': 'en', 'has_previous': False})
        provider.observe_public_voice(1,'The question asks for approval.','The question')
        provider.observe_public_voice(1,'The question asks for approval.','The question asks for approval. The question asks for approval.',start_ms=100,end_ms=200)
        self.assertEqual(provider.public_voice_outputs,[{'turn':1,'expected':'The question asks for approval.',
            'observed':'The question asks for approval. The question asks for approval.','fragments':2,
            'delta_history_truncated':False,'deltas':[{'delta':'The question','start_ms':None,'end_ms':None},
              {'delta':' asks for approval. The question asks for approval.','start_ms':100,'end_ms':200}]}])
        for turn,text in [(4,'public'),(1,'x'*2001)]:
            with self.assertRaisesRegex(Held,'public_voice_diagnostics_bound'):provider.observe_public_voice(turn,'expected',text)
        with self.assertRaisesRegex(Held,'public_voice_diagnostics_binding'):provider.observe_public_voice(1,'changed','public')
        with self.assertRaisesRegex(Held,'public_voice_diagnostics_binding'):provider.observe_public_voice(1,'The question asks for approval.','nonappend')
        diagnostic = json.dumps([provider.public_drafts, provider.predicate_reviews,provider.public_voice_outputs])
        for excluded in ('fixture-only', 'fixture-scope', 'must-not-retain'):
            self.assertNotIn(excluded, diagnostic)
        self.assertEqual(str(held.exception), 'journey_language_match_held')
        with self.assertRaisesRegex(Held, 'public_diagnostics_role'):
            PublicDiagnosticProvider('unused', 'unused', fixture_kind='human_audio')
