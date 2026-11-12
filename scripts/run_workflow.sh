#!/bin/zsh
# Rebuild and rerun the whole workflow set, end to end. Run under caffeinate -i.
set -e
cd "$(dirname "$0")/.."
M=.venv/bin/modal; PY=.venv/bin/python
c() { git add -A && git commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "committed: $1"; }

echo "== stimuli"; $M run scripts/modal_stimuli.py --items workflow 2>&1 | grep -E "items|gate |CONTROLS|FAILED|Error"
$PY -c "from src import prompts as P; from src.episode import load_items, load_stimuli; print(P.assert_prompt_controls(load_items('workflow'), load_stimuli('workflow')))"
c "Workflow v2 stimuli (review_ring fixed)"

echo "== episodes"
for a in gemini qwen; do $M run scripts/modal_collect.py --items workflow --agent $a --confirm 2>&1 | grep -E "wrote|failed|Error" & done; wait
for a in gemini qwen; do
  n=$($PY -c "import json;print(sum(1 for l in open('data/episodes/workflow_episodes_$a.jsonl') if '_meta' not in l))")
  echo "$a: $n of 240"
  if [ "$n" -lt 240 ]; then $M run scripts/modal_collect.py --items workflow --agent $a --resume --confirm 2>&1 | grep -E "wrote|failed|Error"; fi
done
c "Workflow v2 episodes, gemini and qwen"

echo "== monitors"
for a in gemini qwen; do $M run scripts/modal_monitor.py --episodes data/episodes/workflow_episodes_$a.jsonl --monitor gemini --views all --confirm 2>&1 | grep -E "wrote|Error" & done; wait
c "Workflow v2 monitors (gemini, all views)"

echo "== analysis"
for a in gemini qwen; do $PY analysis/analyze.py --agent $a --episodes data/episodes/workflow_episodes_$a.jsonl --tag workflow | tail -1; done
./paper/build.sh
c "Workflow v2 results, report and PDF"
echo "== DONE"
