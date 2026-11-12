#!/bin/zsh
# Track 2.3: apply the three-part evidence standard as a monitor view, both monitors, all episode sets.
set -e
cd "$(dirname "$0")/.."
ENV=/Users/coherenteyes/agent-collusion-bench/.env
FILES=(data/episodes/episodes_gemini.jsonl data/episodes/workflow_episodes_gemini.jsonl
       data/episodes/episodes_qwen.jsonl data/episodes/workflow_episodes_qwen.jsonl)
c() { git add -A && git commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "committed: $1"; }
( for f in $FILES; do .venv/bin/modal run scripts/modal_monitor.py --episodes $f --monitor gemini --views ${VIEW:-standard} --confirm 2>&1 | grep -E "calls|wrote|Error|Traceback"; done ) &
( for f in $FILES; do .venv/bin/modal run scripts/modal_monitor.py --episodes $f --monitor haiku --views ${VIEW:-standard} --local-env $ENV --confirm 2>&1 | grep -E "calls|wrote|Error|Traceback"; done ) &
wait
c "${VIEW:-standard} view (2.3), gemini and haiku monitors, all episode sets"
for a in gemini qwen; do
  .venv/bin/python analysis/analyze.py --agent $a --tag main | tail -1
  .venv/bin/python analysis/analyze.py --agent $a --episodes data/episodes/workflow_episodes_$a.jsonl --tag workflow | tail -1
done
c "Stats with the standard view"
echo "== DONE"
