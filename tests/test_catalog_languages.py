"""Offline structure checks; these do not adjudicate translation meaning."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {'en', 'es', 'vi', 'ar', 'zh-Hans', 'fil'}
EXPANDED_LANGUAGES = {'vi', 'ar', 'zh-Hans', 'fil'}
SOURCES = {
    'rate': 'If approved, the COMBAT sales tax would continue at 0.25 cent for 10 years.',
    'dates': 'The election date is 2026-11-03 in Jackson County, Missouri.',
    'polarity': 'A YES vote approves the printed proposal. A NO vote rejects the printed proposal.',
    'exception': 'The proposal does not repeal the tax, except under the printed condition.',
    'attribution': 'Candidate Example states: "I support the proposal." This is an attributed statement, not an independently verified result.',
}
ANCHORS = {
    'rate': {'approved', '0.25', 'cent', '10', 'years', 'COMBAT'},
    'dates': {'2026-11-03', 'Jackson County, Missouri'},
    'polarity': {'YES', 'approves', 'NO', 'rejects'},
    'exception': {'does not repeal', 'except', 'the printed condition'},
    'attribution': {'Candidate Example', 'states', 'attributed statement', 'not an independently verified result'},
}
KINDS = {'condition', 'number', 'unit', 'scope', 'date', 'polarity', 'negation', 'exception', 'attribution'}
IMMUTABLE_NAMES = ('COMBAT', 'Jackson County, Missouri', 'Candidate Example', 'YES', 'NO')


class CatalogLanguagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_path = ROOT / 'open_oracle/locale_catalog.json'
        cls.catalog = json.loads(cls.catalog_path.read_text(encoding='utf-8'))
        cls.fixtures = json.loads((ROOT / 'fixtures/expanded_translations.json').read_text(encoding='utf-8'))
        cls.official_source = json.loads((ROOT / 'fixtures/official_combat.json').read_text(encoding='utf-8'))
        cls.official_translations = json.loads((ROOT / 'fixtures/official_translations.json').read_text(encoding='utf-8'))

    def test_complete_catalog_keys_and_values(self):
        catalogs = self.catalog['catalogs']
        self.assertEqual(set(catalogs), LANGUAGES)
        expected = set(catalogs['en'])
        self.assertTrue({'reason.vote_advice', 'reason.translation_not_verified',
                         'status.erased', 'status.changed', 'status.language_short',
                         'status.language_uncertain', 'status.language_mixed',
                         'idle.invitation', 'idle.ready', 'idle.experimental',
                         'idle.choose', 'idle.static'} <= expected)
        for language, catalog in catalogs.items():
            with self.subTest(language=language):
                self.assertEqual(set(catalog), expected)
                self.assertTrue(all(isinstance(v, str) and v.strip() for v in catalog.values()))
                # User-supplied strings use isolation at rendering time. Catalogs
                # contain no direction overrides that could reorder safety text.
                self.assertFalse(any(c in '\u202a\u202b\u202c\u202d\u202e' for value in catalog.values() for c in value))

    def test_web_and_python_catalogs_are_exact_copies(self):
        self.assertEqual(self.catalog_path.read_bytes(), (ROOT / 'web/locales.json').read_bytes())

    def test_authored_status_not_verified_claim(self):
        self.assertEqual(self.catalog['validation'], 'offline_fixture_authored_not_human_adjudicated')
        self.assertEqual(self.fixtures['validation'], 'offline_fixture_authored_not_human_adjudicated')
        for language in EXPANDED_LANGUAGES:
            # A non-English safety label must actually have authored native text.
            self.assertNotEqual(self.catalog['catalogs'][language]['status.fixture'],
                                self.catalog['catalogs']['en']['status.fixture'])
            self.assertNotEqual(self.catalog['catalogs'][language]['reason.translation_not_verified'],
                                self.catalog['catalogs']['en']['reason.translation_not_verified'])

    def test_expanded_fixture_cases_and_exact_sources(self):
        rows = self.fixtures['translations']
        pairs = [(row['language'], row['id']) for row in rows]
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertEqual(set(pairs), {(lang, id) for lang in EXPANDED_LANGUAGES for id in SOURCES})
        for row in rows:
            with self.subTest(language=row['language'], id=row['id']):
                self.assertEqual(row['source'], SOURCES[row['id']])
                self.assertIsInstance(row['target'], str)
                self.assertTrue(row['target'].strip())
                self.assertNotEqual(row['target'], row['source'])

    def test_anchor_bindings_numeric_notation_and_names(self):
        for row in self.fixtures['translations']:
            with self.subTest(language=row['language'], id=row['id']):
                features = row['features']
                self.assertEqual({f['source_phrase'] for f in features}, ANCHORS[row['id']])
                self.assertEqual(len(features), len(ANCHORS[row['id']]))
                for feature in features:
                    self.assertIn(feature['kind'], KINDS)
                    self.assertIn(feature['source_phrase'], row['source'])
                    self.assertIsInstance(feature['target_phrase'], str)
                    self.assertTrue(feature['target_phrase'].strip())
                    self.assertIn(feature['target_phrase'], row['target'])
                pattern = r'(?<!\w)\d+(?:[./-]\d+)*(?!\w)'
                self.assertEqual(re.findall(pattern, row['source']), re.findall(pattern, row['target']))
                for name in IMMUTABLE_NAMES:
                    if name in row['source']:
                        self.assertEqual(row['source'].count(name), row['target'].count(name))

    def test_official_span_fixture_coverage_and_bound_anchors(self):
        self.assertEqual(self.official_translations['validation'],
                         'offline_fixture_authored_not_human_adjudicated')
        expected = {
            'official_rate': ('at the rate of one-quarter of one cent',
                              'The printed tax rate is one-quarter of one cent.',
                              {('number', 'one-quarter'), ('unit', 'one cent')}),
            'official_time': ('for a period of ten years',
                              'The proposed continuation lasts ten years.',
                              {('number', 'ten years'), ('unit', 'ten years')}),
        }
        rows = self.official_translations['translations']
        pairs = [(r['language'], r['id']) for r in rows]
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertEqual(set(pairs), {(lang, id) for lang in LANGUAGES - {'en'} for id in expected})
        original = self.official_source['evidence']['text']
        for row in rows:
            with self.subTest(language=row['language'], id=row['id']):
                quote, english, anchors = expected[row['id']]
                self.assertEqual(row['source_quote'], quote)
                self.assertEqual(row['english'], english)
                # The source has retained linebreaks between one-quarter/of.
                # Match without changing its immutable text or claiming that
                # normalized text shares the original byte offsets.
                pattern = r'\s+'.join(re.escape(word) for word in quote.split())
                self.assertIsNotNone(re.search(pattern, original))
                self.assertTrue(row['target'].strip())
                self.assertIsNone(re.search(r'\d', row['target']))
                self.assertEqual({(f['kind'], f['source_phrase']) for f in row['features']}, anchors)
                self.assertEqual(len(row['features']), len(anchors))
                for feature in row['features']:
                    self.assertIn(feature['source_phrase'], quote)
                    self.assertEqual(feature['english_phrase'], feature['source_phrase'])
                    self.assertIn(feature['english_phrase'], english)
                    self.assertTrue(feature['target_phrase'].strip())
                    self.assertIn(feature['target_phrase'], row['target'])

    def test_official_span_context_preserves_proposal_status(self):
        evidence = self.official_source['evidence']
        for row in self.official_translations['translations']:
            with self.subTest(language=row['language'], id=row['id']):
                context = row['context']
                self.assertEqual(context['source_id'], evidence['id'])
                self.assertEqual(context['source_original_sha256'], self.official_source['original_sha256'])
                self.assertEqual(context['authority'], evidence['issuer'])
                self.assertEqual(context['source_role'], 'official_ballot')
                self.assertEqual(context['scope'], 'printed proposal; not an assertion of enacted current law')
                if row['id'] == 'official_time':
                    condition = context['proposal_condition']
                    self.assertEqual(condition['source_phrase'], 'Shall Jackson County continue')
                    self.assertIn(condition['source_phrase'], evidence['text'])
                    self.assertEqual(condition['english_phrase'], 'proposed continuation')
                    self.assertIn(condition['english_phrase'], row['english'])
                    self.assertTrue(condition['target_phrase'].strip())
                    self.assertIn(condition['target_phrase'], row['target'])
                    self.assertEqual(condition['binding'],
                                     'whole_retained_original_context; not inside the narrow duration span')


if __name__ == '__main__':
    unittest.main()
