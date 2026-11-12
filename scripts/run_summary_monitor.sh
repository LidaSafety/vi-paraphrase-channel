#!/usr/bin/env bash
# Both monitors on the summary-channel episodes: what the agent saw (delivered) and the original (raw).
set -uo pipefail
cd "$(dirname "$0")/.."
ENV=/Users/coherenteyes/agent-collusion-bench/.env
for a in ${AGENTS:-gemini qwen}; do
  f=data/episodes/summary_episodes_$a.jsonl
  ( .venv/bin/modal run scripts/modal_monitor.py --episodes $f --monitor gemini --views channel --confirm 2>&1 | grep -E "calls|wrote|Error" ) &
  ( .venv/bin/modal run scripts/modal_monitor.py --episodes $f --monitor haiku --views channel --local-env $ENV --confirm 2>&1 | grep -E "calls|wrote|Error" ) &
  wait
  git add data/monitor && git commit -q -m "summary-channel monitor verdicts: $a" || true
done
echo "== DONE"
