"""Play Bot Experiment games and build their reports, for any caller.

RunExperiment uses these from the terminal, and the app's Evaluate uses the
same ones, so both play the same games and write the same report (ADR 0017).
Nothing here imports PyTorch.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import random
import statistics
import time
import uuid

from snake.engine.SnakeEngine import SnakeEngine
from snake.sessions.TrainQLearning import play_game
from snake.storage.CodeIdentity import code_identity


REPORT_SCHEMA_VERSION = 3
# Game n is played on engine seed base + n, and the bot's random source uses
# that seed plus this offset.
BOT_SEED_OFFSET = 1


def make_engine(config, seed):
    return SnakeEngine(
        config,
        start_position=None,
        random_source=random.Random(seed),
    )


def game_outcome(engine):
    """How a finished game ended: won, collision, or stopped at the move limit."""
    if engine.game_won:
        return "won"
    if engine.game_over:
        return "collision"
    return "move_limit"


def game_record(seed, engine, moves):
    """One game's entry in a report."""
    return {
        "seed": seed,
        "score": engine.score,
        "moves": moves,
        "outcome": game_outcome(engine),
    }


def play_evaluation_game(engine, bot, seed, max_moves):
    """Play one bounded game; return its report entry and its play wall time."""
    start_time = time.perf_counter()
    moves = play_game(engine, bot, max_moves)
    elapsed_seconds = time.perf_counter() - start_time
    return game_record(seed, engine, moves), elapsed_seconds


def summarize_games(games, elapsed_seconds):
    """Summarize completed games; win rate is a fraction from zero to one."""
    scores = [game["score"] for game in games]
    moves = [game["moves"] for game in games]
    wins = sum(game["outcome"] == "won" for game in games)

    return {
        "mean_score": statistics.mean(scores),
        "median_score": statistics.median(scores),
        "best_score": max(scores),
        "score_std_dev": statistics.pstdev(scores),
        "wins": wins,
        "win_rate": wins / len(games),
        "collisions": sum(game["outcome"] == "collision" for game in games),
        "move_limits": sum(game["outcome"] == "move_limit" for game in games),
        "total_moves": sum(moves),
        "mean_moves": statistics.mean(moves),
        "median_moves": statistics.median(moves),
        "min_moves": min(moves),
        "max_moves": max(moves),
        "elapsed_seconds": elapsed_seconds,
        "games_per_second": len(games) / elapsed_seconds if elapsed_seconds > 0 else 0,
    }


def q_learning_identity(bot):
    """Identify the policy file and settings used for Evaluation Mode."""
    return {
        "feature_set": bot.feature_set,
        "table_path": str(bot.q_table_file),
        "table_sha256": hashlib.sha256(Path(bot.q_table_file).read_bytes()).hexdigest(),
        "epsilon": bot.epsilon,
        "game_trained": bot.game_trained,
        "learning_rate": bot.learning_rate,
        "discount_rate": bot.discount_rate,
        "min_epsilon": bot.min_epsilon,
        "epsilon_decay": bot.epsilon_decay,
        "evaluation_mode": bot.evaluation_mode,
        # How the table was trained, as it stood when this experiment ran.
        "training_history": bot.training_history,
    }


def build_report(config, base_seed, game_count, max_moves, bot_modes, results):
    """The report for a Bot Experiment; callers add each evaluated model's identity."""
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "code": code_identity(),
        "python_version": platform.python_version(),
        "timing_basis": (
            "sum of per-game play wall times using time.perf_counter; "
            "excludes setup, Q-table validation, and result writing"
        ),
        "board": {
            "width": config.width,
            "height": config.height,
            "tile_size": config.tile_size,
        },
        "game_count": game_count,
        "base_seed": base_seed,
        "seeds": [base_seed + game_number for game_number in range(game_count)],
        "bot_seed_offset": BOT_SEED_OFFSET,
        "max_moves": max_moves,
        "selected_bot_modes": list(bot_modes),
        "bots": results,
    }


def save_report(report, directory=Path("experiments")):
    """Save a report as a new JSON file in the folder and return its path."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    result_path = directory / f"experiment_{uuid.uuid4().hex}.json"
    with result_path.open("x", encoding="utf-8") as result_file:
        json.dump(report, result_file, indent=2)
        result_file.write("\n")
    return result_path
