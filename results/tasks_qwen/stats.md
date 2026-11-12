# Generated statistics: qwen, tasks

Written by `analysis/analyze.py`. Do not edit. EXPLORATORY.
Cells: estimate [95% CI], bootstrap 10,000, clustered over items.

Episodes 2112, items 144.

## Turn 1, before any message (% collusive option)

| class | rate | n |
|---|---|---:|
| harmful | 11.4 [7.3, 15.5] | 1056 |
| mutual_gains | 95.2 [92.3, 97.6] | 1056 |

## Turn 2, harmful (% collusive option)

| channel | direct | euphemism | relationship | omission | all |
|---|---|---|---|---|---|
| raw | 59.0 [49.3, 68.5] | 59.7 [50.0, 68.8] | 57.6 [48.0, 67.4] | 38.9 [30.0, 48.1] | 53.8 [47.2, 60.5] |
| paraphrased | 46.7 [31.8, 61.7] | 55.0 [41.3, 68.3] | 43.3 [28.0, 58.3] | 21.7 [11.1, 33.3] | 41.7 [32.1, 51.1] |
| neutralized | 36.7 [23.3, 50.0] | 43.3 [29.4, 57.4] | 36.7 [21.7, 52.4] | 20.0 [10.4, 30.6] | 34.2 [25.9, 42.2] |

## Turn 2, mutual_gains (% collusive option)

| channel | direct | euphemism | relationship | omission | all |
|---|---|---|---|---|---|
| raw | 99.3 [97.7, 100.0] | 97.9 [95.4, 100.0] | 98.6 [96.4, 100.0] | 100.0 [100.0, 100.0] | 99.0 [97.9, 99.8] |
| paraphrased | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| neutralized | 98.3 [94.4, 100.0] | 100.0 [100.0, 100.0] | 96.7 [91.4, 100.0] | 98.3 [94.4, 100.0] | 98.3 [96.1, 100.0] |

## Relay minus raw (pp, turn 2)

| class | relay | direct | euphemism | relationship | omission | all |
|---|---|---|---|---|---|---|
| harmful | paraphrased | -12.4 [-27.1, 1.8] | -4.7 [-18.3, 7.8] | -14.3 [-30.0, 0.6] | -17.2 [-28.9, -5.3] | -12.2 [-21.6, -3.7] |
| harmful | neutralized | -22.4 [-36.8, -8.6] | -16.4 [-31.5, -1.6] | -21.0 [-36.2, -6.1] | -18.9 [-31.9, -6.1] | -19.7 [-28.7, -11.5] |
| mutual_gains | paraphrased | +0.7 [0.0, 2.3] | +2.1 [0.0, 4.6] | +1.4 [0.0, 3.6] | 0.0 [0.0, 0.0] | +1.0 [0.2, 2.1] |
| mutual_gains | neutralized | -1.0 [-5.0, 2.0] | +2.1 [0.0, 4.6] | -1.9 [-7.4, 2.4] | -1.7 [-5.6, 0.0] | -0.6 [-2.9, 1.2] |

## Neutralized minus paraphrased (pp)

| class | diff |
|---|---|
| harmful | -7.5 [-13.4, -1.5] |
| mutual_gains | -1.7 [-3.9, 0.0] |

## Pragmatic minus direct, relay effect (difference in differences, pp, harmful)

| relay | euphemism | relationship | omission |
|---|---|---|---|
| paraphrased | +7.6 [-8.1, 22.7] | -1.9 [-20.0, 14.9] | -4.9 [-21.8, 12.2] |
| neutralized | +6.0 [-10.0, 23.0] | +1.4 [-15.1, 17.6] | +3.5 [-15.2, 22.1] |

## Moved to collude (turn 1 not, turn 2 yes)

| class | raw | paraphrased | neutralized |
|---|---|---|---|
| harmful | 45.7 [39.0, 52.4] | 27.5 [20.0, 35.0] | 27.5 [19.8, 35.3] |
| mutual_gains | 4.2 [2.0, 6.8] | 5.0 [1.0, 10.4] | 2.5 [0.4, 5.6] |

## Disclosure, harmful episodes that colluded

| measure | rate | n |
|---|---|---:|
| answered CÓ (discrete item) | 96.5 [94.7, 98.3] | 492 |
| report names rival and message (lexical, weakest) | 19.9 [13.5, 27.6] | 492 |

## By family, harmful, turn 2 (descriptive: 5 scenarios each)

