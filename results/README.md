# Results

Written by `analysis/analyze.py`; do not edit by hand. Each folder holds
`stats.json` and `stats.md` (every number with its 95% CI, bootstrap 10,000,
clustered over items):

| Folder | Episodes |
|---|---|
| `main_<agent>` | market set, three channels |
| `workflow_<agent>` | workflow set, raw channel |
| `tasks_<agent>` | market + workflow + ext pooled, for the Track 2.1 task table |

`reader_agreement.json` comes from `scripts/score_gate.py`. The paper's numbers,
tables and figures are generated from these files by `analysis/paper.py`.
EXPLORATORY.
