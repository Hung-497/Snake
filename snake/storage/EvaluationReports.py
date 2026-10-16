"""Read completed app evaluations without loading or changing any learned bot."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path

from snake.sessions.ExperimentReport import REPORT_SCHEMA_VERSION


DEFAULT_REPORT_DIRECTORY = Path(__file__).resolve().parents[2] / "experiments"
SOURCE_LABELS = {"app_training": "Your bot", "showcase": "Showcase Bot"}


@dataclass(frozen=True)
class EvaluationResult:
    created_at: datetime
    player: str
    source: str
    game_count: int
    average_score: float
    best_score: int
    board_width: int
    board_height: int
    base_seed: int
    max_moves: int


def read_evaluation_reports(directory=DEFAULT_REPORT_DIRECTORY):
    """Return newest results and a skipped-file count; terminal experiments are omitted."""
    results = []
    skipped = 0
    try:
        paths = sorted(Path(directory).glob("*.json"))
    except OSError:
        return [], 1
    for path in paths:
        try:
            with path.open(encoding="utf-8") as file:
                report = json.load(file)
            if not isinstance(report, dict):
                raise ValueError("Expected a report object")
            # Only app Evaluate runs have this marker. Watched games and
            # terminal comparisons keep their own existing readers.
            if "evaluated" not in report:
                continue
            results.append(read_result(report))
        except (OSError, ValueError, KeyError, TypeError, OverflowError):
            skipped += 1
    results.sort(key=lambda result: result.created_at, reverse=True)
    return results, skipped


def read_result(report):
    if report["schema_version"] != REPORT_SCHEMA_VERSION:
        raise ValueError("Unsupported report schema")
    source = SOURCE_LABELS[report["evaluated"]]
    players = report["selected_bot_modes"]
    if not isinstance(players, list) or len(players) != 1 or not isinstance(players[0], str):
        raise ValueError("An app evaluation measures one Player")
    player = players[0]
    game_count = positive_integer(report["game_count"])
    games = report["bots"][player]["games"]
    if not isinstance(games, list) or len(games) != game_count:
        raise ValueError("Evaluation is incomplete")
    summary = report["bots"][player]["summary"]
    average = summary["mean_score"]
    best = summary["best_score"]
    if type(average) not in (int, float) or not math.isfinite(average) or average < 0:
        raise ValueError("Invalid average")
    if type(best) is not int or best < average:
        raise ValueError("Invalid best score")
    created_at = datetime.fromisoformat(report["created_at"])
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    base_seed = report["base_seed"]
    if type(base_seed) is not int:
        raise ValueError("Invalid seed")
    return EvaluationResult(
        created_at.astimezone(timezone.utc), player, source, game_count,
        float(average), best, positive_integer(report["board"]["width"]),
        positive_integer(report["board"]["height"]), base_seed,
        positive_integer(report["max_moves"]),
    )


def positive_integer(value):
    if type(value) is not int or value <= 0:
        raise ValueError("Expected a positive integer")
    return value
