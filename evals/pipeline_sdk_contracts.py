"""Canonical completion bridge tests through actual Strands SDK, authored model.

Separate child with no credentials and denied sockets. No production provider
construction or invocation. Owner test names are a frozen seam, not silently discovered.
"""
import importlib
import json
from pathlib import Path
import sys
import unittest
import time

stage = Path(__file__).resolve().parents[1]
repo = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(stage), str(repo), str(repo / 'tests')]
from oracle_pipeline_evals.suite import offline

METHODS = {
    'same_agent': 'test_same_agent_existing_cited_answer_all_three_fact_bindings',
    'missing_context': 'test_missing_context_keeps_ballot_fact_and_explicit_two_gaps',
    'default_off': 'test_default_request_does_not_expose_completion_tools',
    'cross_fact': 'test_cross_fact_issued_id_cannot_bridge_claim',
    'cancelled': 'test_cancellation_before_dispatch_blocks_source_and_model',
    'token_cap': 'test_shared_token_limit_holds_before_additional_source_work',
    'model_cap': 'test_shared_model_limit_holds_before_expansion',
    'provisional_scope': 'test_provisional_ballot_read_cannot_become_legal_finding',
}


def main():
    cases = json.loads(sys.stdin.read())
    output = []
    with offline():
        module = importlib.import_module('test_completion_bridge')
        if Path(module.__file__).resolve().parent != repo / 'tests':
            raise ValueError('owner_test_import_mismatch')
        for case in cases:
            start = time.monotonic()
            test = module.CompletionBridgeTests(METHODS[case['operation']])
            requests = []
            original_request = test.request
            def captured_request(*args, **kwargs):
                request = original_request(*args, **kwargs)
                requests.append(request)
                return request
            test.request = captured_request
            result = unittest.TestResult()
            test.run(result)
            # Never serialize exception messages, inputs, citations or model content.
            output.append({'case_id': case['id'], 'actual': 'sdk_contract_pass' if result.wasSuccessful()
                           and result.testsRun == 1 else 'sdk_contract_fail',
                           'elapsed_ms': (time.monotonic()-start)*1000,
                           'synthetic_sdk': {'model_dispatches': sum(r.model_calls for r in requests) if requests else None,
                               'tool_events': sum(len(r.receipt.snapshot().get('tool_events', [])) for r in requests) if requests else None,
                               'requests': len(requests) if requests else None}})
    sys.stdout.write(json.dumps(output))


if __name__ == '__main__':
    main()
