"""Eight reviewed, partial Ordinance 6096 passages; no legal/release approval.

The index binds reviewer locators (inspection aids, not glyph coordinates).
Original PDF bytes remain in the caller's retained archive. Nothing is copied,
downloaded, split, inferred, indexed remotely, or released by this loader.
"""
from __future__ import annotations

import json
from pathlib import Path

from .research_corpus import Chunk, Source, digest

SOURCE_ID = 'combat-6096-selected-v1'
ORIGINAL_SHA256 = '5fa4474560da047207bfd7c7033de0d0a1febb20d6e92cc6447982ca71a1afde'
READING_SHA256 = '229da53b66722072ed5f980c09ef91125b573fb1a18c333d2ed14961163f83a5'
INDEX_SHA256 = '13b7602bf7d7d6553465732f343156ba5900480521900f1633baf5c21de32d39'
PACKET_SHA256 = 'ad8c7fe44fd934217615cd7c931f824e005f104657900b359e0fb47f67e316b2'
DATA = Path(__file__).resolve().parents[1] / 'data'

# The full question includes its trust-fund sentence; Section 4 includes the
# voter condition and both collection dates; Section 2 includes the exception.
SELECTED = (
    ('prior_authorization', 179, 532, 1, 'first WHEREAS recital'),
    ('existing_expiry', 586, 669, 1, 'third WHEREAS recital'),
    ('submission_scope_rate_duration_purposes', 746, 1330, 2, 'Section 1, full body'),
    ('administration_and_election_cost_exception', 1410, 1705, 2, 'Section 2, full body'),
    ('submitted_ballot_full_question', 1806, 2363, 3, 'Section 3, complete question and trust-fund condition'),
    ('approval_condition_and_extension_dates', 2439, 2717, 3, 'Section 4, full body'),
    ('election_board_notification', 2782, 3107, 4, 'Section 5, full body'),
    ('ordinance_effective_condition', 3191, 3296, 5, 'Effective Date, full printed sentence'),
)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate selected-index key')
        result[key] = value
    return result


def _index(path: Path) -> dict:
    raw = path.read_bytes()
    if digest(raw) != INDEX_SHA256:
        raise ValueError('Selected index changed from approved version')
    index = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object)
    expected = {
        'schema_version': 1, 'source_id': SOURCE_ID, 'role': 'adopted_proposal',
        'quality': 'verified_reading_copy', 'issuer': 'Jackson County Legislature',
        'state': 'MO', 'county': 'jackson-county-mo', 'authority': None,
        'election_date': '2026-11-03', 'effective_from': None,
        'retrieved_date': '2026-10-11', 'status': 'retained_snapshot',
        'original_sha256': ORIGINAL_SHA256, 'original_bytes': 466739,
        'original_pages': 5, 'reading_file': '6096-selected-reading.txt',
        'reading_sha256': READING_SHA256, 'verification_packet_sha256': PACKET_SHA256,
        'partial': True, 'runtime_release_approved': False,
    }
    if any(index.get(key) != value for key, value in expected.items()):
        raise ValueError('Invalid selected source schema, scope, role or pins')
    if set(index) != set(expected) | {
            'source_url', 'offset_basis', 'transcription_method', 'verification_limit', 'passages'}:
        raise ValueError('Unexpected selected-index fields')
    passages = index['passages']
    if not isinstance(passages, list) or len(passages) != len(SELECTED):
        raise ValueError('Expected exactly eight approved passages')
    seen = set()
    for span, approved in zip(passages, SELECTED):
        if set(span) != {'id', 'start', 'end', 'text_sha256', 'pdf_page_1_based',
                         'section_or_locator', 'reviewer_locator', 'transcription',
                         'runtime_release_approved'}:
            raise ValueError('Unexpected selected-passage fields')
        if (span['id'], span['start'], span['end'], span['pdf_page_1_based'],
                span['section_or_locator']) != approved or span['id'] in seen:
            raise ValueError('Changed, duplicate or unapproved passage/offset/page/locator')
        seen.add(span['id'])
        if any(type(span[k]) is not int for k in ('start', 'end', 'pdf_page_1_based')):
            raise ValueError('Offsets and PDF pages must be integers')
        locator = span['reviewer_locator']
        if set(locator) != {'image_file', 'approximate_normalized_bbox', 'semantics'}:
            raise ValueError('Invalid reviewer locator schema')
        box = locator['approximate_normalized_bbox']
        if (not isinstance(box, list) or len(box) != 4 or
                any(type(n) not in {int, float} or not 0 <= n <= 1 for n in box) or
                not (box[0] < box[2] and box[1] < box[3])):
            raise ValueError('Invalid reviewer locator box')
        if span['runtime_release_approved'] is not False:
            raise ValueError('Source inspection does not approve runtime release')
    return index


