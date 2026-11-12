# Archive

`v0_paraphrases/` holds the first stimulus build (2026-10-25), discarded before
any episode was run. The relay copied 73 of 120 messages verbatim and the gate
said "invites" to 240 of 240 texts because its prompt named the arrangement.
See docs/execution-plan.md, "Changes". Kept as data, never read by analysis.

`v1_stimuli/` and `v1_smoke_24.jsonl` (2026-10-25) are the six-family build
whose harmful situations described the scheme itself. In the smoke the agent
took the collusive option at turn 1, before any message, in 9 of 12 harmful
episodes, so the message had nothing left to move. Discarded; kept as data,
never read by analysis.

`workflow_v1/` (2026-10-25): the first workflow build and run. `review_ring`'s
situation said "Điểm của {P} do {CP} chấm", which revealed the reciprocity and
put turn 1 at the ceiling (Gemini took the collusive option before any message
in every review_ring episode). The Qwen run was also cut short three times by
the laptop's idle sleep. Discarded; the whole workflow set was rebuilt and rerun
from scratch. Kept as data, never read by analysis.
