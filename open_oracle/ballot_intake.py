"""Bounded local intake. Uploaded/pasted content never becomes official evidence.

No persistence, logging, network, model, OCR or visitor-provided paths. Owner
ticket/currentness and source/release admission remain the core's responsibility.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import errno
import json
import math
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Callable
import unicodedata

SCHEMA = 'ballot_intake_v1'
SEPARATOR = '\n\f\n'
PROVENANCE = 'unverified_user_content'
HEADINGS = re.compile(r'^[ \t]*(?:(?:CONSTITUTIONAL[ \t]+)?AMENDMENT|(?:BALLOT[ \t]+)?QUESTION|PROPOSITION|REFERENDUM|MEASURE)(?:[ \t]+(?:NO\.?|NUMBER))?[ \t]+(?:[0-9]{1,3}|[A-Z])\b[^\r\n\f]*', re.I | re.M)


class _Failure(Exception):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True)
class Limits:
    max_pdf_bytes: int = 5 * 1024**2
    max_text_bytes: int = 256 * 1024
    max_text_chars: int = 80_000
    max_pages: int = 30
    max_question_chars: int = 20_000
    max_candidates: int = 40
    max_output_bytes: int = 512 * 1024
    wall_seconds: float = 8.0

    def __post_init__(self):
        caps = {'max_pdf_bytes': 5*1024**2, 'max_text_bytes': 256*1024,
                'max_text_chars': 80_000, 'max_pages': 30,
                'max_question_chars': 20_000, 'max_candidates': 40,
                'max_output_bytes': 512*1024}
        for key, cap in caps.items():
            if type(getattr(self, key)) is not int or not 1 <= getattr(self, key) <= cap:
                raise ValueError('invalid_limits')
        if type(self.wall_seconds) not in (int, float) or not math.isfinite(self.wall_seconds) or not .05 <= self.wall_seconds <= 8:
            raise ValueError('invalid_limits')


@dataclass(frozen=True)
class IntakeContext:
    """Complete existing owner ticket, not a replacement session controller."""
    owner_ticket_json: str = field(repr=False)
    document_revision: int

    def __post_init__(self):
        try:
            ticket = json.loads(self.owner_ticket_json)
            if not isinstance(ticket, dict) or not isinstance(ticket.get('request_id'), str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,120}', ticket['request_id']):
                raise ValueError
            if len(self.owner_ticket_json.encode('utf-8')) > 4096:
                raise ValueError
            _ticket_values(ticket)
        except (ValueError, TypeError, UnicodeError):
            raise ValueError('invalid_owner_ticket') from None
        if type(self.document_revision) is not int or not 0 <= self.document_revision <= 2**53 - 1:
            raise ValueError('invalid_document_revision')

    @classmethod
    def from_owner(cls, ticket, document_revision):
        try:
            return cls(json.dumps(ticket, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False), document_revision)
        except (ValueError, TypeError, UnicodeError):
            raise ValueError('invalid_owner_context') from None

    @property
    def owner_ticket(self):
        return json.loads(self.owner_ticket_json)


def _ticket_values(value, depth=0):
    if depth > 4:
        raise ValueError
    if value is None or type(value) is bool:
        return
    if type(value) is int and abs(value) <= 2**53-1:
        return
    if isinstance(value, str) and len(value) <= 200:
        value.encode('utf-8', errors='strict')
        return
    if isinstance(value, dict) and len(value) <= 20 and all(isinstance(k, str) and len(k) <= 64 for k in value):
        for item in value.values():
            _ticket_values(item, depth+1)
        return
    raise ValueError


@dataclass(frozen=True)
class PageSpan:
    page: int
    start: int
    end: int
    blank: bool


@dataclass(frozen=True)
class QuestionBlock:
    block_id: str
    start: int
    end: int
    pages: tuple[int, ...]
    kind: str  # heading_block | whole_document; neither proves completeness


@dataclass(frozen=True)
class IntakeDocument:
    context: IntakeContext
    kind: str
    raw: bytes = field(repr=False)
    text: str = field(repr=False)
    raw_sha256: str
    text_sha256: str
    pages: tuple[PageSpan, ...]
    questions: tuple[QuestionBlock, ...]
    warnings: tuple[str, ...]
    extraction_method: str
    status: str
    provenance: str = PROVENANCE
    source_locale: str = 'unknown'

    def private_projection(self):
        """Private UI intake data; never an AcceptedStore/review/source receipt."""
        return {'schema': SCHEMA, 'owner_ticket': self.context.owner_ticket,
                'document_revision': self.context.document_revision,
                'kind': self.kind, 'status': self.status, 'provenance': PROVENANCE,
                'source_locale': 'unknown', 'raw_sha256': self.raw_sha256,
                'text_sha256': self.text_sha256, 'text': self.text,
                'offset_unit': 'unicode_code_points', 'page_separator': SEPARATOR if self.kind == 'pdf' else '',
                'pages': [vars(p).copy() for p in self.pages],
                'questions': [vars(q).copy() for q in self.questions],
                'warnings': list(self.warnings), 'extraction_method': self.extraction_method,
                'official_source_receipt': None, 'original_verified': False}


@dataclass(frozen=True)
class IntakeResult:
    status: str
    reason: str
    document: IntakeDocument | None = field(default=None, repr=False)


@dataclass(frozen=True)
class SelectedQuestion:
    context: IntakeContext
    block_id: str
    raw_sha256: str
    text_sha256: str
    start: int
    end: int
    quote: str = field(repr=False)
    quote_sha256: str
    pages: tuple[int, ...]
    completeness: str = 'user_confirmed_unverified'
    provenance: str = PROVENANCE
    source_locale: str = 'unknown'


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _check(cancel):
    try:
        state = cancel()
    except Exception:
        raise _Failure('owner_check_unavailable') from None
    if type(state) is not bool:
        raise _Failure('owner_check_unavailable')
    if state:
        raise _Failure('cancelled')


def _validate_text(text, limits, allow_page_break=False):
    if not isinstance(text, str):
        raise _Failure('invalid_text')
    try:
        text.encode('utf-8', errors='strict')
    except UnicodeError:
        raise _Failure('invalid_utf8') from None
    if len(text) > limits.max_text_chars:
        raise _Failure('text_too_large')
    allowed = '\t\n\r' + ('\f' if allow_page_break else '')
    if any(unicodedata.category(c) in ('Cc', 'Cs') and c not in allowed for c in text):
        raise _Failure('binary_or_control_text')
    return ('unicode_format_controls',) if any(unicodedata.category(c) == 'Cf' for c in text) else ()


def _document(raw, pages, kind, context, method, limits, cancel):
    _check(cancel)
    text = SEPARATOR.join(pages) if kind == 'pdf' else pages[0]
    warnings = _validate_text(text, limits, allow_page_break=kind == 'pdf')
    spans, offset = [], 0
    for n, page in enumerate(pages, 1):
        spans.append(PageSpan(n, offset, offset+len(page), not page.strip()))
        offset += len(page) + (len(SEPARATOR) if kind == 'pdf' else 0)
    empty = all(p.blank for p in spans)
    partial = kind == 'pdf' and not empty and any(p.blank for p in spans)
    status = 'ocr_required' if empty and kind == 'pdf' else ('empty' if empty else ('partial_extraction' if partial else 'ready_for_selection'))
    warnings += (('pdf_reading_order_unverified',) if kind == 'pdf' else ())
    if partial:
        warnings += ('blank_pages_require_review_or_paste',)
    blocks = _blocks(text, spans, limits) if status == 'ready_for_selection' else ()
    _check(cancel)
    return IntakeDocument(context, kind, raw, text, _hash(raw), _hash(text.encode('utf-8')), tuple(spans), tuple(blocks), warnings, method, status)


def _blocks(text, spans, limits):
    matches = list(HEADINGS.finditer(text))
    if len(matches) > limits.max_candidates:
        raise _Failure('too_many_questions')
    blocks = []
    for i, match in enumerate(matches):
        start, end = match.start(), matches[i+1].start() if i+1 < len(matches) else len(text)
        blocks.append(QuestionBlock(f'q{i+1}', start, end, tuple(p.page for p in spans if p.start < end and p.end > start), 'heading_block'))
    # Whole-text selection prevents a detector miss from hiding conditions.
    blocks.append(QuestionBlock('whole', 0, len(text), tuple(p.page for p in spans), 'whole_document'))
    return tuple(blocks)


def _failed(exc):
    status = 'cancelled' if exc.reason == 'cancelled' else ('unavailable' if exc.reason in ('parser_unavailable', 'parser_limits_unavailable', 'owner_check_unavailable') else 'rejected')
    return IntakeResult(status, exc.reason)


def parse_paste(text, context, *, limits=Limits(), cancelled=lambda: False):
    try:
        _check(cancelled)
        if not isinstance(context, IntakeContext):
            raise _Failure('invalid_owner_context')
        _validate_text(text, limits)
        raw = text.encode('utf-8')
        if len(raw) > limits.max_text_bytes:
            raise _Failure('text_too_large')
        doc = _document(raw, (text,), 'paste', context, 'exact_unicode_utf8_v1', limits, cancelled)
        return IntakeResult(doc.status, 'none' if doc.status == 'ready_for_selection' else 'empty_text', doc)
    except _Failure as exc:
        return _failed(exc)


@dataclass(frozen=True)
class PopplerTools:
    """Deployment-owned absolute paths, never supplied by an endpoint caller."""
    pdfinfo: str
    pdftotext: str

    def __post_init__(self):
        for name in ('pdfinfo', 'pdftotext'):
            path = getattr(self, name)
            if not isinstance(path, str) or not os.path.isabs(path) or os.path.basename(path) != name or not os.access(path, os.X_OK):
                raise ValueError('invalid_parser_path')

    @classmethod
    def installed(cls):
        info, text = shutil.which('pdfinfo'), shutil.which('pdftotext')
        if not info or not text:
            raise _Failure('parser_unavailable')
        return cls(info, text)


def _rss_guard():
    if sys.platform != 'darwin':
        return lambda process: None
    # Apple's proc_taskinfo ABI: six uint64 fields followed by twelve int32.
    # Observe only this child, never process names/arguments or visitor data.
    try:
        import ctypes
        class TaskInfo(ctypes.Structure):
            _fields_ = [('virtual', ctypes.c_uint64), ('resident', ctypes.c_uint64),
                        ('times', ctypes.c_uint64*4), ('stats', ctypes.c_int32*12)]
        lib = ctypes.CDLL('/usr/lib/libproc.dylib', use_errno=True)
        call = lib.proc_pidinfo
        call.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_int]
        call.restype = ctypes.c_int
    except (OSError, AttributeError):
        raise _Failure('parser_limits_unavailable') from None
    def check(process):
        if process.poll() is not None:
            return
        task = TaskInfo()
        size = ctypes.sizeof(task)
        ctypes.set_errno(0)
        if call(process.pid, 4, 0, ctypes.byref(task), size) != size:
            # A dying task can disappear from proc_pidinfo before waitpid is
            # ready. Only accept that race after observing actual child exit.
            if ctypes.get_errno() == errno.ESRCH:
                try:
                    process.wait(timeout=.03)
                except subprocess.TimeoutExpired:
                    pass
            if process.poll() is None:
                raise _Failure('parser_limits_unavailable')
        elif task.resident > 256*1024**2:
            raise _Failure('extraction_memory_limit')
    return check


def _run_poppler(mode, raw, tools, limits, deadline, cancel):
    if os.name != 'posix':
        raise _Failure('parser_limits_unavailable')
    _check(cancel)
    if time.monotonic() >= deadline:
        raise _Failure('extraction_timeout')
    tool = tools.pdfinfo if mode == 'info' else tools.pdftotext
    worker = str(Path(__file__).with_name('ballot_pdf_worker.py'))
    output_limit = min(limits.max_output_bytes, 16*1024) if mode == 'info' else limits.max_output_bytes
    process, temporary = None, None
    rss_guard = _rss_guard()
    try:
        temporary = tempfile.TemporaryDirectory(prefix='oracle-intake-')
        directory = temporary.name
        # No inherited credentials, home path, proxy or debug environment.
        process = subprocess.Popen([sys.executable, '-I', '-B', worker, mode, tool],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            cwd=directory, env={'LC_ALL':'C', 'LANG':'C', 'PATH':'/usr/bin:/bin', 'TMPDIR':directory},
            start_new_session=True, close_fds=True)
        output, sent = bytearray(), 0
        with selectors.DefaultSelector() as selector:
            os.set_blocking(process.stdin.fileno(), False)
            os.set_blocking(process.stdout.fileno(), False)
            selector.register(process.stdin, selectors.EVENT_WRITE, 'in')
            selector.register(process.stdout, selectors.EVENT_READ, 'out')
            while selector.get_map():
                _check(cancel)
                rss_guard(process)
                if time.monotonic() >= deadline:
                    raise _Failure('extraction_timeout')
                for key, _ in selector.select(timeout=min(.03, max(0, deadline-time.monotonic()))):
                    if key.data == 'in':
                        try:
                            written = os.write(key.fd, raw[sent:sent+32768])
                            sent += written
                        except BlockingIOError:
                            continue
                        except BrokenPipeError:
                            sent = len(raw)
                        if sent == len(raw):
                            selector.unregister(key.fileobj)
                            process.stdin.close()
                    else:
                        try:
                            chunk = os.read(key.fd, 32768)
                        except BlockingIOError:
                            continue
                        if not chunk:
                            selector.unregister(key.fileobj)
                        elif len(output)+len(chunk) > output_limit:
                            raise _Failure('extraction_output_limit')
                        else:
                            output.extend(chunk)
        while process.poll() is None:
            _check(cancel)
            rss_guard(process)
            if time.monotonic() >= deadline:
                raise _Failure('extraction_timeout')
            try:
                process.wait(timeout=.03)
            except subprocess.TimeoutExpired:
                pass
        _check(cancel)
        if process.returncode == 126:
            raise _Failure('parser_limits_unavailable')
        if process.returncode != 0:
            raise _Failure('pdf_parse_failed')
        return bytes(output)
    except (OSError, ValueError, subprocess.SubprocessError):
        raise _Failure('parser_unavailable') from None
    finally:
        if process is not None:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                except PermissionError:
                    # Some managed sandboxes permit only direct-child signals.
                    process.kill()
            process.wait(timeout=1)
            for stream in (process.stdin, process.stdout):
                if stream and not stream.closed:
                    stream.close()
        if temporary is not None:
            temporary.cleanup()


def _pdf_pages(raw, tools, limits, cancel):
    deadline = time.monotonic()+limits.wall_seconds
    info = _run_poppler('info', raw, tools, limits, deadline, cancel)
    count = re.findall(rb'^Pages:[ \t]+([0-9]+)[ \t]*$', info, re.M)
    encrypted = re.findall(rb'^Encrypted:[ \t]+(yes|no)\b', info, re.M)
    js = re.findall(rb'^JavaScript:[ \t]+(yes|no)\b', info, re.M)
    forms = re.findall(rb'^Form:[ \t]+([^\r\n]+)', info, re.M)
    if len(count) != 1 or len(encrypted) != 1 or len(js) != 1 or len(forms) != 1:
        raise _Failure('pdf_metadata_unavailable')
    if encrypted[0] != b'no':
        raise _Failure('encrypted_pdf_unsupported')
    if js[0] != b'no' or forms[0].strip() != b'none':
        raise _Failure('active_pdf_unsupported')
    if len(count[0]) > 3:
        raise _Failure('page_limit')
    page_count = int(count[0])
    if not 1 <= page_count <= limits.max_pages:
        raise _Failure('page_limit')
    out = _run_poppler('text', raw, tools, limits, deadline, cancel)
    try:
        text = out.decode('utf-8', errors='strict')
    except UnicodeError:
        raise _Failure('invalid_utf8') from None
    if not text.endswith('\f'):
        raise _Failure('pdf_page_mapping_failed')
    pages = tuple(text[:-1].split('\f'))
    if len(pages) != page_count:
        raise _Failure('pdf_page_mapping_failed')
    return pages


def parse_upload(raw, kind, context, *, limits=Limits(), cancelled=lambda: False, tools=None):
    try:
        _check(cancelled)
        if not isinstance(context, IntakeContext):
            raise _Failure('invalid_owner_context')
        if type(raw) is not bytes or not raw:
            raise _Failure('empty_upload' if raw == b'' else 'invalid_upload')
        if kind not in ('pdf', 'txt'):
            raise _Failure('unsupported_file_type')
        cap = limits.max_pdf_bytes if kind == 'pdf' else limits.max_text_bytes
        if len(raw) > cap:
            raise _Failure('upload_too_large')
        if kind == 'txt':
            if raw.startswith((b'%PDF-', b'PK\x03\x04', b'\x1f\x8b')):
                raise _Failure('content_type_mismatch')
            try:
                # One leading UTF-8 BOM is removed by this explicit decoding rule.
                text = raw.decode('utf-8-sig', errors='strict')
            except UnicodeError:
                raise _Failure('invalid_utf8') from None
            doc = _document(raw, (text,), 'txt', context, 'strict_utf8_optional_bom_v1', limits, cancelled)
        else:
            if not re.match(rb'%PDF-(?:1\.[0-9]|2\.0)[\r\n]', raw):
                raise _Failure('content_type_mismatch')
            selected_tools = tools if tools is not None else PopplerTools.installed()
            if not isinstance(selected_tools, PopplerTools):
                raise _Failure('parser_unavailable')
            pages = _pdf_pages(raw, selected_tools, limits, cancelled)
            doc = _document(raw, pages, 'pdf', context, 'poppler_layout_utf8_v1', limits, cancelled)
        reason = {'ready_for_selection':'none', 'empty':'empty_text', 'ocr_required':'no_pdf_text_ocr_unavailable', 'partial_extraction':'incomplete_pdf_text'}.get(doc.status, 'intake_held')
        return IntakeResult(doc.status, reason, doc)
    except _Failure as exc:
        return _failed(exc)


def select_question(document, block_id, context, *, confirmed_complete, limits=Limits(), cancelled=lambda: False):
    """Select a whole detected block, never arbitrary client start/end/text.

