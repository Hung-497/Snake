"""Compare selected Bot Modes in repeatable headless games."""

import argparse
import random

from snake.bots.BotFactory import (
    OPT_IN_EXPERIMENT_MODES, create_bot_mode, normal_experiment_modes, supports_board,
)
from snake.bots.BotModeCatalogue import BOT_MODES
from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.sessions.ExperimentReport import (
    BOT_SEED_OFFSET, build_report, make_engine, play_evaluation_game,
    q_learning_identity, save_report, summarize_games,
)
from snake.sessions.TrainQLearning import FEATURE_SET_BY_BOT_MODE


# The app's names, except dqn: here it evaluates whichever DQN model it is
# given, so its Feature Set version is not known from the name.
BOT_NAMES = {**{mode.key: mode.label for mode in BOT_MODES}, "dqn": "DQN"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a Bot Experiment")
    parser.add_argument("--games", type=int, default=1)
    parser.add_argument("--width", type=int, default=24)
    parser.add_argument("--height", type=int, default=25)
    parser.add_argument("--tile-size", type=int, default=25)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-moves", type=int, default=5000)
    parser.add_argument("--q-table", help="Q-table to evaluate (defaults to the saved table)")
    parser.add_argument(
        "--q-table-v3", help="Q Learning v3 table to evaluate (defaults to the saved v3 table)",
    )
    parser.add_argument("--dqn-model", help="Saved DQN evaluation model for explicit DQN selection")
    parser.add_argument(
        "--bots", nargs="+", choices=(*normal_experiment_modes(), *OPT_IN_EXPERIMENT_MODES, "dqn"),
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
    q_table_by_bot_mode = {
        "q_learning": options.q_table,
        "q_learning_v3": options.q_table_v3,
    }

    def make_q_learning_bot(bot_mode, engine, bot_seed):
        return QLearningBot(
            engine,
            random_source=random.Random(bot_seed),
            evaluation_mode=True,
            q_table_file=q_table_by_bot_mode[bot_mode],
            feature_set=FEATURE_SET_BY_BOT_MODE[bot_mode],
        )

    q_reference_bots = {}
    for bot_mode in bot_modes:
        if bot_mode not in FEATURE_SET_BY_BOT_MODE:
            continue
        # Check the selected table before any Bot Mode starts playing.
        try:
            q_reference_bots[bot_mode] = make_q_learning_bot(
                bot_mode, make_engine(config, seeds[0]), seeds[0] + BOT_SEED_OFFSET,
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
            from snake.storage.DQNArtifacts import (
                artifact_feature_set, load_artifact, model_identity,
            )
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
            if bot_mode in FEATURE_SET_BY_BOT_MODE:
                bot = make_q_learning_bot(bot_mode, engine, game_seed + BOT_SEED_OFFSET)
            elif bot_mode == "dqn":
                bot = DQNBot(
                    engine,
                    random_source=random.Random(game_seed + BOT_SEED_OFFSET),
                    settings=dqn_model["metadata"]["learning_settings"],
                    evaluation_mode=True,
                    feature_set=artifact_feature_set(
                        dqn_model["metadata"], options.dqn_model
                    ),
                )
                bot.network.load_state_dict(dqn_model["online_weights"])
            else:
                bot = create_bot_mode(
                    bot_mode, engine, random_source=random.Random(game_seed + BOT_SEED_OFFSET)
                )

            game, game_seconds = play_evaluation_game(
                engine, bot, game_seed, options.max_moves
            )
            elapsed_seconds += game_seconds
            games.append(game)
            print(
                f"{name} game {len(games)}/{options.games}: "
                f"score {game['score']}, moves {game['moves']}, {game['outcome']}",
                flush=True,
            )

        results[bot_mode] = {
            "games": games,
            "summary": summarize_games(games, elapsed_seconds),
        }

    report = build_report(
        config, options.seed, options.games, options.max_moves, bot_modes, results,
    )
    for bot_mode, q_reference_bot in q_reference_bots.items():
        report[bot_mode] = q_learning_identity(q_reference_bot)
    if dqn_model is not None:
        report["dqn"] = dqn_model_identity
        report["training_board"] = dqn_model["metadata"]["training_board"]
        report["evaluation_board"] = dict(report["board"])

    result_path = save_report(report)

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
