import random

from GameConfig import GameConfig
from GameTypes import Direction
from SnakeEngine import SnakeEngine


def test_engine_places_food_on_a_free_cell():
    engine = SnakeEngine(
        GameConfig(width=3, height=1, tile_size=25),
        start_position=(0, 0),
        body=((25, 0),),
        direction=Direction.RIGHT,
        random_source=random.Random(4),
    )

    assert engine.food_position not in {
        engine.snake_position,
        *engine.snake_body,
    }


def test_eating_grows_snake_and_increases_score():
    engine = SnakeEngine(
        GameConfig(width=3, height=1, tile_size=25),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        food_position=(25, 0),
        random_source=random.Random(4),
    )

    moved = engine.step()

    assert moved is True
    assert engine.snake_position == (25, 0)
    assert engine.snake_body == ((0, 0),)
    assert engine.score == 1
    assert engine.game_over is False
    assert engine.game_won is False
    assert engine.food_position == (50, 0)


def test_eating_final_free_cell_wins_without_spawning_more_food():
    class FailingRandom:
        def randint(self, start, end):
            raise AssertionError("full board must not request another food cell")

    engine = SnakeEngine(
        GameConfig(width=2, height=1, tile_size=25),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        food_position=(25, 0),
        random_source=FailingRandom(),
    )

    engine.step()

    assert engine.score == 1
    assert engine.game_over is True
    assert engine.game_won is True
    assert engine.food_position is None


def test_reset_recreates_a_deterministic_valid_state_from_a_seed():
    first = SnakeEngine(
        GameConfig(width=4, height=4, tile_size=25),
        start_position=(0, 0),
        random_source=random.Random(10),
    )
    second = SnakeEngine(
        GameConfig(width=4, height=4, tile_size=25),
        start_position=(0, 0),
        random_source=random.Random(10),
    )

    assert first.state == second.state

    first.step()
    second.step()
    first.reset()
    second.reset()

    assert first.state == second.state
    assert first.score == 0
    assert first.game_over is False
    assert first.game_won is False
