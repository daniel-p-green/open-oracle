"""Harness failure/privacy tests; imported application behavior tested by case suite."""
import json
import socket
import unittest
from copy import deepcopy
from oracle_pipeline_evals.contracts import measurement, project_result, release_matrix
from oracle_pipeline_evals.suite import catalog, offline, PipelineSuite, ROOT
from oracle_pipeline_evals.literacy import fixtures, find, bound, decisions_request, diagnostics


class PipelineHarnessTests(unittest.TestCase):
    def test_network_denied_without_connecting(self):
        with offline(), socket.socket() as connection:
            with self.assertRaisesRegex(RuntimeError, 'offline_network_forbidden'):
                connection.connect(('127.0.0.1', 1))

    def test_unknown_usage_never_zero(self):
        row = measurement()
        self.assertIsNone(row['calls'])
        self.assertIsNone(row['cost_usd'])
        for bad in (True, -1, float('nan')):
            with self.assertRaises(ValueError):
                measurement(calls=bad)

    def test_operational_projection_drops_private_payload(self):
        case = catalog()[0]
        row = project_result({'status': 'pass', 'elapsed_ms': 1, 'actual': 'answered',
                              'raw': 'PRIVATE_CANARY', 'provider_id': 'PRIVATE_ID'}, case)
        self.assertNotIn('PRIVATE', json.dumps(row))
        for actual in ('PRIVATE_CANARY', {'raw': 'secret'}):
            with self.assertRaises((ValueError, TypeError)):
                project_result({'status': 'pass', 'elapsed_ms': 1, 'actual': actual}, case)

    def test_synthetic_pass_never_promotes_other_tiers(self):
        case = catalog()[0]
        row = project_result({'status': 'pass', 'elapsed_ms': 1, 'actual': 'answered'}, case)
        matrix = release_matrix([row])
        self.assertEqual(len(matrix), 6)
        for language in matrix:
            self.assertFalse(language['spoken_ready'])
            for stage in language['stages'].values():
                for tier in ('live_provider', 'browser', 'physical_device'):
                    self.assertEqual(stage[tier]['status'], 'unrun')

    def test_unique_fixed_catalog_with_sign_regression_all_languages(self):
        cases = catalog()
        self.assertEqual(len(cases), len({c['id'] for c in cases}))
        self.assertEqual({c['language'] for c in cases if c['operation'] == 'speech_sign_change'},
                         {'en', 'es', 'vi', 'ar', 'zh-Hans', 'fil'})
        self.assertTrue(all(c['expected'] == 'held' for c in cases if c['operation'] == 'speech_sign_change'))

    def test_literacy_eight_candidates_same_original_bound_unreviewed(self):
        rows = fixtures()['styles']
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({r['source_fingerprint'] for r in rows}), 1)
        self.assertTrue(all(bound(row) for row in rows))
        self.assertTrue(all(row['validation'] == 'agent_authored_unreviewed' for row in rows))
        self.assertTrue(all(row['review']['meaning'] == 'unrun' for row in rows))

    def test_literacy_caveat_and_metadata_changes_held(self):
        for row in fixtures()['styles']:
            changed = deepcopy(row)
            changed['text'] = '\n\n'.join(row['layers'][:-1])
            self.assertFalse(bound(changed))
            changed = deepcopy(row)
            changed['source_original_sha256'] = '0' * 64
            self.assertFalse(bound(changed))

    def test_decisions_draft_atomic_bounded_no_unsupported_controls(self):
        request = decisions_request(find('es', 'simplest_useful'))
        self.assertEqual(set(request), {'model', 'input', 'questions'})
        self.assertEqual(len(request['questions']), 12)
        self.assertTrue(all(q['type'] == 'predicate' for q in request['questions']))
        self.assertEqual(len(request['questions']), len({q['name'] for q in request['questions']}))
        self.assertNotIn('expected', json.loads(request['input']))

    def test_readability_not_comprehension_or_spanish_english_grade(self):
        for language in ('en', 'es'):
            report = diagnostics(find(language, 'simplest_useful'))
            self.assertEqual(report['comprehension'], 'not_measured')
            self.assertTrue(report['diagnostic_only'])
            if language == 'es':
                self.assertNotIn('flesch_kincaid_grade_level', report['scores'])
                self.assertEqual(report['implementation_validation'], 'pending_reference_token_counts')

    def test_wcag_inventory_does_not_claim_automated_conformance(self):
        matrix = json.loads((ROOT / 'evals/wcag-release-matrix.json').read_text())
        self.assertEqual(matrix['target'], 'WCAG 2.2 AA web content')
        self.assertEqual(len(matrix['criteria']), 55)
        self.assertEqual(len({c['criterion'] for c in matrix['criteria']}), 55)
        self.assertTrue(all(c['result'] == 'unrun' for c in matrix['criteria']))
        self.assertTrue(all(c['final_build_sha256'] is None for c in matrix['criteria']))
        self.assertEqual(matrix['conformance'], 'not_established')


if __name__ == '__main__':
    unittest.main()
