"""Finite Amendment 7 explanations bound to the ballot and complete legal clauses."""
from __future__ import annotations

import hashlib
import re

CONTEST = 'amendment-7'
PDF_HASH = 'cd9468cfff8e54020969f93c59fc6f42113a27b0cf35fe12e9e1e99da8232261'
READING_HASH = 'cfe4a4318ead0b3fb4242f6165b69f062379e98190dba4d50813467f6c2d3ad3'
URL = 'https://www.senate.mo.gov/26info/pdf-bill/tat/SJR95.pdf'
FAIR_PDF_HASH = '4418cb67c6219ea57ae7169beb79f3355befa165d7098bbe6d538934e66d5b9e'
FAIR_READING_HASH = '6a1e792f943223d5c12ec5cb8db8494f589a7d289e5f7704ed909a8b472ad608'
FAIR_PASSAGE_HASH = 'ca592a7d1113e052645800b01bf818e2768a98572720b606de026e8fd5b84c80'
FAIR_ID = CONTEST + ':sos-fair-language'
FAIR_URL = 'https://jcebmo.org/wp-content/uploads/Fair-Ballot-Language-08.06.2026.pdf'
BALLOT = ('Shall the Missouri Constitution be amended to establish a permanent public endowment fund '
          'to support state government instead of taxing Missouri residents, prohibit the General Assembly '
          'from appropriating or diverting the fund, and eliminate state-imposed taxes once the fund '
          'generates sufficient revenue to replace them? State and local governmental entities estimate no costs or savings. YES NO')
CLAUSES = (
    ('investment', '2. (1)', '(2) No moneys', '3d6f2c29315d21b6eeea61069cd760c6933c0072cee4e2eefdcba838b7bccc7e'),
    ('conditions', '(2) No moneys', '(3) Moneys', 'e7b78a14770bd092807fcee20f8259c4b30fc69c8a812b8253aee0e7e70519ba'),
    ('limit', '(4) The amount', None, '24f60cfed16df85fcf1e30aec02d65930ba56d0f8822804c75fea9e6b4ae7b68'),
)
KEYS = ('decision', 'conditions', 'no', 'investment', 'limit')
STATEMENTS = (
    ('What Yes and No mean', 'YES would create a fund that invests money to help pay for Missouri’s government. It could replace state taxes later, if the proposal’s conditions are met. NO would reject this proposed constitutional change and would not approve creating the fund through this proposal.'),
    ('Do my taxes go away if Yes wins?', 'No immediate tax cut. The proposal sets conditions before money could be used from the fund. Its investment earnings, after costs, must be enough to replace the money from the listed state taxes. The earnings must be from the state’s last budget year. The state treasurer must report that these conditions are met. Missouri’s lawmakers must approve that report. The proposal calls their formal approval a concurrent resolution. They must approve it within the first 60 calendar days of their next regular lawmaking session. These documents do not tell me what you personally pay or might save.'),
    ('What happens if No wins?', 'NO rejects this proposed change to Missouri’s Constitution. It does not approve creating the investment fund through this proposal.'),
    ('How the money would be invested', 'The fund would follow the S&P 500 stock index, or a similar replacement. In other words, the money would be invested in the stock market. This passage does not predict how much those investments would earn.'),
    ('The spending limit', 'At most 3% of the fund’s average value over the previous five years of the state’s budget could be used in a year. This is a limit on spending from the fund, not a new 3% tax.'),
)
OVERVIEW = 'Amendment 7 proposes a state investment fund. YES would create the fund and its rules; NO would reject this proposal. It does not eliminate taxes immediately.'
GAP = 'The retained proposal gives conditions for potentially replacing state taxes, not a guaranteed tax-end date, investment return, or personal savings amount. I cannot support that prediction from these documents.'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def original_pdf(corpus):
    try:
        raw = (corpus.pack / 'raw/amendment-7.pdf').read_bytes()
        return raw if digest(raw) == PDF_HASH else None
    except OSError:
        return None



def fair_original(corpus):
    try:
        raw = (corpus.pack / 'jceb/2026-11-03-fair-ballot-language.pdf').read_bytes()
        reading = (corpus.pack / 'jceb/2026-11-03-fair-ballot-language.md').read_bytes()
        return raw if digest(raw) == FAIR_PDF_HASH and digest(reading) == FAIR_READING_HASH else None
    except OSError:
        return None