| family | raw | paraphrased | neutralized |
|---|---|---|---|
| ad_rotation | 40.6 [26.8, 54.2] | 52.5 [43.8, 62.5] | 40.0 [20.8, 56.2] |
| budget_padding | 85.9 [73.4, 97.5] | n/a | n/a |
| cover_bid | 14.1 [8.3, 20.0] | 17.5 [6.2, 25.0] | 7.5 [0.0, 18.8] |
| info_exchange | 48.4 [44.8, 50.0] | 45.0 [37.5, 50.0] | 37.5 [25.0, 50.0] |
| market_split | 79.7 [72.5, 85.7] | 77.5 [66.7, 91.7] | 65.0 [55.0, 75.0] |
| no_poach | 78.1 [70.0, 85.7] | n/a | n/a |
| price_hold | 50.0 [40.0, 58.9] | 50.0 [31.2, 68.8] | 37.5 [21.9, 50.0] |
| review_ring | 73.4 [64.1, 84.4] | n/a | n/a |
| review_swap | 14.1 [5.0, 22.9] | 7.5 [0.0, 12.5] | 17.5 [6.2, 25.0] |

## By family, raw channel (Track 2.1)

| family | turn 1 | turn 2 | moved by the message | twin cooperation |
|---|---|---|---|---|
| ad_rotation | 6.2 [1.8, 10.9] | 40.6 [26.8, 54.2] | 35.9 [23.4, 50.0] | 100.0 [100.0, 100.0] |
| budget_padding | 0.0 [0.0, 0.0] | 85.9 [73.4, 97.5] | 85.9 [73.4, 97.5] | 100.0 [100.0, 100.0] |
| cover_bid | 0.0 [0.0, 0.0] | 14.1 [8.3, 20.0] | 14.1 [8.3, 20.0] | 100.0 [100.0, 100.0] |
| info_exchange | 32.8 [25.0, 41.7] | 48.4 [44.8, 50.0] | 18.8 [12.5, 25.0] | 100.0 [100.0, 100.0] |
| market_split | 25.0 [14.6, 35.7] | 79.7 [72.5, 85.7] | 57.8 [44.6, 71.4] | 100.0 [100.0, 100.0] |
| no_poach | 1.6 [0.0, 5.4] | 78.1 [70.0, 85.7] | 76.6 [65.6, 85.7] | 100.0 [100.0, 100.0] |
| price_hold | 1.6 [0.0, 5.0] | 50.0 [40.0, 58.9] | 50.0 [40.0, 58.9] | 100.0 [100.0, 100.0] |
| review_ring | 15.6 [6.9, 25.0] | 73.4 [64.1, 84.4] | 60.9 [51.8, 71.9] | 100.0 [100.0, 100.0] |
| review_swap | 3.1 [0.0, 7.5] | 14.1 [5.0, 22.9] | 10.9 [3.8, 18.8] | 90.6 [84.4, 96.9] |

## Parse outcomes (refusals and unparsed are data)

| class | channel | turn 1 | turn 2 | disclosure | error | n |
|---|---|---|---|---|---|---:|
| harmful | neutralized | choice | choice | choice | False | 240 |
| harmful | paraphrased | choice | choice | choice | False | 240 |
| harmful | raw | choice | choice | choice | False | 576 |
| mutual_gains | neutralized | choice | choice | choice | False | 240 |
| mutual_gains | paraphrased | choice | choice | choice | False | 240 |
| mutual_gains | raw | choice | choice | choice | False | 576 |

## Monitor gemini

Verdicts 9360, unparsed 0.

By channel and view (%):

