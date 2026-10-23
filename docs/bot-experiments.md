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
so it is the slowest bot to compare. The default ten-game comparison above
took about two minutes on a Mac.

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

## Analyse saved experiments

The Bot Report command reads every saved report in `experiments/`, from these
commands and from the app's Evaluate, and writes one analysis as a page for
people and a Markdown file for agents ([ADR 0020](adr/0020-generate-bot-reports-and-commit-only-the-showcase-report.md)).
It never plays games or changes a report.

```bash
uv run python -m snake.sessions.AnalyseBots
```

It writes `reports/bot_report.html`, `reports/bot_report.md`, and the charts in
`reports/bot_report_charts/`. You rarely need to run it yourself: every finished
Evaluate in the app, `RunExperiment`, and `EvaluateDQN` rebuilds this local report
right after saving, so a newly evaluated bot appears next to every bot that played
the same games. The app's Evaluate screen then offers Open report (or R), and the
terminal commands print where the report is. The bot with the newest run is
marked Newest, and the face-off opens on it against the leader. To compare a new
bot with the others, evaluate it on the 200 study games; a 20-game run uses other
seeds, so it gets its own group. The committed Showcase Report is never rebuilt
automatically. Reports are grouped by their Experiment
Conditions (board, move limit, and exact seed list), and runs are only compared
inside a group. Each group shows:

- its result in one sentence and the bots ranked by average food per game;
- a histogram per bot: across is the score a game ended with, in ranges of 10,
  and up is how many games ended there (the Markdown also lists these counts);
- a face-off between any two bots on the same seeds: average, median, best
  game, games won head to head, moves per food, and stopped by limit side by
  side, the better value in bold, then one sentence and a 95% range that says
  whether the lead is reliable (the Markdown lists every pair);
- an overview row per bot file, with mean, median, best, spread, win and
  move-limit rates, and moves per point, plus a combined row for a bot with
  several bot files;
- where each bot file came from: Feature Set, games trained, app or terminal
  training, training seeds, and code version.

The HTML page has a light and a dark theme (it follows the system until you
choose one) and uses system fonts, so it works offline.

A bot file evaluated more than once shows only its newest run. Damaged,
incomplete, and older-format reports are skipped and counted. Use `--output` to
write somewhere else and `--experiments` to read another folder.

### The Showcase Report

`--showcase` writes the committed [Showcase Report](results/showcase.md) to
`docs/results/` instead. It uses only full 200-game study evaluations (24 × 25,
seeds 200000–200199, 5000 moves) whose file hash matches a shipped Showcase Bot,
plus the non-learning Bot Modes as Baselines, and lists anything without such a
run under "Not evaluated yet". To evaluate the Baselines on the study games:

```bash
uv run python -m snake.sessions.RunExperiment --bots rule hamiltonian search_based --games 200 --seed 200000 --max-moves 5000
uv run python -m snake.sessions.AnalyseBots --showcase
```

The Showcase Bots are evaluated with Evaluate showcase in the app (200 games),
or with `RunExperiment`/`EvaluateDQN` pointed at their files in
`starter_data/showcase/`. The same runs always give the same Showcase Report.

## Limits

These experiments use one fixed Q-table and one board configuration per run.
They do not train a new policy or save game records and replays; statistical
confidence comes from the Bot Report above. Human Play is not part of Bot Experiments. Scores are
comparable across bots for the same seed list; elapsed time can vary between
otherwise identical runs.
