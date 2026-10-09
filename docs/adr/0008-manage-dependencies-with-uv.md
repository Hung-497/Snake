# Manage Dependencies with uv

Setup used pip with three requirements files, CI ran Python 3.13 while local environments drifted to other versions, and the docs mixed `python3`, `pip`, and `.venv/bin/python3` commands. Declare all dependencies in one `pyproject.toml`, commit a `uv.lock`, pin Python 3.13 in `.python-version`, and run everything (app, tests, CI, training, experiments) through `uv sync` and `uv run` so every machine resolves the same versions.

## Considered Options

- Keep pip and the requirements files, and use uv only locally as a faster installer.
- Keep the requirements files as a pip fallback generated from the lock file.
- Replace them with `pyproject.toml` and `uv.lock` as the single source of truth.

The last option removes duplicate dependency lists that could drift apart and makes local runs match CI.

## Consequences

- Contributors must install uv before setup. Plain `pip install -r` no longer works.
- Arcade is a project dependency, pytest is in the `dev` dependency group, and numpy and torch are in an optional `dqn` group (`uv sync --group dqn`), so the default setup and CI stay free of PyTorch.
- CI runs `uv sync --locked` and fails when `uv.lock` is out of date with `pyproject.toml`.
- The project `.venv` is still used, but uv creates and owns it.