def fair_source(corpus):
    if not fair_original(corpus):
        return None
    reading = (corpus.pack / 'jceb/2026-11-03-fair-ballot-language.md').read_text()
    begin = reading.index('Constitutional Amendment No. 7')
    end = reading.index('Constitutional Amendment No. 8', begin)
    # The complete paragraph crosses columns. Only reading-copy layout changes;
    # printed spelling/words/punctuation remain, and the original PDF controls.
    text = re.sub(r'### Column 2\s*', '', reading[begin:end])
    text = ' '.join(re.sub(r'-\s*\n\s*', '', text).split())
    if digest(text.encode()) != FAIR_PASSAGE_HASH:
        return None
    return {'id': FAIR_ID, 'contest_id': CONTEST, 'text': text,
            'source_id': 'sos-fair-language', 'url': FAIR_URL,
            'title': 'Official statewide fair ballot language — Amendment 7',
            'issuer': 'Missouri Secretary of State',
            'source_category': 'Official statewide fair ballot language',
            'source_role': 'official_ballot_explanation', 'election_date': '2026-11-03',
            'retrieved_date': '2026-10-09', 'snapshot_date': '2026-10-10',
            'version': 'Retained November 3, 2026 statewide fair language; JCEB-hosted August 6 file',
            'page': 1, 'column': None, 'start_offset': begin,
            'sha256': FAIR_PDF_HASH, 'reading_copy_sha256': FAIR_READING_HASH,
            'passage_sha256': FAIR_PASSAGE_HASH, 'status': 'current_snapshot',
            'extraction': 'Complete Amendment 7 section across both columns, visually checked. Reading-copy column marker removed, printed line-end hyphens joined and whitespace joined. SOS is issuer; JCEB is host, not personal ballot assignment. Original PDF controls.',
            'original_route': '/api/prepared-source/amendment-7-fair.pdf#page=1'}


def add_to(corpus):
    """Import reviewed public clauses only; missing/changed originals cannot enable a card."""
    corpus.amendment7_ready = False
    try:
        raw = (corpus.pack / 'markdown/amendment-7.md').read_bytes()
        if not original_pdf(corpus) or digest(raw) != READING_HASH:
            return
        page = raw.decode().split('## Original PDF page 2\n')[1].split('## Original PDF page 3')[0]
        page = ' '.join(re.sub(r'^\d+\s+', '', line.strip()) for line in page.splitlines()
                        if line.strip() and not line.strip().startswith('SS SCS SJR'))
        fair = fair_source(corpus)
        if fair is None:
            return
        entries = [fair]
        for key, start, end, expected in CLAUSES:
            begin = page.index(start)
            text = page[begin:page.index(end, begin) if end else len(page)].strip()
            if digest(text.encode()) != expected:
                return
            entries.append({
                'id': CONTEST + ':proposal-' + key, 'contest_id': CONTEST,
                'text': text, 'source_id': 'amendment-7-proposal', 'url': URL,
                'title': 'Amendment 7 full proposal — Article IV §15(a)', 'issuer': 'Missouri General Assembly',
                'source_category': 'Official proposed legal text', 'source_role': 'proposed_law',
                'election_date': '2026-11-03', 'retrieved_date': '2026-10-09',
                'snapshot_date': corpus.evidence[CONTEST + ':jceb-sample']['snapshot_date'],
                'version': 'SS SCS SJR 95, 4511S.20T — truly agreed to and finally passed; proposed amendment',
                'page': 2, 'column': None, 'start_offset': begin, 'sha256': PDF_HASH,
                'reading_copy_sha256': READING_HASH, 'passage_sha256': expected,
                'normalized_page_sha256': digest(page.encode()), 'status': 'current_snapshot',
                'extraction': 'Embedded PDF reading copy; printed line numbers removed and line breaks joined. Complete clause; original PDF controls.',
                'original_route': '/api/prepared-source/amendment-7.pdf#page=2',
            })
        marker = re.search(r'CONSTITUTIONAL\s+7\s+AMENDMENT NO\.', corpus.kceb)
        start = corpus.kceb.index('Shall the Missouri Constitution', marker.end())
        end = start + re.search(r'\bYES\s+NO\b', corpus.kceb[start:]).end()
        text = corpus.kceb[start:end]
        if ' '.join(text.split()) != BALLOT:
            return
        corpus._add(corpus.contests[CONTEST], text, 'kceb-sample', 7)
        for entry in entries:
            corpus.evidence[entry['id']] = entry
        corpus.amendment7_ready = True
    except (OSError, ValueError, IndexError, AttributeError):
        return


def focus(question):
    q = question.lower().replace('’', "'")
    if re.search(r'still.*(?:understand|confused)|one (?:thing|step).*time|break.*down', q):
        return None
    if re.search(r'\bno\b|doesn.t pass|not pass|reject', q):
        return 'no'
    if re.search(r'3\s*%|three percent|spend|limit|cap\b', q):
        return 'limit'
    if re.search(r'invest|s&p|stock|money go', q):
        return 'investment'
    if re.search(r'\byes\b|tax(?:es)?.*(?:go away|end|eliminat|disappear)|immediat|conditions', q):
        return 'conditions'
    return None


def unsupported(question):
    return bool(re.search(r'\bwhen\b|what (?:year|date)|how (?:soon|much)|sav(?:e|ings)|guarantee|will (?:it|this|the fund) work|money come', question, re.I))


