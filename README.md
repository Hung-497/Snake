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

## Run Tests

Install the development test dependency:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run the tests from the project root:

```bash
python3 -m pytest
```

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
AppShell.py          # Which screen is showing, and closing the app
MenuView.py          # Menu screen
SettingsView.py      # Settings screen
PlayView.py          # Bot Mode choice
GameView.py          # Watch a bot play
ReplayView.py        # Choose a saved replay
ReplayPlaybackView.py # Watch a saved replay
RecordsView.py       # Records screen
Theme.py             # Shared colours, type sizes, spacing, and controls
WindowLayout.py      # Window minimum, board position, and compact layout
MotionRules.py       # Display-free timing rules for visual effects
BoardRenderer.py     # Draws the board at positions from WindowLayout
SessionSettings.py   # Speed, board size, and tile size for this session
GameSession.py       # Repeated games, scores, records, and replays
ReplaySession.py     # Replays a saved game
RecordsBrowser.py    # Reads, filters, and summarises saved records
SnakeEngine.py       # Snake rules, with no screen of its own
GameConfig.py        # Validated board settings
GameTypes.py         # Position and Direction
BotMode.py           # Shared bot helper methods
BotFactory.py        # Builds the selected bot
RuleBasedBot.py      # Rule-based bot
QLearningBot.py      # Tabular Q-learning bot
HamiltonianBot.py    # Hamiltonian cycle bot
RecordManager.py     # Saves and reads CSV game records
ReplayManager.py     # Saves and loads replay JSON files
records/             # Saved game result CSV data
replays/             # Saved replay JSON files
learning_data/       # Saved Q-table data
docs/                # Architecture decisions and the smoke checklist
DEVLOG.md            # Development diary
```

## Development Diary

I documented the learning process, bugs, experiments, and results in [DEVLOG.md](DEVLOG.md).
