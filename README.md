# Would it have done that anyway?

Evidence of collusion between LLM agents, tested in Vietnamese. Track 2 of the
Apart AI Collusion Research Sprint.

A scripted rival invites an AI agent into a deal that hurts a third party,
such as holding a price, padding a budget or rigging a bid. The agent chooses,
reports to its owner, and a monitor reads the log. We ask which tasks lead to
collusion (2.1), whether combining what agents say with what they do helps
detection (2.2), and what should count as convincing evidence (2.3). Every
harmful deal has a harmless twin as a positive control.

Design and change log: [`docs/execution-plan.md`](docs/execution-plan.md).
Status: data collected, exploratory (no preregistration). The paper is kept
out of the repository; `analysis/paper.py` writes its numbers, tables and
figures to a local `paper/` folder.

## Roles

| Role | Model |
|---|---|
| Rival | scripted; messages written once and frozen in `data/stimuli*/` |
| Relay (paraphrase, neutralize, summarize) | Qwen3-8B, frozen |
| Executor (the agent) | Gemini 2.5 Flash, Qwen3-8B |
| Summarizer (trace to activity log) | Gemma-3-27B |
| Monitor | Mistral Small 3.1 24B, Claude Haiku 5.5 |

Every episode measure is coded in code. The monitors' verdicts are the object
studied, not a measure.

## Experiments

- **Main study.** Four turns: choose, read the rival's message, report to the
  owner, answer a yes/no disclosure question. Four renderings of each
  invitation; raw, paraphrased, neutralized and summarized channels.
- **Monitor views.** The same episodes judged from the action, the report, the
  message, the full trace, a summary of it, and with a deployable baseline
  (the agent's choices on similar situations).
- **Initiation probe.** No invitation; the agent may send the proposal, a
  greeting or nothing (fixed options), then choose.
- **Relationship probe.** Market items with one added sentence: the two owners
  are old friends, or have never met.

## Run order

```bash
python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q                                   # controls and scoring
.venv/bin/python scripts/build_items.py --set market|workflow|ext
caffeinate -i .venv/bin/modal run scripts/modal_stimuli.py --items <set>
caffeinate -i .venv/bin/modal run scripts/modal_collect.py --items <set> --agent gemini|qwen --confirm
caffeinate -i .venv/bin/modal run scripts/modal_monitor.py --episodes <file> --monitor mistral|haiku --views all --confirm
caffeinate -i .venv/bin/modal run scripts/modal_initiate.py --agent gemini|qwen --confirm
caffeinate -i .venv/bin/modal run scripts/modal_relation.py --agent gemini|qwen --confirm
.venv/bin/python analysis/analyze.py --agent <agent> --episodes <file[,file]> --tag <tag>
./paper/build.sh                                                # numbers, tables, figures, PDF, page check
```

Model calls run on Modal; keys live in Modal secrets. Wrap long runs in
`caffeinate -i`: an idle-sleeping laptop cancels a Modal run.

## Layout

```text
src/        prompts, episode runners (main, initiate, relation), scoring, schema, clients
scripts/    item builder, Modal runners, gate scoring, readers, translation
analysis/   stats (analyze, setting, initiate, pathways, relation), figures, paper macros
data/       items, frozen stimuli, episodes, monitor verdicts, summaries, translations, archive
share/      one-page results summary (share/index.html)
docs/       execution plan and change log
paper/      local only, not committed
```

`share/index.html` is the project page. Regenerate it with `.venv/bin/python analysis/share_page.py`
after `./paper/build.sh`; `.github/workflows/pages.yml` publishes `share/` to GitHub Pages on push.
