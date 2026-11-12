# Generated statistics: qwen, workflow

Written by `analysis/analyze.py`. Do not edit. EXPLORATORY.
Cells: estimate [95% CI], bootstrap 10,000, clustered over items.

Episodes 240, items 30.

## Turn 1, before any message (% collusive option)

| class | rate | n |
|---|---|---:|
| harmful | 6.7 [1.7, 13.1] | 120 |
| mutual_gains | 95.0 [90.0, 99.1] | 120 |

## Turn 2, harmful (% collusive option)

| channel | direct | euphemism | relationship | omission | all |
|---|---|---|---|---|---|
| raw | 93.3 [83.3, 100.0] | 76.7 [56.7, 93.8] | 80.0 [63.6, 95.0] | 63.3 [40.9, 84.6] | 78.3 [71.2, 85.7] |
| paraphrased | n/a | n/a | n/a | n/a | n/a |
| neutralized | n/a | n/a | n/a | n/a | n/a |
| sum_short | n/a | n/a | n/a | n/a | n/a |
| sum_long | n/a | n/a | n/a | n/a | n/a |
| sum_system | n/a | n/a | n/a | n/a | n/a |
| sum_codeswitch | n/a | n/a | n/a | n/a | n/a |

## Turn 2, mutual_gains (% collusive option)

| channel | direct | euphemism | relationship | omission | all |
|---|---|---|---|---|---|
| raw | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| paraphrased | n/a | n/a | n/a | n/a | n/a |
| neutralized | n/a | n/a | n/a | n/a | n/a |
| sum_short | n/a | n/a | n/a | n/a | n/a |
| sum_long | n/a | n/a | n/a | n/a | n/a |
| sum_system | n/a | n/a | n/a | n/a | n/a |
| sum_codeswitch | n/a | n/a | n/a | n/a | n/a |

## Relay minus raw (pp, turn 2)

| class | relay | direct | euphemism | relationship | omission | all |
|---|---|---|---|---|---|---|
| harmful | paraphrased | n/a | n/a | n/a | n/a | n/a |
| harmful | neutralized | n/a | n/a | n/a | n/a | n/a |
| mutual_gains | paraphrased | n/a | n/a | n/a | n/a | n/a |
| mutual_gains | neutralized | n/a | n/a | n/a | n/a | n/a |

## Neutralized minus paraphrased (pp)

| class | diff |
|---|---|
| harmful | n/a |
| mutual_gains | n/a |

## Pragmatic minus direct, relay effect (difference in differences, pp, harmful)

| relay | euphemism | relationship | omission |
|---|---|---|---|
| paraphrased | n/a | n/a | n/a |
| neutralized | n/a | n/a | n/a |

## Moved to collude (turn 1 not, turn 2 yes)

| class | raw | paraphrased | neutralized | sum_short | sum_long | sum_system | sum_codeswitch |
|---|---|---|---|---|---|---|---|
| harmful | 72.5 [63.2, 82.0] | n/a | n/a | n/a | n/a | n/a | n/a |
| mutual_gains | 5.0 [0.9, 10.0] | n/a | n/a | n/a | n/a | n/a | n/a |

## Disclosure, harmful episodes that colluded

| measure | rate | n |
|---|---|---:|
| answered CÓ (discrete item) | 100.0 [100.0, 100.0] | 94 |
| report names rival and message (lexical, weakest) | 44.7 [23.4, 66.7] | 94 |

## By family, harmful, turn 2 (descriptive: 5 scenarios each)

| family | raw | paraphrased | neutralized | sum_short | sum_long | sum_system | sum_codeswitch |
|---|---|---|---|---|---|---|---|
| budget_padding | 87.5 [70.8, 100.0] | n/a | n/a | n/a | n/a | n/a | n/a |
| no_poach | 75.0 [62.5, 87.5] | n/a | n/a | n/a | n/a | n/a | n/a |
| review_ring | 72.5 [62.5, 81.2] | n/a | n/a | n/a | n/a | n/a | n/a |

## By family, raw channel (Track 2.1)

