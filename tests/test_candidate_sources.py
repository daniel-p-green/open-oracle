import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from open_oracle.candidate_sources import CandidateSources
from open_oracle.corpus import Corpus, ELECTION, normalized
from open_oracle.engine import EvidenceLoop


class CandidateSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus()
        cls.index = cls.corpus.candidate_sources
        cls.loop = EvidenceLoop(cls.corpus)

    def test_full_roster_preserved_and_position_text_not_fabricated(self):
        self.assertTrue(self.index.available)
        self.assertEqual(len(self.index.people), 73)
        response = self.loop.answer('Compare Scott Fitzpatrick and Quentin Wilson positions')
        self.assertEqual(response['status'], 'insufficient_evidence')
        self.assertEqual(response['claims'], [])
        self.assertEqual(response['evidence'], [])
        self.assertEqual({p['candidate_name'] for p in response['candidate_sources']}, {'SCOTT FITZPATRICK', 'QUENTIN WILSON'})
        for person in response['candidate_sources']:
            self.assertEqual(person['position_evidence'], 'not_retained')
            for source in person['sources']:
                self.assertFalse(source['candidate_statement_text_available'])
                self.assertEqual(source['kind'], 'candidate_statement_link')
                self.assertEqual(source['election_date'], ELECTION)
                self.assertEqual(source['jurisdiction'], 'Missouri')
                self.assertTrue(source['url'].startswith('https://'))
                self.assertTrue(source['publication_date'] and source['retrieved_date'])

    def test_name_collisions_and_explicit_identity_conflict(self):
        ambiguous = self.loop.answer('Wilson positions')
        self.assertEqual(ambiguous['status'], 'clarification')
        self.assertEqual(ambiguous['candidate_sources'], [])
        wrong = self.loop.answer('Show Paul Wilson sources', contest_id='state-auditor')
        self.assertEqual(wrong['status'], 'clarification')
        self.assertEqual(wrong['candidate_sources'], [])
        self.assertEqual({c['id'] for c in wrong['choices']}, {'state-auditor', 'retention-paul-c-wilson'})
        right = self.loop.answer('Show Quentin Wilson sources')
        self.assertEqual([p['candidate_name'] for p in right['candidate_sources']], ['QUENTIN WILSON'])
        self.assertTrue(all('paul' not in s['source_id'] for s in right['candidate_sources'][0]['sources']))

    def test_missing_coverage_and_nonresponse_are_not_positions(self):
        dustin = self.loop.answer('Show Dustin Coffell positions')['candidate_sources'][0]
        self.assertEqual(dustin['sources'][0]['coverage'], 'source_specific_nonresponse')
        self.assertEqual(dustin['position_evidence'], 'not_retained')
        gap = self.loop.answer('Show Chris Stigall positions')['candidate_sources'][0]
        self.assertEqual(gap['sources'], [])
        self.assertIn('not a position', gap['gap'])
        susan = self.loop.answer('Show Susan B. Wilson sources')['candidate_sources'][0]
        self.assertEqual(susan['sources'][0]['coverage'], 'mentioned_not_surveyed')

    def test_historical_scope_and_records_cannot_leak_current_positions(self):
        for question, scope in [('Show 2024 Stacy Lake positions', {}), ('Show Stacy Lake positions', {'election_date': '2025-11-04'})]:
            result = self.loop.answer(question, scope)
            self.assertEqual(result['candidate_sources'], [])
            self.assertEqual(result['claims'], [])
        result = self.loop.answer('Show Rick Brattin record')
        source = result['candidate_sources'][0]['sources'][0]
        self.assertEqual(source['kind'], 'official_record_gateway')
        self.assertIn('not a federal voting record', source['document_period'])
        self.assertFalse(source['candidate_statement_text_available'])
        self.assertEqual(result['claims'], [])

    def test_retained_survey_citations_and_allowlist(self):
        result = self.loop.answer('Show Paul C. Wilson survey')
        self.assertEqual(result['status'], 'insufficient_evidence')
        source = result['candidate_sources'][0]['sources'][0]
        self.assertEqual(source['kind'], 'third_party_judicial_survey')
        self.assertEqual(source['coverage'], 'retained_original')
        self.assertIn('2026', source['document_period'])
        self.assertTrue(source['original_route'])
        original = self.index.original(source['source_id'])
        self.assertTrue(original.startswith(b'%PDF'))
        self.assertEqual(hashlib.sha256(original).hexdigest(), source['original_sha256'])
        for ident in ('congress-alford', '../../.env', 'judge-2026-../../.env-lawyer', 'judges-printable-2026'):
            self.assertIsNone(self.index.original(ident))

    def test_altered_original_and_metadata_are_blocked_without_research_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            pack = Path(temp); records = pack / 'candidate_records'; records.mkdir()
            for name in ('candidate-sources.md', 'manifest.json', 'judge-2026-paul-wilson-lawyer.raw.pdf'):
                (records / name).write_bytes((self.index.root / name).read_bytes())
            fake = SimpleNamespace(pack=pack, contests=self.corpus.contests, allowed=self.corpus.allowed)
            index = CandidateSources(fake)
            self.assertTrue(index.original('judge-2026-paul-wilson-lawyer'))
            pdf = records / 'judge-2026-paul-wilson-lawyer.raw.pdf'; pdf.write_bytes(pdf.read_bytes() + b'altered')
            self.assertIsNone(index.original('judge-2026-paul-wilson-lawyer'))
            summary = records / 'candidate-sources.md'; summary.write_text(summary.read_text() + '\nAltered coverage\n')
            changed = CandidateSources(fake)
            self.assertFalse(changed.available)
            self.assertEqual(changed.lookup(self.corpus.contests['state-auditor'], 'Scott Fitzpatrick', {})['people'], [])
