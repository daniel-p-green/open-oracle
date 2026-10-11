"""Request-local validation categories; never serialize a Pydantic error payload."""
from contextvars import ContextVar

SCHEMA_NAME = 'cited_answer_v1'
CATEGORIES = frozenset({'missing','list_type','model_type','string_type','string_too_short',
    'string_too_long','string_pattern_mismatch','literal_error','extra_forbidden',
    'too_short','too_long','value_error','dict_type','validation_other'})
FIELD_PATHS = frozenset({'root','unrecognized_field','claims','gaps','clarification',
    'claims.*','claims.*.part_id','claims.*.text','claims.*.citations',
    'claims.*.citations.*','claims.*.citations.*.chunk_id',
    'claims.*.citations.*.exact_quote','claims.*.citations.*.citation_span_id',
    'gaps.*','gaps.*.part_id','gaps.*.reason'})
collector = ContextVar('oracle_schema_validation_collector', default=None)


def normalized_path(location):
    if not isinstance(location, (tuple,list)):
        return 'unrecognized_field'
    if not location:
        return 'root'
    if len(location)>5:
        return 'unrecognized_field'
    parts=[]
    for part in location:
        if type(part) is int and part>=0:
            parts.append('*')
        elif type(part) is str and part in {'claims','gaps','clarification','part_id','text',
                                         'citations','chunk_id','exact_quote','citation_span_id','reason'}:
            parts.append(part)
        else:
            return 'unrecognized_field'
    path='.'.join(parts)
    return path if path in FIELD_PATHS else 'unrecognized_field'


def validation_events(error, schema_sha256):
    # Explicit exclusions prevent values, contexts, messages or external URLs
    # entering the projection. Extra-field locations are still untrusted strings.
    errors=error.errors(include_input=False, include_context=False, include_url=False)
    return [{'schema':SCHEMA_NAME,'schema_sha256':schema_sha256,
             'category':e['type'] if e.get('type') in CATEGORIES else 'validation_other',
             'field_path':normalized_path(e.get('loc'))} for e in errors[:8]]


def record_validation(error, schema_sha256):
    callback=collector.get()
    if callback is not None:
        for event in validation_events(error,schema_sha256):
            callback(**event)
