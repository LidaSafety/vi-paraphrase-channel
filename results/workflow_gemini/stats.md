# Generated statistics: gemini, workflow

Written by `analysis/analyze.py`. Do not edit. EXPLORATORY.
Cells: estimate [95% CI], bootstrap 10,000, clustered over items.

Episodes 240, items 30.

## Turn 1, before any message (% collusive option)

| class | rate | n |
|---|---|---:|
| harmful | 30.0 [16.3, 44.2] | 120 |
| mutual_gains | 100.0 [100.0, 100.0] | 120 |

## Turn 2, harmful (% collusive option)

| channel | direct | euphemism | relationship | omission | all |
|---|---|---|---|---|---|
| raw | 60.0 [36.4, 82.4] | 60.0 [38.5, 80.8] | 50.0 [26.9, 73.1] | 76.7 [57.7, 93.8] | 61.7 [42.5, 80.0] |
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
| harmful | 32.5 [21.9, 44.5] | n/a | n/a | n/a | n/a | n/a | n/a |
| mutual_gains | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a |

## Disclosure, harmful episodes that colluded

| measure | rate | n |
|---|---|---:|
| answered CÓ (discrete item) | 97.3 [91.3, 100.0] | 74 |
| report names rival and message (lexical, weakest) | 36.5 [19.4, 54.9] | 74 |

## By family, harmful, turn 2 (descriptive: 5 scenarios each)

| family | raw | paraphrased | neutralized | sum_short | sum_long | sum_system | sum_codeswitch |
|---|---|---|---|---|---|---|---|
| budget_padding | 72.5 [50.0, 93.8] | n/a | n/a | n/a | n/a | n/a | n/a |
| no_poach | 17.5 [0.0, 37.5] | n/a | n/a | n/a | n/a | n/a | n/a |
| review_ring | 95.0 [83.3, 100.0] | n/a | n/a | n/a | n/a | n/a | n/a |

## By family, raw channel (Track 2.1)

