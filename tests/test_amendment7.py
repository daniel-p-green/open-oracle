"""Offline behavior and negative controls for the Amendment 7 demo contract."""
import copy
import hashlib
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.claim_bindings import validate_factual_display
from open_oracle.view_plan import validate_view_plan
from open_oracle.server import make_server


class Amendment7Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus()

    def test_pitch_questions_release_conditions_no_and_correct_authority(self):
        cases = [('Explain Amendment 7', 'measure_parts', 0),
                 ('If I vote Yes on Amendment 7, do my taxes go away?', 'measure_focus', 1),
                 ('What does No mean?', 'measure_focus', 2),
                 ("I still don't understand", 'measure_parts', 0),
                 ('What is the spending limit?', 'measure_focus', 4)]
        for authority in ('KCEB', 'JCEB'):
            for query, component, initial in cases:
                with self.subTest(authority=authority, query=query):
                    r = EvidenceLoop(self.corpus).answer(query, {'authority': authority}, contest_id='amendment-7')
                    self.assertEqual(r['status'], 'answered')
                    self.assertEqual(r['fact_validation']['status'], 'supported')
                    self.assertEqual(r['review']['status'], 'not_run')
                    self.assertEqual(r['view_plan']['component'], component)
                    self.assertEqual(r['view_plan']['initial_part'], initial)
                    self.assertTrue(validate_view_plan(r['view_plan'], r))
                    self.assertEqual(len(r['evidence']), 5)
                    ballot = next(e for e in r['evidence'] if e['source_category'] == 'Official election sample')
                    self.assertEqual(ballot['issuer'], 'Kansas City Election Board' if authority == 'KCEB' else 'Jackson County Election Board')
                    self.assertEqual(ballot['page'], 7 if authority == 'KCEB' else 2)
                    clauses = {e['id']: e for e in r['evidence']}
                    for facet in r['card']['facets']:
                        self.assertEqual(clauses[facet['evidence_id']]['text'][facet['start']:facet['end']], facet['quote'])
                    if initial == 1:
                        self.assertIn('No immediate tax cut', r['answer'])
                        self.assertIn('treasurer', r['answer'])
                        self.assertIn('lawmakers must approve', r['answer'])
                        self.assertIn('do not tell me what you personally pay or might save', r['answer'])
                        quote = r['card']['facets'][1]['quote']
                        self.assertIn('concurrent resolution', quote)
                        self.assertIn('within the first sixty', quote)
                    if initial == 2:
                        self.assertIn('does not approve creating the investment fund', r['answer'])
                    if initial == 4:
                        self.assertIn('3%', r['answer'])
                        self.assertIn('previous five years', r['answer'])
                        self.assertIn('not a new 3% tax', r['answer'])

    def test_predictions_advice_and_wrong_election_do_not_release_explanations(self):
        for query, status in [('When will Amendment 7 eliminate taxes?', 'insufficient_evidence'),
                              ('How much will I save with Amendment 7?', 'insufficient_evidence'),
                              ('Does Amendment 7 guarantee investment returns?', 'insufficient_evidence'),
                              ('Should I vote Yes on Amendment 7?', 'neutrality_boundary'),
                              ('Explain Amendment 7 in 2024', 'insufficient_evidence')]:
            with self.subTest(query=query):
                r = EvidenceLoop(self.corpus).answer(query, {'authority': 'KCEB'})
                self.assertEqual(r['status'], status)
                self.assertIsNone(r['card'])

    def test_partial_live_selection_cannot_borrow_unread_legal_conditions(self):
        select = lambda *args: (['amendment-7:kceb-sample'], [])
        r = EvidenceLoop(self.corpus, selector=select).answer('Explain Amendment 7', {'authority': 'KCEB'})
        self.assertEqual(r['status'], 'insufficient_evidence')
        self.assertIsNone(r['card'])
        self.assertIn('requires the complete checked', r['answer'])
        foreign = lambda *args: (['amendment-7:jceb-sample', *['amendment-7:proposal-' + k for k in ('investment', 'conditions', 'limit')]], [])
        r = EvidenceLoop(self.corpus, selector=foreign).answer('Explain Amendment 7', {'authority': 'KCEB'})
        self.assertEqual(r['status'], 'insufficient_evidence')
        self.assertIsNone(r['card'])

    def test_changed_prose_polarity_number_clause_and_jurisdiction_are_withheld(self):
        base = EvidenceLoop(self.corpus).answer('Explain Amendment 7', {'authority': 'KCEB'})
        mutations = [lambda r: r.update(answer='YES eliminates taxes immediately.'),
                     lambda r: r['card']['facets'][2].update(statement='NO creates the fund.'),
                     lambda r: r['card']['facets'][4].update(statement='The spending limit is 30%.'),
                     lambda r: r['card']['facets'][1].update(quote=r['card']['facets'][1]['quote'].split('provided that')[0]),
                     lambda r: r['card'].update(jurisdiction='Jackson County, Missouri'),
                     lambda r: r['evidence'][1].update(source_role='current_law')]
        for mutate in mutations:
            changed = copy.deepcopy(base); mutate(changed)
            self.assertEqual(validate_factual_display(changed, self.corpus)['status'], 'unsupported')

    def test_missing_or_changed_proposal_cannot_enable_the_card(self):
        with tempfile.TemporaryDirectory() as directory:
            research = Path(directory)
            pack = research / 'OpenOracle-JacksonCounty-2026-Research'
            files = ['jceb/2026-11-03-notice-sample-ballot.pdf', 'raw/kceb-sample.pdf',
                     'jceb/2026-11-03-notice-sample-ballot.md', 'markdown/kceb-sample.md', 'COUNTYWIDE-INVENTORY.md']
            for name in files:
                dest = pack / name; dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((self.corpus.pack / name).read_bytes())
            for changed in (False, True):
                if changed:
                    (pack / 'raw/amendment-7.pdf').write_bytes((self.corpus.pack / 'raw/amendment-7.pdf').read_bytes())
                    (pack / 'markdown/amendment-7.md').write_text((self.corpus.pack / 'markdown/amendment-7.md').read_text().replace('sixty', 'six'))
                c = Corpus(research)
                self.assertFalse(c.amendment7_ready)
                r = EvidenceLoop(c).answer('Explain Amendment 7', {'authority': 'KCEB'})
                self.assertEqual(r['status'], 'insufficient_evidence')
                self.assertIsNone(r['card'])

    def test_changed_original_after_startup_withholds_explanation(self):
        with patch('open_oracle.amendment7.original_pdf', return_value=None):
            r = EvidenceLoop(self.corpus).answer('Explain Amendment 7', {'authority': 'KCEB'})
        self.assertEqual(r['status'], 'unavailable')
        self.assertIsNone(r['card'])

    def test_yes_explanation_retains_net_earnings_and_timed_approval_conditions(self):
        result = EvidenceLoop(self.corpus).answer('What does Yes mean?', {'authority': 'KCEB'}, contest_id='amendment-7')
        clause = self.corpus.evidence['amendment-7:proposal-conditions']['text']
        self.assertIn('net investment earnings', clause)
        self.assertIn('previous fiscal year', clause)
        self.assertIn('concurrent resolution within the first sixty calendar days', clause)
        self.assertIn('regular session immediately following', clause)
        self.assertIn('investment earnings, after costs', result['answer'])
        self.assertIn('earnings must be from the state’s last budget year', result['answer'])
        self.assertIn('formal approval a concurrent resolution', result['answer'])
        self.assertIn('first 60 calendar days of their next regular lawmaking session', result['answer'])
        self.assertEqual(result['card']['facets'][1]['quote'], clause)
        self.assertEqual(validate_factual_display(result, self.corpus)['status'], 'supported')

    def test_complete_fair_language_is_sos_issued_and_statewide_under_both_boards(self):
        from open_oracle.amendment7 import FAIR_ID, FAIR_PDF_HASH, FAIR_PASSAGE_HASH
        for authority in ('KCEB', 'JCEB'):
            result = EvidenceLoop(self.corpus).answer('What does No mean?', {'authority': authority}, contest_id='amendment-7')
            fair = next(e for e in result['evidence'] if e['id'] == FAIR_ID)
            self.assertEqual(fair['issuer'], 'Missouri Secretary of State')
            self.assertEqual(fair['source_role'], 'official_ballot_explanation')
            self.assertEqual(fair['sha256'], FAIR_PDF_HASH)
            self.assertEqual(hashlib.sha256(fair['text'].encode()).hexdigest(), FAIR_PASSAGE_HASH)
            self.assertIn('insolvency, revenue shortfall, or program failure', fair['text'])
            self.assertIn('If passed, this measure will have no immediate impact on taxes', fair['text'])
            self.assertNotIn('Constitutional Amendment No. 8', fair['text'])
            no = result['card']['facets'][2]
            self.assertEqual(no['evidence_id'], FAIR_ID)
            self.assertEqual(fair['text'][no['start']:no['end']], no['quote'])
            self.assertNotIn('If passed', no['quote'])
            self.assertEqual(result['scope']['authority'], authority)

    def test_missing_changed_or_unread_fair_language_holds_display_and_speech(self):
        from open_oracle.amendment7 import FAIR_ID
        from tests.test_session_receipts import SyntheticReview
        from open_oracle.session_control import accepted_speech
        def partial(q, scope, contest, corpus):
            return [e['id'] for e in corpus.search(contest, scope) if e['id'] != FAIR_ID], []
        held = EvidenceLoop(self.corpus, selector=partial).answer('What does No mean?', {'authority':'KCEB'}, contest_id='amendment-7')
        self.assertEqual(held['status'], 'insufficient_evidence')
        self.assertIsNone(held['card'])
        accepted = EvidenceLoop(self.corpus, reviewer=SyntheticReview()).answer('What does No mean?', {'authority':'KCEB'}, contest_id='amendment-7')
        self.assertIsNotNone(accepted_speech(accepted, self.corpus))
        with patch('open_oracle.amendment7.fair_original', return_value=None):
            self.assertIsNone(accepted_speech(accepted, self.corpus))
            self.assertEqual(EvidenceLoop(self.corpus).answer('What does No mean?', {'authority':'KCEB'}, contest_id='amendment-7')['status'], 'unavailable')
        altered = copy.deepcopy(accepted)
        altered['answer'] = 'Existing taxes will never change if No wins.'
        self.assertEqual(validate_factual_display(altered, self.corpus)['status'], 'unsupported')

    def test_short_conditions_preserve_source_sequence_and_no_standalone_tax_prediction(self):
        from open_oracle.amendment7 import STATEMENTS
        text = STATEMENTS[1][1]
        # Independent semantic anchors, not a claim about a review score.
        ordered = ['before money could be used', 'investment earnings, after costs',
                   'replace the money from the listed state taxes', 'last budget year',
                   'state treasurer must report', 'lawmakers must approve',
                   'concurrent resolution', 'first 60 calendar days', 'next regular lawmaking session']
        positions = [text.index(term) for term in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn('(', text)
        no = STATEMENTS[2][1]
        self.assertNotIn('Existing taxes would not change', no)
        self.assertIn('rejects this proposed change', no)
        self.assertIn('through this proposal', no)
        self.assertNotIn('eliminate', no)

    def test_focused_live_answer_cannot_borrow_a_different_registered_facet(self):
        # An authored accepted-review fixture exercises the boundary, not inference.
        from tests.test_session_receipts import SyntheticReview
        from open_oracle.session_control import accepted_speech
        from open_oracle.amendment7 import OVERVIEW, STATEMENTS
        def selector(question, scope, contest_id, corpus):
            return [e['id'] for e in corpus.search(contest_id, scope)], []
        result = EvidenceLoop(self.corpus, selector=selector, reviewer=SyntheticReview()).answer(
            'What does Yes mean?', {'authority': 'KCEB'}, contest_id='amendment-7')
        self.assertEqual(result['status'], 'answered')
        self.assertEqual(result['card']['facet_keys'], ['conditions'])
        self.assertEqual(result['answer'], result['card']['facets'][0]['statement'])
        self.assertIsNotNone(accepted_speech(result, self.corpus))
        for other_answer in (OVERVIEW, STATEMENTS[2][1]):
            changed = copy.deepcopy(result)
            changed['answer'] = changed['speech']['text'] = other_answer
            self.assertEqual(validate_factual_display(changed, self.corpus)['status'], 'unsupported')
            self.assertIsNone(accepted_speech(changed, self.corpus))

    def test_synthetic_accepted_speech_still_rechecks_proposal_original(self):
        # Authored review fixture exercises receipt logic; no live review or speech.
        from tests.test_session_receipts import SyntheticReview
        from open_oracle.session_control import accepted_speech
        r = EvidenceLoop(self.corpus, reviewer=SyntheticReview()).answer('Explain Amendment 7 in November 2026', {'authority': 'KCEB'})
        self.assertEqual(r['status'], 'answered')
        self.assertIsNotNone(accepted_speech(r, self.corpus))
        with patch('open_oracle.amendment7.original_pdf', return_value=None):
            self.assertIsNone(accepted_speech(r, self.corpus))

    def test_actual_http_retained_pdf_and_contextual_no_followup(self):
        server = make_server(port=0, corpus=self.corpus)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
        try:
            conn.request('GET', '/api/prepared-source/amendment-7.pdf')
            response = conn.getresponse(); raw = response.read()
            self.assertEqual(response.status, 200)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), 'cd9468cfff8e54020969f93c59fc6f42113a27b0cf35fe12e9e1e99da8232261')
            conn.request('GET', '/api/prepared-source/amendment-7-fair.pdf')
            response = conn.getresponse(); raw = response.read()
            self.assertEqual(response.status, 200)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), '4418cb67c6219ea57ae7169beb79f3355befa165d7098bbe6d538934e66d5b9e')
            for query, phrase in [('Explain Amendment 7', 'does not eliminate taxes immediately'),
                                  ('What does No mean?', 'does not approve creating the investment fund')]:
                conn.request('POST', '/api/ask', json.dumps({'question': query, 'scope': {'authority': 'KCEB'}}),
                             {'Content-Type': 'application/json', 'X-Oracle-Session': 'f265d99e-2bd2-4ba2-a370-9ef39702ee5d'})
                response = conn.getresponse(); body = json.loads(response.read())
                self.assertEqual(response.status, 200)
                self.assertEqual(body['status'], 'answered')
                self.assertIn(phrase, body['answer'])
        finally:
            conn.close(); server.shutdown(); server.server_close(); thread.join()
