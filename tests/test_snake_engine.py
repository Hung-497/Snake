import pytest

from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import SnakeEngine


CONFIG = GameConfig(width=4, height=4, tile_size=25)


def make_engine(position=(1, 1), body=(), direction=Direction.RIGHT, food_position=None):
    return SnakeEngine(
        CONFIG,
        start_position=position,
        body=body,
        direction=direction,
        food_position=food_position,
    )


def test_engine_state_is_available_without_a_gui():
    engine = make_engine()

    state = engine.state

    assert state.board_width == 4
    assert state.board_height == 4
    assert state.snake_position == (1, 1)
    assert state.snake_body == ()
    assert state.direction is Direction.RIGHT
    assert state.game_over is False


def test_step_moves_one_cell_and_change_direction_prevents_reversal():
    engine = make_engine()

    assert engine.change_direction(Direction.LEFT) is False
    engine.step()

    assert engine.snake_position == (2, 1)
    assert engine.direction is Direction.RIGHT


def test_wall_collision_ends_game_without_moving():
    engine = make_engine(position=(3, 1), direction=Direction.RIGHT)

    moved = engine.step()

    assert moved is False
    assert engine.snake_position == (3, 1)
    assert engine.game_over is True


def test_body_collision_ends_game_without_moving():
    engine = make_engine(
        position=(1, 1),
        body=((2, 1), (0, 1)),
        direction=Direction.RIGHT,
    )

    moved = engine.step()

    assert moved is False
    assert engine.snake_position == (1, 1)
    assert engine.snake_body == ((2, 1), (0, 1))
    assert engine.game_over is True


def test_move_into_departing_tail_is_allowed():
    engine = make_engine(
        position=(1, 1),
        body=((0, 1),),
        direction=Direction.RIGHT,
        # Pinned away from the path: random food here would be eaten and grow the snake.
        food_position=(3, 3),
    )

    moved = engine.step()

    assert moved is True
    assert engine.snake_position == (2, 1)
    assert engine.snake_body == ((1, 1),)
    assert engine.game_over is False


def test_state_body_cannot_be_mutated_through_public_state():
    engine = make_engine(body=((0, 1),))

    state = engine.state

    assert isinstance(state.snake_body, tuple)
    with pytest.raises(AttributeError):
        state.snake_body.append((1, 1))


def test_reset_restores_the_initial_playable_state():
    engine = make_engine()
    engine.step()
    engine.change_direction(Direction.DOWN)
    engine.step()
    engine.reset()

    assert engine.state.snake_position == (1, 1)
    assert engine.state.snake_body == ()
    assert engine.state.direction is Direction.RIGHT
    assert engine.game_over is False


def test_a_snake_with_no_body_can_start_by_turning_around():
    # Nothing is behind the head yet, so facing the other way is safe.
    engine = make_engine(direction=Direction.RIGHT)

    assert engine.choose_start_direction(Direction.LEFT) is True
    engine.step()

    assert engine.direction is Direction.LEFT
    assert engine.snake_position == (0, 1)
    assert engine.game_over is False


def test_a_snake_with_a_body_still_cannot_start_by_turning_around():
    engine = make_engine(position=(2, 1), body=((1, 1),), direction=Direction.RIGHT)

    assert engine.choose_start_direction(Direction.LEFT) is False
    assert engine.direction is Direction.RIGHT
