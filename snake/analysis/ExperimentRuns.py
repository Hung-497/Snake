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
class BotFile:
    """The saved Q-table or DQN model a learning Bot Mode played with.

    Anything the report did not record is None, so it can be shown as unknown.
    """

    sha256: str
    feature_set: str | None
    games_trained: int | None
    trained_by: str | None
    training_seeds: tuple


@dataclass(frozen=True)
class ExperimentRun:
    bot_mode: str
    created_at: datetime
    conditions: ExperimentConditions
    games: tuple
    # None for non-learning Bot Modes and for reports that did not identify the file.
    bot_file: BotFile | None = None
    code_version: str | None = None


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
    code = report.get("code")
    commit = code.get("git_commit") if isinstance(code, dict) else None
    code_version = commit[:7] if isinstance(commit, str) and commit else None
    return [
        ExperimentRun(
            bot_mode, created_at, conditions, read_games(bot["games"], seeds),
            read_bot_file(report, bot_mode), code_version,
        )
        for bot_mode, bot in bots.items()
    ]


# Training History sources -> how the report names them.
TRAINING_SOURCES = {"app": "App", "train_command": "Terminal command"}


def read_bot_file(report, bot_mode):
    """Identify the learning bot's saved file; provenance it lacks stays None.

    Evaluation saves the bot's identity next to "bots", under the Bot Mode name.
    """
    identity = report.get(bot_mode)
    if not isinstance(identity, dict):
        return None
    sha256 = identity.get("table_sha256") or identity.get("model_sha256")
    if not isinstance(sha256, str):
        return None
    games_trained = identity.get("game_trained")
    if type(games_trained) is not int:
        games_trained = None

    if "table_sha256" in identity:
        # Q-tables saved before Feature Sets were recorded are v2.
        feature_set = identity.get("feature_set", "v2")
        trained_by, training_seeds = q_table_training(identity.get("training_history"))
    else:
        feature_set = identity.get("feature_set")
        schema = identity.get("feature_schema")
        if feature_set is None and isinstance(schema, str):
            # DQN models name their Feature Set at the end, e.g. ..._space_state_v3.
            feature_set = schema.rsplit("_", 1)[-1]
        trained_by = "App" if report.get("evaluated") == "app_training" else "Terminal command"
        seed = identity.get("base_seed")
        training_seeds = (seed,) if type(seed) is int else ()
    if not isinstance(feature_set, str):
        feature_set = None
    return BotFile(sha256, feature_set, games_trained, trained_by, training_seeds)


def q_table_training(history):
    """Who trained a Q-table, and with which seeds, from its Training History."""
    if not isinstance(history, list):
        return None, ()
    sources = []
    seeds = []
    for entry in history:
        if not isinstance(entry, dict) or entry.get("source") == "unrecorded":
            continue
        source = TRAINING_SOURCES.get(entry.get("source"), entry.get("source"))
        if isinstance(source, str) and source not in sources:
            sources.append(source)
        if type(entry.get("seed")) is int and entry["seed"] not in seeds:
            seeds.append(entry["seed"])
    return (", ".join(sources) or None), tuple(seeds)


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
