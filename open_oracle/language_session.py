"""Volatile locale adapter for existing web/Pi controllers; no transport or capture.

Owner MUST perform cancellation before applying language changes/stop/erase.
Tokens supplement existing request/evidence/playback gates, never replace them.
Recognition offers a suggestion; explicit choice determines output language.
"""
from dataclasses import dataclass, asdict
from uuid import uuid4
import inspect
from .language_capabilities import locale_tag

@dataclass(frozen=True)
class LanguageToken:
    session_id: str
    epoch: int
    language_revision: int
    request_id: str
    language: str

class LanguageSession:
    def __init__(self, cancel_pending, language='en'):
        if not callable(cancel_pending): raise ValueError('cancellation_required')
        self.cancel_pending = cancel_pending
        self.session_id = str(uuid4())
        self.epoch = 0
        self.revision = 0
        self.language = locale_tag(language)
        self.optional_english = False
        self.stopped = True
        self.pending = None
        self.recognition = None
        self.transcript = None

    def token(self, request_id):
        if self.stopped or not isinstance(request_id, str) or not request_id or len(request_id) > 120:
            raise ValueError('session_stopped_or_invalid_request')
        self.pending = LanguageToken(self.session_id, self.epoch, self.revision, request_id, self.language)
        return asdict(self.pending)

    def accepts(self, token):
        return not self.stopped and self.pending is not None and token == asdict(self.pending)

    def _invalidate(self):
        result = self.cancel_pending()  # failure prevents dependent mutation
        if inspect.isawaitable(result):
            if inspect.iscoroutine(result): result.close()
            raise ValueError('synchronous_cancellation_required')
        self.epoch += 1
        self.pending = None

    def choose(self, language, optional_english=False):
        tag = locale_tag(language)
        if type(optional_english) is not bool: raise ValueError('invalid_english_preference')
        if tag != self.language or optional_english != self.optional_english:
            self._invalidate()
            self.revision += 1
            self.language, self.optional_english = tag, optional_english
            self.recognition = None
            self.transcript = None
            self.stopped = True

    def suggest(self, languages, token):
        if not self.accepts(token): return False
        tags = list(dict.fromkeys(locale_tag(x) for x in languages))
        if not tags or len(tags) > 8: raise ValueError('invalid_recognition')
        self.recognition = {'languages': tags, 'mixed': len(tags) > 1, 'requires_choice': True}
        return True

    def correct_transcript(self, text, language, token):
        if not self.accepts(token): return False
        if not isinstance(text, str) or not 0 < len(text) <= 2000: raise ValueError('invalid_transcript')
        tag = locale_tag(language)
        self._invalidate()
        self.transcript = {'text': text, 'language': tag, 'corrected': True}
        self.stopped = True
        return True

    def stop(self):
        self._invalidate()
        self.stopped = True
        self.recognition = None

    def resume(self):
        if not self.stopped: return
        self._invalidate()
        self.stopped = False

    def erase(self):
        self._invalidate()
        self.session_id = str(uuid4())
        self.stopped = True
        self.recognition = self.transcript = None
        # Locale is a station preference; no visitor text is retained.
