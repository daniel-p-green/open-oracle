import json
from pathlib import Path
import unittest

from open_oracle.readability import (analyze_readability, build_readability_tool,
                                     formula_scores, measure_span, sentences)


class ReadabilityTests(unittest.TestCase):
    def test_hand_counted_fixture_and_formulas(self):
        result = analyze_readability("The cat sat on the mat.", "Hand-counted English fixture")
        self.assertEqual({k: result['counts'][k] for k in ('words', 'sentences', 'syllables')},
                         {'words': 6, 'sentences': 1, 'syllables': 6})
        self.assertEqual(result['scores'], {'flesch_reading_ease': 116.145, 'flesch_kincaid_grade_level': -1.45})
        self.assertEqual(formula_scores(100, 5, 150), {'flesch_reading_ease': 59.635, 'flesch_kincaid_grade_level': 9.91})

    def test_scores_not_clipped_or_rounded_to_whole_grades(self):
        self.assertLess(formula_scores(100, 1, 250)['flesch_reading_ease'], 0)
        self.assertGreater(formula_scores(100, 1, 250)['flesch_kincaid_grade_level'], 40)

    def test_empty_and_punctuation_return_null_not_zero(self):
        for text in ('', ' \n ', '...?! ●'):
            result = analyze_readability(text, 'Empty fixture')
            self.assertEqual(result['status'], 'empty')
            self.assertIsNone(result['scores'])
            self.assertIsNone(result['counts'])

    def test_sentence_boundaries_abbreviations_decimals_semicolons(self):
        text = 'Shall Dr. Smith pay 1.5 dollars under House Bill No. 1 in the U.S.? Yes; only if approved.'
        self.assertEqual(len(sentences(text)), 2)
        self.assertEqual(len(sentences('A. B. Smith agrees. The cat sleeps!')), 2)
        self.assertEqual(len(sentences('a. cats run.')), 2)
        self.assertEqual(len(sentences('One; two; three?')), 1)

    def test_short_text_numerals_compounds_and_contractions(self):
        result = analyze_readability("Don't tax voter-approved sales at 80% or 1.5 dollars.", 'Counting fixture')
        self.assertEqual(result['counts']['words'], 10)
        self.assertEqual([t['token'] for t in result['token_audit'] if t['basis'] == 'numeric_placeholder'], ['80%', '1.5'])
        self.assertTrue(any('short_text' in w for w in result['warnings']))
        self.assertTrue(any('numbers:' in w for w in result['warnings']))

    def test_cleanup_preserves_raw_and_does_not_delete_conditions(self):
        raw = '●Allow abortions\n (under twelve-weeks’ gestation);\n●preserve consent?'
        result = analyze_readability(raw, 'Preservation fixture')
        self.assertEqual(result['raw_text'], raw)
        self.assertIn("(under twelve-weeks' gestation)", result['scored_text'])
        self.assertEqual([a['operation'] for a in result['cleaning_audit']],
                         ['curly_apostrophes_to_ascii', 'bullet_glyphs_to_spaces', 'collapse_whitespace'])
        self.assertNotEqual(result['raw_text_sha256'], result['scored_text_sha256'])

    def test_fragment_ocr_and_unknown_word_warn(self):
        result = analyze_readability('shallJackson pay zzzxx', 'OCR fixture', extraction_method='ocr_unreviewed')
        self.assertTrue(any('extraction_review' in w for w in result['warnings']))
        self.assertTrue(any('out_of_dictionary' in w for w in result['warnings']))
        self.assertIn('unterminated_fragment_counted_as_sentence', result['warnings'])
        self.assertEqual(result['scored_text'], 'shallJackson pay zzzxx')

    def test_non_english_rejected_and_size_bounded(self):
        for text, lang in [('¿Debe aprobarse?', 'es'), ('Vote yes.', 'es'), ('Votación', 'en')]:
            result = analyze_readability(text, 'Language fixture', language=lang)
            self.assertEqual(result['status'], 'unsupported_language')
            self.assertIsNone(result['scores'])
        with self.assertRaises(ValueError): analyze_readability('x' * 20001, 'Too large')
        with self.assertRaises(ValueError): analyze_readability('Vote.', '')

    def test_span_selection_keeps_follow_on_legal_condition(self):
        raw = 'QUESTION # 1\nShall the tax continue? Proceeds shall go to a separate trust fund.\nYES NO'
        question, start, end = measure_span(raw, 'question')
        self.assertIn('separate trust fund', question)
        self.assertEqual(raw[start:end], question)
        with self.assertRaises(ValueError): measure_span(raw, 'fiscal_summary')
        raw = 'AMENDMENT\nShall it pass?\nState and local governmental entities estimate no costs or savings.\nYES NO'
        self.assertEqual(measure_span(raw, 'question')[0].strip(), 'Shall it pass?')
        self.assertTrue(measure_span(raw, 'fiscal_summary')[0].startswith('State and local'))
        raw = 'Shall it pass?\nState and local government entities estimate no costs or savings.\nYES NO'
        self.assertEqual(measure_span(raw, 'question')[0].strip(), 'Shall it pass?')
        self.assertTrue(measure_span(raw, 'fiscal_summary')[0].startswith('State and local government entities'))

    def test_wrapper_cannot_replace_bound_evidence_or_score_candidate(self):
        class Corpus:
            contests = {'m': {'kind': 'measure', 'title': 'Measure M'}, 'c': {'kind': 'candidate'}}
            def read(self, ident, scope):
                if ident == 'm': return {'text': 'Shall it pass? YES NO', 'contest_id': 'm'}
                if ident == 'c': return {'text': 'A candidate roster', 'contest_id': 'c'}
        tool = build_readability_tool(Corpus())
        self.assertEqual(tool(evidence_id='m')['scored_text'], 'Shall it pass?')
        with self.assertRaises(ValueError): tool(evidence_id='m', text='Replacement')
        with self.assertRaises(ValueError): tool(evidence_id='c')
        with self.assertRaises(ValueError): tool(evidence_id='unknown')


