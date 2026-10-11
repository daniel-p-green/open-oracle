"""Buffered AG-UI release adapter. Never forwards provider text or tool streams."""
import json


def parse_run(data):
    if not isinstance(data, dict):
        raise ValueError('Expected an AG-UI run')
    for key in ('threadId', 'runId'):
        if not isinstance(data.get(key), str) or not 0 < len(data[key]) <= 120:
            raise ValueError('Invalid run identity')
    if data.get('tools') or data.get('context') or data.get('resume'):
        raise ValueError('Client tools, context and resume are not supported')
    messages = data.get('messages')
    if not isinstance(messages, list) or len(messages) != 1:
        raise ValueError('Send only the current reviewed question')
    message = messages[0]
    if not isinstance(message, dict) or message.get('role') != 'user' or not isinstance(message.get('content'), str):
        raise ValueError('Expected one text user question')
    if not 0 < len(message['content'].strip()) <= 2000:
        raise ValueError('Invalid question length')
    props = data.get('forwardedProps') or {}
    if not isinstance(props, dict) or set(props) - {'scope', 'contest_id'}:
        raise ValueError('Invalid application context')
    scope = props.get('scope', {})
    if not isinstance(scope, dict) or set(scope) - {'election_date', 'authority', 'municipality', 'district'} or any(not isinstance(v, str) or len(v) > 100 for v in scope.values()):
        raise ValueError('Invalid election scope')
    contest_id = props.get('contest_id')
    if contest_id is not None and (not isinstance(contest_id, str) or len(contest_id) > 120):
        raise ValueError('Invalid contest identity')
    return message['content'], scope, contest_id


def release_events(result, thread_id, run_id, corpus=None):
    """Only the application's completed release result becomes visible state."""
    if result.get('request_id') != run_id:
        raise ValueError('Mismatched response identity')
    review = result.get('review', {})
    # A second boundary prevents an accidental upstream withholding regression.
    if review.get('status') not in ('not_run', 'accepted'):
        if result.get('card') or result.get('evidence') or result.get('claims') or result.get('candidate_sources'):
            raise ValueError('Withheld content cannot become AG-UI state')
    if result.get('mode') == 'live_strands' and (review.get('status') != 'accepted' or review.get('execution') != 'real_api') and result.get('status') != 'unavailable':
        raise ValueError('Live content requires accepted review')
    if result.get('mode') == 'reviewed_strands_research' and (review.get('status') != 'accepted' or review.get('execution') != 'real_api'):
        if result.get('public_display') or result.get('status') == 'answered':
            raise ValueError('Live content requires accepted review')
    if result.get('display_contract') == 'source_bound_research_browser_v1' and result.get('public_display'):
        from .research_display import validate_display
        if corpus is None or validate_display(result, corpus)['status'] != 'supported':
            raise ValueError('Research display bindings must pass before streaming')
    from .claim_bindings import validate_factual_display
    if result.get('status') == 'answered' and (corpus is None or validate_factual_display(result, corpus)['status'] != 'supported'):
        raise ValueError('Factual display bindings must pass before streaming')
    from .source_fallback import validate_fallback
    from .view_plan import validate_view_plan
    if result.get('source_fallback') and not validate_fallback(result['source_fallback'], result, corpus):
        raise ValueError('Unbound original-source fallback')
    if result.get('view_plan') and not validate_view_plan(result['view_plan'], result):
        raise ValueError('Invalid declarative view plan')
    # Diagnostic tool trace is deliberately absent from streamed state.
    public = {k: v for k, v in result.items() if k not in ('trace', 'integration_error')}
    events = [{'type': 'RUN_STARTED', 'threadId': thread_id, 'runId': run_id},
              {'type': 'STATE_SNAPSHOT', 'snapshot': {'response': public}}]
    # A complete, application-selected descriptor, emitted only after validation.
    # It renders a local component; it grants no execution or model-facing frontend tool.
    if public.get('view_plan'):
        tool_id = 'view-' + run_id
        events += [{'type': 'TOOL_CALL_START', 'toolCallId': tool_id, 'toolCallName': 'renderEvidenceView'},
                   {'type': 'TOOL_CALL_ARGS', 'toolCallId': tool_id, 'delta': json.dumps(public['view_plan'])},
                   {'type': 'TOOL_CALL_END', 'toolCallId': tool_id},
                   {'type': 'TOOL_CALL_RESULT', 'toolCallId': tool_id, 'messageId': 'view-result-' + run_id,
                    'role': 'tool', 'content': '{"status":"validated_component_ready"}'}]
    events.append({'type': 'RUN_FINISHED', 'threadId': thread_id, 'runId': run_id})
    return events


def encode_events(events):
    return ''.join('data: ' + json.dumps(event, ensure_ascii=False, allow_nan=False) + '\n\n' for event in events)
