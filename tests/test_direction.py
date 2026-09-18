from GameTypes import Direction
from Movement import Movement


def test_direction_contains_the_four_canonical_values():
    assert [direction.value for direction in Direction] == [
        "Up",
        "Down",
        "Left",
        "Right",
    ]


def test_invalid_direction_does_not_change_movement():
    movement = Movement()
    movement.change_direction(Direction.RIGHT)
    original_velocity = (movement.velocity_x, movement.velocity_y)

    accepted = movement.change_direction("Diagonal")

    assert accepted is False
    assert (movement.velocity_x, movement.velocity_y) == original_velocity
