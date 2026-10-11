# Results

Results of experiments run with the project's own commands. To run your own,
see [Training the Learning Bots](training.md) and
[Bot Experiments](bot-experiments.md).

## Feature Set v3 experiment

Feature Set v3 ([ADR 0009](adr/0009-version-learned-artifacts-by-feature-set.md))
adds three "can I still reach my tail?" features and counts open space as the
tail moves away. This experiment checks whether that helps Q Learning and DQN,
and which of the two learns better with it.

### Setup

Every bot trained on the 24 × 25 board with a 5000-move limit, starting from an
empty table or a new network. Each bot was trained three times with the same
three seeds, so one lucky or unlucky run cannot decide the result and v2 and v3
get exactly the same chances. Every bot then played the same 200 evaluation
games (seeds 200000–200199), which no bot trained on, in Evaluation Mode.

| Bot | Training games | Training seeds |
| --- | --- | --- |
| Q Learning v2 | 2000 each | 9000, 12000, 15000 |
| DQN v2 | 2000 each | 9000, 12000, 15000 |
| Q Learning v3 | 2000 each | 9000, 12000, 15000 |
| DQN v3 | 2000 each | 9000, 12000, 15000 |

### v2 against v3 (5000-move limit)

Mean score over the 200 games:

| Bot | Each training seed | Average | Best game |
| --- | --- | --- | --- |
| Q Learning v2 | 43.6, 44.1, 43.1 | 43.6 | 87 |
| DQN v2 | 32.9, 37.8, 31.1 | 33.9 | 76 |
| Q Learning v3 | 105.3, 123.6, 127.7 | 118.9 | 173 |
| DQN v3 | 140.8, 139.6, 128.3 | 136.2 | 176 |

Compared game by game, Q Learning v3 scores 75.3 more than v2 (95% range
72.6 to 78.0) and DQN v3 scores 102.3 more (100.0 to 104.6). v3 scores higher
in all 200 games for both bots. Many v3 games reached the 5000-move limit
while the snake was still alive (up to 159 of 200), so these v3 scores are
lower than the bots' real results; no v2 game reached the limit.

With v2, Q Learning scores 9.7 more than DQN (95% range 8.1 to 11.3) and is
ahead in 159 of the 200 games. With v3 the order flips: DQN v3 scores 17.4
more than Q Learning v3 (14.4 to 20.3) at this limit, and 60.0 more at the
20,000-move limit below.

### Q Learning v3 against DQN v3 (20,000-move limit)

The same six v3 bots were evaluated again with room to play on:

| Bot | Each training seed | Average | Best game |
| --- | --- | --- | --- |
| Q Learning v3 | 108.7, 132.1, 155.4 | 132.1 | 302 |
| DQN v3 | 236.4, 196.8, 143.0 | 192.0 | 356 |

Game by game, DQN v3 scores 60.0 more than Q Learning v3 (95% range 53.0 to
66.9) and wins 171 of the 200 games. Even 20,000 moves cut off 100 games for
one DQN model; those were its best games (316 food on average), so DQN's real
lead is larger still. No bot filled the board.

### Verdict

- v3 breaks the v2 ceiling: Q Learning scores about 2.7 times higher and DQN
  about 4 times higher, because knowing whether the tail is still reachable
  stops the snake trapping itself.
- The better learner depends on the Feature Set. With v2, the table beats the
  network by about 10 points; with v3, DQN is clearly better. v2 has few
  possible situations, so a table can learn each one; v3 has many more, and the
  neural network generalises between similar ones where the table must learn
  each one separately.
- The training seed matters a lot for v3. DQN v3 models differ by up to 93
  points at the 20,000-move limit, so compare several runs rather than one.
  The v2 runs agree within about 7 points.

### Limitations and notes

- The move limit cuts off many v3 games, so v3 scores, and DQN's lead at
  20,000 moves, are lower than the bots' real results (see above).
- The v2 bots above were trained and evaluated on a Windows computer and the v3
  bots on a Mac; the 20,000-move evaluations also ran on a different computer,
  and every game that ended before move 5000 matched the 5000-move run exactly.
- An earlier baseline used an older local Q Learning v2 table (about 2000
  games) and DQN v2 runs with other seeds (1000, 3000, 6000; 2000, 1200 and
  1200 games). That DQN v2 baseline scored 33.0, the same as the matched runs
  above. The old Q Learning v2 table scored only 33.1, 10.5 less than the
  matched tables (95% range 8.6 to 12.3). That table was trained before
  Q-tables kept a Training History
  ([ADR 0010](adr/0010-keep-q-learning-training-history-inside-the-q-table.md)),
  so the reason is unknown.