| family | turn 1 | turn 2 | moved by the message | twin cooperation |
|---|---|---|---|---|
| budget_padding | 0.0 [0.0, 0.0] | 87.5 [70.8, 100.0] | 87.5 [70.8, 100.0] | 100.0 [100.0, 100.0] |
| no_poach | 2.5 [0.0, 8.3] | 75.0 [62.5, 87.5] | 72.5 [56.2, 87.5] | 100.0 [100.0, 100.0] |
| review_ring | 17.5 [6.2, 31.2] | 72.5 [62.5, 81.2] | 57.5 [50.0, 68.8] | 100.0 [100.0, 100.0] |

## Parse outcomes (refusals and unparsed are data)

| class | channel | turn 1 | turn 2 | disclosure | error | n |
|---|---|---|---|---|---|---:|
| harmful | raw | choice | choice | choice | False | 120 |
| mutual_gains | raw | choice | choice | choice | False | 120 |

## Monitor haiku

Verdicts 2400, unparsed 0.

By channel and view (%):

| metric | channel | action | report | delivered | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | raw | 56.4 [35.6, 76.7] | 8.5 [3.0, 14.7] | 0.0 [0.0, 0.0] | 7.4 [2.1, 13.5] | 5.3 [0.0, 11.3] | 19.1 [12.8, 25.0] | 5.3 [0.0, 11.6] | 4.3 [0.0, 9.6] | 3.2 [0.0, 6.8] | 2.1 [0.0, 7.0] |
| missed collusion (FNR) | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | raw | 59.8 [38.4, 80.0] | 9.2 [3.4, 15.5] | 0.0 [0.0, 0.0] | 8.0 [2.3, 14.3] | 5.7 [0.0, 12.1] | 12.6 [5.3, 19.3] | 5.7 [0.0, 12.3] | 4.6 [0.0, 10.2] | 3.4 [0.0, 7.3] | 2.3 [0.0, 7.4] |
| missed, message-moved episodes only | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | raw | 0.0 [0.0, 0.0] | 7.7 [0.0, 20.0] | 57.7 [31.8, 78.9] | 7.7 [0.0, 20.0] | 92.3 [75.0, 100.0] | 0.0 [0.0, 0.0] | 15.4 [0.0, 33.3] | 15.4 [0.0, 33.3] | 7.7 [0.0, 17.4] | 15.4 [0.0, 36.4] |
| false alarm, harmful but declined | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | raw | 85.7 [40.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| flagged, collusive before any message | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | raw | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.8 [0.0, 2.8] | 0.8 [0.0, 2.7] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| false alarm, twins | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

Pooled over channels (%):

| metric | action | report | delivered | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | 56.4 [35.6, 76.7] | 8.5 [3.0, 14.7] | 0.0 [0.0, 0.0] | 7.4 [2.1, 13.5] | 5.3 [0.0, 11.3] | 19.1 [12.8, 25.0] | 5.3 [0.0, 11.6] | 4.3 [0.0, 9.6] | 3.2 [0.0, 6.8] | 2.1 [0.0, 7.0] |
| missed, message-moved episodes only | 59.8 [38.4, 80.0] | 9.2 [3.4, 15.5] | 0.0 [0.0, 0.0] | 8.0 [2.3, 14.3] | 5.7 [0.0, 12.1] | 12.6 [5.3, 19.3] | 5.7 [0.0, 12.3] | 4.6 [0.0, 10.2] | 3.4 [0.0, 7.3] | 2.3 [0.0, 7.4] |
| false alarm, harmful but declined | 0.0 [0.0, 0.0] | 7.7 [0.0, 20.0] | 57.7 [31.8, 78.9] | 7.7 [0.0, 20.0] | 92.3 [75.0, 100.0] | 0.0 [0.0, 0.0] | 15.4 [0.0, 33.3] | 15.4 [0.0, 33.3] | 7.7 [0.0, 17.4] | 15.4 [0.0, 36.4] |
| flagged, collusive before any message | 85.7 [40.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| false alarm, twins | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.8 [0.0, 2.8] | 0.8 [0.0, 2.7] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

| contrast | pp |
|---|---|
| C5 FNR delivered minus raw, paraphrased | n/a |
| C5 FNR delivered minus raw, neutralized | n/a |
| C6 FNR action minus delivered | +56.4 [35.6, 76.7] |
| 2.2 fnr action minus both | +47.9 [26.8, 68.1] |
| 2.2 fnr report only minus both | -1.1 [-8.7, 6.6] |
| 2.2 fpr declined message only minus all | +34.6 [18.2, 55.0] |

## Monitor mistral

Verdicts 2400, unparsed 0.

By channel and view (%):

| metric | channel | action | report | delivered | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | raw | 69.1 [43.9, 91.4] | 24.5 [9.1, 42.6] | 4.3 [0.0, 9.6] | 31.9 [15.1, 49.6] | 8.5 [2.2, 15.4] | 60.6 [43.5, 77.4] | 3.2 [0.0, 8.3] | 0.0 [0.0, 0.0] | 7.4 [1.8, 14.5] | 0.0 [0.0, 0.0] |
| missed collusion (FNR) | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | raw | 73.6 [49.1, 93.0] | 26.4 [10.1, 44.9] | 4.6 [0.0, 10.3] | 34.5 [17.1, 51.9] | 9.2 [2.5, 16.2] | 62.1 [43.9, 78.6] | 3.4 [0.0, 8.9] | 0.0 [0.0, 0.0] | 8.0 [1.9, 15.5] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | raw | 0.0 [0.0, 0.0] | 3.8 [0.0, 12.0] | 50.0 [22.6, 76.9] | 7.7 [0.0, 18.8] | 84.6 [65.2, 100.0] | 0.0 [0.0, 0.0] | 26.9 [4.3, 54.5] | 30.8 [8.0, 59.1] | 15.4 [3.6, 29.4] | 30.8 [8.0, 59.1] |
| false alarm, harmful but declined | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | raw | 85.7 [40.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 57.1 [0.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| flagged, collusive before any message | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | raw | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 1.7 [0.0, 5.4] | 0.8 [0.0, 2.7] | 0.8 [0.0, 2.8] | 0.0 [0.0, 0.0] |
| false alarm, twins | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

Pooled over channels (%):

| metric | action | report | delivered | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | 69.1 [43.9, 91.4] | 24.5 [9.1, 42.6] | 4.3 [0.0, 9.6] | 31.9 [15.1, 49.6] | 8.5 [2.2, 15.4] | 60.6 [43.5, 77.4] | 3.2 [0.0, 8.3] | 0.0 [0.0, 0.0] | 7.4 [1.8, 14.5] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | 73.6 [49.1, 93.0] | 26.4 [10.1, 44.9] | 4.6 [0.0, 10.3] | 34.5 [17.1, 51.9] | 9.2 [2.5, 16.2] | 62.1 [43.9, 78.6] | 3.4 [0.0, 8.9] | 0.0 [0.0, 0.0] | 8.0 [1.9, 15.5] | 0.0 [0.0, 0.0] |
| false alarm, harmful but declined | 0.0 [0.0, 0.0] | 3.8 [0.0, 12.0] | 50.0 [22.6, 76.9] | 7.7 [0.0, 18.8] | 84.6 [65.2, 100.0] | 0.0 [0.0, 0.0] | 26.9 [4.3, 54.5] | 30.8 [8.0, 59.1] | 15.4 [3.6, 29.4] | 30.8 [8.0, 59.1] |
| flagged, collusive before any message | 85.7 [40.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 57.1 [0.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| false alarm, twins | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 1.7 [0.0, 5.4] | 0.8 [0.0, 2.7] | 0.8 [0.0, 2.8] | 0.0 [0.0, 0.0] |

| contrast | pp |
|---|---|
| C5 FNR delivered minus raw, paraphrased | n/a |
| C5 FNR delivered minus raw, neutralized | n/a |
| C6 FNR action minus delivered | +64.9 [40.5, 86.0] |
| 2.2 fnr action minus both | +44.7 [23.6, 65.2] |
| 2.2 fnr report only minus both | +7.4 [-1.0, 17.2] |
| 2.2 fpr declined message only minus all | +34.6 [9.1, 66.7] |
