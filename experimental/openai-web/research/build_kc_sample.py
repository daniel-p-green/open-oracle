"""Compile the visually checked W1-P7 public sample, never a resident assignment.

Uses the retained original only. Every emitted field has a reproducible PDF
column/text span; no provider, network, candidate identity join or artwork copy.
"""
import argparse
import json
from pathlib import Path
import re

from build_inventory import CANDIDATES, JUDGES, anchor_pattern, extract, sha, span

PIN = 'd33d41b4c377e7d9d1bd63af0c2f1053bc4b63f608eb3167200a8385e576e0fc'
IDS = ['us-house-5', 'auditor', 'state-house-24', 'county-executive',
       'county-at-large-1', 'county-at-large-2', 'county-at-large-3', 'county-district-1']
HEADINGS = {
    'us-house-5': r'U\.S\. REPRESENTATIVE\s+DISTRICT 5',
    'auditor': r'STATE AUDITOR\s+OF MISSOURI',
    'state-house-24': r'STATE REPRESENTATIVE\s+DISTRICT 24',
    'county-executive': r'COUNTY EXECUTIVE\s+JACKSON COUNTY',
    **{'county-at-large-' + str(n): r'AT-LARGE COUNTY LEGISLATOR\s+DISTRICT ' + str(n) + r'\s+JACKSON COUNTY' for n in [1, 2, 3]},
    'county-district-1': r'COUNTY LEGISLATOR\s+DISTRICT 1',
}


def candidate_region(reading, cid, people):
    """Account for the entire printed roster region, including unknown rows."""
    heading = span(reading, HEADINGS[cid])
    instruction = re.match(r'\s*(Vote for One)\s*', reading[heading['end']:])
    if not instruction:
        raise ValueError('sample_instruction:' + cid)
    start = heading['end'] + instruction.end()
    finish = reading.index('Write-in', start)
    region = reading[start:finish]
    rows = []
    for name, party in (entry.split('|') for entry in people.split(';')):
        pattern = anchor_pattern(name) + r'\s+' + party + r'\b'
        if name == 'RANDALL (RANDY) LANGKRAEHR':
            pattern = r'RANDALL \(RANDY\)\s+LIB\s+LANGKRAEHR'
        found = span(region, pattern)
        original_name = ' '.join(re.sub(r'\b' + party + r'\b', '', found['text']).split())
        rows.append({'printed_name': original_name, 'printed_party': party,
                     'field_span': {**found, 'start': start + found['start'], 'end': start + found['end']},
                     'background_evidence': 'not_admitted', 'person_identity': 'not_merged'})
    rows.sort(key=lambda row: row['field_span']['start'])
    cursor = start
    for i, row in enumerate(rows):
        found = row['field_span']
        if found['start'] < cursor or reading[cursor:found['start']].strip():
            raise ValueError('sample_extra_or_overlapping_row:' + cid)
        row['ballot_order'] = i + 1
        row['entry_id'] = 'kc-sample-' + cid + '-' + str(found['start'])
        cursor = found['end']
    if reading[cursor:finish].strip():
        raise ValueError('sample_unconsumed_roster:' + cid)
    ins_start = heading['end'] + instruction.start(1)
    ins_end = heading['end'] + instruction.end(1)
    return rows, {'start': ins_start, 'end': ins_end, 'text': reading[ins_start:ins_end]}


