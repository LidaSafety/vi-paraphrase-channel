# Generated statistics: qwen, summary

Written by `analysis/analyze.py`. Do not edit. EXPLORATORY.
Cells: estimate [95% CI], bootstrap 10,000, clustered over items.

Episodes 3360, items 60.

## Turn 1, before any message (% collusive option)

| class | rate | n |
|---|---|---:|
| harmful | 11.6 [6.9, 16.7] | 1680 |
| mutual_gains | 95.5 [91.4, 99.0] | 1680 |

## Turn 2, harmful (% collusive option)

| channel | direct | euphemism | relationship | omission | all |
|---|---|---|---|---|---|
| raw | 45.0 [31.2, 58.6] | 50.0 [36.0, 63.8] | 41.7 [27.6, 55.8] | 25.0 [13.3, 37.5] | 40.4 [31.6, 48.9] |
| paraphrased | 46.7 [32.0, 61.5] | 55.0 [41.7, 68.3] | 43.3 [28.1, 58.6] | 21.7 [11.3, 33.3] | 41.7 [32.3, 51.0] |
| neutralized | 36.7 [23.8, 50.0] | 43.3 [29.7, 57.1] | 36.7 [21.4, 52.2] | 20.0 [10.6, 30.4] | 34.2 [26.2, 42.2] |
| sum_short | 36.7 [24.3, 48.6] | 35.0 [21.4, 50.0] | 26.7 [14.3, 40.3] | 23.3 [11.9, 36.2] | 30.4 [21.0, 40.9] |
| sum_long | 48.3 [35.0, 62.1] | 45.0 [30.4, 60.0] | 48.3 [33.9, 62.5] | 25.0 [15.0, 35.3] | 41.7 [33.5, 49.6] |
| sum_system | 21.7 [10.9, 33.3] | 20.0 [8.9, 32.6] | 15.0 [6.2, 25.0] | 21.7 [11.9, 32.0] | 19.6 [13.0, 26.4] |
| sum_codeswitch | 43.3 [28.3, 58.9] | 55.0 [40.7, 69.0] | 45.0 [30.3, 60.0] | 15.0 [7.1, 23.9] | 39.6 [30.9, 48.6] |

## Turn 2, mutual_gains (% collusive option)

