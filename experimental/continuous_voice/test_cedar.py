"""Offline compatibility/configuration proof, never synthesized Cedar audio."""
import unittest
from typing import get_args
from openai.types.live.built_in_voice import BuiltInVoice
from openai.types.live.session_config_param import AudioOutputVoice
from open_oracle.openai_integrations import LiveSessions


class CedarTests(unittest.TestCase):
    def test_installed_python_live_type_supports_cedar(self):
        self.assertIn('cedar', get_args(BuiltInVoice))
        self.assertIn(BuiltInVoice, get_args(AudioOutputVoice))

    def test_canonical_webrtc_startup_uses_cedar_with_injected_offline_transport(self):
        calls = []
        def offline(endpoint, body):
            calls.append((endpoint, body))
            return {'session': {'id': 'SYNTHETIC-only'}, 'transport': {'type': 'webrtc', 'sdp': 'v=0\r\n'}}
        sessions = LiveSessions(transport=offline)
        sessions.create('v=0\r\n')
        self.assertEqual(sessions.execution, 'offline_stub')
        self.assertEqual(len(calls), 1)
        endpoint, body = calls[0]
        self.assertEqual(endpoint, 'live/sessions')
        self.assertEqual(body['session']['model'], 'gpt-live-1')
        self.assertEqual(body['session']['audio']['output']['voice'], 'cedar')
        self.assertFalse(body['session']['store'])


if __name__ == '__main__':
    unittest.main()
