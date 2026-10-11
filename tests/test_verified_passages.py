"""Pure local integrity/retrieval/release checks; actual retained original used.

No server, provider, install, cloud upload or model inference is run.
"""
from copy import deepcopy
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase, main

os.environ['OTEL_SDK_DISABLED'] = 'true'
PROJECT = Path(__file__).resolve().parents[1]
STAGE = PROJECT
from strands_quality import verified_passages as vp
from strands_quality.research_corpus import Registry, Scope, digest, load_verified_corpus
from open_oracle.corpus import Corpus
from open_oracle.research_release import FORMS, requested_parts, validate_draft

ORIGINAL = Corpus().pack / 'raw/combat-6096-adopted.pdf'


class SelectedPassageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.chunks = vp.load_6096_selected(ORIGINAL)
        cls.registry = Registry([cls.source], cls.chunks)

    def test_actual_original_reading_index_and_packet_pins(self):
        self.assertEqual(ORIGINAL.stat().st_size, 466739)
        self.assertEqual(digest(ORIGINAL.read_bytes()), vp.ORIGINAL_SHA256)
        self.assertEqual(digest((STAGE / 'data/6096-selected-reading.txt').read_bytes()), vp.READING_SHA256)
        self.assertEqual(digest((STAGE / 'data/6096-selected-index.json').read_bytes()), vp.INDEX_SHA256)
        self.assertEqual(vp.PACKET_SHA256, 'ad8c7fe44fd934217615cd7c931f824e005f104657900b359e0fb47f67e316b2')

    def test_exactly_eight_direct_spans_and_explicit_partial_source_role(self):
        self.assertEqual(len(self.chunks), 8)
        self.assertEqual(len({c.id for c in self.chunks}), 8)
        self.assertEqual(self.source.role, 'adopted_proposal')
        self.assertEqual(self.source.quality, 'verified_reading_copy')
        self.assertIsNone(self.source.authority)
        self.assertIsNone(self.source.effective_from)
        self.assertIn('partial', self.source.title)
        self.assertIn('visual line breaks joined', self.source.extraction)
        self.assertIn('voter approval', self.source.extraction)
        for c, (ident, a, b, page, locator) in zip(self.chunks, vp.SELECTED):
            self.assertEqual((c.start, c.end, c.page, c.section), (a, b, page, locator))
            self.assertTrue(c.id.endswith(':' + ident))
            self.assertEqual(c.text, self.source.text[a:b])
            self.assertEqual(c.sha256, digest(c.text.encode()))
            self.assertNotIn('[' + ident + ']', c.text)
            binding = vp.selected_passage_binding(c)
            self.assertEqual(binding['original_sha256'], self.source.original_sha256)
            self.assertEqual(binding['reading_sha256'], self.source.extraction_sha256)
            self.assertFalse(binding['runtime_release_approved'])
            self.assertTrue(binding['partial'])
            self.assertIn('Reviewer locator only', binding['reviewer_locator']['semantics'])

    def test_all_eight_exact_citations_bind_reading_offsets_and_original(self):
        for c in self.chunks:
            cite = self.registry.citation(c.id, c.text)
            self.assertEqual(self.source.text[cite['quote_start']:cite['quote_end']], c.text)
            self.assertEqual(cite['original_sha256'], vp.ORIGINAL_SHA256)
            self.assertEqual(cite['extraction_sha256'], vp.READING_SHA256)
            self.assertEqual(cite['page'], c.page)
            self.assertEqual(cite['section'], c.section)
            self.assertEqual(cite['role'], 'adopted_proposal')

    def test_full_question_and_separate_trust_fund_remain_one_chunk(self):
        c = self.chunks[4]
        self.assertTrue(c.text.startswith('Shall Jackson County continue'))
        self.assertIn('The proceeds of this tax shall be deposited', c.text)
        self.assertTrue(c.text.endswith('separate from the general fund or any other county funds.'))

    def test_voter_condition_and_collection_dates_remain_one_chunk(self):
        c = self.chunks[5]
        self.assertTrue(c.text.startswith('If a majority of the qualified voters'))
        self.assertIn('April 1, 2027', c.text)
        self.assertIn('March 31, 2037', c.text)
        self.assertNotIn('immediately upon its signature', c.text)
        self.assertIn('immediately upon its signature by the County Executive', self.chunks[7].text)
        self.assertNotIn('April 1, 2027', self.chunks[7].text)

    def test_chapter93_election_cost_exception_remains_one_chunk(self):
        c = self.chunks[3]
        self.assertIn('Chapter 93, Jackson County Code, 1984, except that', c.text)
        self.assertIn('appropriate election authorities in conducting the election', c.text)

    def test_recitals_and_notification_are_attributed_text_only(self):
        self.assertTrue(self.chunks[0].text.startswith('WHEREAS'))
        self.assertTrue(self.chunks[1].text.startswith('WHEREAS, unless continued by the voters'))
        self.assertIn('authorized and directed to notify', self.chunks[6].text)
        self.assertEqual({c.source_id for c in self.chunks}, {vp.SOURCE_ID})
        self.assertNotIn('6120', self.source.text)
        self.assertNotIn('December 11, 2018', self.source.text)

    def test_only_legal_reference_is_eligible_in_both_county_authorities(self):
        for authority in ('JCEB', 'KCEB'):
            scope = Scope(authority=authority)
            self.assertTrue(self.registry.rank('Chapter 93', scope, 'combat', 'legal_reference'))
            for purpose in ('ballot_fact', 'current_law', 'prediction'):
                self.assertEqual(self.registry.rank('tax', scope, 'combat', purpose), [])

    def test_wrong_scope_contest_date_and_version_fail_before_retrieval(self):
        for scope in (Scope(state='KS'), Scope(county='other'), Scope(authority='other'),
                      Scope(election_date='2024-11-05'),
                      Scope(versions=((vp.SOURCE_ID, '0' * 64),))):
            self.assertEqual(self.registry.rank('tax', scope, 'combat', 'legal_reference'), [])
        self.assertEqual(self.registry.rank('tax', Scope(), 'other', 'legal_reference'), [])

    def test_changed_original_fails_loader_and_later_registry_acquisition(self):
        with TemporaryDirectory() as tmp:
            changed = Path(tmp) / 'original.pdf'
            raw = bytearray(ORIGINAL.read_bytes()); raw[100] ^= 1
            changed.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'Original changed'):
                vp.load_6096_selected(changed)
            registry = Registry([replace(self.source, original_path=changed)], self.chunks)
            with self.assertRaisesRegex(ValueError, 'Original changed'):
                registry.citation(self.chunks[0].id, self.chunks[0].text)

    def test_changed_reading_or_unapproved_extra_ocr_fails(self):
        for edit in (lambda t: t.replace('one-quarter', 'one-half', 1),
                     lambda t: t + '\nUnreviewed additional ordinance text\n',
                     lambda t: t.replace('If a majority of the qualified voters', 'If no voters')):
            with self.subTest(edit=edit), TemporaryDirectory() as tmp:
                directory = Path(tmp)
                shutil.copytree(STAGE / 'data', directory, dirs_exist_ok=True)
                path = directory / '6096-selected-reading.txt'
                path.write_text(edit(path.read_text()))
                with self.assertRaisesRegex(ValueError, 'Selected reading copy changed'):
                    vp.load_6096_selected(ORIGINAL, data_dir=directory)

    def test_any_changed_manifest_offsets_pages_locators_roles_scope_schema_fails(self):
        base = json.loads((STAGE / 'data/6096-selected-index.json').read_text())
        edits = [
            lambda d: d.update(role='current_law'), lambda d: d.update(role='ballot_proposal'),
            lambda d: d.update(quality='native_html'), lambda d: d.update(retrieved_date='2026-10-09'),
            lambda d: d.update(state='KS'), lambda d: d.update(county='other'),
            lambda d: d.update(election_date='2024-11-05'), lambda d: d.update(schema_version=2),
            lambda d: d.update(effective_from='2027-04-01'),
            lambda d: d.update(runtime_release_approved=True),
            lambda d: d['passages'][0].update(start=180),
            lambda d: d['passages'][0].update(end=531),
            lambda d: d['passages'][0].update(pdf_page_1_based=2),
            lambda d: d['passages'][0].update(section_or_locator='invented'),
            lambda d: d['passages'][0]['reviewer_locator'].update(approximate_normalized_bbox=[.2,.3,.8,.4]),
            lambda d: d['passages'].append(deepcopy(d['passages'][0])),
            lambda d: d['passages'].__setitem__(1, deepcopy(d['passages'][0])),
            lambda d: d['passages'].pop(), lambda d: d.update(unapproved='extra'),
        ]
        for edit in edits:
            with self.subTest(edit=edit), TemporaryDirectory() as tmp:
                directory = Path(tmp); shutil.copytree(STAGE / 'data', directory, dirs_exist_ok=True)
                manifest = deepcopy(base); edit(manifest)
                (directory / '6096-selected-index.json').write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, 'Selected index changed'):
                    vp.load_6096_selected(ORIGINAL, data_dir=directory)

    def test_chunk_binding_rejects_mutated_page_offset_text_scope_and_extra_id(self):
        c = self.chunks[0]
        for changes in ({'page': 5}, {'start': c.start + 1}, {'text': c.text + ' '},
                        {'section': 'other'}, {'source_id': 'combat-6096'},
                        {'applicability': 'municipal'}, {'location': 'other'}, {'column': 2},
                        {'id': 'combat:unreviewed'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                vp.selected_passage_binding(replace(c, **changes))

    def test_existing_ocr_remains_unverified_and_no_archive_copy_is_staged(self):
        base = load_verified_corpus(Corpus())
        self.assertEqual(base.sources['combat-6096'].quality, 'unverified_ocr')
        self.assertIn(vp.SOURCE_ID, base.sources)
        self.assertEqual(sum(c.source_id == vp.SOURCE_ID for c in base.chunks.values()), 8)
        old = next(c for c in base.chunks.values() if c.source_id == 'combat-6096')
        with self.assertRaisesRegex(ValueError, 'Unverified extraction'):
            base.citation(old.id, old.text[:min(200, len(old.text))])
        self.assertTrue(all(c.source_id in {'combat-6096', vp.SOURCE_ID} for c in base.chunks.values() if '6096' in c.source_id))

    def test_generic_legal_release_refused_even_with_valid_selected_citation(self):
        for question in ('What is Chapter 93 for COMBAT?', 'When is Ordinance 6096 effective?',
                         'What is the COMBAT rate and current law?'):
            with self.assertRaises(ValueError): requested_parts(question)
        cite = self.registry.citation(self.chunks[4].id, self.chunks[4].text)
        part = SimpleNamespace(id='rate', purpose='legal_reference', question='What is the COMBAT rate?')
        plan = SimpleNamespace(contest_id='combat', model_dump=lambda: {'contest_id': 'combat'})
        draft = {'plan': plan.model_dump(), 'claims': [
            {'part_id': 'rate', 'text': FORMS['rate'], 'citations': [cite]}], 'gaps': []}
        request = SimpleNamespace(check=lambda: None, plan=plan, result=object(),
                                  finalize=lambda result: draft, part=lambda ident: part,
                                  registry=self.registry, scope=Scope())
        with self.assertRaisesRegex(ValueError, 'Research claim purpose binding failed'):
            validate_draft(request, draft, 'What is the COMBAT rate?')
        part.purpose = 'ballot_fact'
        request.read_by_part = {'rate': {self.chunks[4].id}}
        with self.assertRaisesRegex(ValueError, 'Research original/part citation binding failed'):
            validate_draft(request, draft, 'What is the COMBAT rate?')


if __name__ == '__main__':
    main()