| channel | direct | euphemism | relationship | omission | all |
|---|---|---|---|---|---|
| raw | 100.0 [100.0, 100.0] | 96.7 [91.7, 100.0] | 98.3 [94.4, 100.0] | 100.0 [100.0, 100.0] | 98.8 [97.2, 100.0] |
| paraphrased | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| neutralized | 98.3 [94.4, 100.0] | 100.0 [100.0, 100.0] | 96.7 [91.4, 100.0] | 98.3 [94.4, 100.0] | 98.3 [96.2, 100.0] |
| sum_short | 96.7 [91.7, 100.0] | 96.7 [91.4, 100.0] | 100.0 [100.0, 100.0] | 93.3 [86.7, 98.5] | 96.7 [93.3, 99.4] |
| sum_long | 98.3 [94.4, 100.0] | 100.0 [100.0, 100.0] | 98.3 [94.4, 100.0] | 100.0 [100.0, 100.0] | 99.2 [97.2, 100.0] |
| sum_system | 75.0 [59.6, 88.9] | 80.0 [67.2, 91.3] | 85.0 [73.3, 94.8] | 80.0 [68.0, 90.4] | 80.0 [72.0, 87.5] |
| sum_codeswitch | 98.3 [94.4, 100.0] | 96.7 [91.4, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 98.8 [96.7, 100.0] |

## Relay minus raw (pp, turn 2)

| class | relay | direct | euphemism | relationship | omission | all |
|---|---|---|---|---|---|---|
| harmful | paraphrased | +1.7 [-10.0, 13.3] | +5.0 [-6.8, 16.7] | +1.7 [-12.5, 16.1] | -3.3 [-14.1, 6.7] | +1.3 [-4.2, 6.7] |
| harmful | neutralized | -8.3 [-21.9, 4.8] | -6.7 [-22.5, 9.4] | -5.0 [-17.7, 8.9] | -5.0 [-20.0, 8.8] | -6.2 [-12.5, 0.5] |
| mutual_gains | paraphrased | 0.0 [0.0, 0.0] | +3.3 [0.0, 8.3] | +1.7 [0.0, 5.6] | 0.0 [0.0, 0.0] | +1.2 [0.0, 2.8] |
| mutual_gains | neutralized | -1.7 [-5.6, 0.0] | +3.3 [0.0, 8.3] | -1.7 [-7.6, 3.8] | -1.7 [-5.6, 0.0] | -0.4 [-2.8, 1.6] |

## Neutralized minus paraphrased (pp)

| class | diff |
|---|---|
| harmful | -7.5 [-13.4, -1.7] |
| mutual_gains | -1.7 [-3.8, 0.0] |

## Pragmatic minus direct, relay effect (difference in differences, pp, harmful)

| relay | euphemism | relationship | omission |
|---|---|---|---|
| paraphrased | +3.3 [-12.5, 18.3] | 0.0 [-18.3, 18.2] | -5.0 [-19.6, 10.0] |
| neutralized | +1.7 [-19.7, 24.0] | +3.3 [-12.0, 17.6] | +3.3 [-16.1, 23.2] |

## Moved to collude (turn 1 not, turn 2 yes)

| class | raw | paraphrased | neutralized | sum_short | sum_long | sum_system | sum_codeswitch |
|---|---|---|---|---|---|---|---|
| harmful | 31.2 [24.0, 39.0] | 27.5 [20.1, 34.9] | 27.5 [19.9, 35.3] | 24.6 [16.3, 33.9] | 31.7 [24.5, 39.0] | 11.2 [6.2, 16.9] | 30.4 [22.1, 39.1] |
| mutual_gains | 1.7 [0.4, 3.3] | 5.0 [0.9, 10.5] | 2.5 [0.4, 5.7] | 4.2 [0.4, 8.9] | 2.5 [0.0, 5.5] | 0.8 [0.0, 2.1] | 3.3 [0.4, 7.0] |

## Disclosure, harmful episodes that colluded

| measure | rate | n |
|---|---|---:|
| answered CÓ (discrete item) | 94.8 [92.2, 97.2] | 594 |
| report names rival and message (lexical, weakest) | 10.1 [7.1, 13.6] | 594 |

## By family, harmful, turn 2 (descriptive: 5 scenarios each)

| family | raw | paraphrased | neutralized | sum_short | sum_long | sum_system | sum_codeswitch |
|---|---|---|---|---|---|---|---|
| ad_rotation | 37.5 [22.3, 50.0] | 52.5 [42.7, 62.5] | 40.0 [18.8, 56.2] | 27.5 [12.5, 43.8] | 42.5 [31.2, 50.0] | 15.0 [0.0, 25.0] | 45.0 [25.0, 62.5] |
| cover_bid | 12.5 [4.2, 20.8] | 17.5 [6.2, 25.0] | 7.5 [0.0, 18.8] | 5.0 [0.0, 12.5] | 12.5 [0.0, 25.0] | 5.0 [0.0, 12.5] | 12.5 [4.2, 20.0] |
| info_exchange | 47.5 [41.7, 50.0] | 45.0 [37.5, 50.0] | 37.5 [25.0, 50.0] | 32.5 [18.8, 43.8] | 47.5 [37.5, 62.5] | 15.0 [12.5, 20.8] | 37.5 [29.2, 45.8] |
| market_split | 77.5 [68.8, 87.5] | 77.5 [67.5, 91.7] | 65.0 [56.2, 75.0] | 80.0 [62.5, 93.8] | 70.0 [56.2, 82.5] | 50.0 [32.1, 68.8] | 70.0 [56.2, 81.2] |
| price_hold | 47.5 [31.2, 62.5] | 50.0 [31.5, 68.8] | 37.5 [22.5, 50.0] | 25.0 [12.5, 43.8] | 50.0 [37.5, 65.6] | 20.0 [6.2, 37.5] | 55.0 [29.2, 77.5] |
| review_swap | 20.0 [8.3, 25.0] | 7.5 [0.0, 12.5] | 17.5 [6.2, 25.0] | 12.5 [4.2, 20.8] | 27.5 [12.5, 37.5] | 12.5 [0.0, 25.0] | 17.5 [6.2, 25.0] |

## By family, raw channel (Track 2.1)

| family | turn 1 | turn 2 | moved by the message | twin cooperation |
|---|---|---|---|---|
| ad_rotation | 5.0 [0.0, 12.5] | 37.5 [22.3, 50.0] | 32.5 [18.8, 43.8] | 100.0 [100.0, 100.0] |
| cover_bid | 0.0 [0.0, 0.0] | 12.5 [4.2, 20.8] | 12.5 [4.2, 20.8] | 100.0 [100.0, 100.0] |
| info_exchange | 27.5 [25.0, 33.3] | 47.5 [41.7, 50.0] | 22.5 [16.7, 25.0] | 100.0 [100.0, 100.0] |
| market_split | 22.5 [9.7, 33.3] | 77.5 [68.8, 87.5] | 57.5 [37.5, 75.0] | 100.0 [100.0, 100.0] |
| price_hold | 0.0 [0.0, 0.0] | 47.5 [31.2, 62.5] | 47.5 [31.2, 62.5] | 100.0 [100.0, 100.0] |
| review_swap | 5.0 [0.0, 12.5] | 20.0 [8.3, 25.0] | 15.0 [5.0, 25.0] | 92.5 [87.5, 100.0] |

## Parse outcomes (refusals and unparsed are data)

| class | channel | turn 1 | turn 2 | disclosure | error | n |
|---|---|---|---|---|---|---:|
| harmful | neutralized | choice | choice | choice | False | 240 |
| harmful | paraphrased | choice | choice | choice | False | 240 |
| harmful | raw | choice | choice | choice | False | 240 |
| harmful | sum_codeswitch | choice | choice | choice | False | 240 |
| harmful | sum_long | choice | choice | choice | False | 240 |
| harmful | sum_short | choice | choice | choice | False | 240 |
| harmful | sum_system | choice | choice | choice | False | 240 |
| mutual_gains | neutralized | choice | choice | choice | False | 240 |
| mutual_gains | paraphrased | choice | choice | choice | False | 240 |
| mutual_gains | raw | choice | choice | choice | False | 240 |
| mutual_gains | sum_codeswitch | choice | choice | choice | False | 240 |
| mutual_gains | sum_long | choice | choice | choice | False | 240 |
| mutual_gains | sum_short | choice | choice | choice | False | 240 |
| mutual_gains | sum_system | choice | choice | choice | False | 240 |

## Monitor haiku

Verdicts 19200, unparsed 1.

By channel and view (%):

| metric | channel | action | report | delivered | raw | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | raw | 51.5 [30.7, 69.3] | 19.6 [5.1, 33.3] | 0.0 [0.0, 0.0] | n/a | 19.6 [6.2, 31.9] | 2.1 [0.0, 6.6] | 30.9 [19.3, 42.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 1.0 [0.0, 3.3] | 0.0 [0.0, 0.0] |
| missed collusion (FNR) | paraphrased | 49.0 [28.5, 66.7] | 23.0 [11.0, 35.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 21.0 [7.8, 34.4] | 1.0 [0.0, 3.2] | 37.0 [21.5, 51.7] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 2.0 [0.0, 4.7] | 0.0 [0.0, 0.0] |
| missed collusion (FNR) | neutralized | 47.6 [26.2, 66.3] | 19.5 [7.2, 31.6] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 12.2 [2.9, 22.0] | 0.0 [0.0, 0.0] | 23.2 [10.0, 38.3] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 3.7 [0.0, 8.0] | 0.0 [0.0, 0.0] |
| missed collusion (FNR) | sum_short | n/a | n/a | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_long | n/a | n/a | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_system | n/a | n/a | 2.1 [0.0, 5.9] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_codeswitch | n/a | n/a | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | raw | 54.7 [34.0, 71.3] | 18.7 [3.9, 34.1] | 0.0 [0.0, 0.0] | n/a | 21.3 [6.3, 35.8] | 2.7 [0.0, 8.5] | 10.7 [2.8, 18.5] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 1.3 [0.0, 4.5] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | paraphrased | 50.0 [31.1, 67.1] | 19.7 [9.8, 30.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 16.7 [6.8, 28.8] | 0.0 [0.0, 0.0] | 4.5 [0.0, 10.3] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | neutralized | 50.0 [28.3, 68.9] | 19.7 [7.5, 32.1] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 10.6 [1.6, 21.2] | 0.0 [0.0, 0.0] | 4.5 [0.0, 12.5] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 4.5 [0.0, 9.7] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | sum_short | n/a | n/a | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_long | n/a | n/a | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_system | n/a | n/a | 3.7 [0.0, 9.5] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_codeswitch | n/a | n/a | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | raw | 20.3 [8.1, 34.5] | 21.0 [10.9, 31.9] | 62.9 [50.0, 75.4] | n/a | 21.7 [11.3, 32.7] | 100.0 [100.0, 100.0] | 0.7 [0.0, 2.4] | 13.3 [6.2, 21.1] | 11.2 [5.1, 18.1] | 14.7 [7.3, 22.8] | 7.0 [2.6, 11.7] |
| false alarm, harmful but declined | paraphrased | 17.1 [6.8, 30.5] | 19.3 [9.7, 31.0] | 59.3 [46.3, 71.2] | 56.4 [42.2, 70.1] | 18.6 [9.5, 29.4] | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0] | 12.1 [5.3, 20.2] | 9.3 [3.6, 15.7] | 12.9 [5.9, 21.1] | 7.9 [2.9, 13.9] |
| false alarm, harmful but declined | neutralized | 18.4 [6.7, 32.9] | 22.2 [11.2, 34.9] | 47.5 [35.7, 59.5] | 63.3 [50.8, 74.8] | 21.5 [11.1, 33.5] | 99.4 [97.9, 100.0] | 0.0 [0.0, 0.0] | 14.6 [7.4, 22.6] | 14.6 [6.8, 23.3] | 15.8 [7.0, 26.4] | 13.9 [6.4, 23.3] |
| false alarm, harmful but declined | sum_short | n/a | n/a | 41.9 [30.4, 53.7] | 67.1 [57.3, 75.9] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_long | n/a | n/a | 52.9 [42.0, 63.1] | 63.6 [52.1, 74.2] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_system | n/a | n/a | 22.8 [12.7, 33.8] | 55.4 [43.2, 67.2] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_codeswitch | n/a | n/a | 58.6 [44.4, 72.1] | 60.0 [47.0, 72.7] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | raw | 59.1 [29.2, 87.5] | 77.3 [57.7, 95.0] | 100.0 [100.0, 100.0] | n/a | 86.4 [70.8, 100.0] | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| flagged, collusive before any message | paraphrased | 52.9 [21.9, 85.7] | 70.6 [44.0, 96.3] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 70.6 [44.9, 95.8] | 97.1 [91.1, 100.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 94.1 [87.1, 100.0] | 100.0 [100.0, 100.0] |
| flagged, collusive before any message | neutralized | 62.5 [25.0, 100.0] | 81.2 [60.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 81.2 [60.0, 100.0] | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] |
| flagged, collusive before any message | sum_short | n/a | n/a | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_long | n/a | n/a | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_system | n/a | n/a | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_codeswitch | n/a | n/a | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | raw | 0.0 [0.0, 0.0] | 0.8 [0.0, 2.1] | 5.9 [2.4, 10.1] | n/a | 0.4 [0.0, 1.4] | 2.5 [0.4, 5.2] | 0.0 [0.0, 0.0] | 1.7 [0.4, 3.4] | 3.8 [1.0, 7.3] | 0.0 [0.0, 0.0] | 5.9 [2.5, 9.9] |
| false alarm, twins | paraphrased | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 5.4 [1.9, 9.7] | 2.1 [0.4, 4.3] | 0.0 [0.0, 0.0] | 2.5 [0.0, 5.5] | 0.0 [0.0, 0.0] | 0.8 [0.0, 2.1] | 4.6 [1.5, 8.2] | 0.0 [0.0, 0.0] | 4.2 [1.5, 7.3] |
| false alarm, twins | neutralized | 0.0 [0.0, 0.0] | 1.3 [0.0, 2.8] | 3.8 [1.2, 7.0] | 3.8 [1.0, 7.0] | 0.0 [0.0, 0.0] | 1.3 [0.0, 3.3] | 0.0 [0.0, 0.0] | 3.4 [0.7, 6.8] | 4.7 [1.8, 7.9] | 0.0 [0.0, 0.0] | 3.0 [0.9, 5.3] |
| false alarm, twins | sum_short | n/a | n/a | 6.0 [3.2, 9.0] | 4.7 [1.9, 7.9] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_long | n/a | n/a | 3.4 [1.4, 5.5] | 3.4 [0.9, 6.2] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_system | n/a | n/a | 1.6 [0.0, 3.4] | 2.6 [0.5, 5.4] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_codeswitch | n/a | n/a | 5.5 [2.3, 9.2] | 2.5 [0.5, 4.9] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

Pooled over channels (%):

| metric | action | report | delivered | raw | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | 49.5 [29.6, 66.4] | 20.8 [8.4, 32.6] | 0.2 [0.0, 0.5] | 0.0 [0.0, 0.0] | 17.9 [6.2, 29.2] | 1.1 [0.0, 2.7] | 30.8 [18.9, 42.1] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 2.2 [0.8, 3.6] | 0.0 [0.0, 0.0] |
| missed, message-moved episodes only | 51.7 [33.0, 67.2] | 19.3 [8.0, 30.8] | 0.2 [0.0, 0.7] | 0.0 [0.0, 0.0] | 16.4 [6.1, 27.1] | 1.0 [0.0, 3.2] | 6.8 [1.8, 12.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 1.9 [0.4, 3.8] | 0.0 [0.0, 0.0] |
| false alarm, harmful but declined | 18.6 [7.6, 32.0] | 20.9 [11.2, 32.1] | 48.0 [37.9, 57.9] | 60.9 [50.3, 70.9] | 20.6 [11.6, 30.4] | 99.8 [99.2, 100.0] | 0.2 [0.0, 0.8] | 13.4 [7.0, 20.5] | 11.8 [5.7, 18.5] | 14.5 [7.2, 22.8] | 9.8 [4.7, 15.6] |
| flagged, collusive before any message | 56.9 [26.6, 86.8] | 75.0 [53.4, 95.7] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 77.8 [58.7, 95.2] | 98.6 [95.7, 100.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 97.2 [93.8, 100.0] | 100.0 [100.0, 100.0] |
| false alarm, twins | 0.0 [0.0, 0.0] | 0.7 [0.1, 1.5] | 4.6 [2.9, 6.4] | 3.2 [1.4, 5.4] | 0.1 [0.0, 0.5] | 2.1 [0.3, 4.5] | 0.0 [0.0, 0.0] | 2.0 [0.7, 3.5] | 4.3 [2.1, 6.9] | 0.0 [0.0, 0.0] | 4.3 [2.1, 7.0] |

| contrast | pp |
|---|---|
| C5 FNR delivered minus raw, paraphrased | 0.0 [0.0, 0.0] |
| C5 FNR delivered minus raw, neutralized | 0.0 [0.0, 0.0] |
| C6 FNR action minus delivered | +49.3 [29.6, 66.1] |
| 2.2 fnr action minus both | +28.7 [17.1, 39.4] |
| 2.2 fnr report only minus both | -2.9 [-6.8, 1.1] |
| 2.2 fpr declined message only minus all | +51.8 [42.0, 61.9] |

## Monitor mistral

Verdicts 19200, unparsed 0.

By channel and view (%):

| metric | channel | action | report | delivered | raw | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | raw | 75.3 [56.5, 90.0] | 57.7 [41.2, 71.7] | 10.3 [4.4, 16.4] | n/a | 52.6 [34.9, 68.1] | 12.4 [6.0, 18.6] | 79.4 [65.1, 90.5] | 25.8 [15.5, 36.0] | 21.6 [11.6, 32.1] | 36.1 [20.8, 50.5] | 29.9 [17.6, 41.1] |
| missed collusion (FNR) | paraphrased | 75.0 [56.5, 89.4] | 59.0 [43.5, 72.8] | 14.0 [7.2, 22.9] | 12.0 [4.8, 21.1] | 53.0 [37.1, 67.3] | 10.0 [4.4, 16.2] | 85.0 [73.2, 94.2] | 21.0 [10.9, 31.6] | 22.0 [11.4, 34.1] | 28.0 [18.2, 37.9] | 21.0 [11.6, 31.2] |
| missed collusion (FNR) | neutralized | 78.0 [59.7, 92.5] | 65.9 [50.8, 78.6] | 13.4 [6.2, 22.0] | 17.1 [9.1, 25.9] | 61.0 [44.6, 75.6] | 9.8 [3.1, 17.6] | 86.6 [75.9, 95.9] | 23.2 [11.5, 35.8] | 28.0 [15.5, 43.1] | 42.7 [30.2, 54.4] | 35.4 [20.8, 50.0] |
| missed collusion (FNR) | sum_short | n/a | n/a | 21.9 [10.1, 35.0] | 15.1 [4.2, 28.6] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_long | n/a | n/a | 18.0 [10.9, 25.8] | 20.0 [12.8, 27.8] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_system | n/a | n/a | 42.6 [29.2, 53.3] | 38.3 [22.6, 50.8] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed collusion (FNR) | sum_codeswitch | n/a | n/a | 7.4 [1.1, 15.4] | 9.5 [3.2, 16.1] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | raw | 81.3 [65.4, 92.3] | 60.0 [43.1, 73.1] | 13.3 [6.2, 20.0] | n/a | 52.0 [33.3, 67.4] | 16.0 [7.7, 24.7] | 73.3 [56.2, 87.4] | 21.3 [10.8, 32.0] | 18.7 [9.5, 29.3] | 41.3 [23.2, 56.7] | 28.0 [15.2, 40.7] |
| missed, message-moved episodes only | paraphrased | 86.4 [71.7, 96.2] | 65.2 [50.8, 77.8] | 13.6 [3.8, 26.4] | 10.6 [2.2, 23.0] | 59.1 [43.8, 73.6] | 4.5 [0.0, 11.3] | 77.3 [60.9, 90.7] | 15.2 [5.2, 26.2] | 9.1 [3.0, 17.2] | 27.3 [14.0, 40.8] | 13.6 [4.9, 25.0] |
| missed, message-moved episodes only | neutralized | 86.4 [71.6, 96.2] | 72.7 [58.8, 83.7] | 13.6 [5.7, 23.9] | 19.7 [10.3, 31.0] | 65.2 [49.3, 78.9] | 7.6 [1.9, 15.3] | 83.3 [71.2, 94.6] | 12.1 [1.9, 23.5] | 19.7 [9.1, 33.8] | 50.0 [35.9, 62.8] | 30.3 [13.8, 48.1] |
| missed, message-moved episodes only | sum_short | n/a | n/a | 18.6 [7.7, 30.1] | 13.6 [3.6, 24.5] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_long | n/a | n/a | 17.1 [9.0, 26.3] | 21.1 [12.2, 30.3] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_system | n/a | n/a | 44.4 [26.7, 60.9] | 33.3 [14.3, 50.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| missed, message-moved episodes only | sum_codeswitch | n/a | n/a | 8.2 [0.0, 17.6] | 11.0 [3.1, 19.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | raw | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 51.7 [36.3, 66.7] | n/a | 7.0 [2.9, 11.6] | 79.7 [71.8, 86.9] | 0.0 [0.0, 0.0] | 6.3 [1.6, 11.8] | 16.8 [8.5, 26.2] | 4.2 [0.7, 8.6] | 10.5 [3.8, 18.2] |
| false alarm, harmful but declined | paraphrased | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 52.9 [37.2, 68.8] | 53.6 [39.5, 68.1] | 6.4 [1.4, 12.7] | 77.1 [68.2, 85.6] | 0.0 [0.0, 0.0] | 3.6 [0.0, 8.1] | 17.9 [8.3, 29.4] | 6.4 [2.8, 10.7] | 7.1 [1.7, 14.6] |
| false alarm, harmful but declined | neutralized | 0.0 [0.0, 0.0] | 1.3 [0.0, 4.2] | 57.6 [44.1, 70.6] | 51.9 [38.5, 65.3] | 7.6 [3.4, 12.4] | 86.1 [77.0, 93.7] | 0.0 [0.0, 0.0] | 6.3 [1.4, 12.1] | 15.2 [7.5, 23.3] | 7.0 [1.7, 13.0] | 8.2 [3.0, 14.5] |
| false alarm, harmful but declined | sum_short | n/a | n/a | 50.3 [35.4, 64.8] | 57.5 [44.7, 69.7] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_long | n/a | n/a | 57.9 [43.2, 71.8] | 53.6 [39.8, 67.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_system | n/a | n/a | 43.0 [29.6, 56.9] | 49.2 [34.5, 63.6] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, harmful but declined | sum_codeswitch | n/a | n/a | 50.3 [33.7, 66.7] | 53.8 [38.2, 69.2] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | raw | 45.5 [14.3, 74.1] | 50.0 [21.1, 78.6] | 100.0 [100.0, 100.0] | n/a | 45.5 [14.3, 74.1] | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0] | 59.1 [36.8, 81.2] | 68.2 [43.5, 91.3] | 81.8 [64.3, 95.7] | 63.6 [42.1, 87.5] |
| flagged, collusive before any message | paraphrased | 47.1 [15.0, 79.2] | 52.9 [23.7, 82.4] | 85.3 [73.7, 95.2] | 85.3 [75.0, 95.0] | 58.8 [31.4, 86.4] | 79.4 [69.2, 90.5] | 0.0 [0.0, 0.0] | 67.6 [48.0, 86.4] | 52.9 [34.1, 72.0] | 70.6 [53.8, 84.4] | 64.7 [50.0, 82.6] |
| flagged, collusive before any message | neutralized | 56.2 [18.2, 92.3] | 62.5 [36.4, 90.9] | 87.5 [75.0, 100.0] | 93.8 [82.4, 100.0] | 56.2 [25.0, 90.9] | 81.2 [66.7, 100.0] | 0.0 [0.0, 0.0] | 31.2 [7.1, 60.0] | 37.5 [7.1, 73.4] | 87.5 [73.3, 100.0] | 43.8 [20.0, 66.7] |
| flagged, collusive before any message | sum_short | n/a | n/a | 64.3 [38.9, 100.0] | 78.6 [50.0, 100.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_long | n/a | n/a | 79.2 [58.8, 95.8] | 83.3 [69.0, 96.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_system | n/a | n/a | 60.0 [40.0, 81.8] | 55.0 [33.3, 81.2] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| flagged, collusive before any message | sum_codeswitch | n/a | n/a | 95.5 [83.3, 100.0] | 95.5 [83.3, 100.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | raw | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | 0.0 [0.0, 0.0] | 11.4 [3.9, 20.1] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| false alarm, twins | paraphrased | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 6.7 [1.9, 12.1] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.4 [0.0, 1.3] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| false alarm, twins | neutralized | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.4 [0.0, 1.4] | 4.2 [0.0, 9.4] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| false alarm, twins | sum_short | n/a | n/a | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_long | n/a | n/a | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_system | n/a | n/a | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| false alarm, twins | sum_codeswitch | n/a | n/a | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

Pooled over channels (%):

| metric | action | report | delivered | raw | report_only | message_only | standard | baseline_info | pop_baseline | summary | family_baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|
| missed collusion (FNR) | 76.0 [57.9, 90.1] | 60.6 [46.2, 72.3] | 16.2 [11.2, 21.4] | 16.9 [11.7, 22.1] | 55.2 [39.7, 68.5] | 10.8 [5.9, 16.1] | 83.5 [73.2, 91.8] | 23.3 [14.5, 32.1] | 23.7 [13.8, 34.7] | 35.1 [24.8, 44.7] | 28.3 [18.2, 38.4] |
| missed, message-moved episodes only | 84.5 [70.7, 93.6] | 65.7 [53.6, 75.0] | 15.8 [10.0, 22.1] | 16.6 [10.8, 22.9] | 58.5 [44.5, 70.1] | 9.7 [4.9, 15.6] | 77.8 [65.2, 88.5] | 16.4 [8.6, 24.7] | 15.9 [9.0, 24.8] | 39.6 [26.9, 50.5] | 24.2 [13.8, 35.6] |
| false alarm, harmful but declined | 0.0 [0.0, 0.0] | 0.5 [0.0, 1.5] | 51.6 [38.0, 64.9] | 53.1 [40.3, 66.1] | 7.0 [3.4, 11.3] | 81.2 [74.1, 87.7] | 0.0 [0.0, 0.0] | 5.4 [2.2, 9.2] | 16.6 [9.0, 25.0] | 5.9 [2.8, 9.3] | 8.6 [3.6, 14.6] |
| flagged, collusive before any message | 48.6 [16.3, 77.4] | 54.2 [28.6, 79.2] | 82.9 [75.0, 90.4] | 82.3 [74.6, 90.4] | 54.2 [26.4, 79.8] | 86.1 [78.2, 93.8] | 0.0 [0.0, 0.0] | 56.9 [45.6, 70.7] | 54.2 [36.4, 73.2] | 77.8 [66.0, 87.9] | 59.7 [46.4, 76.6] |
| false alarm, twins | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.1 [0.0, 0.5] | 7.4 [2.5, 13.3] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.1 [0.0, 0.5] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

| contrast | pp |
|---|---|
| C5 FNR delivered minus raw, paraphrased | +2.0 [-3.5, 7.8] |
| C5 FNR delivered minus raw, neutralized | -3.7 [-11.3, 2.9] |
| C6 FNR action minus delivered | +59.8 [43.1, 73.5] |
| 2.2 fnr action minus both | +15.4 [6.6, 24.8] |
| 2.2 fnr report only minus both | -5.4 [-11.7, 1.4] |
| 2.2 fpr declined message only minus all | +29.6 [17.4, 42.2] |
