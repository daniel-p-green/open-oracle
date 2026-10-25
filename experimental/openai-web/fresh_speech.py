"""Fresh checked public speech, buffered and independently transcribed before release.

No microphone, visitor text, reusable answer library or automatic playback.
The existing job owner supplies the same-owner ready parent; all media is memory-only.
"""
import hashlib
import io
import math
import re
import struct
import unicodedata
import wave
from journey import QUESTION_PIN, load_question, validate_unit
from providers import Held, check_cancel

TASKS = {'speech:en','speech:es'}
MAX_PCM = 60 * 24000 * 2


def words(text):
    # Closed pronunciation/typography equivalences for this admitted question.
    # Never normalize a free-standing negation "no" or arbitrary numbers.
    text=unicodedata.normalize('NFC',text)
    text=re.sub(r'\b(?:St\.?|Saint)\s+Louis\b','Saint Louis',text,flags=re.I)
    text=re.sub(r'\b(?:Missouri|Misuri)\b','Missouri',text,flags=re.I)
    text=re.sub(r'\bA\.\s*I\.?(?!\w)', 'AI',text,flags=re.I)
    text=re.sub(r'\bI\.\s*A\.?(?!\w)', 'IA',text,flags=re.I)
    text=re.sub(r'\bHouse Bill\s+(?:No\.?|number)\s*(?:1|one|uno)\b','House Bill number 1',text,flags=re.I)
    text=re.sub(r'\b(?:two thousand(?: and)? twenty[- ]five|twenty twenty[- ]five|dos mil veinticinco)\b','2025',text,flags=re.I)
    return re.findall(r'\w+',text.casefold())


def reading_for(prior, language):
    if (type(prior) is not dict or prior.get('source_version') != QUESTION_PIN
            or prior.get('mode') != 'fresh_grounded_generation'
            or prior.get('raw_visitor_input_sent') is not False):
        raise Held('parent_source_mismatch')
    unit=prior.get('unit',{})
    if unit.get('language') != language: raise Held('speech_language')
    validate_unit(unit,unit.get('operation'),language,load_question())
    notice = ('Explicación por IA, revisión humana pendiente.' if language=='es' else 'AI explanation, human review pending.')
    label = ('Explicación del texto de la pregunta, no es una cita.' if language=='es' else 'Explanation of the ballot wording, not a quotation.')
    quality=[]
    if prior.get('request_fit') == 'unconfirmed':
        quality.append('El nivel de sencillez o detalle solicitado no está confirmado.' if language=='es'
                       else 'The requested simplicity or detail is unconfirmed.')
    scope = ('Esta muestra pública no verifica su boleta ni su distrito.' if language=='es'
             else 'This public sample does not verify your ballot or district.')
    text=' '.join([notice,scope,label,*quality,*(p['text'] for p in unit['sections'])])
    if not 1 <= len(text) <= 1000 or any(mark in text for mark in ('⟦','⟧')): raise Held('speech_reading_bound')
    return text


def speech_preflight(prior,language):
    text=reading_for(prior,language)
    # Conservative admission heuristic, not a measured duration guarantee.
    if len(text)/12>45: raise Held('speech_too_long')
    return text


class FreshSpeechPipeline:
    def __init__(self, provider, allow_spanish=False):
        self.provider, self.allow_spanish=provider,allow_spanish

    def run_task(self,task,cancel,stage,meter,prior=None):
        check_cancel(cancel)
        if task not in TASKS: raise Held('task_unadmitted')
        language=task.split(':')[1]
        if language=='es' and not self.allow_spanish: raise Held('translation_review_required')
        stage('retrieval')
        text=speech_preflight(prior,language)
        stage('audio')
        audio=self.provider.speak(text,cancel,language=language,reading_seconds=52,canonicalize=words)
        meter('fresh_audio',audio.get('usage'));check_cancel(cancel)
        stage('validation')
        pcm=audio.get('pcm')
        if (audio.get('finalized') is not True or audio.get('reason')!='close_requested'
                or audio.get('errors') or audio.get('backend_events')!=0
                or type(audio.get('transcript')) is not str or words(audio['transcript'])!=words(text) or type(pcm) is not bytes
                or not 24000<=len(pcm)<=MAX_PCM or len(pcm)%2
                or not any(v[0] for v in struct.iter_unpack('<h',pcm))):
            raise Held('fresh_audio_withheld')
        seconds=audio.get('usage',{}).get('seconds')
        if type(seconds) not in (int,float) or not math.isfinite(seconds) or not 0<seconds<=75:
            raise Held('audio_usage_unconfirmed')
        buffer=io.BytesIO()
        with wave.open(buffer,'wb') as output:
            output.setnchannels(1);output.setsampwidth(2);output.setframerate(24000);output.writeframes(pcm)
        wav=buffer.getvalue();duration=len(pcm)/48000
        stage('transcription')
        # No supplied expected transcript, prompt, or language hint biases ASR.
        transcript=self.provider.transcribe(wav,cancel)
        meter('transcription',{'seconds':duration});check_cancel(cancel)
        stage('validation')
        detected=transcript.get('languages')
        if type(detected) is not list or not detected or type(detected[0]) is not dict or detected[0].get('code')!=language:
            raise Held('independent_language_mismatch')
        if type(transcript.get('text')) is not str or words(transcript['text'])!=words(text):
            raise Held('independent_transcript_mismatch')
        if reading_for(prior,language)!=text: raise Held('parent_source_mismatch')
        return {'mode':'fresh_checked_speech','source_version':QUESTION_PIN,'language':language,
                'reading':text,'bytes':len(wav),'sha256':hashlib.sha256(wav).hexdigest(),
                'asr_model':'gpt-transcribe','independent_asr_match':True,'finalized':True,
                'provider_timing_ms':{name:value for name,value in (audio.get('timing_ms') if type(audio.get('timing_ms')) is dict else {}).items()
                    if name in {'connected','session_started','reading_sent','first_audio_delta','last_audio_delta','close_requested','finalized'}
                    and type(value) in (int,float) and math.isfinite(value) and 0<=value<=90000},
                'duration_seconds':duration,'live_close_trigger':audio.get('close_trigger','unknown'),
                'acoustic_human_review':False,'translation_review':'pending' if language=='es' else 'not_a_human_review',
                'raw_visitor_input_sent':False,'playback_enabled':False},wav
