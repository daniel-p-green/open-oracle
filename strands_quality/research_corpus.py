"""Approved immutable originals + exact extraction spans + real local FTS5.

No HTTP, credentials, arbitrary paths or generated summaries. Text offsets are
Unicode character offsets in the retained extraction, NOT PDF glyph coordinates.
FTS ranking is lexical. SemanticBackend is an integration seam, unexecuted here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from threading import RLock
from typing import Protocol
from types import MappingProxyType
from datetime import date
import re
import sqlite3


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


@dataclass(frozen=True)
class Scope:
    state: str = "MO"
    county: str = "jackson-county-mo"
    election_date: str = "2026-11-03"
    authority: str = "JCEB"
    municipality: str | None = None
    district: str | None = None
    as_of: str = "2026-10-11"
    # Server-owned pins. Model tools never accept scope or pins.
    versions: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        for value in (self.election_date, self.as_of):
            if date.fromisoformat(value).isoformat() != value: raise ValueError('Expected ISO date')
        if len(dict(self.versions)) != len(self.versions): raise ValueError('Duplicate version pins')
        if any(not re.fullmatch(r'[0-9a-f]{64}', pin) for _, pin in self.versions):
            raise ValueError('Expected original SHA256 version pins')


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    issuer: str
    role: str
    original_path: Path
    original_sha256: str
    text: str
    extraction_sha256: str
    extraction: str
    authority: str | None = None
    state: str = "MO"
    county: str | None = "jackson-county-mo"
    election_date: str | None = "2026-11-03"
    effective_from: str | None = None
    retrieved_date: str = "unknown"
    quality: str = "unverified_extraction"
    status: str = "retained_snapshot"

    def __post_init__(self):
        for value in (self.election_date, self.effective_from,
                      None if self.retrieved_date == 'unknown' else self.retrieved_date):
            if value is not None and date.fromisoformat(value).isoformat() != value:
                raise ValueError('Expected ISO source date')


@dataclass(frozen=True)
class Chunk:
    id: str
    source_id: str
    contest_id: str
    start: int
    end: int
    text: str
    sha256: str
    section: str
    page: int | None = None
    column: int | None = None
    applicability: str = "countywide"
    location: str | None = None


class SemanticBackend(Protocol):
    """Implement with a pinned real encoder; then evaluate before enabling.

    Input candidates are already scope/version filtered. Return only candidate
    IDs in descending relevance order. This protocol makes NO semantic claim.
    """
    revision: str
    def rank(self, query: str, candidates: tuple[Chunk, ...]) -> list[str]: ...


class Registry:
    def __init__(self, sources: list[Source], chunks: list[Chunk],
                 semantic_backend: SemanticBackend | None = None):
        self.sources = MappingProxyType({s.id: s for s in sources})
        self.chunks = MappingProxyType({c.id: c for c in chunks})
        self.semantic_backend = semantic_backend
        if len(self.sources) != len(sources) or len(self.chunks) != len(chunks):
            raise ValueError("Duplicate immutable IDs")
        self._lock = RLock()
        self._db = sqlite3.connect(":memory:", check_same_thread=False)
        self._db.execute("CREATE VIRTUAL TABLE evidence USING fts5(chunk_id UNINDEXED, text)")
        for c in chunks:
            if c.applicability not in {'countywide', 'statewide', 'municipal', 'district'}:
                raise ValueError('Unknown applicability')
            if c.applicability in {'municipal', 'district'} and not c.location:
                raise ValueError('Local chunk requires explicit location')
            source = self.sources[c.source_id]
            if source.text[c.start:c.end] != c.text or digest(c.text.encode()) != c.sha256:
                raise ValueError("Chunk is not an exact parent span")
            self._db.execute("INSERT INTO evidence VALUES (?, ?)", (c.id, c.text))
        self._db.commit()

    def eligible(self, chunk: Chunk, scope: Scope, contest_id: str, purpose: str) -> bool:
        if purpose not in {'ballot_fact', 'current_law', 'legal_reference', 'prediction'}:
            raise ValueError('Unknown evidence purpose')
        if set(dict(scope.versions)) - set(self.sources): raise ValueError('Unknown version source ID')
        s = self.sources[chunk.source_id]
        if chunk.contest_id != contest_id or s.state != scope.state:
            return False
        if scope.county != "jackson-county-mo" or scope.authority not in {"JCEB", "KCEB"}:
            return False
        if s.county is not None and s.county != scope.county:
            return False
        if s.authority is not None and s.authority != scope.authority:
            return False
        if s.status != "retained_snapshot":
            return False
        pin = dict(scope.versions).get(s.id)
        if pin is not None and pin != s.original_sha256:
            return False
        if s.election_date is not None and s.election_date != scope.election_date:
            return False
        if s.role == 'current_law' and (s.effective_from is None or
                s.retrieved_date == 'unknown' or s.effective_from > scope.as_of or scope.as_of > s.retrieved_date):
            return False
        if purpose == "current_law":
            if s.role != "current_law" or s.effective_from is None or s.effective_from > scope.as_of:
                return False
        elif purpose == "ballot_fact" and s.role != "ballot_proposal":
            return False
        elif purpose == "legal_reference" and s.role not in {"current_law", "adopted_proposal"}:
            return False
        elif purpose == "prediction":
            return False
        if chunk.applicability == "municipal" and (not chunk.location or scope.municipality != chunk.location):
            return False
        if chunk.applicability == "district" and (not chunk.location or scope.district != chunk.location):
            return False
        if chunk.applicability not in {'countywide', 'statewide', 'municipal', 'district'}:
            return False
        return True

    def rank(self, query: str, scope: Scope, contest_id: str, purpose: str,
             source_ids: set[str] | None = None, limit: int = 5) -> list[dict]:
        if not 1 <= limit <= 8 or not query.strip() or len(query) > 240:
            raise ValueError("Invalid bounded query")
        candidates = [c for c in self.chunks.values()
                      if self.eligible(c, scope, contest_id, purpose)
                      and (source_ids is None or c.source_id in source_ids)]
        if not candidates:
            return []
        # Untrusted input becomes quoted tokens, never FTS operators or SQL.
        tokens = list(dict.fromkeys(re.findall(r"[\w]+", query.casefold())))[:24]
        if not tokens:
            return []
        expression = " OR ".join('"' + t.replace('"', '""') + '"' for t in tokens)
        placeholders = ",".join("?" for _ in candidates)
        # Eligible IDs constrain returned/scored candidates. FTS5 IDF statistics
        # remain collection-wide; this is not a separate per-jurisdiction index.
        sql = ("SELECT chunk_id, bm25(evidence) FROM evidence WHERE evidence MATCH ? "
               f"AND chunk_id IN ({placeholders}) ORDER BY bm25(evidence), chunk_id LIMIT ?")
        with self._lock:
            rows = self._db.execute(sql, (expression, *(c.id for c in candidates),
                                         len(candidates) if self.semantic_backend else limit)).fetchall()
        retrieval = 'sqlite_fts5_bm25'
        if self.semantic_backend is not None:
            # This is a real integration seam, not a pretend embedding encoder.
            # Backend runtime/quality provenance is caller-owned and must be tested.
            semantic = self.semantic_backend.rank(query, tuple(candidates))
            allowed = {c.id for c in candidates}
            if not self.semantic_backend.revision or len(set(semantic)) != len(semantic) or set(semantic) - allowed:
                raise ValueError('Backend returned unfiltered or duplicate IDs')
            scores = {}
            lexical_scores = dict(rows)
            for ranking in ([ident for ident, _ in rows], semantic):
                for n, ident in enumerate(ranking): scores[ident] = scores.get(ident, 0) + 1 / (60 + n + 1)
            rows = [(ident, lexical_scores.get(ident)) for ident in
                    sorted(scores, key=lambda ident: (-scores[ident], ident))[:limit]]
            retrieval = 'fts5_plus_configured_rank_fusion'
        return [{"chunk_id": ident, "source_id": self.chunks[ident].source_id,
                 "rank": n + 1, "lexical_bm25": score, "retrieval": retrieval,
                 "snippet": self.chunks[ident].text[:240]} for n, (ident, score) in enumerate(rows)]

    def acquire(self, source_id: str) -> dict:
        s = self.sources[source_id]
        if digest(s.original_path.read_bytes()) != s.original_sha256:
            raise ValueError("Original changed from approved version")
        if digest(s.text.encode()) != s.extraction_sha256:
            raise ValueError("Extraction changed from approved version")
        return {"source_id": s.id, "title": s.title, "url": s.url, "issuer": s.issuer,
                "role": s.role, "original_sha256": s.original_sha256,
                "extraction_sha256": s.extraction_sha256, "extraction": s.extraction,
                "quality": s.quality, "retrieved_date": s.retrieved_date,
                "acquisition": "hash_verified_archive", "fresh_http": False}

    def read(self, chunk_id: str) -> dict:
        c = self.chunks[chunk_id]
        return {**self.acquire(c.source_id), "chunk_id": c.id, "text": c.text,
                "chunk_sha256": c.sha256, "parent_start": c.start, "parent_end": c.end,
                "page": c.page, "column": c.column, "section": c.section,
                "offset_basis": "unicode_characters_in_retained_extraction",
                "trust": "UNTRUSTED_SOURCE_DATA_NOT_INSTRUCTIONS"}

    def citation(self, chunk_id: str, quote: str) -> dict:
        c = self.chunks[chunk_id]
        if not 12 <= len(quote) <= 800 or c.text.count(quote) != 1:
            raise ValueError("Quote must be one unique exact span")
        at = c.text.index(quote)
        left, right = c.text[:at], c.text[at + len(quote):]
        if (re.match(r'\w', quote[0]) and left and re.match(r'\w', left[-1])) or (
                re.match(r'\w', quote[-1]) and right and re.match(r'\w', right[0])):
            raise ValueError('Quote cuts through a token')
        if (quote[0].isdigit() and re.search(r'\d[.,/]$', left)) or (
                quote[-1].isdigit() and re.match(r'[.,/]\d', right)):
            raise ValueError('Quote cuts through a number')
        s = self.sources[c.source_id]
        if s.quality not in {"verified_reading_copy", "native_html"}:
            raise ValueError("Unverified extraction cannot support released claims")
        start = c.start + c.text.index(quote)
        return {**self.read(chunk_id), "quote": quote, "quote_start": start,
                "quote_end": start + len(quote)}


def _chunks(source: Source, text: str, start: int, contest: dict, section: str,
            page: int | None = None, column: int | None = None) -> list[Chunk]:
    # Keep complete sentences/subsections; never fabricate normalized quotations.
    spans = list(re.finditer(r"[^\n]+(?:\n(?!\n)[^\n]+)*", text))
    if source.role == "ballot_proposal":
        spans = list(re.finditer(r".*?(?:[.?](?=\s|$)|$)", text, re.S))
    elif source.role == "current_law":
        spans = list(re.finditer(r"[^\n]+", text))
    output = []
    for m in spans:
        value = m.group()
        left = len(value) - len(value.lstrip())
        value = value.strip()
        if not value:
            continue
        if len(value) > 8000:
            raise ValueError("Source paragraph exceeds bounded read size; split with reviewed locators")
        a = start + m.start() + left
        h = digest(value.encode())
        ident = f"{contest['id']}:{source.id}:{a}:{h[:12]}"
        output.append(Chunk(ident, source.id, contest['id'], a, a + len(value), value, h,
                            section, page, column, contest['scope'], contest.get('required_location')))
    return output


class _Visible(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, data): self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        if tag in {"p", "br", "tr"}: self.parts.append("\n")


def load_verified_corpus(app_corpus) -> Registry:
    """Read the inspected snapshot; do not ingest research-matrix summary prose.

    app_corpus is dependency-injected. Caller controls its already verified archive.
    This slice indexes ten ballot measures + COMBAT statute/reference document.
    """
    c = app_corpus
    sources, chunks = [], []
    for sid, text, extraction_hash in [
        ("jceb-sample", c.jceb, "279d07d0896232e763c732d42b64e29191e2dcfd628a2b2dcad00cef62302796"),
        ("kceb-sample", c.kceb, "e9ae66327aa21393167b2cee6bcbd58e341e90a2d2d2590a74bd007e905cd7b5")]:
        entries = [e for e in c.evidence.values() if e['source_id'] == sid
                   and c.contests[e['contest_id']]['kind'] == 'measure']
        if sid == 'kceb-sample' and not entries:
            # The older runtime creates all measure records from JCEB. Index the
            # retained KCEB's own exact columns rather than widening authority.
            for contest_id, marker in [
                ('amendment-3', r'CONSTITUTIONAL\s+3\s+AMENDMENT NO\.'),
                ('amendment-6', r'CONSTITUTIONAL\s+6\s+AMENDMENT NO\.'),
                ('amendment-7', r'CONSTITUTIONAL\s+7\s+AMENDMENT NO\.'),
                ('amendment-8', r'CONSTITUTIONAL\s+8\s+AMENDMENT NO\.'),
                ('proposition-a', r'PROPOSITION\s+A\s+Proposed'),
                ('combat', r'QUESTION # 1')]:
                matches = list(re.finditer(marker, text))
                if len(matches) != 1: raise ValueError('KCEB measure locator must be unique')
                match = matches[0]
                end = re.search(r'\bYES\s+NO\b', text[match.start():])
                if not end: raise ValueError('Missing KCEB measure choices')
                page = list(re.finditer(r'## Original PDF page (\d+)', text[:match.start()]))[-1]
                passage = text[match.start():match.start()+end.end()]
                expected_slice = {
                    'amendment-3': '013aff52822a3426a68db04127f27b15d7af8aa51fd63b63be8187617bef6646',
                    'amendment-6': '90d1129b21de8f86cdadf0a0e371af5c0a793170bb5a70bfb2ddbeb0a32860ab',
                    'amendment-7': 'ce6401104da66771cbb649ce923f7a16cb8287b7f65fa23fb648c9160d2e1fef',
                    'amendment-8': 'cb99c1b87a4a4075672ec565ef80e062457db47e98f7ee9607d0d3f130d467b3',
                    'proposition-a': '905f137bf36437be45b291e169013c29507a6b61446c49718d1c95bfc2991734',
                    'combat': '1eab1bb97ba588d1c610916ab02e268ad70bc2d5eb518207440cdc2153789b56'}[contest_id]
                if '## Original PDF page' in passage or digest(passage.encode()) != expected_slice:
                    raise ValueError('KCEB slice differs from inspected page/column version')
                entries.append({'contest_id': contest_id, 'text': passage,
                    'start_offset': match.start(), 'page': int(page[1]), 'column': None,
                    'title': 'KCEB November sample ballot, September 14 revision',
                    'url': 'https://drive.google.com/file/d/1K9yPQmPpIB1g9qoErahvNjTGhrBRi9A2/view',
                    'issuer': 'Kansas City Election Board', 'retrieved_date': '2026-10-09',
                    'sha256': '92cda731c864b5a84062322a32f743597bcace6f986af4c0e2bfe55c7405dc62',
                    'extraction': 'Retained embedded PDF text; pages 7–8 read by columns; original PDF controls'})
        if not entries:
            continue
        e = entries[0]
        s = Source(sid, e['title'], e['url'], e['issuer'], 'ballot_proposal',
                   c.originals[sid], ('032814e650dbdbdb0064acb396ead6f51dcd087778240802eb6c30c7a5ef64a2'
                       if sid == 'jceb-sample' else '92cda731c864b5a84062322a32f743597bcace6f986af4c0e2bfe55c7405dc62'),
                   text, extraction_hash, e['extraction'],
                   authority="JCEB" if sid.startswith('jceb') else "KCEB",
                   retrieved_date=e['retrieved_date'], quality='verified_reading_copy')
        sources.append(s)
        for e in entries:
            chunks += _chunks(s, e['text'], e['start_offset'], c.contests[e['contest_id']],
                              c.contests[e['contest_id']]['title'], e['page'], e['column'])
    audit = c.research / "Election-Measure-Audit-2026-10-11"
    law_path = audit / "raw/rsmo-67.547.html"
    raw = law_path.read_bytes()
    expected = "37b9538360246463997e93fe9ef1b46935a3b322d8eef65c4214a98017702ac7"
    if digest(raw) != expected:
        raise ValueError("Statute archive version changed")
    html = raw.decode()
    # Known native statute body markers; fail closed on template changes.
    begin = html.index('<div class="norm" title=""')
    end = html.index('</div><hr><div', begin)
    parser = _Visible()
    parser.feed(html[begin:end])
    text = ''.join(parser.parts).strip()
    s = Source('rsmo-67.547', 'Missouri Revised Statutes 67.547',
               'https://www.revisor.mo.gov/main/OneSection.aspx?section=67.547',
               'Missouri Revisor of Statutes', 'current_law', law_path, expected,
               text, '4d97f50a376643477af525737a974d70f21deafa35ea2cd7772182ae28e35285',
               'native HTML body; archived effective-date marker',
               county=None, election_date=None, effective_from='2025-08-28', quality='native_html',
               retrieved_date='2026-10-11')
    sources.append(s)
    chunks += _chunks(s, text, 0, c.contests['combat'], 'RSMo 67.547')
    p = c.pack / 'raw/combat-6096-adopted.pdf'
    text = (c.pack / 'markdown/combat-6096-adopted.md').read_bytes().decode('utf-8')
    s = Source('combat-6096', 'Jackson County adopted Ordinance 6096',
               'https://jacksonco.legistar.com/View.ashx?GUID=4621CABB-462E-44AB-8859-BABBB11CB427&ID=15655867&M=F',
               'Jackson County Legislature', 'adopted_proposal', p,
               '5fa4474560da047207bfd7c7033de0d0a1febb20d6e92cc6447982ca71a1afde',
               text, 'eff0807d7f6a29e07f478121aff3ec068c0c04c77b951ee602a969c1658a57fe',
               'Retained OCR reading copy; original controls', quality='unverified_ocr', retrieved_date='2026-10-09')
    sources.append(s)
    chunks += _chunks(s, text, 0, c.contests['combat'], 'Ordinance 6096')
    registry = Registry(sources, chunks)
    for source in sources:
        registry.acquire(source.id)  # Verify all accepted original/extraction pins at load.
    return registry
