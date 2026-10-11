"""Server-only GPT-Live render: accepted text in, validated ephemeral WAV out."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from .session_control import SessionCancelled

def render_speech(contract, cancel):
    from .openai_integrations import require_live_authorization
    require_live_authorization()
    node = shutil.which('node')
    if not node:
        raise RuntimeError('Local Node runtime unavailable')
    script = Path(__file__).resolve().parents[1] / 'scripts/live-ws/ws-speech.cjs'
    process = subprocess.Popen([node, str(script), '--trusted-stdin'], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=os.environ.copy())
    deadline = time.monotonic() + 65
    data = json.dumps({'text': contract['text']}).encode()
    try:
        while True:
            if cancel.is_set():
                raise SessionCancelled('Speech cancelled')
            if time.monotonic() > deadline:
                raise TimeoutError('Speech deadline exceeded')
            try:
                output, _ = process.communicate(input=data, timeout=.1)
                break
            except subprocess.TimeoutExpired:
                data = None
        if len(output) > 6 * 1024 * 1024 or process.returncode:
            raise ValueError('Speech did not finish')
        result = json.loads(output)
        if not result.get('accepted'):
            return {'accepted': False, 'report': result.get('report', {}), 'usage': result.get('usage')}
        return {**result, 'request_id': contract['request_id'], 'text': contract['text'], 'language': contract['language']}
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=3)

