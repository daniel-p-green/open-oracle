"""Ground-truth passages and actual SDK tool orchestration; no network or inference."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from open_oracle.corpus import Corpus
from open_oracle.demo_sources import CONTEST, ROOT, QUESTIONS, comparison_parts, load, requested_topic
from open_oracle.engine import EvidenceLoop
from open_oracle.orchestration import select_with_strands
from open_oracle.server import make_server
from test_strands import OfflineToolModel


class DemoPathsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = Corpus()
        if not cls.corpus.prepared_sources_ready:
            raise RuntimeError('Prepare inspected sources with python -m open_oracle.prepare_sources first')

    def test_both_paths_through_actual_strands_sdk(self):
        cases = [('Explain COMBAT', 'combat', {}, ['combat:jceb-sample'], 'measure_explanation'),
                 ('Compare Pollard and Fields priorities', CONTEST, {'_comparison_topic': 'issues'},
                  [CONTEST + ':beacon:issues:pollard', CONTEST + ':beacon:issues:fields'], 'candidate_comparison')]
        for question, contest, scope, ids, card_type in cases:
            def selector(q, s, ident, c):
                return select_with_strands(OfflineToolModel(contest_id=contest, evidence_ids=ids), q, s, ident, c, execution='offline_stub')
            response = EvidenceLoop(self.corpus, selector=selector).answer(question)
            self.assertEqual(response['status'], 'answered', response)
            self.assertEqual(response['card']['type'], card_type)
            self.assertEqual([e['id'] for e in response['evidence']], ids)
            self.assertEqual([s['tool'] for s in response['trace']], ['resolve_contest', 'search_evidence'] + ['read_evidence'] * len(ids))
            self.assertTrue(all(not s['live'] and s['provider_execution'] == 'offline_stub' for s in response['trace']))

    def test_comparison_preserves_full_same_question_answers_and_attribution(self):
        for query, topic in [('Compare Pollard and Fields priorities', 'issues'),
                             ('Compare Pollard and Fields property taxes', 'property'),
                             ('Compare Pollard and Fields approaches to property taxes', 'property'),
                             ('Compare the differences between Pollard and Fields on property assessments', 'property')]:
            r = EvidenceLoop(self.corpus).answer(query)
            self.assertEqual(r['card']['title'], QUESTIONS[topic])
            self.assertEqual({x['candidate_name'] for x in r['card']['responses']}, {'LANCE POLLARD', 'CARLA FIELDS'})
            for response in r['card']['responses']:
                e = next(e for e in r['evidence'] if e['id'] == response['evidence_id'])
                self.assertEqual(response['quote'], e['text'])
                self.assertEqual(e['publication_date'], '2026-09-22')
                self.assertEqual(e['topic'], topic)
                self.assertEqual(e['source_category'], 'Published candidate questionnaire answer')
            if topic == 'property':
                fields = next(x for x in r['card']['responses'] if x['candidate_name'] == 'CARLA FIELDS')
                self.assertEqual(len(fields['quote'].split('\n\n')), 6)  # All six published list items, including independent review.

    def test_one_sided_wrong_topic_or_foreign_selection_never_releases_comparison(self):
        for ids in ([CONTEST + ':beacon:issues:pollard'], [CONTEST + ':beacon:property:pollard', CONTEST + ':beacon:property:fields'], ['combat:jceb-sample']):
            r = EvidenceLoop(self.corpus, selector=lambda *args: (ids, [])).answer('Compare Pollard and Fields priorities')
            self.assertEqual(r['status'], 'insufficient_evidence')
            self.assertIsNone(r['card']); self.assertEqual(r['evidence'], [])
        for query in ('Compare Pollard and Fields on climate',):
            r = EvidenceLoop(self.corpus).answer(query)
            self.assertEqual(r['status'], 'insufficient_evidence'); self.assertIsNone(r['card'])
        wrong_person = EvidenceLoop(self.corpus).answer('Compare Pollard and Peyton priorities', contest_id=CONTEST)
        self.assertIn(wrong_person['status'], ('clarification', 'insufficient_evidence'))
        self.assertIsNone(wrong_person['card']); self.assertEqual(wrong_person['claims'], [])

    def test_comparison_request_parts_preserve_unknown_and_mixed_requests(self):
        # Public handoff contract for independently accounting for requested parts.
        cases = [
            ('And property taxes?', ['property'], [], False, 'property'),
            ('Compare Pollard and Fields property taxes and climate', ['property'], ['climate'], False, None),
            ('Compare priorities and property assessments', ['issues', 'property'], [], False, None),
            ('Compare Pollard and Fields housing', [], ['housing'], True, None),
            ('Compare Pollard and Fields property taxes and housing', ['property'], ['housing'], True, None),
            ('What about climate?', [], ['climate'], False, None),
            ('And?', [], [], True, None),
        ]
        for query, topics, gaps, unclassified, legacy in cases:
            with self.subTest(query=query):
                self.assertEqual(comparison_parts(query), {'topics': topics, 'gaps': gaps, 'unclassified': unclassified})
                self.assertEqual(requested_topic(query), legacy)

    def test_prepared_archive_corruption_and_missing_files_are_source_gaps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(load(root), [])
            for name in ('beacon-atlarge.json', 'beacon-atlarge-2026-09-22.html'):
                (root / name).write_bytes((ROOT / name).read_bytes())
            self.assertEqual(len(load(root)), 4)
            p = root / 'beacon-atlarge.json'
            doc = json.loads(p.read_text()); doc['entries'][0]['candidate_name'] = 'CARLA FIELDS'
            p.write_text(json.dumps(doc)); self.assertEqual(load(root), [])

    def test_bedrock_mode_requires_openai_review(self):
        with patch('open_oracle.orchestration.build_bedrock_selector', return_value=lambda *a: ([], [])) as builder, patch('open_oracle.openai_integrations.require_live_authorization') as openai:
            server = make_server(port=0, bedrock=True)
            server.server_close()
            builder.assert_called_once(); openai.assert_called_once()
