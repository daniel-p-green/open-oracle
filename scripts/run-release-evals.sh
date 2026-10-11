#!/bin/sh
# Offline regressions only. Live/browser/device acceptance remains separate.
set -eu
oracle_repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
oracle_eval_output=${1:-"$oracle_repo_root/evals/pipeline-offline"}
cd "$oracle_repo_root"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$oracle_repo_root"
export PROMPTFOO_DISABLE_TELEMETRY=1
export PROMPTFOO_CONFIG_DIR="$oracle_eval_output/promptfoo-config"
export OPEN_ORACLE_ALLOW_LIVE=0
mkdir -p "$oracle_eval_output"
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B evals/run_pipeline.py --repo-root "$oracle_repo_root" \
  --language-root "$oracle_repo_root/open_oracle" --output-dir "$oracle_eval_output"
promptfoo eval --config promptfooconfig.yaml --output "$oracle_eval_output/exact-source-promptfoo.json" \
  --no-cache --no-write --no-share --no-progress-bar --no-table --max-concurrency 1
promptfoo eval --config promptfoo.pipeline.yaml --output "$oracle_eval_output/pipeline-promptfoo.json" \
  --no-cache --no-write --no-share --no-progress-bar --no-table --max-concurrency 1
