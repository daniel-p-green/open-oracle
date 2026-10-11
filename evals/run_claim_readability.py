"""Offline only: deny network, run authored cases and existing Strands tool."""
import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import socket
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def denied(*args, **kwargs):
    raise AssertionError('External network forbidden in offline eval')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--styles', type=Path, default=ROOT / 'fixtures/literacy_styles.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with ExitStack() as stack:
        for name in ('connect', 'connect_ex'):
            stack.enter_context(patch.object(socket.socket, name, denied))
        stack.enter_context(patch.object(socket, 'create_connection', denied))
        stack.enter_context(patch.object(socket, 'getaddrinfo', denied))
        from open_oracle.corpus import Corpus
        from oracle_eval_extensions.eval_suite import run_case
        from oracle_eval_extensions.readability_outputs import run_fixture_matrix
        corpus = Corpus()
        catalog = json.loads((ROOT / 'evals/claim_readability_cases.json').read_text())
        results = [run_case(corpus, case) for case in catalog['cases']]
        styles = args.styles.read_bytes()
        matrix = run_fixture_matrix(json.loads(styles))
        report = {'contract_cases': results, 'passed': sum(x['pass'] for x in results),
                  'total': len(results), 'readability_matrix': matrix,
                  'style_fixture_sha256': hashlib.sha256(styles).hexdigest(),
                  'execution': 'offline_contracts_actual_sdk_tool', 'paid_calls': 0,
                  'live_decisions_calls': 0, 'model_inference_calls': 0,
                  'formula_tool_invocations': len(matrix), 'threshold': 0.95,
                  'calibration': 'not_validated', 'human_comprehension': 'not_measured',
                  'production_release_authorized': False, 'raw_data': 'authored_public_fixtures_only'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    print(json.dumps({k: report[k] for k in ('passed', 'total', 'formula_tool_invocations', 'paid_calls')}))
    return 0 if report['passed'] == report['total'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
