"""Optional local Whisper adapter; no capture, file retention or cloud transport.

Not wired to a microphone route. The caller owns consent, Stop/Erase generation
fencing and visible correction/confirmation before selecting a public action.
Whisper is loaded only on explicit construction from existing verified weights.
"""
import hashlib
import math
from pathlib import Path
from providers import Held, check_cancel

MAX_INPUT_SECONDS = 15


class LocalWhisperInput:
    def __init__(self, model_file, model_name='base'):
        if model_name not in {'tiny', 'base', 'small'}:
            raise Held('local_input_model_unadmitted')
        # Optional installed dependency: never download/install a package/model.
        import importlib.metadata
        import torch
        import whisper
        if importlib.metadata.version('openai-whisper') != '20250625':
            raise Held('local_input_version_unreviewed')
        path = Path(model_file).expanduser().resolve(strict=True)
        if not path.is_file() or path.stat().st_size > 500_000_000:
            raise Held('local_input_weights_unavailable')
        expected = whisper._MODELS[model_name].split('/')[-2]
        with path.open('rb') as source:
            actual = hashlib.file_digest(source, 'sha256').hexdigest()
        if actual != expected:
            raise Held('local_input_weights_integrity')
        torch.set_num_threads(4)
        # A verified explicit file path, rather than model alias, avoids Whisper's
        # alias path that may download missing weights. No fallback is attempted.
        self.model = whisper.load_model(str(path), device='cpu')

    def transcribe_pcm(self, pcm, language, cancel):
        check_cancel(cancel)
        if language not in {'en', 'es'} or type(pcm) is not bytes or not 3200 <= len(pcm) <= MAX_INPUT_SECONDS * 16000 * 2 or len(pcm) % 2:
            raise Held('local_input_format')
        import numpy as np
        samples = np.frombuffer(pcm, dtype='<i2').astype(np.float32) / 32768
        if not math.isfinite(float(np.max(np.abs(samples)))) or not np.any(samples):
            raise Held('local_input_empty')
        result = self.model.transcribe(samples, language=language, task='transcribe',
            fp16=False, temperature=0, beam_size=1, best_of=1,
            condition_on_previous_text=False, verbose=None)
        # Native inference cannot be interrupted mid-call. A stale result is
        # discarded here; a future capture owner must also fence UI delivery.
        check_cancel(cancel)
        text = result.get('text')
        if not isinstance(text, str) or not 1 <= len(text.strip()) <= 500:
            raise Held('local_input_unrecognized')
        # This can contain private speech. Only return to local correction UI.
        # Never persist/log it or pass it as a model prompt. Language is a user
        # preference, not proof of detected language or transcript correctness.
        return {'text': text.strip(), 'language_preference': language,
                'requires_local_confirmation': True, 'cloud_sent': False}