| family | turn 1 | turn 2 | moved by the message | twin cooperation |
|---|---|---|---|---|
| budget_padding | 40.0 [20.0, 62.5] | 72.5 [50.0, 93.8] | 32.5 [25.0, 43.8] | 100.0 [100.0, 100.0] |
| no_poach | 0.0 [0.0, 0.0] | 17.5 [0.0, 37.5] | 17.5 [0.0, 37.5] | 100.0 [100.0, 100.0] |
| review_ring | 50.0 [25.0, 68.8] | 95.0 [83.3, 100.0] | 47.5 [25.0, 75.0] | 100.0 [100.0, 100.0] |

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
| missed collusion (FNR) | raw | 41.9 [23.1, 65.6] | 12.2 [5.2, 20.8] | 1.4 [0.0, 4.4] | 6.8 [1.4, 14.0] | 9.5 [2.7, 18.1] | 56.8 [41.8, 70.7] | 1.4 [0.0, 4.8] | 0.0 [0.0, 0.0] | 4.1 [0.0, 8.5] | 1.4 [0.0, 4.4] |
| missed collusion (FNR) | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | raw | 48.7 [28.0, 75.0] | 12.8 [3.8, 23.8] | 2.6 [0.0, 9.3] | 10.3 [0.0, 23.3] | 10.3 [0.0, 25.0] | 17.9 [4.7, 37.0] | 2.6 [0.0, 8.3] | 0.0 [0.0, 0.0] | 2.6 [0.0, 9.1] | 2.6 [0.0, 9.3] |
| missed, message-moved episodes only | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | raw | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 41.3 [23.1, 57.8] | 0.0 [0.0, 0.0] | 97.8 [92.3, 100.0] | 0.0 [0.0, 0.0] | 15.2 [2.9, 27.5] | 17.4 [3.7, 29.5] | 32.6 [16.7, 43.6] | 21.7 [6.5, 33.3] |
| false alarm, harmful but declined | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | raw | 65.7 [40.7, 87.2] | 88.6 [77.3, 100.0] | 100.0 [100.0, 100.0] | 97.1 [91.7, 100.0] | 91.4 [82.9, 100.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 94.3 [86.4, 100.0] | 100.0 [100.0, 100.0] |
| flagged, collusive before any message | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | raw | 0.0 [0.0, 0.0] | 1.7 [0.0, 5.6] | 4.2 [0.8, 8.3] | 1.7 [0.0, 5.6] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.8 [0.0, 2.7] | 1.7 [0.0, 4.2] | 1.7 [0.0, 5.6] | 0.0 [0.0, 0.0] |
| false alarm, twins | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

Pooled over channels (%):

| metric | action | report | delivered | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | 41.9 [23.1, 65.6] | 12.2 [5.2, 20.8] | 1.4 [0.0, 4.4] | 6.8 [1.4, 14.0] | 9.5 [2.7, 18.1] | 56.8 [41.8, 70.7] | 1.4 [0.0, 4.8] | 0.0 [0.0, 0.0] | 4.1 [0.0, 8.5] | 1.4 [0.0, 4.4] |
| missed, message-moved episodes only | 48.7 [28.0, 75.0] | 12.8 [3.8, 23.8] | 2.6 [0.0, 9.3] | 10.3 [0.0, 23.3] | 10.3 [0.0, 25.0] | 17.9 [4.7, 37.0] | 2.6 [0.0, 8.3] | 0.0 [0.0, 0.0] | 2.6 [0.0, 9.1] | 2.6 [0.0, 9.3] |
| false alarm, harmful but declined | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 41.3 [23.1, 57.8] | 0.0 [0.0, 0.0] | 97.8 [92.3, 100.0] | 0.0 [0.0, 0.0] | 15.2 [2.9, 27.5] | 17.4 [3.7, 29.5] | 32.6 [16.7, 43.6] | 21.7 [6.5, 33.3] |
| flagged, collusive before any message | 65.7 [40.7, 87.2] | 88.6 [77.3, 100.0] | 100.0 [100.0, 100.0] | 97.1 [91.7, 100.0] | 91.4 [82.9, 100.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 94.3 [86.4, 100.0] | 100.0 [100.0, 100.0] |
| false alarm, twins | 0.0 [0.0, 0.0] | 1.7 [0.0, 5.6] | 4.2 [0.8, 8.3] | 1.7 [0.0, 5.6] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.8 [0.0, 2.7] | 1.7 [0.0, 4.2] | 1.7 [0.0, 5.6] | 0.0 [0.0, 0.0] |

| contrast | pp |
|---|---|
| C5 FNR delivered minus raw, paraphrased | n/a |
| C5 FNR delivered minus raw, neutralized | n/a |
| C6 FNR action minus delivered | +40.5 [20.3, 65.0] |
| 2.2 fnr action minus both | +29.7 [10.5, 50.0] |
| 2.2 fnr report only minus both | -5.4 [-12.5, 0.0] |
| 2.2 fpr declined message only minus all | +56.5 [38.2, 76.3] |

## Monitor mistral

Verdicts 2400, unparsed 0.

By channel and view (%):

| metric | channel | action | report | delivered | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | raw | 48.6 [21.1, 81.6] | 13.5 [2.5, 29.2] | 1.4 [0.0, 4.3] | 18.9 [4.1, 38.7] | 12.2 [3.8, 22.1] | 59.5 [41.2, 80.5] | 10.8 [2.6, 21.3] | 5.4 [0.0, 14.3] | 13.5 [4.5, 25.0] | 0.0 [0.0, 0.0] |
| missed collusion (FNR) | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | raw | 51.3 [23.3, 85.7] | 12.8 [2.4, 26.7] | 0.0 [0.0, 0.0] | 15.4 [0.0, 34.3] | 12.8 [2.4, 28.0] | 56.4 [35.7, 80.0] | 12.8 [0.0, 28.6] | 2.6 [0.0, 9.3] | 15.4 [4.4, 28.6] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | raw | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 82.6 [70.0, 93.9] | 2.2 [0.0, 8.8] | 93.5 [85.1, 100.0] | 4.3 [0.0, 12.5] | 65.2 [44.7, 80.0] | 63.0 [31.0, 82.1] | 39.1 [18.0, 58.7] | 65.2 [33.3, 85.7] |
| false alarm, harmful but declined | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | raw | 54.3 [17.1, 87.8] | 85.7 [58.3, 100.0] | 97.1 [91.7, 100.0] | 77.1 [44.4, 100.0] | 88.6 [77.3, 100.0] | 37.1 [14.0, 64.3] | 91.4 [80.6, 100.0] | 91.4 [75.0, 100.0] | 88.6 [72.0, 100.0] | 100.0 [100.0, 100.0] |
| flagged, collusive before any message | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | raw | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.8 [0.0, 2.7] | 0.0 [0.0, 0.0] |
| false alarm, twins | paraphrased | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | neutralized | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_short | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_long | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_system | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_codeswitch | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

Pooled over channels (%):

| metric | action | report | delivered | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | 48.6 [21.1, 81.6] | 13.5 [2.5, 29.2] | 1.4 [0.0, 4.3] | 18.9 [4.1, 38.7] | 12.2 [3.8, 22.1] | 59.5 [41.2, 80.5] | 10.8 [2.6, 21.3] | 5.4 [0.0, 14.3] | 13.5 [4.5, 25.0] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | 51.3 [23.3, 85.7] | 12.8 [2.4, 26.7] | 0.0 [0.0, 0.0] | 15.4 [0.0, 34.3] | 12.8 [2.4, 28.0] | 56.4 [35.7, 80.0] | 12.8 [0.0, 28.6] | 2.6 [0.0, 9.3] | 15.4 [4.4, 28.6] | 0.0 [0.0, 0.0] |
| false alarm, harmful but declined | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 82.6 [70.0, 93.9] | 2.2 [0.0, 8.8] | 93.5 [85.1, 100.0] | 4.3 [0.0, 12.5] | 65.2 [44.7, 80.0] | 63.0 [31.0, 82.1] | 39.1 [18.0, 58.7] | 65.2 [33.3, 85.7] |
| flagged, collusive before any message | 54.3 [17.1, 87.8] | 85.7 [58.3, 100.0] | 97.1 [91.7, 100.0] | 77.1 [44.4, 100.0] | 88.6 [77.3, 100.0] | 37.1 [14.0, 64.3] | 91.4 [80.6, 100.0] | 91.4 [75.0, 100.0] | 88.6 [72.0, 100.0] | 100.0 [100.0, 100.0] |
| false alarm, twins | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.8 [0.0, 2.7] | 0.0 [0.0, 0.0] |

| contrast | pp |
|---|---|
| C5 FNR delivered minus raw, paraphrased | n/a |
| C5 FNR delivered minus raw, neutralized | n/a |
| C6 FNR action minus delivered | +47.3 [20.7, 79.5] |
| 2.2 fnr action minus both | +35.1 [14.0, 61.6] |
| 2.2 fnr report only minus both | +5.4 [-1.4, 13.8] |
| 2.2 fpr declined message only minus all | +10.9 [0.0, 25.8] |