Confirmation is a user assertion about supplied text, not source verification.
Raises fixed ValueError reasons; caller must keep visitor content out of logs.
"""
    try:
        _check(cancelled)
        if not isinstance(document, IntakeDocument) or document.status != 'ready_for_selection':
            raise _Failure('document_not_selectable')
        if context != document.context:
            raise _Failure('stale_document')
        if confirmed_complete is not True:
            raise _Failure('complete_question_confirmation_required')
        if document.provenance != PROVENANCE or document.source_locale != 'unknown':
            raise _Failure('intake_provenance_invalid')
        if _hash(document.raw) != document.raw_sha256 or _hash(document.text.encode('utf-8')) != document.text_sha256:
            raise _Failure('document_hash_mismatch')
        offset = 0
        if document.kind not in ('pdf', 'txt', 'paste') or not document.pages or len(document.pages) > limits.max_pages:
            raise _Failure('page_spans_invalid')
        for n, page in enumerate(document.pages, 1):
            if (page.page != n or type(page.start) is not int or type(page.end) is not int
                    or page.start != offset or not offset <= page.end <= len(document.text)
                    or type(page.blank) is not bool or page.blank != (not document.text[page.start:page.end].strip())):
                raise _Failure('page_spans_invalid')
            offset = page.end
            if n < len(document.pages):
                if document.kind != 'pdf' or document.text[offset:offset+len(SEPARATOR)] != SEPARATOR:
                    raise _Failure('page_spans_invalid')
                offset += len(SEPARATOR)
        if offset != len(document.text):
            raise _Failure('page_spans_invalid')
        if document.questions != _blocks(document.text, document.pages, limits):
            raise _Failure('question_blocks_mismatch')
        matches = [q for q in document.questions if q.block_id == block_id]
        if len(matches) != 1:
            raise _Failure('unknown_question_block')
        block = matches[0]
        if not (type(block.start) is int and type(block.end) is int and 0 <= block.start < block.end <= len(document.text)):
            raise _Failure('question_span_invalid')
        quote = document.text[block.start:block.end]
        if len(quote) > limits.max_question_chars:
            raise _Failure('question_too_large_use_complete_paste')
        if not quote.strip():
            raise _Failure('empty_question')
        _check(cancelled)
        return SelectedQuestion(context, block.block_id, document.raw_sha256, document.text_sha256,
                                block.start, block.end, quote, _hash(quote.encode('utf-8')), block.pages)
    except _Failure as exc:
        raise ValueError(exc.reason) from None
