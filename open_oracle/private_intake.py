"""Private, bounded intake transactions inside the existing visitor session owner.

No corpus insertion, provider calls, accepted-answer receipts, persistence or telemetry.
The HTTP host supplies the existing complete ticket; it must invalidate local work before
committing or selecting. Server signal rotation independently cancels prior server work.
"""
from copy import deepcopy
from dataclasses import replace
import hashlib
from importlib.metadata import version
import threading
from uuid import uuid4

from .ballot_intake import IntakeContext, parse_paste, parse_upload, select_question
from .session_control import SessionCancelled


class IntakeFailure(Exception):
    def __init__(self, reason, status=409):
        super().__init__(reason)
        self.reason, self.status = reason, status


def ticket_context(ticket, revision):
    context = IntakeContext.from_owner(ticket, revision)
    # Map existing host tickets rather than minting a second visitor controller.
    if type(ticket.get('epoch')) is not int or not 0 <= ticket['epoch'] <= 2**53 - 1:
        raise ValueError('existing_epoch_required')
    counter = 'generation' if 'generation' in ticket else 'sequence'
    if type(ticket.get(counter)) is not int or not 0 <= ticket[counter] <= 2**53 - 1:
        raise ValueError('existing_generation_or_sequence_required')
    return context


def fresh_ticket(previous, ticket, revision):
    context = ticket_context(ticket, revision)
    counter = 'generation' if 'generation' in previous else 'sequence'
    if (set(previous) != set(ticket) or ticket.get(counter, -1) <= previous[counter]
            or ticket['request_id'] == previous['request_id']
            or any(ticket[k] != previous[k] for k in previous if k not in (counter, 'request_id'))):
        raise IntakeFailure('fresh_same_owner_ticket_required')
    return context


