"""Consume evaluation owner's eight private candidates without duplicating copy.

This adapter ONLY binds private draft text to exact retained evidence. It cannot
release it. Translation/style semantic review and whole-display checks remain
pending. Spanish readability requires its own method, never English FRE/FKGL.
"""
from copy import deepcopy
import json
from pathlib import Path
from .translation_validation import digest,text_hash
from .explanation_styles import explanation_style,strands_style_context

def private_style_candidate(language,style,retained_source):
    style=explanation_style(style)
    if language not in ('en','es') or style=='standard':raise ValueError('style_fixture_unavailable')
    fixture=json.loads((Path(__file__).resolve().parents[1]/'fixtures/literacy_styles.json').read_text())
    if not isinstance(retained_source,dict) or retained_source!=fixture['source'] or digest(retained_source)!=fixture['source_fingerprint']:
        raise ValueError('style_source_unbound')
    candidates=[s for s in fixture['styles'] if s['language']==language and s['explanation_style']==style]
    if len(candidates)!=1:raise ValueError('style_fixture_unavailable')
    row=candidates[0]
    if (row['source_original_sha256']!=retained_source['sha256'] or row['source_text_sha256']!=text_hash(retained_source['text'])
        or row['text']!='\n\n'.join(row['layers']) or row['source_fingerprint']!=digest(retained_source)):
        raise ValueError('style_source_unbound')
    return {'private_draft':deepcopy(row),'source_binding':digest(retained_source),'invariants':deepcopy(fixture['invariants']),
        'context':strands_style_context(style,language),'production_release':'withheld','speech':None,
        'review_required':['underlying_english_source_release','deterministic_translation_invariants','translation_predicates','complete_display_projection'],
        'readability_method': 'Spanish IFSZ candidate; local counts unvalidated' if language=='es' else 'English FRE/FKGL diagnostic; no comprehension guarantee'}
