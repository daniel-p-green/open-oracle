"""Actual retained-source integration; authored review is never live approval."""
from dataclasses import replace
from copy import deepcopy
from hashlib import sha256
import unittest
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.claim_bindings import validate_factual_display
from open_oracle.quality_policy import assistant_texts, release_block
from open_oracle.language_fixtures import official_fixtures, SCOPE, accepted_fixture_transport
from open_oracle.translation_validation import TranslationGate, TranslationDecisionsCheck, SourceOperation

class CoreTranslationBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus()

    def setUp(self):
        self.sources, all_forms = official_fixtures()
        self.forms = [f for f in all_forms if f.language == 'es']
        self.calls = []
        self.response = EvidenceLoop(self.corpus).answer('What is the COMBAT tax rate?')
        self.review = TranslationDecisionsCheck(self.transport)

    def transport(self, resource, request):
        self.calls.append(request)
        return accepted_fixture_transport(resource, request)

    def claims(self, forms=None):
        return [{'form_id': f.id, 'text': f.target, 'language': 'es'} for f in (forms or self.forms)]

    def english_check(self, envelope):
        if release_block(self.response, self.corpus): return 'english_source_guard'
        if validate_factual_display(self.response, self.corpus)['status'] != 'supported': return 'english_display_guard'
        original = self.corpus.originals['jceb-sample'].read_bytes()
        if sha256(original).hexdigest() != self.sources['combat:jceb-sample'].original_sha256: return 'english_original_guard'
        # This fixture examines one checked focal sentence, not a public full display.
        if [c['english'] for c in envelope['claims']] != [self.response['answer']]: return 'english_projection_coverage'
        return None

    def gate(self, forms=None, sources=None, english_check=None, current=None):
        return TranslationGate((sources or self.sources).get, forms or self.forms,
            english_check or self.english_check, self.review, lambda: None,
            current_operation=current)

    def test_actual_english_original_and_single_focal_span_fixture_rebind(self):
        f = next(f for f in self.forms if f.id == 'es:official_rate')
        r = self.gate([f]).release('offline-core-rate', 'es', self.claims([f]), SCOPE, fixture_mode=True)
        self.assertEqual(r['status'], 'fixture_validated')
        self.assertEqual(r['review']['execution'], 'offline_stub')
        self.assertEqual(r['originals'][0]['text'], self.corpus.evidence[f.source_id]['text'])
        self.assertEqual(r['primary'], f.target)
        self.assertIsNone(r['speech'])
        self.assertEqual(len(self.calls), 1)

    def test_unknown_or_non_english_cannot_gain_english_source_locale(self):
        ident = 'combat:jceb-sample'
        for language in ('unknown', None, 'es', 'vi', 'ar', 'zh-Hans', 'fil', 'en-US'):
            with self.subTest(language=language):
                source = replace(self.sources[ident], language=language)
                forms = [replace(f, source_binding=source.binding()) for f in self.forms]
                r = self.gate(forms, {ident: source}, lambda _: None).release(
                    'offline-bad-source', 'es', self.claims(forms), SCOPE, fixture_mode=True)
                self.assertEqual(r['reason'], 'source_language_not_verified')
                self.assertEqual(r['status'], 'withheld')
                self.assertIsNone(r['primary'])
        self.assertEqual(self.calls, [])

    def test_source_guard_rejects_changed_english_even_with_accepting_judge(self):
        self.response = deepcopy(self.response)
        self.response['answer'] += ' Vote YES.'
        f = self.forms[0]
        r = self.gate([f]).release('offline-advice', 'es', self.claims([f]), SCOPE, fixture_mode=True)
        self.assertEqual(r['reason'], 'english_release_rejected')
        self.assertEqual(self.calls, [])

    def test_partial_forms_cannot_cover_complete_accepted_display(self):
        self.response = EvidenceLoop(self.corpus).answer('What is the COMBAT tax rate and how long would it last?')
        units = assistant_texts(self.response)
        self.assertEqual(len(units), 16)
        self.assertFalse(all(any(f.english == unit for f in self.forms) for unit in units))
        def whole_display_check(envelope):
            if release_block(self.response, self.corpus): return 'source_guard'
            return None if [c['english'] for c in envelope['claims']] == units else 'incomplete_coverage'
        r = self.gate(english_check=whole_display_check).release(
            'offline-full-display', 'es', self.claims(), SCOPE, fixture_mode=True)
        self.assertEqual(r['reason'], 'english_release_rejected')
        self.assertEqual(self.calls, [])

    def test_production_fixture_holds_before_any_paid_review(self):
        f = self.forms[0]
        op = SourceOperation('source-operation', 'a' * 64, 1, 1)
        r = self.gate([f], current=lambda _: True).release(
            'offline-production-attempt', 'es', self.claims([f]), SCOPE, operation=op)
        self.assertEqual(r['reason'], 'translation_not_verified')
        self.assertEqual(self.calls, [])

    def test_english_projection_is_rechecked_after_slow_review(self):
        f = self.forms[0]
        def changed(resource, request):
            self.response['answer'] = 'An unsupported tax claim.'
            return self.transport(resource, request)
        self.review = TranslationDecisionsCheck(changed)
        r = self.gate([f]).release('offline-changed-answer', 'es', self.claims([f]), SCOPE, fixture_mode=True)
        self.assertEqual(r['reason'], 'english_release_rejected')
        self.assertIsNone(r['primary'])
        self.assertEqual(len(self.calls), 1)

if __name__ == '__main__': unittest.main()
