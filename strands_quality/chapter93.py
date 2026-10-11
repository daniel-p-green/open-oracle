"""Full inspected 2018 County Code Chapter 93 snapshot; currency unadjudicated."""
from pathlib import Path
from .research_corpus import Source, Chunk, digest

SOURCE_ID = 'county-code-ch93-2018'
ORIGINAL_SHA256 = 'b437d1e21fdd3fa83e0403fda45e9d781a8e891e9d9d5601a2041cb4bcd83596'
TEXT_SHA256 = '575830242331f0ac78797ddc53b862cdc2fbc95654cb06d9c69cd8179bb9cc2d'
URL = 'https://www.jacksongov.org/files/sharedassets/public/v/1/our-county/county-code/93-anti-crime-sales-tax-new_201812201058143143.pdf'

def load_chapter93(archive: Path):
    archive = Path(archive)
    original = archive / 'chapter-93.pdf'
    raw = original.read_bytes()
    reading = (archive / 'chapter-93.txt').read_bytes()
    if len(raw) != 48655 or digest(raw) != ORIGINAL_SHA256 or digest(reading) != TEXT_SHA256:
        raise ValueError('Chapter 93 original or extraction changed')
    text = reading.decode('utf-8')
    pages = text.split('\f')
    if len(pages) != 4 or pages[-1] != '':
        raise ValueError('Expected three complete Chapter 93 pages')
    source = Source(SOURCE_ID, 'Jackson County Code Chapter 93 — printed 2018 snapshot; currency unverified',
                    URL, 'Jackson County Legislature / official County Code site', 'historical_law',
                    original, ORIGINAL_SHA256, text, TEXT_SHA256,
                    'Full native PDF extraction; all three page images inspected. Printed December 11, 2018; '
                    'includes later effective-date annotations. Current site linked it October 11, 2026. '
                    'Not an exhaustive subsequent-amendment reconciliation; no current-law or public-release approval.',
                    retrieved_date='2026-10-11', quality='verified_reading_copy')
    chunks, offset = [], 0
    for page, content in enumerate(pages[:-1], 1):
        chunks.append(Chunk('combat:'+SOURCE_ID+':page-'+str(page), SOURCE_ID, 'combat',
                            offset, offset+len(content), content, digest(content.encode('utf-8')),
                            'Chapter 93 printed snapshot; full three-page context required', page=page))
        offset += len(content)+1
    return source, chunks
