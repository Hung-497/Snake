"""Evaluate a saved DQN model without learning or changing its files."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import random
import time
import uuid

import torch

from snake.bots.DQNBot import DQNBot
from snake.engine.GameConfig import GameConfig
from snake.sessions.RunExperiment import code_identity, make_engine, summarize_games
from snake.sessions.TrainQLearning import play_game
from snake.storage.DQNArtifacts import board_details, load_artifact, model_identity


def main(argv=None):
    parser = argparse.ArgumentParser(description="Evaluate a saved DQN model")
    parser.add_argument("--model", required=True, help="DQN evaluation model.pt")
    parser.add_argument("--games", type=int, default=1)
    parser.add_argument("--width", type=int, default=24)
    parser.add_argument("--height", type=int, default=25)
    parser.add_argument("--tile-size", type=int, default=25)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-moves", type=int, default=5000)
    options = parser.parse_args(argv)

    if options.games <= 0:
        parser.error("--games must be a positive integer")
    if options.max_moves <= 0:
        parser.error("--max-moves must be a positive integer")
    try:
        config = GameConfig(options.width, options.height, options.tile_size)
    except ValueError as error:
        parser.error(str(error))
    if config.width * config.height < 2:
        parser.error("DQN evaluation needs at least two cells for food")
    try:
        model = load_artifact(options.model, "dqn_evaluation_model")
    except ValueError as error:
        parser.error(str(error))

    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    seeds = [options.seed + game_number for game_number in range(options.games)]
    games = []
    elapsed_seconds = 0.0
    for game_seed in seeds:
        engine = make_engine(config, game_seed)
        bot = DQNBot(
            engine, random_source=random.Random(game_seed + 1),
            settings=model["metadata"]["learning_settings"], evaluation_mode=True,
        )
        bot.network.load_state_dict(model["online_weights"])
        start_time = time.perf_counter()
        moves = play_game(engine, bot, options.max_moves)
        elapsed_seconds += time.perf_counter() - start_time
        outcome = (
            "won" if engine.game_won else
            "collision" if engine.game_over else "move_limit"
        )
        games.append({
            "seed": game_seed, "score": engine.score,
            "moves": moves, "outcome": outcome,
        })

    report = {
        "schema_version": 3,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "code": code_identity(),
        "python_version": platform.python_version(),
        "timing_basis": (
            "sum of per-game play wall times using time.perf_counter; "
            "excludes setup, model validation, and result writing"
        ),
        "board": board_details(config),
        "training_board": model["metadata"]["training_board"],
        "evaluation_board": board_details(config),
        "game_count": options.games,
        "base_seed": options.seed,
        "seeds": seeds,
        "bot_seed_offset": 1,
        "max_moves": options.max_moves,
        "selected_bot_modes": ["dqn"],
        "bots": {"dqn": {
            "games": games,
            "summary": summarize_games(games, elapsed_seconds),
        }},
        "dqn": model_identity(options.model, model),
    }
    output_directory = Path("experiments")
    output_directory.mkdir(exist_ok=True)
    result_path = output_directory / f"experiment_{uuid.uuid4().hex}.json"
    with result_path.open("x", encoding="utf-8") as result_file:
        json.dump(report, result_file, indent=2)
        result_file.write("\n")

    summary = report["bots"]["dqn"]["summary"]
    print(
        f"DQN: mean {summary['mean_score']:.2f}, "
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