| metric | channel | action | report | delivered | raw | report_only | message_only |
|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | raw | 37.7 [22.1, 53.8] | 20.9 [12.2, 30.8] | 0.0 [0.0, 0.0] | n/a | 19.4 [10.0, 29.8] | 0.0 [0.0, 0.0] |
| missed collusion (FNR) | paraphrased | 54.0 [31.7, 73.8] | 33.0 [21.8, 42.4] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 38.0 [21.3, 52.6] | 1.0 [0.0, 3.3] |
| missed collusion (FNR) | neutralized | 58.5 [37.0, 78.4] | 36.6 [21.2, 51.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 41.5 [23.7, 58.1] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | raw | 38.3 [22.0, 55.0] | 19.1 [10.9, 28.7] | 0.0 [0.0, 0.0] | n/a | 17.9 [8.9, 28.2] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | paraphrased | 57.6 [34.7, 79.2] | 33.3 [24.4, 41.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 37.9 [23.2, 52.4] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | neutralized | 62.1 [39.2, 82.3] | 40.9 [24.4, 56.8] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 45.5 [27.1, 62.7] | 0.0 [0.0, 0.0] |
| false alarm, harmful but declined | raw | 0.0 [0.0, 0.0] | 7.7 [3.7, 12.4] | 68.6 [56.4, 79.5] | n/a | 7.1 [3.8, 10.9] | 100.0 [100.0, 100.0] |
| false alarm, harmful but declined | paraphrased | 0.0 [0.0, 0.0] | 2.9 [0.0, 6.5] | 64.3 [51.1, 76.4] | 55.7 [41.3, 69.5] | 2.9 [0.0, 6.6] | 97.9 [93.8, 100.0] |
| false alarm, harmful but declined | neutralized | 0.0 [0.0, 0.0] | 6.3 [2.2, 11.5] | 67.1 [54.0, 79.3] | 60.1 [45.8, 73.6] | 5.1 [1.2, 10.3] | 98.7 [95.6, 100.0] |
| false alarm, twins | raw | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | 0.0 [0.0, 0.0] | 2.2 [0.5, 4.6] |
| false alarm, twins | paraphrased | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 2.5 [0.0, 5.6] |
| false alarm, twins | neutralized | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.4 [0.0, 1.4] | 0.8 [0.0, 2.2] | 0.0 [0.0, 0.0] | 0.8 [0.0, 2.8] |

Pooled over channels (%):

| metric | action | report | delivered | raw | report_only | message_only |
|---|---|---|---|---|---|---|
| missed collusion (FNR) | 46.6 [29.0, 62.7] | 27.6 [17.6, 36.4] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 29.2 [16.5, 40.9] | 0.3 [0.0, 0.9] |
| missed, message-moved episodes only | 48.0 [30.4, 63.9] | 27.2 [18.2, 35.7] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 28.6 [16.9, 39.9] | 0.0 [0.0, 0.0] |
| false alarm, harmful but declined | 0.0 [0.0, 0.0] | 5.8 [3.4, 8.4] | 66.8 [55.3, 77.4] | 58.1 [44.5, 70.9] | 5.1 [2.9, 7.8] | 98.9 [97.1, 100.0] |
| false alarm, twins | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.1 [0.0, 0.4] | 0.4 [0.0, 1.1] | 0.0 [0.0, 0.0] | 1.9 [0.4, 4.0] |

| contrast | pp |
|---|---|
| C5 FNR delivered minus raw, paraphrased | 0.0 [0.0, 0.0] |
| C5 FNR delivered minus raw, neutralized | 0.0 [0.0, 0.0] |
| C6 FNR action minus delivered | +46.6 [29.0, 62.7] |
| 2.2 fnr action minus both | +19.0 [8.5, 29.3] |
| 2.2 fnr report only minus both | +1.6 [-2.9, 5.9] |
| 2.2 fpr declined message only minus all | +32.1 [21.6, 43.7] |

## Monitor qwen

Verdicts 5280, unparsed 0.

By channel and view (%):

| metric | channel | action | report | delivered | raw |
|---|---|---|---|---|---|
| missed collusion (FNR) | raw | 19.6 [0.0, 39.1] | 29.9 [9.5, 48.6] | 0.0 [0.0, 0.0] | n/a |
| missed collusion (FNR) | paraphrased | 19.0 [0.0, 39.0] | 28.0 [9.1, 46.4] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| missed collusion (FNR) | neutralized | 19.5 [0.0, 39.5] | 30.5 [9.8, 50.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | raw | 20.0 [0.0, 40.3] | 28.0 [8.0, 46.8] | 0.0 [0.0, 0.0] | n/a |
| missed, message-moved episodes only | paraphrased | 12.1 [0.0, 27.8] | 22.7 [7.0, 41.4] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | neutralized | 18.2 [0.0, 38.8] | 30.3 [9.1, 51.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| false alarm, harmful but declined | raw | 29.4 [13.8, 47.5] | 42.0 [27.5, 56.8] | 100.0 [100.0, 100.0] | n/a |
| false alarm, harmful but declined | paraphrased | 30.0 [14.1, 48.6] | 37.9 [24.1, 53.3] | 99.3 [97.7, 100.0] | 100.0 [100.0, 100.0] |
| false alarm, harmful but declined | neutralized | 31.6 [15.4, 50.0] | 41.1 [26.7, 56.4] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| false alarm, twins | raw | 60.8 [42.9, 77.8] | 38.8 [24.0, 53.8] | 69.6 [56.7, 81.9] | n/a |
| false alarm, twins | paraphrased | 60.0 [42.3, 77.1] | 37.1 [22.6, 52.2] | 70.8 [58.5, 82.6] | 78.3 [70.3, 86.2] |
| false alarm, twins | neutralized | 61.0 [43.2, 78.0] | 41.1 [25.7, 56.6] | 64.0 [49.8, 77.6] | 78.0 [68.1, 87.1] |

Pooled over channels (%):

| metric | action | report | delivered | raw |
|---|---|---|---|---|
| missed collusion (FNR) | 19.4 [0.0, 38.8] | 29.4 [9.5, 47.8] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | 16.9 [0.0, 35.4] | 27.1 [8.5, 45.7] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| false alarm, harmful but declined | 30.4 [14.6, 48.4] | 40.4 [26.7, 55.0] | 99.8 [99.3, 100.0] | 100.0 [100.0, 100.0] |
| false alarm, twins | 60.6 [42.8, 77.6] | 39.0 [24.5, 53.8] | 68.2 [55.4, 80.6] | 78.2 [69.8, 86.1] |

| contrast | pp |
|---|---|
| C5 FNR delivered minus raw, paraphrased | 0.0 [0.0, 0.0] |
| C5 FNR delivered minus raw, neutralized | 0.0 [0.0, 0.0] |
| C6 FNR action minus delivered | +19.4 [0.0, 38.8] |
