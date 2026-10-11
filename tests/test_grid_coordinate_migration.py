import random

from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction, Position
from snake.storage.ReplayManager import ReplayManager
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


def test_tile_size_does_not_change_seeded_engine_outcomes():
    first = SnakeEngine(
        GameConfig(width=4, height=3, tile_size=20),
        start_position=(0, 0),
        random_source=random.Random(12),
    )
    second = SnakeEngine(
        GameConfig(width=4, height=3, tile_size=40),
        start_position=(0, 0),
        random_source=random.Random(12),
    )

    assert (first.snake_position.x, first.snake_position.y) == (
        second.snake_position.x,
        second.snake_position.y,
    )
    assert (first.food_position.x, first.food_position.y) == (
        second.food_position.x,
        second.food_position.y,
    )

    first.step()
    second.step()

    assert (first.snake_position.x, first.snake_position.y) == (
        second.snake_position.x,
        second.snake_position.y,
    )
    assert first.score == second.score


def test_equal_actions_have_equal_outcomes_for_different_tile_sizes():
    first = SnakeEngine(
        GameConfig(width=4, height=4, tile_size=20),
        start_position=(1, 1),
        direction=Direction.RIGHT,
        food_position=(3, 3),
    )
    second = SnakeEngine(
        GameConfig(width=4, height=4, tile_size=40),
        start_position=(1, 1),
        direction=Direction.RIGHT,
        food_position=(3, 3),
    )

    for direction in (Direction.RIGHT, Direction.DOWN, Direction.LEFT):
        first.change_direction(direction)
        second.change_direction(direction)
        assert first.step() == second.step()
        assert first.snake_position == second.snake_position
        assert first.snake_body == second.snake_body
        assert first.food_position == second.food_position
        assert first.score == second.score
        assert first.game_over == second.game_over


def test_engine_replays_use_the_versioned_grid_storage_format(tmp_path):
    manager = ReplayManager(folder_name=str(tmp_path))
    engine = SnakeEngine(
        GameConfig(width=4, height=3, tile_size=20),
        start_position=(1, 1),
        food_position=(2, 1),
    )

    manager.start_recording("rule", 4, 3, 20, 1, engine=engine)
    manager.record_food(Position(3, 2))

    assert manager.replay_data["schema_version"] == 2
    assert manager.replay_data["coordinate_system"] == "grid"
    assert manager.replay_data["start_snake"] == [1, 1]
    assert manager.replay_data["start_food"] == [2, 1]
    assert manager.replay_data["foods"][-1] == [3, 2]
