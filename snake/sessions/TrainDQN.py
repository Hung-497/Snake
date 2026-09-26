"""Train a DQN Bot Mode without opening the Arcade app."""

import argparse
from pathlib import Path
import platform
import random
import uuid

import torch

from snake.bots.DQNBot import DEFAULT_DQN_SETTINGS, DQNBot
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine
from snake.sessions.TrainQLearning import play_game
from snake.storage.DQNArtifacts import (
    board_details, checkpoint_data, common_metadata, evaluation_model_data,
    load_artifact, save_json_data, save_torch_data,
)


def positive_integer(parser, value, option):
    if value <= 0:
        parser.error(f"{option} must be a positive integer")


def make_engine(config, seed):
    return SnakeEngine(
        config, start_position=None, random_source=random.Random(seed)
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Train DQN headlessly on CPU")
    parser.add_argument("--games", type=int, required=True)
    parser.add_argument("--resume", help="Full checkpoint to continue in a new run")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--tile-size", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--max-moves", type=int)
    parser.add_argument("--checkpoint-every", type=int)
    parser.add_argument("--batch-size", type=int)
    options = parser.parse_args(argv)

    positive_integer(parser, options.games, "--games")
    checkpoint = None
    source_checkpoint = None
    if options.resume:
        source_checkpoint = str(Path(options.resume).resolve())
        try:
            checkpoint = load_artifact(source_checkpoint, "dqn_training_checkpoint")
        except ValueError as error:
            parser.error(str(error))
        saved = checkpoint["metadata"]
        saved_board = saved["training_board"]
        saved_values = {
            "width": saved_board["width"],
            "height": saved_board["height"],
            "tile_size": saved_board["tile_size"],
            "seed": saved["base_seed"],
            "max_moves": saved["max_moves"],
            "checkpoint_every": saved["checkpoint_every"],
            "batch_size": saved["learning_settings"]["batch_size"],
        }
        for name, saved_value in saved_values.items():
            requested = getattr(options, name)
            if requested is not None and requested != saved_value:
                parser.error(f"--{name.replace('_', '-')} conflicts with the checkpoint")
            setattr(options, name, saved_value)
    else:
        defaults = {
            "width": 24, "height": 25, "tile_size": 25, "seed": 0,
            "max_moves": 5000, "checkpoint_every": 25,
            "batch_size": DEFAULT_DQN_SETTINGS["batch_size"],
        }
        for name, default in defaults.items():
            if getattr(options, name) is None:
                setattr(options, name, default)

    positive_integer(parser, options.max_moves, "--max-moves")
    positive_integer(parser, options.checkpoint_every, "--checkpoint-every")
    positive_integer(parser, options.batch_size, "--batch-size")
    try:
        config = GameConfig(options.width, options.height, options.tile_size)
    except ValueError as error:
        parser.error(str(error))
    if config.width * config.height < 2:
        parser.error("DQN training needs at least two cells for food")

    settings = (
        dict(checkpoint["metadata"]["learning_settings"]) if checkpoint else
        {**DEFAULT_DQN_SETTINGS, "batch_size": options.batch_size}
    )
    if settings["batch_size"] > settings["replay_capacity"]:
        parser.error("--batch-size cannot exceed replay capacity")

    # CPU and independent random sources keep this run repeatable.
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(options.seed + 3)
    starting_game_count = (
        checkpoint["state"]["game_trained"] if checkpoint else 0
    )
    engine = make_engine(config, options.seed + max(0, starting_game_count - 1))
    bot = DQNBot(
        engine,
        random_source=random.Random(options.seed + 1),
        replay_random_source=random.Random(options.seed + 2),
        settings=settings,
    )
    if checkpoint:
        state = checkpoint["state"]
        bot.network.load_state_dict(state["online_weights"])
        bot.target_network.load_state_dict(state["target_weights"])
        bot.optimizer.load_state_dict(state["optimizer"])
        bot.replay.extend(state["replay"])
        bot.epsilon = state["epsilon"]
        bot.game_trained = state["game_trained"]
        bot.optimizer_steps = state["optimizer_steps"]
        engine.random_source.setstate(state["engine_random_state"])
        bot.random_source.setstate(state["bot_random_state"])
        bot.replay_random_source.setstate(state["replay_random_state"])
        torch.set_rng_state(state["torch_random_state"])
    run_id = uuid.uuid4().hex
    run_directory = Path("learning_data") / "dqn_runs" / run_id
    metadata = common_metadata(
        config, settings, options.seed, options.max_moves, run_id, source_checkpoint
    )
    metadata["checkpoint_every"] = options.checkpoint_every
    metadata["python_version"] = platform.python_version()
    record = {
        "schema_version": 1,
        "run_id": run_id,
        "source_checkpoint": source_checkpoint,
        "starting_game_count": starting_game_count,
        "training_board": board_details(config),
        "learning_settings": settings,
        "dqn_details": metadata["dqn_details"],
        "base_seed": options.seed,
        "max_moves": options.max_moves,
        "checkpoint_every": options.checkpoint_every,
        "game_count": starting_game_count,
        "games": [],
    }

    print(
        f"Starting DQN training: {options.games} game(s), "
        f"board {config.width}x{config.height}, CPU",
        flush=True,
    )
    for game_number in range(starting_game_count, starting_game_count + options.games):
        game_seed = options.seed + game_number
        if game_number > 0:
            engine = make_engine(config, game_seed)
            bot.engine = engine
        moves = play_game(engine, bot, options.max_moves)
        outcome = (
            "won" if engine.game_won else
            "collision" if engine.game_over else "move_limit"
        )
        mean_loss = bot.take_game_loss()
        game_record = {
            "game_number": bot.game_trained,
            "seed": game_seed,
            "score": engine.score,
            "moves": moves,
            "outcome": outcome,
            "epsilon": bot.epsilon,
            "mean_loss": mean_loss,
            "optimizer_steps": bot.optimizer_steps,
        }
        record["games"].append(game_record)
        record["game_count"] = bot.game_trained
        save_json_data(run_directory / "training.json", record)
        if bot.game_trained % options.checkpoint_every == 0:
            save_torch_data(
                run_directory / "checkpoint.pt",
                checkpoint_data(bot, engine, metadata),
            )
        loss_text = "not started" if mean_loss is None else f"{mean_loss:.4f}"
        print(
            f"DQN game {len(record['games'])}/{options.games}: "
            f"score {engine.score}, moves {moves}, {outcome}, "
            f"epsilon {bot.epsilon:.3f}, loss {loss_text}",
            flush=True,
        )

    save_torch_data(
        run_directory / "checkpoint.pt", checkpoint_data(bot, engine, metadata)
    )
    save_torch_data(
        run_directory / "model.pt", evaluation_model_data(bot, metadata)
    )
    scores = [game["score"] for game in record["games"]]
    print(
        f"Games: {len(scores)}, average score: {sum(scores) / len(scores):.2f}, "
        f"best score: {max(scores)}, trained: {bot.game_trained}, "
        f"epsilon: {bot.epsilon:.3f}"
    )
    print(f"Saved DQN run: {run_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
