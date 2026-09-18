from GameConfig import GameConfig
from GameTypes import Direction
from SnakeEngine import SnakeEngine


def test_direction_contains_the_four_canonical_values():
    assert [direction.value for direction in Direction] == [
        "Up",
        "Down",
        "Left",
        "Right",
    ]


def test_invalid_direction_does_not_change_the_engine():
    engine = SnakeEngine(GameConfig(10, 10), start_position=(5, 5))
    engine.change_direction(Direction.RIGHT)

    accepted = engine.change_direction("Diagonal")

    assert accepted is False
    assert engine.direction == Direction.RIGHT
