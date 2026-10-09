"""Feature Set v3: tail-aware open space plus three tail-reachable features."""

import pytest

from snake.bots.LearningBot import LearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import SnakeEngine


def features(width, height, head, body, direction, food, feature_set="v3"):
    engine = SnakeEngine(
        GameConfig(width, height),
        start_position=head,
        body=body,
        direction=direction,
        food_position=food,
    )
    bot = LearningBot(engine, feature_set=feature_set)
    return bot.features(engine.state)


# The pocket example: the head (2, 2) is inside a loop of its own body, and
# the tail (1, 2) is part of the pocket wall. Moving down from 1 to H:
#
#       0   1   2   3   4   5
#  0    .   .   .   .   .   F
#  1    .   .   1   2   3   .
#  2    .   T   H   .   4   .
#  3    .  10   .   .   5   .
#  4    .   9   8   7   6   .
POCKET = dict(
    width=6,
    height=5,
    head=(2, 2),
    body=(
        (2, 1), (3, 1), (4, 1), (4, 2), (4, 3), (4, 4),
        (3, 4), (2, 4), (1, 4), (1, 3), (1, 2),
    ),
    direction=Direction.DOWN,
    food=(5, 0),
)


def test_v2_sees_the_pocket_moves_as_dead_ends():
    # Straight (down) and Turn Left (east) stay in the 3-cell pocket. Turn
    # Right onto the tail reaches 20 cells: at least the length 12, under 24.
    assert features(**POCKET, feature_set="v2") == (0, 0, 0, 0, 1, 0, 0, 0, 1)


def test_v3_sees_the_pocket_opening_as_the_tail_moves_away():
    assert features(**POCKET) == (0, 0, 0, 0, 1, 0, 2, 2, 2, 1, 1, 1)


def test_tail_is_unreachable_behind_a_wall_of_body():
    # The body is a wall down column 2 and the tail ends on the right side.
    # Facing up: Straight leaves the board, Turn Left goes to the left side,
    # Turn Right goes to the right side, where the tail is.
    result = features(
        width=5,
        height=4,
        head=(2, 0),
        body=((2, 1), (2, 2), (2, 3), (3, 3), (4, 3)),
        direction=Direction.UP,
        food=(0, 3),
    )

    assert result[:3] == (1, 0, 0)
    assert result[9:] == (0, 0, 1)


def test_eating_food_keeps_the_tail_in_place():
    # Eating at (2, 0) grows the snake, so the tail at (0, 0) does not move
    # and the head is shut in at the end of the row.
    result = features(
        width=3,
        height=1,
        head=(1, 0),
        body=((0, 0),),
        direction=Direction.RIGHT,
        food=(2, 0),
    )

    assert result[:3] == (0, 1, 1)
    assert result[6:] == (0, 0, 0, 0, 0, 0)


def test_unknown_feature_set_is_rejected():
    with pytest.raises(ValueError, match="Feature Set"):
        features(**POCKET, feature_set="v9")
