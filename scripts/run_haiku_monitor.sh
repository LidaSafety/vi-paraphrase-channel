#!/bin/zsh
# Second monitor: Claude Haiku 5.5 on every episode set, all views. Local (key in .env).
set -e
cd "$(dirname "$0")/.."
ENV=/Users/coherenteyes/agent-collusion-bench/.env
c() { git add -A && git commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "committed: $1"; }
for a in gemini qwen; do
  for f in data/episodes/episodes_$a.jsonl data/episodes/workflow_episodes_$a.jsonl; do
    .venv/bin/modal run scripts/modal_monitor.py --episodes $f --monitor haiku --views all --local-env $ENV --confirm 2>&1 | grep -E "calls|wrote|Error|Traceback"
  done
  c "Haiku monitor on $a episodes (market and workflow, all views)"
  .venv/bin/python analysis/analyze.py --agent $a --tag main | tail -1
  .venv/bin/python analysis/analyze.py --agent $a --episodes data/episodes/workflow_episodes_$a.jsonl --tag workflow | tail -1
done
c "Stats with the Haiku monitor"
echo "== DONE"
