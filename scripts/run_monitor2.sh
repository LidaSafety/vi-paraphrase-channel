#!/usr/bin/env bash
# Second monitor (MON, default mistral) on every episode file and every view the paper reports (2026-10-26).
# One job per (file, view); three jobs at a time against a vLLM app allowed three GPUs;
# largest jobs first so the three GPUs stay busy. Verdicts are committed once at the end.
set -uo pipefail
cd "$(dirname "$0")/.."
{
  for f in episodes_gemini episodes_qwen; do
    for v in all standard baseline_info pop_baseline family_baseline summary; do echo "$f $v"; done
  done
  echo "summary_episodes_gemini channel"; echo "summary_episodes_qwen channel"
  for f in workflow_episodes_gemini workflow_episodes_qwen; do
    for v in all standard baseline_info pop_baseline family_baseline summary; do echo "$f $v"; done
  done
} | xargs -P 3 -L 1 sh -c '.venv/bin/modal run scripts/modal_monitor.py --monitor ${MON:-mistral} --confirm --episodes data/episodes/$0.jsonl --views $1 2>&1 | grep -E "wrote|Error|Traceback" | sed "s#^#[$0 $1] #"'
git add data/monitor && git commit -q -m "${MON:-mistral} monitor verdicts: all files and views" || true
echo "== DONE"