class PrivateIntake:
    MAX_DOCUMENTS = 4
    MAX_RAW_BYTES = 20 * 1024 * 1024

    def __init__(self, sessions):
        self.sessions = sessions
        self.slot = threading.BoundedSemaphore(1)

    def _entry(self, session, signal=None):
        entry = self.sessions.entries.get(session)
        if not entry or entry['cancel'].is_set():
            raise SessionCancelled('Session erased or expired')
        if signal is not None and entry['cancel'] is not signal:
            raise IntakeFailure('owner_changed')
        return entry

    def _state(self, entry):
        return entry.setdefault('intake', {'revision': 0, 'documents': {}, 'pending': None,
                                         'active_document': None, 'active_ticket': None,
                                         'selection': None})

    def _revision(self, state, revision):
        if type(revision) is not int or revision != state['revision']:
            raise IntakeFailure('document_revision_changed')

    def state(self, session, signal):
        with self.sessions.lock:
            state = self._state(self._entry(session, signal))
            return {'schema': 'open-oracle-private-intake/v1', 'document_revision': state['revision'],
                    'active_document': state['active_document'],
                    'documents': [{'document_id': ident, 'document_revision': doc.context.document_revision,
                                   'kind': doc.kind, 'status': doc.status} for ident, doc in state['documents'].items()],
                    'selection_id': state['selection']['selection_id'] if state['selection'] else None,
                    'source_acceptance': 'not_run', 'translation': 'blocked', 'speech': False}

    def prepare(self, session, signal, ticket, revision, *, text=None, raw=None, kind=None):
        context = ticket_context(ticket, revision + 1)
        nonce = str(uuid4())
        with self.sessions.lock:
            entry = self._entry(session, signal)
            state = self._state(entry)
            self._revision(state, revision)
            if len(state['documents']) >= self.MAX_DOCUMENTS:
                raise IntakeFailure('document_capacity_reached', 413)
            if state['active_ticket'] is not None:
                fresh_ticket(state['active_ticket'], ticket, revision + 1)
            if state['pending'] is not None:
                raise IntakeFailure('preview_already_pending', 409)
            state['pending'] = {'id': nonce, 'document': None, 'signal': signal}
        def cancelled():
            with self.sessions.lock:
                return (signal.is_set() or self.sessions.entries.get(session) is not entry
                        or entry['cancel'] is not signal or state['revision'] != revision
                        or state['pending'] is None or state['pending']['id'] != nonce)
        try:
            result = (parse_paste(text, context, cancelled=cancelled) if kind is None
                      else parse_upload(raw, kind, context, cancelled=cancelled))
            with self.sessions.lock:
                self._entry(session, signal)
                self._revision(state, revision)
                if cancelled(): raise IntakeFailure('preview_replaced')
                if result.document is None:
                    state['pending'] = None
                    if result.status == 'cancelled': raise IntakeFailure('owner_changed')
                    code = 503 if result.status == 'unavailable' else 415 if result.reason in ('invalid_utf8', 'unsupported_file_type', 'content_type_mismatch', 'binary_or_control_text') else 413 if result.reason in (
                        'upload_too_large', 'text_too_large', 'too_many_pages', 'too_many_questions',
                        'output_too_large', 'question_too_large_use_complete_paste') else 422
                    raise IntakeFailure(result.reason, code)
                retained = sum(len(d.raw) for d in state['documents'].values())
                if retained + len(result.document.raw) > self.MAX_RAW_BYTES:
                    state['pending'] = None
                    raise IntakeFailure('document_bytes_capacity_reached', 413)
                state['pending']['document'] = result.document
                return {'status': result.status, 'reason': result.reason, 'prepared_id': nonce,
                        'expected_revision': revision, 'document': result.document.private_projection(),
                        'requires_fresh_ticket_commit': True, 'source_acceptance': 'not_run', 'speech': False}
        except BaseException:
            with self.sessions.lock:
                if state['pending'] is not None and state['pending']['id'] == nonce:
                    state['pending'] = None
            raise

    def discard(self, session, signal, prepared_id):
        with self.sessions.lock:
            state = self._state(self._entry(session, signal))
            if state['pending'] and state['pending']['id'] == prepared_id:
                state['pending'] = None
            return {'status': 'preview_discarded', 'provider_erasure_claimed': False}

    def _invalidate(self, entry):
        # Shared server cancellation, not a new voice/language/controller owner.
        entry['cancel'].set()
        entry['cancel'] = threading.Event()
        entry['receipt'] = None
        entry.pop('context', None)
        entry['touched'] = self.sessions.now()

    def commit(self, session, signal, prepared_id, ticket, revision):
        with self.sessions.lock:
            entry = self._entry(session, signal)
            state = self._state(entry)
            self._revision(state, revision)
            pending = state['pending']
            if not pending or pending['id'] != prepared_id or pending['document'] is None or pending['signal'] is not signal:
                raise IntakeFailure('unknown_private_preview')
            doc = pending['document']
            context = fresh_ticket(doc.context.owner_ticket, ticket, revision + 1)
            if state['active_ticket'] is not None:
                fresh_ticket(state['active_ticket'], ticket, revision + 1)
            self._invalidate(entry)
            document_id = str(uuid4())
            doc = replace(doc, context=context)
            state['revision'] += 1
            state['documents'][document_id] = doc
            state.update(pending=None, active_document=document_id, active_ticket=context.owner_ticket,
                         selection=None)
            return {'status': 'committed_private_document', 'document_id': document_id,
                    'document': doc.private_projection(), 'document_revision': state['revision'],
                    'owner_ticket': context.owner_ticket, 'source_acceptance': 'not_run',
                    'translation': 'blocked', 'speech': False}, entry['cancel']

    def select(self, session, signal, document_id, block_id, ticket, revision,
               confirmed_complete, method_language_assumption):
        with self.sessions.lock:
            entry = self._entry(session, signal)
            state = self._state(entry)
            self._revision(state, revision)
            if document_id != state['active_document'] or document_id not in state['documents']:
                raise IntakeFailure('unknown_or_inactive_private_document')
            doc = state['documents'][document_id]
            context = fresh_ticket(state['active_ticket'], ticket, revision)
            previous_ticket = deepcopy(state['active_ticket'])
        selected = select_question(doc, block_id, doc.context, confirmed_complete=confirmed_complete,
                                   cancelled=signal.is_set)
        report = self._readability(doc, selected, method_language_assumption)
        with self.sessions.lock:
            self._entry(session, signal)
            self._revision(state, revision)
            if state['active_ticket'] != previous_ticket or state['active_document'] != document_id:
                raise IntakeFailure('selection_changed')
            self._invalidate(entry)
            selection_id = str(uuid4())
            binding = {'owner_ticket': context.owner_ticket, 'document_id': document_id,
                       'document_revision': revision, 'block_id': selected.block_id,
                       'raw_sha256': selected.raw_sha256, 'text_sha256': selected.text_sha256,
                       'start': selected.start, 'end': selected.end, 'quote_sha256': selected.quote_sha256,
                       'offset_unit': 'unicode_code_points', 'selection_id': selection_id}
            response = {'schema': 'open-oracle-private-selection/v1', 'status': 'selected_unverified_question',
                        'binding': binding, 'quote': selected.quote, 'pages': list(selected.pages),
                        'completeness': selected.completeness, 'source_locale': 'unknown',
                        'provenance': 'unverified_user_content', 'readability': report,
                        'source_acceptance': 'not_run', 'translation': 'blocked', 'speech': False}
            state.update(pending=None, active_ticket=context.owner_ticket, selection=deepcopy(response))
            return response, entry['cancel']

    def _readability(self, doc, selected, assumption):
        if assumption not in (None, 'en'): raise ValueError('unsupported_method_choice')
        base = {'schema': 'open-oracle-private-readability/v1', 'diagnostic_kind': 'surface_readability',
                'source_locale': doc.source_locale, 'source_provenance': doc.provenance,
                'method_language_assumption': assumption, 'report': None, 'clarity': {'status': 'not_run'},
                'label': 'English formula estimate' if assumption else 'Choose a formula method',
                'scope': 'whole_document' if selected.block_id == 'whole' else 'selected_question',
                'qualifier': 'You selected English; source language not verified. This formula does not test comprehension, accuracy or legal meaning.' if assumption else 'No formula selected. Source language is unverified.'}
        if assumption is None:
            return {**base, 'status': 'unsupported', 'reason': 'explicit_method_choice_required'}
        if doc.source_locale not in ('unknown', 'en'):
            return {**base, 'status': 'unsupported', 'reason': 'known_non_english_source'}
        try:
            from .readability import analyze_readability, METHOD_VERSION
            if version('cmudict') != '1.1.1': raise RuntimeError('dictionary_version')
            report = analyze_readability(selected.quote, 'Supplied complete question' if base['scope'] == 'selected_question' else 'Supplied whole document',
                provenance={'basis': 'unverified_user_content'}, language='en', extraction_method=doc.extraction_method)
            if report['raw_text_sha256'] != selected.quote_sha256: raise RuntimeError('raw_binding')
            code_hash = hashlib.sha256(__import__('pathlib').Path(__file__).with_name('readability.py').read_bytes()).hexdigest()
            base.update(method_version=METHOD_VERSION, dependency={'cmudict': '1.1.1', 'scorer_sha256': code_hash},
                        diagnostic_basis='explicit_english_formula_assumption', report={key: report[key] for key in (
                        'status', 'method_version', 'counts', 'scores', 'warnings', 'method', 'limitations',
                        'raw_text_sha256', 'scored_text_sha256', 'cleaning_audit', 'factual_fidelity_status')})
            status = {'estimated': 'calculated_under_assumption', 'unsupported_language': 'unsupported', 'empty': 'empty'}.get(report['status'], 'unavailable')
            return {**base, 'status': status, 'reason': 'none' if status == 'calculated_under_assumption' else report['status']}
        except Exception:
            return {**base, 'status': 'unavailable', 'reason': 'formula_dependency_or_binding_unavailable'}
