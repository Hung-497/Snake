"""The single training move that headless training and Live Training share."""

import random

from snake.bots.BotFactory import create_bot_mode
from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import SnakeEngine
from snake.sessions.TrainQLearning import play_game, play_move


def make_engine(width=4, seed=0):
    return SnakeEngine(
        GameConfig(width=width, height=4, tile_size=20),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        random_source=random.Random(seed),
    )


class StraightRightBot:
    """Always goes right, and remembers what the move loop told it."""

    def __init__(self):
        self.observed = []
        self.games_ended = 0

    def choose_action(self, state):
        return Direction.RIGHT

    def observe(self, transition):
        self.observed.append(transition)

    def on_game_end(self, result):
        self.games_ended += 1


def test_play_move_makes_exactly_one_move():
    engine = make_engine()
    bot = StraightRightBot()

    game_ended = play_move(engine, bot)

    assert game_ended is False
    assert engine.snake_position == (1, 0)
    assert len(bot.observed) == 1
    # Only the caller knows whether a game is finished (death or move limit).
    assert bot.games_ended == 0


def test_play_move_reports_the_move_that_ends_the_game():
    engine = make_engine(width=4)
    bot = StraightRightBot()

    # From column 0 on a 4-wide board, three moves are safe and the fourth hits the wall.
    results = [play_move(engine, bot) for _ in range(4)]

    assert results == [False, False, False, True]
    assert engine.game_over


def test_moves_one_at_a_time_match_a_whole_game():
    whole_engine = make_engine(width=8, seed=7)
    whole_bot = create_bot_mode("rule", whole_engine, random_source=random.Random(7))
    whole_moves = play_game(whole_engine, whole_bot, max_moves=500)

    stepped_engine = make_engine(width=8, seed=7)
    stepped_bot = create_bot_mode("rule", stepped_engine, random_source=random.Random(7))
    stepped_moves = 0
    game_ended = False
    while not game_ended and stepped_moves < 500:
        game_ended = play_move(stepped_engine, stepped_bot)
        stepped_moves += 1
    stepped_bot.on_game_end(stepped_engine.state)

    assert stepped_moves == whole_moves
    assert stepped_engine.state == whole_engine.state
