"""Exact source reading aids; no civic interpretation or provider call."""
import argparse
import hashlib
import json
from pathlib import Path
import re
INVENTORY_PIN = '0eda572a493274e25e845a1276b8ec28c3321dc40a8c2f13b7d761ad95645773'
ANCHORS = {'amendment-3': [('conditions', 'Allow abortions for rape and incest (under twelve-', 'weeks’ gestation), emergencies, and fetal anomalies;')], 'amendment-6': [('condition', 'prohibit the legislature from changing or repealing', 'without approval from at least 80% of both chambers;')], 'amendment-7': [('full_condition', 'Shall the Missouri Constitution', 'generates sufficient revenue to replace them?')], 'amendment-8': [('full_condition', 'Shall the Missouri Constitution', 'justice?')], 'proposition-a': [('full_question', 'Do the people', 'counties intact?')], 'county-question-1': [('rate_and_duration', 'at the rate of one-quarter', 'a period of ten years'), ('separate_fund', 'The proceeds of this tax', 'funds.')], 'blue-springs-question': [('rate_and_condition', 'Shall the City of Blue Springs', 'shall also be reduced or raised by the same action?')], 'independence-bond-1': [('amount_and_purpose', 'Shall the City of Independence', 'the 1827 Log Courthouse?')], 'lees-summit-question': [('full_question', 'Should the municipality', 'services?')], 'sni-valley-question': [('full_condition', 'Shall Sni Valley', 'tax?')]}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def compile_guides(raw):
    if sha(raw) != INVENTORY_PIN:
        raise ValueError('inventory_version_unadmitted')
    data = json.loads(raw)
    guides = []
    for cid, parts in ANCHORS.items():
        contest = next((c for c in data['contests'] if c['id'] == cid))
        occurrence = next((o for o in contest['occurrences'] if o['source_id'] == 'jceb'))
        normal = re.sub('\\s+', ' ', occurrence['wording'])
        ranges = []
        for role, first, last in parts:
            start = normal.index(first)
            end = normal.index(last, start) + len(last)
            quote = normal[start:end]
            ranges.append({'role': role, 'start': start, 'end': end, 'text': quote, 'sha256': sha(quote.encode())})
        guides.append({'contest_id': cid, 'source_id': 'jceb', 'wording_sha256': occurrence['wording_sha256'], 'normalized_wording_sha256': sha(normal.encode()), 'ranges': ranges})
    return {'version': 1, 'inventory_sha256': INVENTORY_PIN, 'purpose': 'Exact original reading aids, not generated explanations or Yes/No interpretations', 'civic_interpretations_admitted': False, 'guides': guides}
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = (json.dumps(compile_guides(args.inventory.read_bytes()), ensure_ascii=False, indent=2) + '\n').encode()
    args.output.write_bytes(raw)
    print(json.dumps({'sha256': sha(raw), 'bytes': len(raw)}))
