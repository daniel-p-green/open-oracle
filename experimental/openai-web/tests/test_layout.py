import json
from pathlib import Path
import sys
import threading
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from layout import ProductPipeline
from providers import Held


class LayoutTests(unittest.TestCase):
    def test_provider_envelope_cannot_invent_or_hide_evidence(self):
        class Provider:
            def post(self, path, body, cancel):
                self.body = body
                return {'status': 'completed', 'usage': {'input_tokens': 200, 'output_tokens': 25},
                        'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(self.draft)}]}]}
        provider = Provider()
        class Base: pass
        base = Base(); base.provider = provider
        with self.assertRaisesRegex(Held,'native_voice_package_closed'): ProductPipeline(base,voice_fixtures='unused-no-access')
        pipeline = ProductPipeline(base); cancel = threading.Event(); calls = []
        provider.draft = {'intent': 'maps', 'components': ['scope', 'maps', 'map_sources']}
        result, pcm = pipeline.run_task('layout:maps', cancel, lambda _: None, lambda *args: calls.append(args))
        self.assertEqual(result['layout'], provider.draft); self.assertEqual(pcm, b'')
        self.assertEqual(provider.body['max_output_tokens'], 128); self.assertFalse(provider.body['store'])
        self.assertNotIn('tools', provider.body); self.assertNotIn('address', json.dumps(provider.body)); self.assertEqual(len(calls), 1)
        for components in [['scope', 'maps', 'maps'], ['scope', 'maps', 'political_statistics'], ['maps', 'scope', 'map_sources']]:
            provider.draft = {'intent': 'maps', 'components': components}
            with self.assertRaises(Held): pipeline.run_task('layout:maps', cancel, lambda _: None, lambda *args: None)
        cancel.set()
        with self.assertRaises(Held): pipeline.run_task('layout:maps', cancel, lambda _: None, lambda *args: None)
