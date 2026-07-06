# Snake AI Project

## Overview

A Python Snake game built with Tkinter and CustomTkinter.
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
- CustomTkinter bot selection menu
- Settings screen for speed, board size, and tile size
- Records screen with bot filters and summary stats
- Replay saving and playback for saved bot runs
- Q-learning persistence with saved Q-table data

## Installation

This project uses Python, Tkinter, and CustomTkinter for the menu UI.

Tkinter usually comes with Python. You can check it with:

```bash
python3 -m tkinter
```

If a small Tkinter window opens, Tkinter is working.

Install CustomTkinter with:

```bash
python3 -m pip install customtkinter
```

## How to Run

```bash
cd Snake && python3 Menu.py
```

Then use the menu to choose a bot:

```text
Play -> Rule-based bot / Q-learning bot / Hamiltonian bot
```

You can also adjust speed, board size, and tile size in the Settings screen before starting a game.

Saved results can be viewed from:

```text
Logs -> All / Rule / Q-learning / Hamiltonian
```

Saved replays can be played from:

```text
Replay -> Rule Based Replay / Q Learning Replay / Hamiltonian Replay
```

## Bot Results

| Bot             | Result                                                              |
| --------------- | ------------------------------------------------------------------- |
| Rule-based bot  | Can play, but may still trap itself                                 |
| Q-learning bot  | Learns short-term behavior, but struggles with long-term traps      |
| Hamiltonian bot | Beats the game consistently using cycle planning and safe shortcuts |

## Demo

### App Screens

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
Menu.py              # Starts the CustomTkinter menu
Game.py              # Main game loop and score tracking
Window.py            # Tkinter window and drawing
Snake.py             # Snake position and body drawing
Food.py              # Food spawning and drawing
Movement.py          # Movement and collision logic
BaseBot.py           # Shared bot helper methods
RuleBasedBot.py      # Rule-based bot
QLearningBot.py      # Tabular Q-learning bot
HamiltonianBot.py    # Hamiltonian cycle bot
RecordManager.py     # Saves and reads CSV game records
ReplayManager.py     # Saves and loads replay JSON files
ReplayPlayer.py      # Plays saved replay files visually
records/             # Saved game result CSV data
replays/             # Saved replay JSON files
learning_data/       # Saved Q-table data
DEVLOG.md            # Development diary
```

## Development Diary

I documented the learning process, bugs, experiments, and results in [DEVLOG.md](DEVLOG.md).
