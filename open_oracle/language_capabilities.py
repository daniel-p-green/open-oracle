"""Application-owned capabilities, never inferred from a provider's language name.

Provider verification and fixture coverage are deliberately separate. Regional
tags select a base catalog, while the requested tag remains in the request.
"""
from dataclasses import dataclass, asdict
import re
import unicodedata

TAG = re.compile(r'^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8}){0,4}$')
RTL_BASES = frozenset({'ar', 'fa', 'he', 'ur', 'ps', 'sd', 'yi'})
RTL_SCRIPTS = frozenset({'Arab', 'Hebr', 'Thaa', 'Nkoo', 'Adlm', 'Syrc'})

def locale_tag(value):
    if not isinstance(value, str) or not TAG.fullmatch(value):
        raise ValueError('invalid_language')
    parts = value.split('-')
    return '-'.join([parts[0].lower()] + [p.title() if len(p) == 4 and p.isalpha() else p.upper() if len(p) == 2 and p.isalpha() else p.lower() for p in parts[1:]])

def direction(tag, text=None):
    if text is not None:
        for c in text:
            bidi = unicodedata.bidirectional(c)
            if bidi in ('R', 'AL'): return 'rtl'
            if bidi == 'L': return 'ltr'
    parts = locale_tag(tag).split('-')
    scripts = [p for p in parts[1:] if len(p) == 4 and p.isalpha()]
    if scripts: return 'rtl' if scripts[0] in RTL_SCRIPTS else 'ltr'
    return 'rtl' if parts[0] in RTL_BASES else 'ltr'

@dataclass(frozen=True)
class Capability:
    language: str
    label: str
    controls: str
    explanation: str
    recognition: str = 'unverified'
    speech: str = 'unverified'
    voice: str | None = None
    verification: tuple[str, ...] = ()
    spoken_language: str | None = None
    script: str | None = None
    catalog_validation: str = 'offline_authored'
    verified_surfaces: tuple[str, ...] = ()
    verified_scopes: tuple[str, ...] = ()

    def spoken_ready(self, scope=None, surface=None):
        return (self.controls == 'validated' and self.explanation == 'evaluated_finite_contract'
                and self.recognition == 'physically_verified' and self.speech == 'physically_verified'
                and self.voice is not None and self.catalog_validation == 'validated'
                and scope is not None and scope in self.verified_scopes and surface in self.verified_surfaces)

class LanguageRegistry:
    def __init__(self, capabilities=None):
        rows = capabilities if capabilities is not None else (
            Capability('en', 'English', 'fixture_complete', 'existing_source_gated',
                       voice='cedar', verification=('gpt-live-1 SDK contract inspected; audible test pending',),script='Latn'),
            Capability('es', 'Español', 'fixture_complete', 'offline_fixture_only',script='Latn'),
            Capability('vi', 'Tiếng Việt', 'fixture_complete', 'offline_fixture_only',script='Latn'),
            Capability('ar', 'العربية', 'fixture_complete', 'offline_fixture_only', script='Arab'),
            Capability('zh-Hans', '普通话', 'fixture_complete', 'offline_fixture_only', spoken_language='Mandarin', script='Hans'),
            Capability('fil', 'Filipino (Tagalog)', 'fixture_complete', 'offline_fixture_only', spoken_language='Tagalog',script='Latn'),
        )
        self._rows = {}
        for row in rows:
            key = locale_tag(row.language)
            if key != row.language or key in self._rows: raise ValueError('invalid_registry')
            self._rows[key] = row

    def resolve(self, requested):
        tag = locale_tag(requested)
        if tag in self._rows:return self._rows[tag]
        parts=tag.split('-')
        script=next((p for p in parts[1:] if len(p)==4 and p.isalpha()),None)
        if script:
            scripted=self._rows.get(parts[0]+'-'+script)
            if scripted:return scripted
            base=self._rows.get(parts[0])
            return base if base and base.script==script else None
        return self._rows.get(parts[0])

    def describe(self, requested):
        tag = locale_tag(requested)
        row = self.resolve(tag)
        return {'requested_language': tag, 'catalog_language': row.language if row else 'en',
                'direction': direction(tag), 'supported_controls': row is not None,
                'capability': asdict(row) if row else None,
                'fallback_reason': None if row else 'unsupported_language'}

    def public(self, *, scope=None, surface=None):
        return {'version': 1, 'languages': [{**asdict(r), 'direction': direction(r.language),
                    'spoken_ready': r.spoken_ready(scope,surface), 'invitation_key': 'idle.invitation'} for r in self._rows.values()],
                'scope': scope, 'surface': surface,
                'provider_language_coverage': 'not_established', 'physical_voice_verification': 'pending'}
