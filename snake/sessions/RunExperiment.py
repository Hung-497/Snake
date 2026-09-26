"""Compare selected Bot Modes in repeatable headless games."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import random
import statistics
import subprocess
import time
import uuid

from snake.bots.BotFactory import create_bot_mode, normal_experiment_modes, supports_board
from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine
from snake.sessions.TrainQLearning import play_game


BOT_NAMES = {
    "rule": "Rule Based",
    "q_learning": "Q Learning",
    "hamiltonian": "Hamiltonian",
    "search_based": "Search-Based",
    "dqn": "DQN",
}


def make_engine(config, seed):
    return SnakeEngine(
        config,
        start_position=None,
        random_source=random.Random(seed),
    )


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


def code_identity():
    """Identify both the Git revision and the current Python source files."""
    project_root = Path(__file__).resolve().parents[2]
    try:
        revision = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=False,
        )
        git_commit = revision.stdout.strip() if revision.returncode == 0 else None
    except OSError:
        git_commit = None
    source_hash = hashlib.sha256()
    for source_path in sorted((project_root / "snake").rglob("*.py")):
        source_hash.update(str(source_path.relative_to(project_root)).encode())
        source_hash.update(b"\0")
        source_hash.update(source_path.read_bytes())

    return {
        "git_commit": git_commit,
        "source_sha256": source_hash.hexdigest(),
    }


def q_learning_identity(bot):
    """Identify the policy file and settings used for Evaluation Mode."""
    return {
        "table_path": str(bot.q_table_file),
        "table_sha256": hashlib.sha256(Path(bot.q_table_file).read_bytes()).hexdigest(),
        "epsilon": bot.epsilon,
        "game_trained": bot.game_trained,
        "learning_rate": bot.learning_rate,
        "discount_rate": bot.discount_rate,
        "min_epsilon": bot.min_epsilon,
        "epsilon_decay": bot.epsilon_decay,
        "evaluation_mode": bot.evaluation_mode,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a Bot Experiment")
    parser.add_argument("--games", type=int, default=1)
    parser.add_argument("--width", type=int, default=24)
    parser.add_argument("--height", type=int, default=25)
    parser.add_argument("--tile-size", type=int, default=25)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-moves", type=int, default=5000)
    parser.add_argument("--q-table", help="Q-table to evaluate (defaults to the saved table)")
    parser.add_argument("--dqn-model", help="Saved DQN evaluation model for explicit DQN selection")
    parser.add_argument(
        "--bots", nargs="+", choices=(*normal_experiment_modes(), "dqn"),
        metavar="BOT_MODE", help="Bot Modes to compare (defaults to all normal modes)",
    )
    options = parser.parse_args(argv)

    if options.games <= 0:
        parser.error("--games must be a positive integer")
    if options.max_moves <= 0:
        parser.error("--max-moves must be a positive integer")

    try:
        config = GameConfig(options.width, options.height, options.tile_size)
    except ValueError as error:
        parser.error(str(error))

    bot_modes = tuple(options.bots or normal_experiment_modes())
    if len(set(bot_modes)) != len(bot_modes):
        parser.error("--bots must not repeat a Bot Mode")
    for bot_mode in bot_modes:
        if not supports_board(bot_mode, config.width, config.height):
            name = BOT_NAMES.get(bot_mode, bot_mode.replace("_", " ").title())
            parser.error(f"{name} Bot does not support this board")

    seeds = [options.seed + game_number for game_number in range(options.games)]
    q_reference_bot = None
    if "q_learning" in bot_modes:
        # Check the selected table before any Bot Mode starts playing.
        try:
            q_reference_bot = QLearningBot(
                make_engine(config, seeds[0]),
                random_source=random.Random(seeds[0] + 1),
                evaluation_mode=True,
                q_table_file=options.q_table,
            )
        except ValueError as error:
            parser.error(str(error))

    dqn_model = None
    dqn_model_identity = None
    if "dqn" in bot_modes:
        if not options.dqn_model:
            parser.error("DQN selection requires --dqn-model")
        try:
            # PyTorch remains optional until DQN is explicitly selected.
            import torch
            from snake.bots.DQNBot import DQNBot
            from snake.storage.DQNArtifacts import load_artifact, model_identity
        except ImportError as error:
            parser.error(f"DQN requires optional PyTorch: {error}")
        try:
            dqn_model = load_artifact(options.dqn_model, "dqn_evaluation_model")
        except ValueError as error:
            parser.error(str(error))
        dqn_model_identity = model_identity(options.dqn_model, dqn_model)
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)

    results = {}
    for bot_mode in bot_modes:
        name = BOT_NAMES.get(bot_mode, bot_mode.replace("_", " ").title())
        elapsed_seconds = 0.0
        games = []
        for game_seed in seeds:
            engine = make_engine(config, game_seed)
            if bot_mode == "q_learning":
                bot = QLearningBot(
                    engine,
                    random_source=random.Random(game_seed + 1),
                    evaluation_mode=True,
                    q_table_file=options.q_table,
                )
            elif bot_mode == "dqn":
                bot = DQNBot(
                    engine,
                    random_source=random.Random(game_seed + 1),
                    settings=dqn_model["metadata"]["learning_settings"],
                    evaluation_mode=True,
                )
                bot.network.load_state_dict(dqn_model["online_weights"])
            else:
                bot = create_bot_mode(
                    bot_mode, engine, random_source=random.Random(game_seed + 1)
                )

            start_time = time.perf_counter()
            moves = play_game(engine, bot, options.max_moves)
            elapsed_seconds += time.perf_counter() - start_time
            if engine.game_won:
                outcome = "won"
            elif engine.game_over:
                outcome = "collision"
            else:
                outcome = "move_limit"

            games.append({
                "seed": game_seed,
                "score": engine.score,
                "moves": moves,
                "outcome": outcome,
            })
            print(
                f"{name} game {len(games)}/{options.games}: "
                f"score {engine.score}, moves {moves}, {outcome}",
                flush=True,
            )

        results[bot_mode] = {
            "games": games,
            "summary": summarize_games(games, elapsed_seconds),
        }

    report = {
        "schema_version": 3,
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
        "game_count": options.games,
        "base_seed": options.seed,
        "seeds": seeds,
        "bot_seed_offset": 1,
        "max_moves": options.max_moves,
        "selected_bot_modes": list(bot_modes),
        "bots": results,
    }
    if q_reference_bot is not None:
        report["q_learning"] = q_learning_identity(q_reference_bot)
    if dqn_model is not None:
        report["dqn"] = dqn_model_identity
        report["training_board"] = dqn_model["metadata"]["training_board"]
        report["evaluation_board"] = dict(report["board"])

    output_directory = Path("experiments")
    output_directory.mkdir(exist_ok=True)
    result_path = output_directory / f"experiment_{uuid.uuid4().hex}.json"
    with result_path.open("x", encoding="utf-8") as result_file:
        json.dump(report, result_file, indent=2)
        result_file.write("\n")

    for bot_mode in bot_modes:
        summary = results[bot_mode]["summary"]
        name = BOT_NAMES.get(bot_mode, bot_mode.replace("_", " ").title())
        print(
            f"{name}: "
            f"mean {summary['mean_score']:.2f}, "
            f"median {summary['median_score']:.2f}, "
            f"best {summary['best_score']}, "
            f"win rate {summary['win_rate']:.1%}, "
            f"mean moves {summary['mean_moves']:.1f}, "
            f"games/s {summary['games_per_second']:.1f}"
        )
    print(f"Saved experiment: {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
