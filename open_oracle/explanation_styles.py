"""Chosen detail styles are request preferences, never inferred visitor traits."""
from .language_capabilities import locale_tag
STYLES = ('standard','college_detail','high_school','middle_school','simplest_useful')

def explanation_style(value):
    if type(value) is not str or value not in STYLES:raise ValueError('unsupported_explanation_style')
    return value

def strands_style_context(style,language):
    """Private drafting context; core retains all source/release gates."""
    return {'explanation_style':explanation_style(style),'requested_output_language':locale_tag(language),
            'visitor_education':'not_inferred',
            'instruction':'Preserve every material source condition, exception, number, date, unit, YES/NO meaning, scope, attribution and evidence gap at every detail style. Detail preference cannot expand supported facts. This context is not evidence or release approval.',
            'readability_policy':'locale_specific_diagnostic_only; never a fidelity or comprehension gate'}
