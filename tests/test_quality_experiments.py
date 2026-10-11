"""Gate algebra/identity tests use explicit synthetic contract fixtures, no APIs."""
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from strands_quality.experiments import (Configuration, Case, Observation, CRITICAL, QUALITY,
    canonical, fingerprint, freeze, load_frozen, run_frozen, promotion_gate, promote, rollback)

HASH = 'a' * 64


def config(name='baseline', execution='exact_source'):
    return Configuration(name, execution, 'none' if execution == 'exact_source' else 'openai',
                         'no-model' if execution == 'exact_source' else 'contract-unit-fixture',
                         HASH, HASH, HASH, HASH, HASH)


def cases(human=False):
    origin = 'human_reviewed' if human else 'agent_authored'
    return [Case('known', 'regression', 'combat-rate', 'What is COMBAT rate?', 'answered',
                 ('rate',), label_origin=origin),
            Case('new', 'heldout', 'amendment-scope', 'A synthetic new scoped fixture',
                 'insufficient_evidence', label_origin=origin)]


def runner(conf, case):
    # This observation is unit-test data, not a real run or forged tool trace.
    return Observation(conf.execution, case.expected_status, case.expected_facets,
        case.expected_evidence, {k: True for k in CRITICAL}, {k: True for k in QUALITY},
        10 if conf.name == 'prior' else 5, .002 if conf.name == 'prior' else .001,
        {'config_sha256': conf.sha256, 'execution': conf.execution, 'finalized': True})


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'suite.json'

    def decision(self, result, conf):
        prior = next((r['config_sha256'] for r in result['reports'] if r['name'] == 'prior'), None)
        return promotion_gate(self.path, result, conf.sha256, max_case_latency_ms=20,
                              max_total_estimated_cost_usd=.1, baseline_hash=prior)

    def test_frozen_split_and_consumption_reject_tampering_and_repeat(self):
        conf = config()
        freeze(self.path, [conf], cases())
        result = run_frozen(self.path, runner)
        self.assertTrue(result['heldout_consumed'])
        self.assertFalse(result['population_reliability_claim'])
        self.assertIsNone(result['reports'][0]['latency_p95_ms'])
        serialized = json.dumps(result)
        self.assertNotIn('What is COMBAT', serialized)
        with self.assertRaises(FileExistsError): run_frozen(self.path, runner)
        manifest = json.loads(self.path.read_text())
        manifest['cases'][0]['prompt'] = 'Changed after freeze'
        self.path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError): load_frozen(self.path)

    def test_group_leakage_prior_exposure_and_identical_trials_rejected(self):
        overlap = [cases()[0], replace(cases()[1], group='combat-rate')]
        with self.assertRaises(ValueError): freeze(self.path, [config()], overlap)
        with self.assertRaises(ValueError): replace(cases()[1], heldout_prior_exposure=True)
        with self.assertRaises(ValueError): freeze(self.path, [config(), config('same-behavior')], cases())

    def test_fallback_does_not_count_as_real_and_partial_failure_consumes_split(self):
        conf = config(execution='real_api')
        freeze(self.path, [conf], cases())
        with self.assertRaises(ValueError):
            run_frozen(self.path, lambda c, q: Observation('exact_source', q.expected_status))
        with self.assertRaises(FileExistsError): run_frozen(self.path, runner)

    def test_unknown_quality_offline_execution_and_agent_labels_block_promotion(self):
        conf = config()
        freeze(self.path, [conf], cases())
        result = run_frozen(self.path, lambda c,q: replace(runner(c,q), quality={'clarity': None}))
        decision = self.decision(result, conf)
        self.assertFalse(decision['eligible'])
        self.assertIn('real_api_evidence_required', decision['reasons'])
        self.assertIn('human_review_required', decision['reasons'])
        self.assertIn('quality_failed_or_unknown', decision['reasons'])

    def test_receipt_mismatch_is_not_silently_accepted(self):
        freeze(self.path, [config()], cases())
        with self.assertRaises(ValueError):
            run_frozen(self.path, lambda c,q: replace(runner(c,q), receipt={'execution':c.execution}))

    def test_gate_rejects_missing_cases_critical_failure_missing_cost_and_tail(self):
        conf = config(execution='real_api')
        prior = replace(config('prior', execution='real_api'), prompt_sha256='b'*64)
        freeze(self.path, [prior,conf], cases(human=True))
        result = run_frozen(self.path, runner)
        self.assertTrue(self.decision(result, conf)['eligible'])  # Gate algebra only.
        row = result['reports'][1]['cases'][0]
        row['critical']['source_binding'] = False
        row['latency_ms'] = 100
        result['reports'][1]['estimated_cost_usd'] = None
        decision = self.decision(result, conf)
        self.assertIn('critical_boundary_failed_or_unknown', decision['reasons'])
        self.assertIn('latency_missing_or_over_bound', decision['reasons'])
        self.assertIn('estimated_cost_missing_or_over_bound', decision['reasons'])
        result['reports'][1]['cases'].pop()
        self.assertIn('case_set_mismatch', self.decision(result, conf)['reasons'])

    def test_reviewed_local_registry_promotion_stale_write_and_rollback(self):
        conf = config(execution='real_api')
        prior = replace(config('prior', execution='real_api'), prompt_sha256='b'*64)
        freeze(self.path, [prior,conf], cases(human=True))
        decision = self.decision(run_frozen(self.path, runner), conf)
        registry = self.path.parent / 'registry.json'
        registry.write_text(canonical({'version':1,'current':prior.sha256,'previous':None}))
        with self.assertRaises(ValueError):
            promote(registry, candidate_hash=conf.sha256, decision=decision,
                    reviewer_approved=False, expected_current_hash=prior.sha256)
        promote(registry, candidate_hash=conf.sha256, decision=decision,
                reviewer_approved=True, expected_current_hash=prior.sha256)
        with self.assertRaises(ValueError):
            promote(registry, candidate_hash=conf.sha256, decision=decision,
                    reviewer_approved=True, expected_current_hash=prior.sha256)
        rollback(registry, expected_current_hash=conf.sha256)
        self.assertEqual(json.loads(registry.read_text())['current'], prior.sha256)

    def test_bad_config_and_nonfinite_metrics_rejected(self):
        with self.assertRaises(ValueError): replace(config(), max_turns=True)
        with self.assertRaises(ValueError): replace(config(), retry_attempts=6)
        with self.assertRaises(ValueError): Observation('exact_source','answered', latency_ms=float('nan'))

    def test_runner_cannot_mutate_frozen_case_scope(self):
        freeze(self.path, [config()], cases())
        def mutate(c,q):
            q.scope['authority'] = 'KCEB'
            return runner(c,q)
        with self.assertRaises(ValueError): run_frozen(self.path, mutate)
