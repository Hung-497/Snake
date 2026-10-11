import random

import pytest

from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction, Position
from snake.engine.SnakeEngine import SnakeEngine


def test_engine_public_state_uses_board_cells():
    engine = SnakeEngine(
        GameConfig(width=4, height=3, tile_size=20),
        start_position=(1, 1),
        direction=Direction.RIGHT,
        food_position=(2, 1),
    )

    assert isinstance(engine.snake_position, Position)
    assert engine.snake_position == Position(1, 1)
    assert engine.food_position == Position(2, 1)

    engine.step()

    assert engine.snake_position == Position(2, 1)
    assert engine.snake_body == (Position(1, 1),)


def test_tile_size_does_not_change_engine_outcomes():
    # Same seed and same moves on two tile sizes: random food and every step match.
    first = SnakeEngine(
        GameConfig(width=4, height=4, tile_size=20),
        start_position=(1, 1),
        direction=Direction.RIGHT,
        random_source=random.Random(12),
    )
    second = SnakeEngine(
        GameConfig(width=4, height=4, tile_size=40),
        start_position=(1, 1),
        direction=Direction.RIGHT,
        random_source=random.Random(12),
    )
    assert first.food_position == second.food_position

    for direction in (Direction.RIGHT, Direction.DOWN, Direction.LEFT):
        first.change_direction(direction)
        second.change_direction(direction)
        assert first.step() == second.step()
        assert first.snake_position == second.snake_position
        assert first.snake_body == second.snake_body
        assert first.food_position == second.food_position
        assert first.score == second.score
        assert first.game_over == second.game_over



def test_the_engine_accepts_only_grid_cells():
    # (25, 25) is a valid pixel corner on this board, but not a cell.
    with pytest.raises(ValueError, match="inside the board"):
        SnakeEngine(GameConfig(width=4, height=4, tile_size=25), start_position=(25, 25))


def test_a_position_equals_only_its_own_cell():
    assert Position(1, 0) == (1, 0)
    assert Position(1, 0) != (25, 0)
    # Equal values must also hash alike, so sets and dicts agree with ==.
    assert {Position(1, 0)} == {(1, 0)}
