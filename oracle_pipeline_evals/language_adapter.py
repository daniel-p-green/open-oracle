"""Explicit owner-selected offline modules, loaded without mutating canonical imports.

No auto-discovery, production integration, provider or meaning-adjudication claim.
Owner module bytes are pinned by the runner's dependency manifest.
"""
import importlib
import sys
import types
from dataclasses import replace
from pathlib import Path

NAME = '_oracle_pipeline_language_fixture'


def modules(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('language_modules_unavailable')
    package = types.ModuleType(NAME)
    package.__path__ = [str(root)]
    old = sys.modules.get(NAME)
    if old is not None and old.__path__ != package.__path__:
        raise ValueError('language_root_changed')
    sys.modules[NAME] = old or package
    return {name: importlib.import_module(NAME + '.' + name) for name in
            ('language_capabilities', 'language_session', 'language_routing',
             'translation_validation', 'language_fixtures')}


def run(case, root):
    if root is None:
        return 'owner_adapter_unavailable'
    m = modules(root)
    operation, language = case['operation'], case['language']
    if operation.startswith('identification_'):
        routing = m['language_routing']
        labels = dict(routing.LABELS)
        choice = {'identification_mixed': 'mixed', 'identification_unknown': 'unknown',
                  'identification_suggested': language}.get(operation, language)
        ticket = (('epoch', 1), ('language_revision', 0), ('request_id', 'synthetic-request'))
        text = 'COMBAT' if operation == 'identification_short' else 'Synthetic substantive language example, not recognition evidence.'
        requests = []

        def transport(resource, body):
            requests.append(body)
            return {'model': 'gpt-6-luna', 'answers': [{'name': 'spoken_language', 'type': 'choice', 'choice': choice,
                                  'probabilities': [{'value': tag, 'probability': 1.0 if tag == choice else 0.0}
                                                    for tag in labels]}]}
        request = routing.LanguageIdentification(routing.ActivatedInput(ticket, text, True, True),
                                                lambda current: True, transport=transport)
        answer = request.identify()
        request.identify()
        if len(requests) > 1 or answer.get('requires_choice') is not True:
            return 'unsafe_identification'
        return answer['status']
    if operation.startswith('lifecycle_'):
        cancellations = []
        session = m['language_session'].LanguageSession(lambda: cancellations.append(1), language=language)
        session.resume()
        old = session.token('synthetic-request')
        if operation == 'lifecycle_correction':
            session.correct_transcript('Synthetic corrected question', language, old)
        elif operation == 'lifecycle_language_change':
            session.choose('es' if language == 'en' else 'en')
        elif operation == 'lifecycle_stop_resume':
            session.stop()
            session.resume()
        elif operation == 'lifecycle_erase':
            session.transcript = {'text': 'PRIVATE_CANARY'}
            session.recognition = {'languages': [language]}
            session.erase()
            if session.transcript is not None or session.recognition is not None:
                return 'retained_visitor_text'
        return 'stale_rejected' if not session.accepts(old) and len(cancellations) >= 2 else 'stale_accepted'
    if operation == 'accessibility_direction':
        return m['language_capabilities'].direction(language)
    if operation.startswith('translation_'):
        if language == 'en':
            return 'not_applicable'
        fixture = m['language_fixtures']
        validation = m['translation_validation']
        sources, all_forms = fixture.fixtures()
        key = case.get('form', 'rate')
        forms = [form for form in all_forms if form.language == language and form.id.endswith(':' + key)]
        if len(forms) != 1:
            return 'owner_fixture_unavailable'
        form = forms[0]
        target = form.target
        if operation == 'translation_number_change':
            target = target.replace('0.25', '25')
        if operation in ('translation_negation_drop', 'translation_polarity_swap'):
            anchor = next(f for f in form.features if f.kind == ('negation' if operation.endswith('drop') else 'polarity'))
            target = target.replace(anchor.target_phrase, '', 1)
        if operation == 'translation_source_changed':
            sources[form.source_id] = replace(sources[form.source_id], text=form.source_quote + ' changed')
        reviewer = validation.TranslationDecisionsCheck(fixture.accepted_fixture_transport)
        operation_token = validation.SourceOperation('synthetic-release', '0'*64, 1, 0)
        gate = validation.TranslationGate(sources.get, forms, lambda envelope: None, reviewer, lambda: None,
                                          current_operation=lambda token: token == operation_token)
        claims = [{'form_id': form.id, 'text': target, 'language': language}]
        if operation == 'translation_forged_review':
            claims[0]['reviewed'] = True
        result = gate.release('synthetic-request', language, claims, fixture.SCOPE,
                              fixture_mode=operation != 'translation_production_block', operation=operation_token)
        return result['status'] if result['status'] != 'withheld' else result['reason']
    raise ValueError('unknown_language_operation')
