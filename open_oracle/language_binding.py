"""Pi/backend locale seam using continuous owner's identities, no new controller."""
from copy import deepcopy
import inspect
from .language_capabilities import locale_tag

class LanguageBinding:
    def __init__(self, cancel_current, is_current, language='en'):
        self.cancel_current,self.is_current=cancel_current,is_current
        self.language=locale_tag(language)
        self.revision=0
        self.optional_english=False
        self.recognition=None
        self.corrected_transcript=None

    def _cancel(self,reason):
        result=self.cancel_current(reason)
        if result is False:raise ValueError('cancellation_failed')
        if inspect.isawaitable(result):
            if inspect.iscoroutine(result):result.close()
            raise ValueError('synchronous_cancellation_required')
        self.revision+=1

    def choose(self,language,optional_english=False):
        chosen=locale_tag(language)
        if type(optional_english) is not bool:raise ValueError('invalid_english_preference')
        if chosen!=self.language or optional_english!=self.optional_english:
            self._cancel('language_revision')
            self.language,self.optional_english=chosen,optional_english
            self.recognition=self.corrected_transcript=None

    def bind(self,ticket):
        if not isinstance(ticket,dict) or not self.is_current(ticket):raise ValueError('stale_response')
        if set(ticket)&{'language','language_revision'}:raise ValueError('duplicate_language_binding')
        return {**deepcopy(ticket),'language':self.language,'language_revision':self.revision}

    def accepts(self,bound_ticket):
        if not isinstance(bound_ticket,dict) or bound_ticket.get('language')!=self.language or bound_ticket.get('language_revision')!=self.revision:return False
        return bool(self.is_current({k:v for k,v in bound_ticket.items() if k not in ('language','language_revision')}))

    def correction(self,text,transcript_language,bound_ticket):
        if not self.accepts(bound_ticket):return False
        if not isinstance(text,str) or not 0<len(text)<=2000:raise ValueError('invalid_transcript')
        language=locale_tag(transcript_language)
        self._cancel('recognition_revision')
        self.corrected_transcript={'text':text,'language':language,'corrected':True}
        self.recognition=None
        return True

    def erase(self):
        # Existing owner performs erase/epoch rotation; this discards locale data.
        self._cancel('erase_language_state')
        self.recognition=self.corrected_transcript=None
