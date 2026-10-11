import random

from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import SnakeEngine


def test_engine_places_food_on_a_free_cell():
    engine = SnakeEngine(
        GameConfig(width=3, height=1, tile_size=25),
        start_position=(0, 0),
        body=((1, 0),),
        direction=Direction.RIGHT,
        random_source=random.Random(4),
    )

    # Only one cell is free, so the food must be there.
    assert engine.food_position == (2, 0)


def test_eating_grows_snake_and_increases_score():
    engine = SnakeEngine(
        GameConfig(width=3, height=1, tile_size=25),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        food_position=(1, 0),
        random_source=random.Random(4),
    )

    moved = engine.step()

    assert moved is True
    assert engine.snake_position == (1, 0)
    assert engine.snake_body == ((0, 0),)
    assert engine.score == 1
    assert engine.game_over is False
    assert engine.game_won is False
    assert engine.food_position == (2, 0)


def test_reset_clears_the_score_and_places_new_food_on_a_free_cell():
    engine = SnakeEngine(
        GameConfig(width=3, height=1, tile_size=25),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        food_position=(1, 0),
        random_source=random.Random(10),
    )
    engine.step()
    assert engine.score == 1

    engine.reset()

    assert engine.score == 0
    assert engine.snake_position == (0, 0)
    assert engine.state.snake_body == ()
    assert engine.food_position in {(1, 0), (2, 0)}
    assert engine.game_over is False
    assert engine.game_won is False
