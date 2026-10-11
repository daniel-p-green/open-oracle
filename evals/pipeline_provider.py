"""Promptfoo fixed offline case IDs. No prompts/visitor text/provider construction."""
import json
from pathlib import Path
import sys

STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE))


def call_api(prompt, options, context):
    from oracle_pipeline_evals.suite import PipelineSuite
    config = options.get('config', {})
    case_id = context.get('vars', {}).get('case_id')
    if not isinstance(case_id, str) or prompt != case_id:
        raise ValueError('fixed_case_id_required')
    suite = PipelineSuite(config['repo_root'], config.get('language_root'))
    report = suite.run([case_id])
    row = report['results'][0]
    return {'output': json.dumps(row, ensure_ascii=False, allow_nan=False), 'numRequests': 0,
            'tokenUsage': {'total': 0, 'prompt': 0, 'completion': 0},
            'metadata': {'evidence_tier': 'synthetic', 'external_model_calls': 0,
                         'paid_calls': 0, 'readiness': 'not_established'}}
