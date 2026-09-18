"""
Tests for playing back a saved replay.

A substitute replay boundary stands in for the stored JSON files, so these
tests need neither saved replays nor a graphical display. Replay data is
already normalised to grid cells by ReplayManager before it gets here.
"""

import pytest

from ReplayManager import ReplayCompatibilityError
from ReplaySession import ReplaySession, load_replay_session


# 4 is RIGHT and 3 is DOWN in the saved move numbers.
RIGHT = 4
DOWN = 3


def make_replay_data(moves=(RIGHT, RIGHT, RIGHT), foods=((3, 1),), final_score=1, **overrides):
    replay_data = {
        "schema_version": 2,
        "coordinate_system": "grid",
        "board_width": 10,
        "board_height": 10,
        "tile_size": 25,
        "speed_delay": 1,
        "start_snake": [1, 1],
        "start_food": list(foods[0]) if foods else None,
        "foods": [list(food) for food in foods],
        "moves": list(moves),
        "final_score": final_score,
    }
    replay_data.update(overrides)

    return replay_data


class FakeReplayManager:
    """Answers the way ReplayManager does: data, None, or a compatibility error."""

    def __init__(self, replay_data=None, error=None):
        self.replay_data = replay_data
        self.error = error
        self.requested_bot_names = []

    def load_replay(self, bot_name):
        self.requested_bot_names.append(bot_name)

        if (self.error is not None):
            raise self.error

        return self.replay_data


def test_a_saved_replay_loads_into_a_session():
    replay_manager = FakeReplayManager(make_replay_data())

    session, message = load_replay_session(replay_manager, "rule")

    assert message is None
    assert isinstance(session, ReplaySession)
    assert replay_manager.requested_bot_names == ["rule"]


def test_a_missing_replay_explains_itself_instead_of_starting():
    replay_manager = FakeReplayManager(replay_data=None)

    session, message = load_replay_session(replay_manager, "hamiltonian")

    assert session is None
    assert "hamiltonian" in message


def test_an_incompatible_replay_explains_itself_instead_of_being_drawn():
    replay_manager = FakeReplayManager(
        error=ReplayCompatibilityError("Unsupported replay schema version: 1")
    )

    session, message = load_replay_session(replay_manager, "rule")

    assert session is None
    assert message == "Unsupported replay schema version: 1"


def test_a_replay_in_an_unknown_coordinate_system_is_refused():
    replay_data = make_replay_data(coordinate_system="polar")

    with pytest.raises(ReplayCompatibilityError):
        ReplaySession(replay_data)


def test_the_snake_follows_the_saved_moves():
    session = ReplaySession(make_replay_data(moves=(RIGHT, DOWN)))

    session.advance()
    assert session.snake_position == (2, 1)

    session.advance()
    assert session.snake_position == (2, 2)


def test_the_score_goes_up_when_the_snake_reaches_saved_food():
    session = ReplaySession(make_replay_data(moves=(RIGHT, RIGHT), foods=((3, 1),), final_score=1))

    session.advance()
    assert session.score == 0

    session.advance()
    assert session.score == 1
    assert session.snake_body == [(2, 1)]


def test_the_replay_finishes_after_the_last_saved_move():
    session = ReplaySession(make_replay_data(moves=(RIGHT, RIGHT)))

    session.advance()
    assert not session.finished

    session.advance()
    assert session.finished


def test_moves_are_played_at_the_replay_speed():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 5), move_delay=10)

    session.advance_by(0.005)
    assert session.move_index == 0

    session.advance_by(0.005)
    assert session.move_index == 1


def test_a_stopped_replay_plays_no_further_moves():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))

    session.stop()
    session.advance_by(1.0)

    assert session.move_index == 0


def test_a_finished_replay_stops_playing_by_itself():
    session = ReplaySession(make_replay_data(moves=(RIGHT, RIGHT)))

    session.advance_by(1.0)
    moves_after_finishing = session.advance_by(1.0)

    assert session.finished
    assert moves_after_finishing == 0


def test_one_update_cannot_play_an_unlimited_number_of_moves():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 10_000), move_delay=1)

    moves_played = session.advance_by(60.0)

    assert 0 < moves_played <= ReplaySession.MOVES_PER_UPDATE_LIMIT
