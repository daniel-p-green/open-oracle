"""Additional language fence; existing closed-audio/evidence acceptance is mandatory."""
import unicodedata
from .translation_validation import text_hash

def canonical_transcript(text):
    if not isinstance(text,str) or not 0<len(text)<=2400:raise ValueError('invalid_transcript')
    # Do not strip accents, negate words, transliterate or align deltas to audio.
    if any(unicodedata.category(c)=='Cf' for c in text):raise ValueError('hidden_transcript_controls')
    return ' '.join(unicodedata.normalize('NFC',text).split())

def language_speech_matches(accepted_contract,transcript,language_binding,current_source_check,existing_audio_check,media):
    """Contract comes from current SERVER accepted receipt, never a model/client.

    Core must enforce selected startup voice, calibrated/verified capability and
    budget before rendering. This predicate authorizes no playback by itself.
    """
    try:
        if (not language_binding.accepts(accepted_contract['ticket'])
            or accepted_contract['language']!=accepted_contract['ticket']['language']
            or text_hash(accepted_contract['text'])!=accepted_contract['text_sha256']
            or canonical_transcript(transcript)!=canonical_transcript(accepted_contract['text'])
            or not current_source_check(accepted_contract)
            or not existing_audio_check(media,accepted_contract)):
            return False
        return language_binding.accepts(accepted_contract['ticket']) and current_source_check(accepted_contract)
    except (ValueError,TypeError,KeyError,AttributeError):return False