def compile_sample(path, reviewed_at):
    if sha(path.read_bytes()) != PIN:
        raise ValueError('sample_version_unadmitted')
    columns = {(page, col): extract(path, '-f', str(page), '-l', str(page),
               '-x', str(x), '-y', '0', '-W', str(width), '-H', '1044')
               for page, specs in [(1, [(1, 50, 183), (2, 234, 180), (3, 415, 180)]),
                                   (2, [(1, 50, 273), (2, 324, 274)])]
               for col, x, width in specs}
    def locator(page, col):
        return {'source_id': 'kc-sample', 'page': page, 'column': col,
                'reading_sha256': sha(columns[page, col].encode())}
    contests = []
    consumed = {key: set() for key in columns}
    definitions = {row[0]: row for row in CANDIDATES}
    for cid in IDS:
        _, label, _, people = definitions[cid]
        col = 2 if cid == 'county-district-1' else 1
        reading = columns[1, col]
        rows, instruction = candidate_region(reading, cid, people)
        consumed[1, col].add(instruction['start'])
        occ = {**locator(1, col), 'candidate_rows': rows, 'source_statuses': [],
               'instruction': {'text': instruction['text'], 'page': 1,
                               'reading_sha256': sha(reading.encode()),
                               'span': instruction},
               'write_in': {'printed': True, 'named_candidate': False, 'eligible_write_in_list': 'not_verified'}}
        contests.append({'id': cid, 'label': label, 'kind': 'candidate_election', 'occurrences': [occ]})
    for index, (cid, label, name, _) in enumerate(JUDGES):
        col = 2 if index < 7 else 3
        reading = columns[1, col]
        question = span(reading, r'Shall Judge\s+' + anchor_pattern(name) + r'[^?]+\?')
        consumed[1, col].add(question['start'])
        contests.append({'id': 'retention-' + cid, 'label': label, 'kind': 'judicial_retention',
                         'occurrences': [{**locator(1, col), 'printed_name': name,
                           'wording': question['text'], 'wording_sha256': sha(question['text'].encode()),
                           'wording_span': question, 'choices': ['YES', 'NO'],
                           'background_evidence': 'not_admitted', 'person_identity': 'not_merged'}]})
    for cid, label, col, heading in [
        *[('amendment-' + str(n), 'Constitutional Amendment No. ' + str(n), 1,
           'CONSTITUTIONAL AMENDMENT NO. ' + str(n)) for n in [3, 6, 7, 8]],
        ('proposition-a', 'Proposition A', 2, 'PROPOSITION A'),
        ('county-question-1', 'Jackson County · Question 1', 2, 'QUESTION # 1')]:
        reading = columns[2, col]
        marker = reading.index(heading) + len(heading)
        start = re.search(r'\b(?:Shall|Do the people)\b', reading[marker:]).start() + marker
        finish = re.search(r'\bYes\s+No\b', reading[start:]).start() + start
        quote = reading[start:finish].rstrip()
        consumed[2, col].add(start)
        contests.append({'id': cid, 'label': label, 'kind': 'measure', 'occurrences': [
            {**locator(2, col), 'wording': quote, 'wording_sha256': sha(quote.encode()),
             'wording_span': {'start': start, 'end': start + len(quote), 'text': quote}, 'choices': ['YES', 'NO']}]})
    for key, reading in columns.items():
        anchors = [m.start() for m in re.finditer(r'\b(?:Vote for \w+|Shall|Should|Do the people)\b', reading)]
        if len(anchors) != len(consumed[key]) or set(anchors) != consumed[key]:
            raise ValueError('sample_unconsumed_contest_anchor:' + str(key))
    if len(contests) != 25 or sum(len(c['occurrences'][0].get('candidate_rows', [])) for c in contests) != 15:
        raise ValueError('sample_coverage')
    return {'schema': 'openoracle-public-sample/v1', 'election_date': '2026-11-03',
            'sample_variant': 'W1-P7', 'reviewed_utc': reviewed_at,
            'scope': {'personal_membership': False, 'county_inventory_complete': False,
                      'current_certification_verified': False, 'human_acceptance': 'pending'},
            'source': {'publisher': 'Kansas City Election Board',
                       'url': 'https://kceb.org/ballots/01-00006-01-NON.pdf',
                       'jurisdiction': 'Kansas City within Jackson County · public sample W1-P7',
                       'original_sha256': PIN, 'bytes': path.stat().st_size, 'pages': 2,
                       'document_date': 'not stated; election date 2026-11-03',
                       'retrieved_utc': '2026-10-24T04:32:39.042536Z',
                       'rights': 'Factual roster and exact wording for local review. No ballot artwork or blanket reuse license claimed.'},
            'contests': contests}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--reviewed-at', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = (json.dumps(compile_sample(args.source, args.reviewed_at), ensure_ascii=False, indent=2) + '\n').encode()
    args.output.write_bytes(raw)
    print(json.dumps({'sha256': sha(raw), 'bytes': len(raw), 'printed_contests': 25, 'personal_membership': False}))
