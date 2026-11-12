#!/usr/bin/env bash
# Oversight via a third-party summary: summarize every episode file, then score the
# `summary` view with both monitors. Haiku runs locally with the key from .env.
set -euo pipefail
cd "$(dirname "$0")/.."
M=.venv/bin/modal
for f in episodes_gemini episodes_qwen workflow_episodes_gemini workflow_episodes_qwen; do
  $M run scripts/modal_summarize.py --episodes data/episodes/$f.jsonl --confirm
  git add data/summaries && git commit -q -m "summaries: $f" || true
done
for f in episodes_gemini episodes_qwen workflow_episodes_gemini workflow_episodes_qwen; do
  $M run scripts/modal_monitor.py --episodes data/episodes/$f.jsonl --monitor gemini --views summary --confirm
  $M run scripts/modal_monitor.py --episodes data/episodes/$f.jsonl --monitor haiku --views summary --confirm --local-env ../agent-collusion-bench/.env
  git add data/monitor && git commit -q -m "summary view verdicts: $f" || true
done
echo "== DONE"
