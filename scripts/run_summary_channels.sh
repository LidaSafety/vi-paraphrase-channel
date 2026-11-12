#!/usr/bin/env bash
# Agents on the four summary channels (market set), both agents in parallel; data committed per agent.
set -uo pipefail
cd "$(dirname "$0")/.."
for a in gemini qwen; do
  ( .venv/bin/modal run scripts/modal_collect.py --agent $a --channels summaries --confirm 2>&1 | grep -E "episodes|COST|wrote|Error|Traceback"
    git add data/episodes/summary_episodes_$a.jsonl && git commit -q -m "summary-channel episodes: $a" ) &
done
wait
echo "== DONE"
