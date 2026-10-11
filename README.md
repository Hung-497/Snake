# Snake AI Project

## Overview

A Python Snake game built with Arcade 3.
The project starts with a basic Snake game, then adds different AI bots, records,
settings, and replay playback. You can watch a bot play or play yourself with
the keyboard.

## Features

- Basic Snake game
- Human Play: steer the snake yourself with the arrow keys or WASD
- Rule-based bot
- Tabular Q-learning bot
- Hamiltonian cycle bot
- Search-Based bot that checks future moves and avoids food paths with no safe continuation
- Safe shortcut logic
- Tail reachability check
- Flood fill space checking
- Arcade Play menu: play yourself or choose a bot
- Settings screen for speed, board size, and tile size
- Resizable window with a board that scales to fit
- Records screen with filters for each bot and for Human Play, plus summary stats
- Replay saving and playback of the best game for each bot and for Human Play
- Q-learning persistence with saved Q-table data

## Installation

This project uses Python and [Arcade](https://api.arcade.academy) 3 for the whole
app: the window, the screens, the buttons, the timing, and the drawing.

The project uses [uv](https://docs.astral.sh/uv/) to manage Python and its
dependencies. Install uv first by following the
[official install guide](https://docs.astral.sh/uv/getting-started/installation/),
for example on macOS:

```bash
brew install uv
```

Then, from the project root, create the environment:

```bash
uv sync
```

`uv sync` downloads Python 3.13 if needed, creates `.venv`, and installs the
exact versions in `uv.lock`. Every command below starts with `uv run`, which
runs it inside that environment.

Arcade draws with OpenGL, so it needs a normal desktop session with a graphics
driver. It works on macOS, Windows, and Linux.

## How to Run

```bash
cd Snake && uv run python SnakeApp.py
```

The app opens at 900 x 960 in one resizable window and moves between screens
inside it. The board uses the chosen Tile Size when it fits, or smaller whole
tiles when the window is narrow. Window size is not saved between runs.

```text
Menu -> Play -> Play Yourself / Rule Based / Q Learning / Hamiltonian / Search-Based
     -> Settings -> speed, board size, tile size
     -> Replay   -> Rule Based / Q Learning / Hamiltonian / Search-Based / Human
     -> Records  -> All Players / Rule / Q-Learning / Hamiltonian / Search-Based / Human
```

Settings are kept for as long as the app is open, so a game started afterwards
uses the speed, board size, and tile size chosen there. Closing the window
closes the app.

The speed names mean different delays for bots and for Human Play. Bots move
every 10, 5, or 1 ms on Slow, Normal, or Fast; Human Play moves every 150, 100,
or 70 ms so a person can react.

A bot plays one game after another by itself. Records keeps each finished game,
and Replay plays back the best saved game for each bot and for Human Play.
Search-Based games are saved as `search_based` in records and under
`replays/search_based_best.json` for their best replay. Compare and Trends show
Search-Based with its own colour under the chosen Board and Speed.

## Human Play Controls

Choose **Play Yourself** on the Play screen. The snake waits until you press
your first direction key, which can point any way.

| Key                  | Action                                                   |
| -------------------- | -------------------------------------------------------- |
| Arrow keys or WASD   | Steer. Two quick turns in a row are both kept.           |
| P or Space           | Pause or resume during a game                            |
| Space or Enter       | Play again after a game ends                             |
| Esc                  | Return to the menu                                       |

A key that would turn the snake straight back into itself is ignored. The game
also pauses when the window loses focus, and stays paused until you resume it.
A game you leave with Esc before it ends is not saved.

## Local Runtime Data

Games played in the app, by a bot or by you, save game records in `records/`
and best replays in `replays/`. Each record and replay names its Player: one
of the bots, or `human` for Human Play. Records files created before Human Play
used a `bot_name` column instead of `player`; they still load. Q Learning saves
its progress in `learning_data/`, and Bot Experiments save separate reports in
`experiments/`. These folders contain local Runtime Data; Git ignores their
contents. A fresh clone starts with no saved records or replays.

Training and Bot Experiments need a local copy of the bundled Starter
Q-table first; see
[Set up the Starter Q-table](docs/training.md#set-up-the-starter-q-table).

## Training and Bot Experiments

The learning bots can be trained, and all bots compared, from the terminal
without opening the app:

- [Training the Learning Bots](docs/training.md): train Q Learning and DQN,
  resume training, and evaluate DQN models.
- [Bot Experiments](docs/bot-experiments.md): compare Bot Modes on the same
  seeds and read the JSON reports.

## Run Tests

`uv sync` already installs pytest, because it is in the `dev` dependency group.

Run the tests from the project root:

```bash
uv run pytest
```

GitHub Actions runs this same test command on Python 3.13 for pull requests
and pushes to `main`.

## Bot Results

| Bot             | Result                                                              |
| --------------- | ------------------------------------------------------------------- |
| Rule-based bot  | Can play, but may still trap itself                                 |
| Q-learning bot  | Learns short-term behavior, but struggles with long-term traps      |
| Hamiltonian bot | Beats the game consistently using cycle planning and safe shortcuts |
| Search-Based bot | Plans future moves and checks for a safe route after food; may still lose |

The Feature Set v3 experiment, with its setup, results, limitations, and
how to repeat it, is in [Results](docs/results.md).

## Demo

### App Screens

These screenshots were taken before the move to Arcade and before Human Play
was added, so the screens look different now. The Play, Replay, and Records
screens now also offer Human Play.

**Main Menu**

![Main Menu](/img/Main_Menu.png)

**Play Screen**

![Play Screen](/img/Play_Screen.png)

**Settings Screen**

![Settings Screen](/img/Settings_Screen.png)

**Records Screen**

![Records Screen](/img/Logs_Screen.png)

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
  bots/              # BotMode, BotFactory, and the four Bot Modes
  sessions/          # GameSession, ReplaySession, SessionSettings, HumanPlayer,
                     # PlayerFactory, and the TrainQLearning and RunExperiment
                     # commands
  storage/           # RecordManager and ReplayManager
  ui/                # AppShell, Theme, WindowLayout, MotionRules, BoardRenderer,
                     # RecordsBrowser, and PlayerLabels
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
