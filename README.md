# Snake AI Project

## Overview

A Python Snake game built with Tkinter.  
The project starts with a basic Snake game, then adds different AI bots.

## Features

- Basic Snake game
- Rule-based bot
- Tabular Q-learning bot
- Hamiltonian cycle bot
- Safe shortcut logic
- Tail reachability check
- Flood fill space checking
- Bot selection menu

## Installation

This project uses Python and Tkinter.

Tkinter usually comes with Python. You can check it with:

```bash
python3 -m tkinter
```

If a small Tkinter window opens, Tkinter is working.

## How to Run

```bash
cd Snake && python3 main.py
```

Then you can choose a bot by entering the number `1`, `2`, or `3`:

```text
1. Rule-based bot
2. Q-learning bot
3. Hamiltonian bot
```

## Bot results

| Bot             | Result                                                              |
| --------------- | ------------------------------------------------------------------- |
| Rule-based bot  | Can play, but may still trap itself                                 |
| Q-learning bot  | Learns short-term behavior, but struggles with long-term traps      |
| Hamiltonian bot | Beats the game consistently using cycle planning and safe shortcuts |

## Demo

The demos below compare the three bot modes: rule-based, Q-learning, and Hamiltonian cycle.

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
main.py              # Starts the game and bot selection menu
Game.py              # Main game loop and score tracking
Window.py            # Tkinter window and drawing
Snake.py             # Snake position and body drawing
Food.py              # Food spawning and drawing
Movement.py          # Movement and collision logic
Bot.py               # Rule-based bot
QLearningBot.py      # Tabular Q-learning bot
HamiltonianBot.py    # Hamiltonian cycle bot
DEVLOG.md            # Development diary
```
