# Bot Experiments

A Bot Experiment compares Bot Modes on the same board and the same seeds,
without opening the app window. Each run saves a JSON report, separate from the
game records and replays the app keeps
([ADR 0004](adr/0004-run-bot-experiments-headlessly.md)). Run every command
below from the project root.

When Q Learning is part of an experiment, it needs a local saved Q-table first;
see [Set up the Starter Q-table](training.md#set-up-the-starter-q-table). For
results of past experiments, see [Results](results.md).

## Run a comparison

```bash
uv run python -m snake.sessions.RunExperiment --games 10 --width 24 --height 25 --seed 7 --max-moves 5000
```

The command defaults to one game. It uses the same board and seeds for each Bot
Mode: with `--seed 7 --games 10`, the per-game seeds are 7 through 16. Each game
gets fresh Game Engine and bot random sources. The Game Engine uses the listed
seed; the bot uses that seed plus one. Use the same command, code, and
Q-table again to repeat the gameplay results. Each run saves a new JSON file in
`experiments/` and prints its path; older results are kept.

The default board is 24 × 25, the default Tile Size is 25, the default seed is
0, and the default move limit is 5000 per game.

## Choose which bots to compare

By default, the command compares Rule Based, Q Learning, Hamiltonian, and
Search-Based. To compare only particular modes, list them after `--bots`:

```bash
uv run python -m snake.sessions.RunExperiment --bots rule search_based --games 10 --seed 7
```

The selected order is kept in the result. A one-bot experiment is also valid.
The default set follows new normal Bot Modes when they are registered.

The terminal prints each finished game while a comparison is running, then a
summary for each Bot Mode. Search-Based searches future moves on every board,
so ten full-board games can take ten minutes or more even when they make
steady progress. The default ten-game comparison above took about ten and a
half minutes on a Mac.

## Include DQN

To include DQN, explicitly select it and supply an evaluation model (see
[Training the Learning Bots](training.md#dqn)):

```bash
uv run --group dqn python -m snake.sessions.RunExperiment --bots rule q_learning dqn --dqn-model learning_data/dqn_runs/<run-id>/model.pt --games 10 --seed 7
```

DQN can also be selected alone. When Q Learning is selected, its local saved
Q-table or an explicit `--q-table` path is still required. Every selected bot
uses the same board and seed list. DQN's report entry identifies the model and
records the training and evaluation boards, so cross-board results remain
clear.

## Include Q Learning v3

Q Learning v3 is not in the default comparison. Select it explicitly to compare
both versions on the same seeds:

```bash
uv run python -m snake.sessions.RunExperiment --bots q_learning q_learning_v3 --games 10 --seed 7
```

Use `--q-table-v3 path/to/table.json` to evaluate a different v3 table. The
report records each table's Feature Set.

## How bots are checked before play

Q Learning uses Evaluation Mode: it reads the saved Q-table without exploring,
learning, or saving changes. Use `--q-table path/to/table.json` to select a
different table. A Q-table is required when Q Learning is selected, including
in the default comparison; the command never silently loads the Starter
Q-table. Training Mode uses the separate
[training command](training.md#q-learning) and does change the saved Q-table.

The command checks all selected bots and required files before any game begins;
it never silently omits an unsupported bot. Missing or malformed required
tables or models, invalid settings, and boards unsupported by a selected Bot
Mode stop before play. Hamiltonian needs both board dimensions to be at least
two and at least one even dimension.

## What the report records

The version 3 JSON records the selected Bot Modes and keeps every game's seed,
score, moves, and outcome (`won`, `collision`, or `move_limit`). A move limit is
never counted as a win or a collision. On a large board, the move limit may end
a surviving Hamiltonian game before the snake fills every cell. Each Bot Mode's
games and summary are stored under `bots.<bot mode>`, for example
`bots.search_based`. The summary has:

- Mean, median, and best score; population score standard deviation. Lower
  standard deviation means more consistent scores within that workload.
- Wins and win rate (a fraction in JSON, shown as a percentage in the terminal),
  plus collision and move-limit counts.
- Total, mean, median, minimum, and maximum moves, and games per second.

The result records creation time, Python version, Git commit, a hash of the
current `snake/` Python sources, board settings, game count, base and per-game
seeds, move limit, and each selected Q-table's path, hash, learning settings,
and Training History.

It also states the timing basis. Games per second measures wall time for each
Bot Mode's actual gameplay. It excludes engine and bot setup, Q-table loading,
the initial Q-table check, and JSON writing. Throughput varies by machine and
Python version, so compare it under the same environment.

## Limits

These experiments use one fixed Q-table and one board configuration per run.
They do not train a new policy, measure statistical confidence, or save game
records and replays. Human Play is not part of Bot Experiments. Scores are
comparable across bots for the same seed list; elapsed time can vary between
otherwise identical runs.
