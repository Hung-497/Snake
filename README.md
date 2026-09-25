# Snake AI Project

## Overview

A Python Snake game built with Arcade 3.
The project starts with a basic Snake game, then adds different AI bots, records,
settings, and replay playback.

## Features

- Basic Snake game
- Rule-based bot
- Tabular Q-learning bot
- Hamiltonian cycle bot
- Safe shortcut logic
- Tail reachability check
- Flood fill space checking
- Arcade bot selection menu
- Settings screen for speed, board size, and tile size
- Resizable window with a board that scales to fit
- Records screen with bot filters and summary stats
- Replay saving and playback for saved bot runs
- Q-learning persistence with saved Q-table data

## Installation

This project uses Python and [Arcade](https://api.arcade.academy) 3 for the whole
app: the window, the screens, the buttons, the timing, and the drawing.

Install the dependency with:

```bash
python3 -m pip install -r requirements.txt
```

Arcade draws with OpenGL, so it needs a normal desktop session with a graphics
driver. It works on macOS, Windows, and Linux.

## How to Run

```bash
cd Snake && python3 SnakeApp.py
```

The app opens at 900 x 960 in one resizable window and moves between screens
inside it. The board uses the chosen Tile Size when it fits, or smaller whole
tiles when the window is narrow. Window size is not saved between runs.

```text
Menu -> Play -> Rule Based / Q Learning / Hamiltonian
     -> Settings -> speed, board size, tile size
     -> Replay   -> watch the best saved game of a bot
     -> Records  -> summary statistics and recent games
```

Settings are kept for as long as the app is open, so a game started afterwards
uses the speed, board size, and tile size chosen there. Closing the window
closes the app.

## Local Runtime Data

Games save watched-game records in `records/` and best replays in `replays/`.
Q Learning saves its progress in `learning_data/`, and Bot Experiments save
separate reports in `experiments/`. These folders contain local Runtime Data;
Git ignores their contents. Existing local files stay in place during this
cleanup. A fresh clone starts with no saved records or replays.

The project bundles a Starter Q-table at
`starter_data/q_table_space_state_v2.json`. Headless training and Bot
Experiments need a local saved Q-table. From the project root, copy the starter
once before using either command:

```bash
mkdir -p learning_data
cp -n starter_data/q_table_space_state_v2.json learning_data/q_table_space_state_v2.json
```

The `-n` option preserves an existing local table. On Windows, create the
`learning_data` folder and copy the starter with File Explorer only when the
local table does not already exist. Later training updates the local copy; the
Starter Q-table stays unchanged. The app can also start Q Learning without a
saved table, beginning new local progress instead of loading the starter.

## Headless Q Learning Training

Run training from the project root without opening the app window:

```bash
python3 -m snake.sessions.TrainQLearning --games 100 --width 24 --height 25 --seed 7 --max-moves 5000
```

This resumes the existing saved Q-table and saves learning progress back to it
after each game. A missing or malformed table stops the command with an error;
training does not start a new table. The command prints score and learning
progress in the terminal. It does not add watched-game records or replays.

`--games` is required. The default board is 24 × 25, the default Tile Size is
25, the default seed is 0, and the default move limit is 5000 per game.

## Bot Experiments

Compare Rule Based, Q Learning, and Hamiltonian without opening the app:

```bash
python3 -m snake.sessions.RunExperiment --games 10 --width 24 --height 25 --seed 7 --max-moves 5000
```

The command defaults to one game. It uses the same board and seeds for each Bot
Mode: with `--seed 7 --games 10`, the per-game seeds are 7 through 16. Each game
gets fresh Game Engine and bot random sources. The Game Engine uses the listed
seed; the bot uses that seed plus one. Use the same command, code, and
Q-table again to repeat the gameplay results. Each run saves a new JSON file in
`experiments/` and prints its path; older results are kept.

Q Learning uses Evaluation Mode: it reads the saved Q-table without exploring,
learning, or saving changes. Use `--q-table path/to/table.json` to select a
different table. Missing or malformed tables, invalid settings, and boards
unsupported by Hamiltonian stop before play. Hamiltonian needs both board
dimensions to be at least two and at least one even dimension. Training Mode
uses the separate command above and does change the saved Q-table.

The JSON keeps every game's seed, score, moves, and outcome (`won`, `collision`,
or `move_limit`). A move limit is never counted as a win or a collision. On a
large board, the move limit may end a surviving Hamiltonian game before the
snake fills every cell. Each Bot Mode also has:

