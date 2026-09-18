# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Role

Act as a coding tutor and pair programmer, not just a code generator. The user is learning: explain the idea before writing code, write code in small steps, and explain what changed and why after each step. Ask before adding complex AI, neural networks, or reinforcement learning. Do not over-engineer or jump ahead to advanced solutions; do not add deep learning, a hybrid bot, packaging files, or CI unless explicitly requested. Prefer beginner-friendly names and short comments for non-obvious logic. Full rules are in `AGENTS.md`.

## Commands

```bash
# Run the app — the .venv interpreter first on PATH has tkinter + customtkinter
python3 Menu.py

# Run tests from the project root. Always use `python3 -m pytest`, never bare
# `pytest`: the -m form puts the project root on sys.path, so `import GameConfig`
# resolves. Bare `pytest` only adds tests/ and dies with ModuleNotFoundError.
python3 -m pytest

# Single file / single test
python3 -m pytest tests/test_snake_engine.py
python3 -m pytest tests/test_snake_engine.py::test_name -v

# If the repo .venv is activated it has no pytest; either install it there
# (python3 -m pip install -r requirements-dev.txt) or use another interpreter,
# e.g. /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m pytest
```

There is no lint/build step configured (no ruff/pyproject config present despite the `.ruff_cache` directory).

## Architecture

The project is mid-migration from a pixel-coordinate, Tkinter-coupled design to a headless, cell-coordinate game engine. Both styles currently coexist:

- **`SnakeEngine.py`** — the new headless engine (`SnakeEngine`, `EngineState`). Owns snake/food/score/collision/win state using zero-based `(column, row)` grid cells via `GameTypes.Position`. Pure logic, no Tkinter dependency. `GameConfig.py` (frozen dataclass: `width`, `height`, `tile_size`) validates board settings and is passed into the engine.
- **`Window.py` / `Snake.py` / `Food.py` / `Movement.py`** — the legacy pixel-based path (canvas coordinates in multiples of `tile_size`, mutable snake/food objects). `Movement.move_snake(...)` is the legacy step function mirrored by `SnakeEngine.step()`.
- **`Game.py`** — coordinates the main loop and can run in *either* mode: when constructed with `engine=` it drives `SnakeEngine` and syncs a `SimpleNamespace`-based `snake`/`food`/`movement` view back from `engine.state` for rendering (`_sync_engine_views`, `_draw_engine_state`); otherwise it falls back to the legacy pixel objects. `Menu.py` constructs games using `GameConfig` + `SnakeEngine`. The engine loop holds a single `self.bot` and has no per-bot branches: it calls `choose_action`, takes the transition from `engine.preview()` (which `step()` is guaranteed to commit), steps, then calls `observe`, and `on_game_end` when the game finishes.
- **Bot Modes** (`BotMode.py`, `RuleBasedBot.py`, `QLearningBot.py`, `HamiltonianBot.py`) — all subclass `BotMode`, the common contract: `choose_action(state)`, `observe(transition)`, `on_game_end(result)`. A Bot Mode is constructed with the engine plus its own `random_source` (kept separate from engine randomness so exploration never shifts food placement), and reads only presentation-neutral state — never the window, canvas, or the mutable snake/food/movement objects. Immediate legality and safety go through `engine.preview(direction)` rather than re-implementing movement rules; multi-step search (BFS, flood fill) uses the grid helpers on `BotMode`. `BotFactory.create_bot_mode(bot_mode, engine)` builds **only** the selected bot, so unselected ones never load Q-tables or validate cycles.
- **`GameTypes.py`** — `Position` (grid cell, with legacy pixel-tuple equality kept for old characterization tests) and `Direction` (string enum with reversal-prevention helpers used by both `Movement` and `SnakeEngine`).
- **`RecordManager.py`** — appends game results to `records/game_records.csv`.
- **`ReplayManager.py` / `ReplayPlayer.py`** — record and play back per-move JSON replays (`replays/`), supporting both engine- and legacy-recorded games; `ReplayCompatibilityError` signals schema mismatches.
- **`QLearningBot.py`** — persists its Q-table under `learning_data/`.
- **`Menu.py`** — CustomTkinter UI: bot selection, settings (speed/board size/tile size), records browsing, and replay playback, all launched from here.

When changing collision, movement, or scoring rules, check whether the change needs to be made in both `SnakeEngine.step()`/`_get_next_position` and the legacy `Movement.move_snake()`, since tests (`tests/test_movement_characterization.py` vs `tests/test_snake_engine*.py`) characterize both paths independently.

## Domain docs

See `CONTEXT.md` for domain vocabulary (Game Engine, App View, Bot Mode) and `docs/adr/` for architecture decisions. Use `CONTEXT.md` terms in code, tests, and discussion rather than synonyms it excludes.

Note: `docs/adr/0001-use-arcade-for-the-presentation-layer.md` records a decision to replace Tkinter/CustomTkinter with Arcade 3.x once the headless engine is fully extracted. This migration has not happened yet — the presentation layer is still Tkinter/CustomTkinter (`Window.py`, `Menu.py`). Don't assume Arcade is in use; check before adding UI code.