- Re-checked on 2026-10-11 at commit `e2a6d8f`: the Q Learning v2 table from
  training seed 12000 replayed all 200 evaluation games exactly as before, game
  for game, so these results still hold for the current code.

### How to repeat

Train with the seeds above, then evaluate on the same 200 seeds. For training
seed 9000:

```bash
uv run python -m snake.sessions.TrainQLearning --new-table --q-table learning_data/q_table_v2_seed9000.json --seed 9000 --games 2000
uv run --group dqn python -m snake.sessions.TrainDQN --features v2 --seed 9000 --games 2000
uv run --group dqn python -m snake.sessions.RunExperiment --bots q_learning dqn --q-table learning_data/q_table_v2_seed9000.json --dqn-model learning_data/dqn_runs/<run-id>/model.pt --games 200 --seed 200000 --max-moves 5000
uv run python -m snake.sessions.RunExperiment --bots q_learning_v3 --q-table-v3 learning_data/q_table_v3_seed9000.json --games 200 --seed 200000 --max-moves 20000
uv run --group dqn python -m snake.sessions.RunExperiment --bots dqn --dqn-model learning_data/dqn_runs/<run-id>/model.pt --games 200 --seed 200000 --max-moves 20000
```

The v3 bots train the same way, with their own Feature Set:

```bash
uv run python -m snake.sessions.TrainQLearning --bot q_learning_v3 --new-table --q-table learning_data/q_table_v3_seed9000.json --seed 9000 --games 2000
uv run --group dqn python -m snake.sessions.TrainDQN --features v3 --seed 9000 --games 2000
```

Repeat for seeds 12000 and 15000. Training uses the default 24 × 25 board and
5000-move limit.

## Reference bots (no learning)

Rule Based, Search-Based, and Hamiltonian do not learn, so training games
would not change them. They are reference points for the learning bots above,
not competitors: Rule Based shows what simple hand-written rules reach, and
Hamiltonian shows the other extreme, a bot that always fills the board but
needs far more moves.

All runs used the same 24 × 25 board and evaluation seeds as the experiment
above, with code at commit `e2a6d8f` (after the Search-Based loop fix in PR
#133), Python 3.13.16, on a Windows virtual machine on 2026-10-11.

### Rule Based and Search-Based (seeds 200000–200199)

Both bots play until they crash. Their longest games lasted 685 and 1,762
moves, so the 5000-move limit never ended one of their games.

| Bot | Games | Mean score | Median | Best | Mean moves | Moves per food | How the games ended |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Rule Based | 200 | 13.9 | 13 | 37 | 229 | 16.5 | 200 collisions |
| Search-Based | 200 | 38.0 | 36 | 85 | 696 | 18.3 | 200 collisions |

On the same 200 games, the learning bots above average 43.6 (Q Learning v2),
33.9 (DQN v2), 118.9 (Q Learning v3), and 136.2 (DQN v3).

### Hamiltonian (seeds 200000–200019)

Hamiltonian does not crash: it follows a route through every cell, so the
question is how long it takes to win. It ran with a 100,000-move limit, which
no game came near.

| Games | Wins | Mean moves per win | Fewest | Most | Moves per food | Time per win |
| --- | --- | --- | --- | --- | --- | --- |
| 20 | 20 (board filled, score 599) | 46,572 | 43,992 | 49,150 | 77.7 | about 1 min 49 s |

These are the first 20 of the 200 seeds above. More games would not change
the picture: every game filled the board.

### Notes

- Moves per food is the mean number of moves divided by the mean score. It
  shows how directly a bot reaches food: Hamiltonian needs about 4 to 5 times
  more moves per food than Rule Based or Search-Based, which is the price of
  never crashing.
- Hamiltonian is not compared at the 5000-move limit used above: it needs
  about 46,600 moves to fill the board, so a 5000-move cut-off would only show
  how far it got, not how it plays.
- Search-Based is slow per move because it plans ahead: its 200 games took
  about 71 minutes on the virtual machine. Rule Based's time is left out
  because the console was paused during its run. Times depend on the machine;
  scores do not.
- These bots use no randomness, so the same code and seeds give the same
  games: the first 9 games of an earlier, interrupted Hamiltonian run matched
  the 20-game run move for move.

### How to repeat

```bash
uv run python -m snake.sessions.RunExperiment --bots rule search_based --games 200 --seed 200000 --max-moves 5000
uv run python -m snake.sessions.RunExperiment --bots hamiltonian --games 20 --seed 200000 --max-moves 100000
```

No Q-table is needed for these bots.
