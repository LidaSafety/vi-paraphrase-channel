#!/bin/zsh
# Track 2.1 extension end to end: stimuli, episodes (both agents), pooled task table, report.
set -e
cd "$(dirname "$0")/.."
M=.venv/bin/modal; PY=.venv/bin/python
c() { git add -A && git commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && echo "committed: $1"; }

echo "== ext stimuli"; $M run scripts/modal_stimuli.py --items ext 2>&1 | grep -E "items|gate |CONTROLS|FAILED|Error"
$PY -c "from src import prompts as P; from src.episode import load_items, load_stimuli; print(P.assert_prompt_controls(load_items('ext'), load_stimuli('ext')))"
c "Ext stimuli (Track 2.1)"

echo "== ext episodes"
for a in gemini qwen; do $M run scripts/modal_collect.py --items ext --agent $a --confirm 2>&1 | grep -E "wrote|failed|Error" & done; wait
for a in gemini qwen; do
  n=$($PY -c "import json;print(sum(1 for l in open('data/episodes/ext_episodes_$a.jsonl') if '_meta' not in l))")
  echo "$a: $n of 432"
  if [ "$n" -lt 432 ]; then $M run scripts/modal_collect.py --items ext --agent $a --resume --confirm 2>&1 | grep -E "wrote|failed|Error"; fi
done
c "Ext episodes, gemini and qwen"

echo "== pooled task table"
for a in gemini qwen; do
  $PY analysis/analyze.py --agent $a --tag tasks \
    --episodes data/episodes/episodes_$a.jsonl,data/episodes/workflow_episodes_$a.jsonl,data/episodes/ext_episodes_$a.jsonl | tail -1
done
./paper/build.sh
c "Track 2.1 pooled task results (8 scenarios per family), report and PDF"
echo "== DONE"
