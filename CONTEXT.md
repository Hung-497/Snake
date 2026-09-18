# Snake

This context covers the local Snake game, its automated players, and the user-facing screens used to configure, watch, and review games.

## Language

**Game Engine**:
The authoritative Snake state and rules, designed to run without a graphical interface.
_Avoid_: GUI game logic

**App View**:
One user-facing screen within the app's single window, such as Menu, Settings, Game, Replay, or Records.
_Avoid_: separate window, page

**Bot Mode**:
The automated player selected to control a game, currently Rule Based, Q Learning, or Hamiltonian.
_Avoid_: player mode
