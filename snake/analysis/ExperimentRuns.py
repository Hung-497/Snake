"""Read every saved Bot Experiment report as runs, without changing any file.

A run is one Bot Mode's games inside one report. Evaluate and the terminal
Bot Experiment commands write the same report, so both are read here.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from snake.sessions.ExperimentReport import REPORT_SCHEMA_VERSION


GAME_OUTCOMES = {"won", "collision", "move_limit"}


@dataclass(frozen=True, order=True)
class ExperimentConditions:
    """Runs are only compared when all of these are equal."""

    width: int
    height: int
    max_moves: int
    seeds: tuple


@dataclass(frozen=True)
class GameResult:
    seed: int
    score: int
    moves: int
    outcome: str


@dataclass(frozen=True)
class ExperimentRun:
    bot_mode: str
    created_at: datetime
    conditions: ExperimentConditions
    games: tuple


def read_experiment_runs(directory):
    """Return every run and how many report files were skipped.

    A damaged, incomplete, or older-format file is skipped as a whole, so one
    bad file never hides the valid ones.
    """
    runs = []
    skipped = 0
    for path in sorted(Path(directory).glob("*.json")):
        try:
            with path.open(encoding="utf-8") as file:
                runs.extend(read_runs(json.load(file)))
        except (OSError, ValueError, KeyError, TypeError, OverflowError):
            skipped += 1
    return runs, skipped


def read_runs(report):
    if not isinstance(report, dict):
        raise ValueError("Expected a report object")
    if report["schema_version"] != REPORT_SCHEMA_VERSION:
        raise ValueError("Unsupported report schema")
    seeds = report["seeds"]
    if not isinstance(seeds, list) or not seeds or any(type(seed) is not int for seed in seeds):
        raise ValueError("Invalid seeds")
    if report["game_count"] != len(seeds):
        raise ValueError("Seed list does not match the game count")
    conditions = ExperimentConditions(
        positive_integer(report["board"]["width"]),
        positive_integer(report["board"]["height"]),
        positive_integer(report["max_moves"]),
        tuple(seeds),
    )
    created_at = datetime.fromisoformat(report["created_at"])
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    created_at = created_at.astimezone(timezone.utc)

    bots = report["bots"]
    if not isinstance(bots, dict) or not bots:
        raise ValueError("A report needs at least one bot")
    return [
        ExperimentRun(bot_mode, created_at, conditions, read_games(bot["games"], seeds))
        for bot_mode, bot in bots.items()
    ]


def read_games(games, seeds):
    """Every seed must have its game, in order, or the run is incomplete."""
    if not isinstance(games, list) or len(games) != len(seeds):
        raise ValueError("Run is incomplete")
    results = []
    for game, seed in zip(games, seeds):
        if game["seed"] != seed or game["outcome"] not in GAME_OUTCOMES:
            raise ValueError("Invalid game")
        if type(game["score"]) is not int or game["score"] < 0:
            raise ValueError("Invalid score")
        if type(game["moves"]) is not int or game["moves"] < 0:
            raise ValueError("Invalid move count")
        results.append(GameResult(seed, game["score"], game["moves"], game["outcome"]))
    return tuple(results)


def positive_integer(value):
    if type(value) is not int or value <= 0:
        raise ValueError("Expected a positive integer")
    return value
