# Showcase Report

The Showcase Bots shipped with the app and the non-learning Baselines, each measured in Evaluation Mode on the same 200 study games. Built from 6 runs in 1 group of Experiment Conditions. Runs are only compared inside the same group.

Every number is computed from the saved games. The Move-limit rate is the share of games stopped by the move limit rather than ended by a win or a collision. Moves per point is how many moves the bot needed for each point of score; a high value with a high Move-limit rate suggests circling instead of chasing food.

Game by game compares two bots on the same seeds, so the luck of where the food appears cancels out. Each seed gives one difference in score, and the Average difference is their mean. The 95% range shows how far that average could move if the bots were tested on other seeds: when the whole range is above zero, the first bot reliably scores more; when it includes zero, the games cannot show a difference. A bot with several bot files uses its average score on each seed.

Each histogram shows one bot: across is the score a game ended with, in ranges of 10, and up is how many games ended there. All of a group's histograms share one scale.

A bot file is the saved Q-table or DQN model, shown by the start of its hash. When the same bot file was evaluated more than once, only its newest run is shown. A combined row pools the games of every bot file of that bot.

Hamiltonian follows one route over the whole board, so it never collides, but filling the board takes far more than the study's 5000 moves. Its games stop at the move limit while the snake is still alive: its score shows how far that safe route gets in 5000 moves, not whether it can win.

## 24 × 25 board, 5000-move limit, seeds 200000–200199 (200 games)

| Bot | Bot file | Run date (UTC) | Games | Mean | Median | Best | Std dev | Win rate | Move-limit rate | Moves per point |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DQN v3 | 18b5932f | 2026-10-23 17:27 | 200 | 140.8 | 146.5 | 162 | 18.2 | 0.0% | 79.5% | 33.0 |
| Hamiltonian | — | 2026-10-23 17:27 | 200 | 122.5 | 123.0 | 132 | 3.9 | 0.0% | 100.0% | 40.8 |
| Q Learning v2 | 331d4d4a | 2026-10-23 17:27 | 200 | 44.1 | 44.0 | 87 | 14.8 | 0.0% | 0.0% | 24.3 |
| Q Learning v3 | 27fde16d | 2026-10-23 17:27 | 200 | 127.7 | 134.5 | 162 | 21.1 | 0.0% | 51.5% | 33.4 |
| Rule Based | — | 2026-10-23 17:27 | 200 | 13.9 | 13.0 | 37 | 9.4 | 0.0% | 0.0% | 16.5 |
| Search-Based | — | 2026-10-23 17:27 | 200 | 38.0 | 36.0 | 85 | 14.2 | 0.0% | 0.0% | 18.3 |

![Scores per game: 24 × 25 board, 5000-move limit, seeds 200000–200199 (200 games)](showcase_charts/scores_1.svg)

### Scores per game

| Score | DQN v3 | Q Learning v3 | Hamiltonian | Q Learning v2 | Search-Based | Rule Based |
| --- | --- | --- | --- | --- | --- | --- |
| 0 to 9 | 0 | 0 | 0 | 0 | 1 | 78 |
| 10 to 19 | 0 | 0 | 0 | 6 | 17 | 63 |
| 20 to 29 | 0 | 0 | 0 | 30 | 38 | 45 |
| 30 to 39 | 0 | 0 | 0 | 34 | 65 | 14 |
| 40 to 49 | 0 | 1 | 0 | 63 | 37 | 0 |
| 50 to 59 | 1 | 0 | 0 | 41 | 25 | 0 |
| 60 to 69 | 1 | 3 | 0 | 14 | 13 | 0 |
| 70 to 79 | 2 | 3 | 0 | 10 | 3 | 0 |
| 80 to 89 | 3 | 4 | 0 | 2 | 1 | 0 |
| 90 to 99 | 3 | 14 | 0 | 0 | 0 | 0 |
| 100 to 109 | 7 | 13 | 0 | 0 | 0 | 0 |
| 110 to 119 | 6 | 21 | 49 | 0 | 0 | 0 |
| 120 to 129 | 7 | 20 | 144 | 0 | 0 | 0 |
| 130 to 139 | 18 | 52 | 7 | 0 | 0 | 0 |
| 140 to 149 | 87 | 52 | 0 | 0 | 0 | 0 |
| 150 to 159 | 62 | 16 | 0 | 0 | 0 | 0 |
| 160 to 169 | 3 | 1 | 0 | 0 | 0 | 0 |

### Game by game

| Better bot | Compared with | Games | Average difference | 95% range | Verdict | Won / tied / lost |
| --- | --- | --- | --- | --- | --- | --- |
| DQN v3 | Q Learning v3 | 200 | 13.1 | 9.1 to 17.1 | DQN v3 scores more | 144 / 3 / 53 |
| DQN v3 | Hamiltonian | 200 | 18.3 | 15.6 to 20.9 | DQN v3 scores more | 176 / 1 / 23 |
| DQN v3 | Q Learning v2 | 200 | 96.7 | 93.5 to 99.9 | DQN v3 scores more | 199 / 0 / 1 |
| DQN v3 | Search-Based | 200 | 102.8 | 99.5 to 106.1 | DQN v3 scores more | 200 / 0 / 0 |
| DQN v3 | Rule Based | 200 | 126.9 | 124.1 to 129.8 | DQN v3 scores more | 200 / 0 / 0 |
| Q Learning v3 | Hamiltonian | 200 | 5.2 | 2.3 to 8.1 | Q Learning v3 scores more | 135 / 3 / 62 |
| Q Learning v3 | Q Learning v2 | 200 | 83.6 | 79.9 to 87.3 | Q Learning v3 scores more | 199 / 0 / 1 |
| Q Learning v3 | Search-Based | 200 | 89.7 | 86.2 to 93.3 | Q Learning v3 scores more | 198 / 0 / 2 |
| Q Learning v3 | Rule Based | 200 | 113.9 | 110.5 to 117.2 | Q Learning v3 scores more | 200 / 0 / 0 |
| Hamiltonian | Q Learning v2 | 200 | 78.4 | 76.3 to 80.5 | Hamiltonian scores more | 200 / 0 / 0 |
| Hamiltonian | Search-Based | 200 | 84.5 | 82.5 to 86.6 | Hamiltonian scores more | 200 / 0 / 0 |
| Hamiltonian | Rule Based | 200 | 108.7 | 107.2 to 110.2 | Hamiltonian scores more | 200 / 0 / 0 |
| Q Learning v2 | Search-Based | 200 | 6.2 | 3.5 to 8.8 | Q Learning v2 scores more | 128 / 4 / 68 |
| Q Learning v2 | Rule Based | 200 | 30.3 | 27.9 to 32.7 | Q Learning v2 scores more | 195 / 2 / 3 |
| Search-Based | Rule Based | 200 | 24.1 | 21.9 to 26.4 | Search-Based scores more | 180 / 18 / 2 |

### Where each bot came from

| Bot | Bot file | Feature Set | Games trained | Trained by | Training seeds | Code |
| --- | --- | --- | --- | --- | --- | --- |
| DQN v3 | 18b5932f | v3 | 2000 | Terminal command | 9000 | 1b597fe |
| Hamiltonian | — | — | — | — | — | 1b597fe |
| Q Learning v2 | 331d4d4a | v2 | 2000 | unknown | 12000 | 1b597fe |
| Q Learning v3 | 27fde16d | v3 | 2000 | unknown | 15000 | 1b597fe |
| Rule Based | — | — | — | — | — | 1b597fe |
| Search-Based | — | — | — | — | — | 1b597fe |