- Mean, median, and best score; population score standard deviation. Lower
  standard deviation means more consistent scores within that workload.
- Wins and win rate (a fraction in JSON, shown as a percentage in the terminal),
  plus collision and move-limit counts.
- Total, mean, median, minimum, and maximum moves, and games per second.

The result records creation time, Python version, Git commit, a hash of the
current `snake/` Python sources, board settings, game count, base and per-game
seeds, move limit, and the selected Q-table's path, hash, and learning settings.
It also states the timing basis. Games per second measures wall time for each
Bot Mode's actual gameplay. It excludes engine and bot setup, Q-table loading,
the initial Q-table check, and JSON writing. Throughput varies
by machine and Python version, so compare it under the same environment.

These experiments use one fixed Q-table and one board configuration per run.
They do not train a new policy, measure statistical confidence, or save watched
game records and replays. Scores are comparable across bots for the same seed
list; elapsed time can vary between otherwise identical runs.

## Run Tests

Install the app and development test dependencies:

```bash
python3 -m pip install -r requirements.txt -r requirements-dev.txt
```

Run the tests from the project root:

```bash
python3 -m pytest
```

GitHub Actions runs this same test command on Python 3.13 for pull requests
and pushes to `main`.

Saved results can be viewed from:

```text
Records -> All / Rule / Q-Learning / Hamiltonian
```

Saved replays can be played from:

```text
Replay -> Rule Based / Q Learning / Hamiltonian
```

## Bot Results

| Bot             | Result                                                              |
| --------------- | ------------------------------------------------------------------- |
| Rule-based bot  | Can play, but may still trap itself                                 |
| Q-learning bot  | Learns short-term behavior, but struggles with long-term traps      |
| Hamiltonian bot | Beats the game consistently using cycle planning and safe shortcuts |

## Demo

### App Screens

These screenshots were taken before the move to Arcade, so the screens look
different now. The actions on them are the same.

**Main Menu**

![Main Menu](/img/Main_Menu.png)

**Play Screen**

![Play Screen](/img/Play_Screen.png)

**Settings Screen**

![Settings Screen](/img/Settings_Screen.png)

**Logs Screen**

![Logs Screen](/img/Logs_Screen.png)

**Replay Screen**

![Replay Screen](/img/Replay_Screen.png)

### Bot Demos

1. Rule-based Bot

![demo_rule_based_bot](/img/Demo_RuleBasedBot.gif)

_Display_

![result_rule_based_bot](/img/Result_RuleBasedBot.png)

_Results on the terminal_

2. Q-learning Bot

![demo_q_learning_bot](/img/Demo_QLearningBot.gif)

_Display_

![result_q_learning_bot](/img/Result_QLearningBot.png)

_Results on the terminal_

3. Hamiltonian Bot

![demo_hamiltonian_bot](/img/Demo_HamiltonianBot.gif)

_Display_

![result_hamiltonian_bot](/img/Result_HamiltonianBot.png)

_Results on the terminal_

## Project Structure

```text
SnakeApp.py          # Starts the app: the Arcade window and the App Views
snake/
  engine/            # GameConfig, GameTypes, SnakeEngine: board rules and state
  bots/              # BotMode, BotFactory, and the three Bot Modes
  sessions/          # GameSession, ReplaySession, SessionSettings
  storage/           # RecordManager and ReplayManager
  ui/                # AppShell, Theme, WindowLayout, MotionRules, BoardRenderer,
                     # and RecordsBrowser
    views/           # Menu, Settings, Play, Game, Replay, ReplayPlayback,
                     # and Records App Views
tests/               # Behavior and regression tests
assets/              # Bundled fonts
records/             # Saved game result CSV data
replays/             # Saved replay JSON files
learning_data/       # Saved Q-table data
starter_data/        # Bundled Starter Q-table
experiments/         # Saved Bot Experiment reports
docs/                # Architecture decisions and the smoke checklist
DEVLOG.md            # Development diary
```

## Development Diary

I documented the learning process, bugs, experiments, and results in [DEVLOG.md](DEVLOG.md).
