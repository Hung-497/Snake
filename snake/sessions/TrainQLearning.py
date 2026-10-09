"""Run Q Learning Training Mode without opening an Arcade window."""

import argparse
import os
import random

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine


# Each Q Learning Bot Mode observes the board with its own Feature Set.
FEATURE_SET_BY_BOT_MODE = {"q_learning": "v2", "q_learning_v3": "v3"}

def play_game(engine, bot, max_moves):
    """Play one bounded game through the Game Engine and Bot Mode contract."""
    moves = 0

    while not engine.game_over and moves < max_moves:
        direction = bot.choose_action(engine.state)
        if direction is not None:
            engine.change_direction(direction)

        transition = engine.preview()
        engine.step()
        bot.observe(transition)
        moves += 1

    bot.on_game_end(engine.state)
    return moves


def main(argv=None):
    parser = argparse.ArgumentParser(description="Train Q Learning headlessly")
    parser.add_argument("--games", type=int, required=True)
    parser.add_argument("--width", type=int, default=24)
    parser.add_argument("--height", type=int, default=25)
    parser.add_argument("--tile-size", type=int, default=25)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-moves", type=int, default=5000)
    parser.add_argument(
        "--bot", choices=tuple(FEATURE_SET_BY_BOT_MODE), default="q_learning",
        help="Q Learning Bot Mode to train (default: q_learning)",
    )
    parser.add_argument("--q-table", help="Q-table to train (defaults to the saved table)")
    parser.add_argument(
        "--new-table", action="store_true",
        help="Start an empty Q Learning v3 table instead of resuming one",
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

    engine = SnakeEngine(
        config,
        start_position=None,
        random_source=random.Random(options.seed),
    )
    if options.new_table:
        if options.bot != "q_learning_v3":
            parser.error("--new-table only starts a Q Learning v3 table")
        new_table_path = options.q_table or os.path.join(
            "learning_data", "q_table_space_state_v3.json"
        )
        if os.path.exists(new_table_path):
            parser.error(f"Q-table already exists: {new_table_path}")

    try:
        bot = QLearningBot(
            engine,
            random_source=random.Random(options.seed + 1),
            require_saved_table=not options.new_table,
            q_table_file=options.q_table,
            feature_set=FEATURE_SET_BY_BOT_MODE[options.bot],
        )
    except ValueError as error:
        parser.error(str(error))

    scores = []
    wins = 0
    move_limits = 0

    for game_number in range(options.games):
        if game_number > 0:
            engine.reset()

        moves = play_game(engine, bot, options.max_moves)
        scores.append(engine.score)
        wins += int(engine.game_won)
        move_limits += int(not engine.game_over and moves == options.max_moves)

    print(
        f"Games: {options.games}, "
        f"Average score: {sum(scores) / len(scores):.2f}, "
        f"Best score: {max(scores)}, "
        f"Wins: {wins}, "
        f"Move limits: {move_limits}, "
        f"Epsilon: {bot.epsilon:.3f}, "
        f"Total trained: {bot.game_trained}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
