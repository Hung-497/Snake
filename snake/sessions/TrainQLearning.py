"""Run Q Learning Training Mode without opening an Arcade window."""

import argparse
import random

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine


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
    try:
        bot = QLearningBot(
            engine,
            random_source=random.Random(options.seed + 1),
            require_saved_table=True,
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
