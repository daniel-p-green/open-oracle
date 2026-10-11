"""Run fixed offline contracts and emit sanitized proof in an explicit output folder."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', required=True)
    parser.add_argument('--language-root')
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    repo = Path(args.repo_root).resolve()
    sys.path.insert(1, str(repo))
    from oracle_pipeline_evals.suite import PipelineSuite
    from oracle_pipeline_evals.literacy import fixtures, diagnostics, decisions_request
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    dependencies = ['open_oracle/engine.py', 'open_oracle/quality_policy.py', 'open_oracle/claim_bindings.py',
                    'open_oracle/session_control.py', 'open_oracle/openai_integrations.py', 'open_oracle/readability.py',
                    'scripts/live-ws/ws-buffer.cjs', 'web/live.js', 'tests/test_completion_bridge.py',
                    'tests/test_evidence_completion.py', 'tests/fixtures/evidence_completion_source_map.json',
                    'strands_quality/research_agent.py', 'strands_quality/evidence_completion.py']
    dependency_paths = [repo / path for path in dependencies]
    if args.language_root:
        language = Path(args.language_root).resolve()
        for name in ('language_capabilities.py', 'language_session.py', 'language_routing.py',
                     'translation_validation.py', 'language_fixtures.py', 'explanation_styles.py'):
            path = language / name
            dependency_paths.append(path)
        for path in (language.parent / 'fixtures').glob('*.json'):
            dependency_paths.append(path)
    pins = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in dependency_paths}
    report = PipelineSuite(repo, args.language_root).run()
    after = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in dependency_paths}
    if pins != after:
        raise RuntimeError('dependency_changed_during_eval_rerun_required')
    report['dependencies'] = pins
    report['dependency_claim'] = 'listed dependencies unchanged before/after run; re-run after final integration; not a complete build attestation'
    (output / 'pipeline-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    literacy = [{'language': row['language'], 'explanation_style': row['explanation_style'],
                 'candidate_status': row['validation'], 'meaning_review': 'unrun',
                 'translation_review': 'unrun', 'production_release': 'withheld',
                 'diagnostics': diagnostics(row)} for row in fixtures()['styles']]
    (output / 'literacy-diagnostics.json').write_text(json.dumps(literacy, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    requests = [decisions_request(row) for row in fixtures()['styles']]
    (output / 'literacy-decisions-drafts.json').write_text(json.dumps({'execution': 'not_run', 'paid_calls': 0,
            'automatic_retry': False, 'rubric_version': 'literacy-meaning-v1', 'requests': requests},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'summary': report['summary'], 'external_model_calls': 0, 'paid_calls': 0,
                      'media_capture_or_playback': False, 'production_readiness': 'not_established'}))
    return 1 if report['summary']['fail'] or report['summary']['blocked'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
