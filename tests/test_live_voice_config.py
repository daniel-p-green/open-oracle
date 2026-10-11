"""Voice preference configuration, not audible/media/live-provider acceptance."""
import json
from pathlib import Path
import subprocess
from typing import get_args
import unittest
from openai.types.live.built_in_voice import BuiltInVoice
from openai.types.live.session_config import SessionConfig
from open_oracle.openai_integrations import ENGLISH_LIVE_VOICE

class LiveVoiceConfigurationTests(unittest.TestCase):
    def test_cedar_is_declared_in_the_installed_live_specific_sdk_contract(self):
        self.assertEqual(ENGLISH_LIVE_VOICE,'cedar')
        self.assertIn(ENGLISH_LIVE_VOICE,get_args(BuiltInVoice))
        config=SessionConfig(model='gpt-live-1',audio={'output':{'voice':ENGLISH_LIVE_VOICE}})
        self.assertEqual(config.audio.output.voice,'cedar')

    def test_websocket_start_config_matches_webrtc_without_starting_a_session(self):
        repo=Path(__file__).resolve().parents[1]
        result=subprocess.run(['node','-e',"process.stdout.write(JSON.stringify(require('./scripts/live-ws/ws-speech.cjs').speechSession()))"],cwd=repo,capture_output=True,text=True,check=True,timeout=3)
        config=json.loads(result.stdout)
        self.assertEqual(config['model'],'gpt-live-1')
        self.assertEqual(config['audio']['output']['voice'],ENGLISH_LIVE_VOICE)
        self.assertEqual(config['audio']['format'],{'type':'audio/pcm','rate':24000})
        self.assertEqual(config['delegation'],{'type':'client'})
        self.assertIs(config['store'],False)
