from types import SimpleNamespace

import pytest

from Movement import Movement


TILE_SIZE = 25
BOARD_WIDTH = 4
BOARD_HEIGHT = 4


def make_snake(x=25, y=25, body=None):
    return SimpleNamespace(x=x, y=y, body=[] if body is None else list(body))


def make_food(x=75, y=75):
    return SimpleNamespace(x=x, y=y)


@pytest.mark.parametrize(
    ("direction", "expected_position"),
    [
        ("Up", (25, 0)),
        ("Down", (25, 50)),
        ("Left", (0, 25)),
        ("Right", (50, 25)),
    ],
)
def test_moves_one_tile_in_each_direction(direction, expected_position):
    movement = Movement()
    snake = make_snake()
    food = make_food()

    movement.change_direction(direction)
    ate_food, game_over = movement.move_snake(
        snake, TILE_SIZE, food, BOARD_WIDTH, BOARD_HEIGHT, False
    )

    assert (snake.x, snake.y) == expected_position
    assert snake.body == []
    assert ate_food is False
    assert game_over is False


@pytest.mark.parametrize(
    ("direction", "opposite"),
    [("Up", "Down"), ("Down", "Up"), ("Left", "Right"), ("Right", "Left")],
)
def test_direct_reversal_is_ignored(direction, opposite):
    movement = Movement()
    movement.change_direction(direction)
    first_velocity = (movement.velocity_x, movement.velocity_y)

    movement.change_direction(opposite)

    assert (movement.velocity_x, movement.velocity_y) == first_velocity


@pytest.mark.parametrize(
    ("start", "direction"),
    [((0, 25), "Left"), ((75, 25), "Right"), ((25, 0), "Up"), ((25, 75), "Down")],
)
def test_wall_collision_ends_game_without_moving(start, direction):
    movement = Movement()
    snake = make_snake(*start)
    food = make_food()

    movement.change_direction(direction)
    ate_food, game_over = movement.move_snake(
        snake, TILE_SIZE, food, BOARD_WIDTH, BOARD_HEIGHT, False
    )

    assert (snake.x, snake.y) == start
    assert snake.body == []
    assert ate_food is False
    assert game_over is True


def test_body_collision_ends_game_without_moving():
    movement = Movement()
    snake = make_snake(body=[(50, 25), (0, 25)])
    food = make_food()

    movement.change_direction("Right")
    ate_food, game_over = movement.move_snake(
        snake, TILE_SIZE, food, BOARD_WIDTH, BOARD_HEIGHT, False
    )

    assert (snake.x, snake.y) == (25, 25)
    assert snake.body == [(50, 25), (0, 25)]
    assert ate_food is False
    assert game_over is True


def test_moving_into_departing_tail_is_allowed():
    movement = Movement()
    snake = make_snake(x=25, y=25, body=[(0, 25)])
    food = make_food(x=75, y=75)

    movement.change_direction("Right")
    ate_food, game_over = movement.move_snake(
        snake, TILE_SIZE, food, BOARD_WIDTH, BOARD_HEIGHT, False
    )

    assert (snake.x, snake.y) == (50, 25)
    assert snake.body == [(25, 25)]
    assert ate_food is False
    assert game_over is False


def test_eating_tail_does_not_allow_collision_with_tail_that_stays():
    movement = Movement()
    snake = make_snake(x=50, y=25, body=[(25, 25), (0, 25)])
    food = make_food(x=25, y=25)

    movement.change_direction("Left")
    ate_food, game_over = movement.move_snake(
        snake, TILE_SIZE, food, BOARD_WIDTH, BOARD_HEIGHT, False
    )

    assert (snake.x, snake.y) == (50, 25)
    assert snake.body == [(25, 25), (0, 25)]
    assert ate_food is True
    assert game_over is True


def test_eating_adds_the_previous_head_to_the_body():
    movement = Movement()
    snake = make_snake(x=25, y=25, body=[(0, 25)])
    food = make_food(x=50, y=25)

    movement.change_direction("Right")
    ate_food, game_over = movement.move_snake(
        snake, TILE_SIZE, food, BOARD_WIDTH, BOARD_HEIGHT, False
    )

    assert (snake.x, snake.y) == (50, 25)
    assert snake.body == [(25, 25), (0, 25)]
    assert ate_food is True
    assert game_over is False


def test_ended_game_does_not_move_or_eat():
    movement = Movement()
    snake = make_snake()
    food = make_food(x=50, y=25)

    movement.change_direction("Right")
    ate_food, game_over = movement.move_snake(
        snake, TILE_SIZE, food, BOARD_WIDTH, BOARD_HEIGHT, True
    )

    assert (snake.x, snake.y) == (25, 25)
    assert snake.body == []
    assert ate_food is False
    assert game_over is True
