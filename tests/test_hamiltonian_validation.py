import random

import pytest

from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.bots.HamiltonianBot import HamiltonianBot
from snake.engine.SnakeEngine import SnakeEngine


def make_engine(width, height, seed=1):
    return SnakeEngine(
        GameConfig(width=width, height=height, tile_size=25),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        random_source=random.Random(seed),
    )


@pytest.mark.parametrize("width, height", [(4, 3), (3, 4), (2, 2)])
def test_hamiltonian_wins_on_a_board_with_one_odd_side(width, height):
    # A valid cycle visits every cell, so following it fills the whole board.
    engine = make_engine(width, height)
    bot = HamiltonianBot(engine, random_source=random.Random(2))

    for _ in range(10_000):
        if engine.game_over:
            break
        direction = bot.choose_action(engine.state)
        if direction is not None:
            engine.change_direction(direction)
        transition = engine.preview()
        engine.step()
        bot.observe(transition)

    assert engine.game_won is True
    assert engine.score == width * height - 1


def test_odd_by_odd_board_is_rejected_before_direction_is_requested():
    engine = make_engine(3, 3)
    bot = HamiltonianBot(engine)

    with pytest.raises(ValueError, match="valid Hamiltonian cycle"):
        bot.choose_action(engine.state)
