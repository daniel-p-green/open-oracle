from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

from open_oracle.corpus import Corpus
from strands_quality.research_corpus import Registry, Scope, load_verified_corpus
from strands_quality.voting_procedure import load_voting_procedure, inspect_procedure_claim, CONTEST_ID
from strands_quality.research_agent import Part

ARCHIVE = Path(__file__).resolve().parents[1] / '.local/sources/missouri-voting-procedure'

class ProcedureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources, cls.chunks = load_voting_procedure(ARCHIVE)
        cls.registry = Registry(cls.sources, cls.chunks)

    def test_all_retained_hashes_exact_offsets_and_roles(self):
        self.assertEqual(len(self.sources), 5)
        self.assertEqual(len(self.chunks), 15)
        for chunk in self.chunks:
            evidence = self.registry.read(chunk.id)
            self.assertEqual(evidence['text'], self.registry.sources[chunk.source_id].text[chunk.start:chunk.end])
            self.assertEqual(evidence['role'], 'official_voting_procedure')
            self.assertEqual(evidence['fresh_http'], False)

    def test_private_index_additive_default_unchanged(self):
        baseline = load_verified_corpus(Corpus())
        indexed = load_verified_corpus(Corpus(), voting_procedure_archive=ARCHIVE)
        self.assertEqual(len(baseline.sources), 5)
        self.assertEqual(len(indexed.sources), 10)
        self.assertEqual(len(indexed.chunks), len(baseline.chunks) + 15)
        for ident, chunk in baseline.chunks.items():
            self.assertEqual(chunk, indexed.chunks[ident])

    def test_substantive_sqlite_search_and_exact_read_in_both_authorities(self):
        for authority in ('KCEB', 'JCEB'):
            rows = self.registry.rank('provisional identification', Scope(authority=authority), CONTEST_ID, 'voting_procedure')
            self.assertTrue(rows)
            for row in rows:
                self.assertEqual(row['retrieval'], 'sqlite_fts5_bm25')
                self.assertTrue(self.registry.read(row['chunk_id'])['text'])

    def test_no_procedure_promoted_to_ballot_current_law_or_prediction(self):
        for purpose in ('ballot_fact', 'current_law', 'legal_reference', 'prediction'):
            self.assertEqual(self.registry.rank('identification', Scope(), CONTEST_ID, purpose), [])

    def test_wrong_scope_election_version_or_snapshot_has_no_hits(self):
        sid = self.sources[0].id
        for scope in (Scope(state='KS'), Scope(county='other'), Scope(authority='unknown'),
                      Scope(election_date='2024-11-05'), Scope(as_of='2026-10-12'),
                      Scope(as_of='2026-10-10'), Scope(versions=((sid, '0'*64),))):
            self.assertEqual(self.registry.rank('polling', scope, CONTEST_ID, 'voting_procedure', source_ids={sid}), [])
        self.assertEqual(self.registry.rank('polling', Scope(), 'combat', 'voting_procedure'), [])

    def test_wrong_role_cannot_enter_procedure_search(self):
        registry = Registry([replace(s, role='ballot_proposal') for s in self.sources], self.chunks)
        self.assertEqual(registry.rank('polling', Scope(), CONTEST_ID, 'voting_procedure'), [])

    def test_polling_hours_include_closing_line_exception_and_no_personal_assignment(self):
        result = inspect_procedure_claim(self.registry, ARCHIVE, 'polling_hours', Scope())
        self.assertEqual(len(result['evidence']), 2)
        self.assertIn('in line', result['evidence'][1]['text'])
        self.assertFalse(result['public_release_approved'])
        self.assertFalse(result['personal_eligibility_determined'])
        self.assertFalse(result['local_polling_assignment_determined'])

    def test_pdf_layout_inspection_is_not_released_citation(self):
        pdf = [c for c in self.chunks if c.page is not None]
        self.assertTrue(pdf)
        for chunk in pdf:
            self.assertFalse(self.registry.read(chunk.id)['factual_claim_citation_eligible'])
            with self.assertRaises(ValueError):
                self.registry.citation(chunk.id, chunk.text[:100])

    def test_publication_precision_not_retrieval_date(self):
        result = inspect_procedure_claim(self.registry, ARCHIVE, 'accessible_options', Scope())
        self.assertEqual(result['publication_dates']['how-to-vote'], {'date': None, 'precision': None})
        self.assertEqual(result['publication_dates']['acceptable-id-pdf'], {'date': '2025-01', 'precision': 'month'})

    def test_late_original_change_fails_even_after_indexing(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp); shutil.copytree(ARCHIVE, root, dirs_exist_ok=True)
            sources, chunks = load_voting_procedure(root)
            registry = Registry(sources, chunks)
            sources[0].original_path.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                registry.read(next(c.id for c in chunks if c.source_id == sources[0].id))

    def test_changed_original_extraction_manifest_or_missing_file_fails(self):
        for name in ('how-to-vote.html', 'voter-id.txt', 'admission.json', 'acceptable-id-pdf.pdf'):
            with self.subTest(name=name), TemporaryDirectory() as tmp:
                root = Path(tmp); shutil.copytree(ARCHIVE, root, dirs_exist_ok=True)
                path = root/name; path.write_bytes(path.read_bytes()+b'\nchanged')
                with self.assertRaises(ValueError): load_voting_procedure(root)
        with TemporaryDirectory() as tmp:
            root = Path(tmp); shutil.copytree(ARCHIVE, root, dirs_exist_ok=True)
            (root/'absentee-request-pdf.pdf').unlink()
            with self.assertRaises(FileNotFoundError): load_voting_procedure(root)

    def test_model_plan_can_only_select_declared_procedure_purpose(self):
        part = Part(id='hours', question='What hours?', query='polling hours', purpose='voting_procedure')
        self.assertEqual(part.purpose, 'voting_procedure')

if __name__ == '__main__': unittest.main()