class ActualSDKTests(unittest.TestCase):
    def test_strands_schema_and_actual_tool_execution_without_model(self):
        from strands import Agent
        from strands.models import Model

        class OfflineContractModel(Model):
            def update_config(self, **kwargs): pass
            def get_config(self): return {'model_id': 'offline-readability-contract', 'context_window_limit': 128000}
            async def structured_output(self, *args, **kwargs):
                raise AssertionError('No structured-output call expected')
                yield
            async def stream(self, messages, **kwargs):
                raise AssertionError('No model inference permitted')
                yield

        tool = build_readability_tool()
        schema = tool.tool_spec
        self.assertEqual(schema['name'], 'test_ballot_readability')
        self.assertEqual(schema['inputSchema']['json']['properties']['text']['type'], 'string')
        agent = Agent(model=OfflineContractModel(), tools=[tool], callback_handler=None)
        result = agent.tool.test_ballot_readability(text='The cat sat on the mat.', label='SDK fixture')
        self.assertEqual(result['status'], 'success')
        content = json.loads(result['content'][0]['text'])
        self.assertEqual(content['counts']['words'], 6)
        self.assertFalse(content['exact_ballotpedia_score'])
        self.assertEqual(content['provenance']['provenance_status'], 'caller_asserted_unverified')


class OfficialKCEBFixtureTests(unittest.TestCase):
    def test_all_six_complete_questions_and_five_separate_fiscal_spans(self):
        fixtures = json.loads((Path(__file__).parent / 'fixtures/kceb_policy_spans.json').read_text())
        self.assertEqual(len(fixtures), 11)
        expected = {'amendment-3': (52, 1, 117), 'amendment-6': (81, 1, 166),
                    'amendment-7': (46, 1, 93), 'amendment-8': (48, 1, 85),
                    'proposition-a': (42, 1, 76), 'combat': (92, 2, 152)}
        questions = {}
        for fixture in fixtures:
            result = analyze_readability(fixture['raw_text'], fixture['measure_id'], fixture['provenance'])
            self.assertEqual(fixture['provenance']['page'], 7 if fixture['measure_id'] in
                             ('amendment-3', 'amendment-6', 'amendment-7') else 8)
            self.assertNotIn('INSTRUCTIONS', result['scored_text'])
            self.assertNotIn('YES', result['scored_text'])
            self.assertFalse(result['exact_ballotpedia_score'])
            self.assertEqual(result['factual_fidelity_status'], 'not_evaluated')
            if fixture['span'] == 'question':
                questions[fixture['measure_id']] = result['scored_text']
                self.assertEqual(tuple(result['counts'][k] for k in ('words', 'sentences', 'syllables')),
                                 expected[fixture['measure_id']])
        self.assertEqual(set(questions), set(expected))
        self.assertIn("(under twelve-weeks' gestation)", questions['amendment-3'])
        self.assertIn('without approval from at least 80% of both chambers', questions['amendment-6'])
        self.assertIn('once the fund generates sufficient revenue to replace them', questions['amendment-7'])
        self.assertIn('separate from the general fund or any other county funds', questions['combat'])
        self.assertIn('period of ten years', questions['combat'])


if __name__ == '__main__':
    unittest.main()
