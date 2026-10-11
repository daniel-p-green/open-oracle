"""Shared catalog for the Python/Pi surface, with explicitly labelled fallback."""
import json
from pathlib import Path
from .language_capabilities import LanguageRegistry, direction

CATALOG = json.loads(Path(__file__).with_name('locale_catalog.json').read_text())

def message(key, requested_language, registry=None):
    info = (registry or LanguageRegistry()).describe(requested_language)
    language = info['catalog_language']
    catalog = CATALOG['catalogs'].get(language, CATALOG['catalogs']['en'])
    if key not in catalog: raise KeyError(key)
    return {'text': catalog[key], 'language': language, 'direction': direction(language),
            'requested_language': info['requested_language'], 'fallback_reason': info['fallback_reason']}

def refusal(reason, language):
    key = 'reason.' + reason
    if key not in CATALOG['catalogs']['en']: key = 'reason.invalid_translation_envelope'
    return message(key, language)
