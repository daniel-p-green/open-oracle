"""Compile bounded official office excerpts, never candidate performance claims."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from build_evidence import PlainText
SOURCES = {'mo-auditor': ('https://auditor.mo.gov/aboutus', '1d4af9d6efe0a2e50917e906115391611e251ea36947a4e24b25f008d0a79cdd', "Missouri State Auditor's Office"), 'mo-legislature': ('https://documents.house.mo.gov/billtracking/info/howbill.htm', '9bbca6772329f7da4d3a0cf663c8395ad8de53b8847b4c17486864be185517ec', 'Missouri House of Representatives')}
PASSAGES = [('auditor-election', 'mo-auditor', 'The Missouri State Auditor is elected', 'State Auditor and Staff'), ('auditor-role', 'mo-auditor', 'The office works to ensure', 'Responsibilities'), ('assembly-role', 'mo-legislature', 'Legislative power is vested', 'The General Assembly'), ('house-term', 'mo-legislature', 'The House of Representatives consists', 'The General Assembly'), ('senate-term', 'mo-legislature', 'The Senate consists', 'The General Assembly')]

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def compile_offices(directory):
    directory = Path(directory)
    manifest = json.loads((directory / 'manifest.json').read_text())
    sources = {}
    readings = {}
    passages = {}
    for sid, (url, pin, publisher) in SOURCES.items():
        row = next((r for r in manifest if r['id'] == sid))
        raw = (directory / row['file']).read_bytes()
        if row['url'] != url or row['final_url'] != url or row['sha256'] != pin or (sha(raw) != pin):
            raise ValueError('office_source_unadmitted')
        parser = PlainText()
        parser.feed(raw.decode('utf-8'))
        reading = '\n'.join(parser.parts) + '\n'
        readings[sid] = reading
        sources[sid] = {'source_class': 'official_office_explanation', 'publisher': publisher, 'url': url, 'retrieved_utc': row['retrieved_utc'], 'document_date': None, 'last_modified_header': row['last_modified'], 'original_sha256': pin, 'original_bytes': len(raw), 'reading_sha256': sha(reading.encode()), 'extraction': 'HTMLParser text nodes; scripts/styles/templates omitted; excerpts normalize whitespace only', 'rights': 'Bounded factual excerpts for local source review; no blanket state-content reuse license claimed.'}
    for pid, sid, marker, locator in PASSAGES:
        reading = readings[sid]
        if reading.count(marker) != 1:
            raise ValueError('office_marker_ambiguous')
        start = reading.index(marker)
        end = reading.index('.', start) + 1
        original = reading[start:end]
        text = re.sub('\\s+', ' ', original).strip()
        passages[pid] = {'id': pid, 'source_id': sid, 'role': 'institutional_office_description', 'locator': locator, 'reading_span': {'start': start, 'end': end, 'text': original}, 'text': text, 'sha256': sha(text.encode())}
    return {'schema': 'openoracle-office-context/v1', 'sources': sources, 'passages': passages, 'offices': {'mo-auditor': {'title': 'Missouri State Auditor', 'passage_ids': ['auditor-election', 'auditor-role'], 'missing_fields': ['term_not_in_admitted_excerpt']}, 'mo-house': {'title': 'Missouri House of Representatives', 'passage_ids': ['assembly-role', 'house-term'], 'missing_fields': []}, 'mo-senate': {'title': 'Missouri Senate', 'passage_ids': ['assembly-role', 'senate-term'], 'missing_fields': []}}, 'limits': {'candidate_performance': False, 'personal_membership': False, 'human_acceptance': 'pending', 'original_language': 'en', 'reviewed_civic_translations': []}}
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    value = compile_offices(args.inputs)
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    args.output.write_bytes(raw)
    print(json.dumps({'sha256': sha(raw), 'bytes': len(raw), 'office_families': list(value['offices']), 'candidate_claims_admitted': False}))