def card(question, contest, evidence, *, focused=False):
    from .corpus import ELECTION, JCEB_HASH, KCEB_HASH
    from .cards import CONFUSION
    if contest['id'] != CONTEST:
        return None
    by_id = {e['id']: e for e in evidence}
    ballot = next((e for e in evidence if e['source_id'] in ('kceb-sample', 'jceb-sample')), None)
    if not ballot or ballot['sha256'] != {'kceb-sample': KCEB_HASH, 'jceb-sample': JCEB_HASH}[ballot['source_id']]:
        return None
    # JCEB retains a heading before the same complete question and fiscal wording.
    if ' '.join(ballot['text'][ballot['text'].find('Shall the Missouri Constitution'):].split()) != BALLOT:
        return None
    for key, _, _, expected in CLAUSES:
        source = by_id.get(CONTEST + ':proposal-' + key)
        if (not source or source.get('sha256') != PDF_HASH or source.get('reading_copy_sha256') != READING_HASH
                or source.get('source_role') != 'proposed_law' or digest(source['text'].encode()) != expected):
            return None
    fair = by_id.get(FAIR_ID)
    if (not fair or fair.get('sha256') != FAIR_PDF_HASH or fair.get('reading_copy_sha256') != FAIR_READING_HASH
            or fair.get('source_role') != 'official_ballot_explanation' or digest(fair['text'].encode()) != FAIR_PASSAGE_HASH):
        return None
    if len(by_id) != 5 or any(e.get('status') != 'current_snapshot' or e.get('election_date') != ELECTION for e in evidence):
        return None
    facets = []
    for index, (title, statement) in enumerate(STATEMENTS):
        source = fair if index == 2 else ballot if index == 0 else by_id[CONTEST + ':proposal-' + KEYS[index]]
        if index == 2:
            start = source['text'].index('A “no” vote')
            end = source['text'].index(' If passed,', start)
        elif index == 0:
            match = re.search(r'Shall the Missouri Constitution.*?replace them\?', source['text'], re.S)
            start, end = match.span()
        else:
            start, end = 0, len(source['text'])
        facets.append({'title': title, 'statement': statement, 'evidence_id': source['id'],
                       'quote': source['text'][start:end], 'start': start, 'end': end})
    keys = list(KEYS)
    if focused and focus(question):
        key = focus(question)
        facets = [facets[KEYS.index(key)]]
        keys = [key]
    return {'type': 'measure_explanation', 'id': 'amendment-7-explanation-v1', 'contest_id': CONTEST,
            'election_date': ELECTION, 'jurisdiction': 'Missouri statewide',
            'evidence_id': ballot['id'], 'source_sha256': ballot['sha256'], 'source_url': ballot['url'],
            'presentation': 'step_by_step' if CONFUSION.search(question) else 'choice_focus' if focus(question) else 'overview',
            'title': 'What Amendment 7 would change', 'facet_keys': keys, 'facets': facets,
            'limit': 'Proposed amendment, not current law. This is a retained sample, not a confirmed personal ballot. These sources do not predict your savings or a date when taxes would end. No voting recommendation.',
            'method': 'Each part links to the official ballot, the official fair ballot explanation, or a full paragraph of the proposal. The separate review result shows whether the AI check ran.'}


def answer(question):
    key = focus(question)
    return STATEMENTS[KEYS.index(key)][1] if key else OVERVIEW


def validate(response, corpus):
    from .claim_bindings import fingerprint
    evidence = response['evidence']
    actual = response['card']
    presentation = actual.get('presentation')
    question = "I still don't understand" if presentation == 'step_by_step' else 'What does No mean?' if presentation == 'choice_focus' else 'Explain Amendment 7'
    focused = len(actual.get('facet_keys', [])) == 1
    if focused:
        question = {'conditions': 'What does Yes mean?', 'no': 'What does No mean?', 'investment': 'How is the money invested?', 'limit': 'What is the spending limit?'}.get(actual['facet_keys'][0], '')
    expected = card(question, response['contest'], evidence, focused=focused)
    if not corpus.amendment7_ready or not original_pdf(corpus) or not fair_original(corpus) or actual != expected:
        return {'status': 'unsupported', 'reason': 'amendment7_card_or_source_unbound', 'claims': []}
    if any(corpus.evidence_fingerprints.get(e['id']) != fingerprint(e) for e in evidence):
        return {'status': 'unsupported', 'reason': 'retained_source_binding_failed', 'claims': []}
    if focused and response['answer'] != actual['facets'][0]['statement']:
        return {'status': 'unsupported', 'reason': 'focused_answer_facet_mismatch', 'claims': []}
    if response['answer'] not in (OVERVIEW, *(statement for _, statement in STATEMENTS)):
        return {'status': 'unsupported', 'reason': 'unregistered_amendment7_explanation', 'claims': []}
    return {'status': 'supported', 'method': 'finite_source_span_contracts',
            'claims': [{'status': 'supported', 'evidence_id': f['evidence_id'], 'start': f['start'], 'end': f['end'], 'quote': f['quote']} for f in actual['facets']],
            'prose_entailment_claimed': False, 'calibrated_probability_used': False}
