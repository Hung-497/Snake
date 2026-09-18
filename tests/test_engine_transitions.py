import random

import pytest

from GameConfig import GameConfig
from GameTypes import Direction, Position
from SnakeEngine import SnakeEngine


def make_engine(width, height, start_position, direction, food_position, body=()):
    return SnakeEngine(
        GameConfig(width=width, height=height, tile_size=20),
        start_position=start_position,
        body=body,
        direction=direction,
        food_position=food_position,
        random_source=random.Random(7),
    )


SCENARIOS = {
    "ordinary_movement": lambda: make_engine(
        4, 3, (1, 1), Direction.RIGHT, (3, 2)
    ),
    "wall_collision": lambda: make_engine(
        4, 3, (3, 1), Direction.RIGHT, (0, 0)
    ),
    "body_collision": lambda: make_engine(
        4, 4, (1, 1), Direction.RIGHT, (0, 0), body=((2, 1), (2, 2), (1, 2))
    ),
    "departing_tail": lambda: make_engine(
        4, 4, (1, 1), Direction.RIGHT, (0, 0), body=((2, 1),)
    ),
    "eating": lambda: make_engine(
        3, 1, (0, 0), Direction.RIGHT, (1, 0)
    ),
    "full_board_win": lambda: make_engine(
        2, 1, (0, 0), Direction.RIGHT, (1, 0)
    ),
}


def test_preview_reports_an_ordinary_move_without_changing_state():
    engine = SnakeEngine(
        GameConfig(width=4, height=3, tile_size=20),
        start_position=(1, 1),
        direction=Direction.RIGHT,
        food_position=(3, 2),
    )
    state_before = engine.state

    transition = engine.preview()

    assert transition.direction is Direction.RIGHT
    assert transition.position == Position(2, 1)
    assert transition.moved is True
    assert transition.ate_food is False
    assert transition.collision is False
    assert transition.game_over is False
    assert engine.state == state_before


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_preview_and_step_agree_from_the_same_starting_state(scenario):
    engine = SCENARIOS[scenario]()
    state_before = engine.state

    transition = engine.preview()

    assert engine.state == state_before, "preview must not mutate the engine"

    moved = engine.step()

    assert moved is transition.moved
    assert engine.snake_position == transition.position
    assert engine.snake_body == transition.body
    assert engine.score == transition.score
    assert engine.game_over is transition.game_over
    assert engine.game_won is transition.game_won


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
def test_preview_reports_the_score_change_it_commits(scenario):
    engine = SCENARIOS[scenario]()
    score_before = engine.score

    transition = engine.preview()
    engine.step()

    assert transition.score_change == engine.score - score_before


def test_preview_never_consumes_randomness_or_spawns_food():
    class FailingRandom:
        def randint(self, start, end):
            raise AssertionError("preview must not consume randomness")

    engine = SnakeEngine(
        GameConfig(width=3, height=1, tile_size=20),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        food_position=(1, 0),
        random_source=FailingRandom(),
    )
    food_before = engine.food_position

    transition = engine.preview()

    assert transition.ate_food is True
    assert engine.food_position == food_before
    assert engine.score == 0


def test_preview_reports_a_full_board_win_without_requesting_food():
    class FailingRandom:
        def randint(self, start, end):
            raise AssertionError("a full board must not request another food cell")

    engine = SnakeEngine(
        GameConfig(width=2, height=1, tile_size=20),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        food_position=(1, 0),
        random_source=FailingRandom(),
    )

    transition = engine.preview()

    assert transition.game_won is True
    assert transition.game_over is True

    engine.step()

    assert engine.game_won is True
    assert engine.food_position is None


def test_preview_treats_a_refused_reversal_as_the_current_heading():
    engine = make_engine(4, 3, (1, 1), Direction.RIGHT, (3, 2))

    transition = engine.preview(Direction.LEFT)

    assert transition.direction is Direction.RIGHT
    assert transition.position == Position(2, 1)


def test_preview_evaluates_a_candidate_direction_without_committing_it():
    engine = make_engine(4, 3, (1, 1), Direction.RIGHT, (3, 2))

    transition = engine.preview(Direction.DOWN)

    assert transition.direction is Direction.DOWN
    assert transition.position == Position(1, 2)
    assert engine.direction is Direction.RIGHT