def load_6096_selected(original_path: Path, *, data_dir: Path | None = None
                       ) -> tuple[Source, list[Chunk]]:
    """Return a distinct source and eight directly bound chunks, or fail closed.

    data_dir is a caller-owned local test/integration seam, never a model tool
    argument. Its files must match the application-owned immutable pins.
    """
    data_dir = DATA if data_dir is None else Path(data_dir)
    index = _index(data_dir / '6096-selected-index.json')
    original_path = Path(original_path)
    original = original_path.read_bytes()
    if len(original) != index['original_bytes'] or digest(original) != ORIGINAL_SHA256:
        raise ValueError('Original changed from approved version')
    raw = (data_dir / '6096-selected-reading.txt').read_bytes()
    if digest(raw) != READING_SHA256:
        raise ValueError('Selected reading copy changed from approved version')
    text = raw.decode('utf-8')
    source = Source(
        SOURCE_ID, 'Ordinance 6096 — partial selected manual reading copy',
        index['source_url'], index['issuer'], 'adopted_proposal', original_path,
        ORIGINAL_SHA256, text, READING_SHA256,
        index['transcription_method'] + ' ' + index['verification_limit'] +
        ' Selected index SHA256: ' + INDEX_SHA256 + '; verification packet SHA256: ' + PACKET_SHA256,
        authority=None, state='MO', county='jackson-county-mo',
        election_date='2026-11-03', effective_from=None,
        retrieved_date='2026-10-11', quality='verified_reading_copy')
    chunks = []
    for span in index['passages']:
        value = text[span['start']:span['end']]
        if not value or digest(value.encode('utf-8')) != span['text_sha256']:
            raise ValueError('Selected passage is not the approved exact parent span')
        chunks.append(Chunk(
            'combat:' + SOURCE_ID + ':' + span['id'], SOURCE_ID, 'combat',
            span['start'], span['end'], value, span['text_sha256'],
            span['section_or_locator'], page=span['pdf_page_1_based'],
            applicability='countywide'))
    return source, chunks


def selected_passage_binding(chunk: Chunk, *, data_dir: Path | None = None) -> dict:
    """Expose pinned inspection provenance without asserting release approval.

    Existing Registry.read already supplies original/extraction/span hashes and
    page/section/Unicode offsets. Core may expose this extra reviewer metadata
    through its exact-source inspection path if desired.
    """
    index = _index((DATA if data_dir is None else Path(data_dir)) / '6096-selected-index.json')
    for span in index['passages']:
        if chunk.id == 'combat:' + SOURCE_ID + ':' + span['id']:
            if (chunk.source_id != SOURCE_ID or chunk.contest_id != 'combat' or
                    chunk.start != span['start'] or chunk.end != span['end'] or
                    chunk.page != span['pdf_page_1_based'] or
                    chunk.section != span['section_or_locator'] or
                    chunk.sha256 != span['text_sha256'] or
                    digest(chunk.text.encode('utf-8')) != span['text_sha256'] or
                    chunk.applicability != 'countywide' or chunk.location is not None or
                    chunk.column is not None):
                raise ValueError('Chunk differs from approved selected binding')
            return {**span, 'original_sha256': ORIGINAL_SHA256,
                    'reading_sha256': READING_SHA256, 'index_sha256': INDEX_SHA256,
                    'verification_packet_sha256': PACKET_SHA256,
                    'offset_basis': index['offset_basis'], 'partial': True}
    raise ValueError('Not an approved selected chunk')
