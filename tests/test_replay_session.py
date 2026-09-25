"""
Tests for playing back a saved replay.

A substitute replay boundary stands in for the stored JSON files, so these
tests need neither saved replays nor a graphical display. Replay data is
already normalised to grid cells by ReplayManager before it gets here.
"""

import pytest

from snake.storage.ReplayManager import ReplayCompatibilityError
from snake.sessions.ReplaySession import ReplaySession, load_replay_session


# The saved move numbers: 1 UP, 2 LEFT, 3 DOWN, 4 RIGHT.
UP = 1
LEFT = 2
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
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 5))

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
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 10_000))
    session.cycle_speed()
    assert session.speed_name == "Fast"

    moves_played = session.advance_by(60.0)

    assert 0 < moves_played <= ReplaySession.MOVES_PER_UPDATE_LIMIT


def test_a_paused_replay_plays_no_moves():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))

    session.toggle_pause()
    session.advance_by(1.0)

    assert session.paused
    assert session.move_index == 0


def test_resuming_continues_from_the_same_move_without_a_burst():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))
    session.advance_by(0.02)
    position_when_paused = session.snake_position

    session.toggle_pause()
    # A long pause must not turn into catch-up moves on resume.
    session.advance_by(5.0)
    session.toggle_pause()

    assert not session.paused
    assert session.snake_position == position_when_paused

    session.advance_by(0.01)

    assert session.move_index == 3


def test_a_finished_replay_cannot_be_paused():
    session = ReplaySession(make_replay_data(moves=(RIGHT, RIGHT)))
    session.advance_by(1.0)

    session.toggle_pause()

    assert session.finished
    assert not session.paused


def test_a_stopped_replay_cannot_be_paused():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))

    session.stop()
    session.toggle_pause()

    assert not session.paused


def test_restart_brings_back_the_start_of_the_replay():
    session = ReplaySession(make_replay_data(moves=(RIGHT, RIGHT, DOWN), foods=((3, 1),)))
    session.advance_by(0.03)
    assert session.score == 1

    session.restart()

    assert session.snake_position == (1, 1)
    assert session.snake_body == []
    assert session.food_position == (3, 1)
    assert session.score == 0
    assert session.move_index == 0


def test_a_restarted_replay_plays_again_from_the_first_move():
    session = ReplaySession(make_replay_data(moves=(RIGHT, RIGHT, DOWN)))
    session.advance_by(0.03)

    session.restart()
    session.advance_by(0.01)

    assert session.snake_position == (2, 1)


def test_restart_works_after_the_replay_finishes():
    session = ReplaySession(make_replay_data(moves=(RIGHT, RIGHT)))
    session.advance_by(1.0)
    assert session.finished

    session.restart()

    assert not session.finished
    assert session.advance_by(0.01) == 1


def test_restart_plays_right_away_even_when_paused():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))
    session.toggle_pause()

    session.restart()

    assert not session.paused
    assert session.advance_by(0.01) == 1


def test_restart_starts_with_no_leftover_time():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))
    session.advance_by(0.015)

    session.restart()

    assert session.advance_by(0.005) == 0


def test_a_stopped_replay_cannot_be_restarted():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))
    session.advance_by(0.03)
    move_when_stopped = session.move_index

    session.stop()
    session.restart()

    assert session.move_index == move_when_stopped
    assert session.advance_by(1.0) == 0


def test_every_replay_starts_at_the_normal_replay_speed():
    session = ReplaySession(make_replay_data())

    assert session.speed_name == "Normal"


def test_the_replay_speed_cycles_from_slow_to_normal_to_fast():
    session = ReplaySession(make_replay_data())
    speed_names = []

    for _ in range(4):
        session.cycle_speed()
        speed_names.append(session.speed_name)

    assert speed_names == ["Fast", "Slow", "Normal", "Fast"]


@pytest.mark.parametrize(
    "cycles, speed_name, move_seconds",
    [(0, "Normal", 0.010), (1, "Fast", 0.002), (2, "Slow", 0.100)],
)
def test_each_replay_speed_plays_moves_at_its_own_interval(cycles, speed_name, move_seconds):
    # The saved game speed is ignored; only the Replay Speed counts.
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20, speed_delay=500))
    for _ in range(cycles):
        session.cycle_speed()
    assert session.speed_name == speed_name

    session.advance_by(move_seconds * 0.9)
    assert session.move_index == 0

    session.advance_by(move_seconds * 0.2)
    assert session.move_index == 1


def test_changing_the_replay_speed_plays_no_burst_of_moves():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))
    session.cycle_speed()
    session.cycle_speed()
    assert session.speed_name == "Slow"
    session.advance_by(0.09)

    # Leftover Slow time must not turn into many Fast moves.
    session.cycle_speed()
    session.cycle_speed()
    assert session.speed_name == "Fast"

    assert session.advance_by(0.001) == 0


def test_the_replay_speed_can_change_while_paused():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))
    session.toggle_pause()

    session.cycle_speed()
    session.toggle_pause()

    assert session.speed_name == "Fast"
    assert session.advance_by(0.002) == 1


def test_restart_keeps_the_replay_speed():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))
    session.cycle_speed()

    session.restart()

    assert session.speed_name == "Fast"


def test_a_stopped_replay_keeps_its_replay_speed():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))

    session.stop()
    session.cycle_speed()

    assert session.speed_name == "Normal"


def test_progress_starts_at_the_first_of_all_saved_moves():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))

    assert session.moves_played == 0
    assert session.total_moves == 20


def test_progress_counts_up_as_moves_are_played():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))

    session.advance()
    session.advance()

    assert session.moves_played == 2


def test_progress_stays_the_same_while_paused():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))
    session.advance()
    session.toggle_pause()

    session.advance_by(1.0)

    assert session.moves_played == 1


def test_progress_goes_back_to_the_start_on_restart():
    session = ReplaySession(make_replay_data(moves=(RIGHT,) * 20))
    session.advance()
    session.advance()

    session.restart()

    assert session.moves_played == 0
    assert session.total_moves == 20


def test_progress_reaches_every_move_when_the_replay_ends():
    session = ReplaySession(make_replay_data(moves=(RIGHT, RIGHT, DOWN)))

    session.advance_by(1.0)

    assert session.finished
    assert session.moves_played == session.total_moves == 3


# A saved game that ended in a collision also saves the fatal move, but the
# Game Engine never moved the snake for it, so the replay must not either.

def test_a_fatal_move_into_the_wall_leaves_the_head_on_the_board():
    session = ReplaySession(make_replay_data(moves=(RIGHT, RIGHT), foods=((1, 5),),
                                             start_snake=[8, 1], final_score=0))

    session.advance_by(1.0)

    assert session.snake_position == (9, 1)
    assert session.finished
    assert session.moves_played == session.total_moves == 2


def test_a_fatal_move_into_the_body_leaves_the_snake_where_it_was():
    # Four foods make the snake five cells long, then it turns back into itself.
    session = ReplaySession(make_replay_data(
        moves=(RIGHT, RIGHT, RIGHT, RIGHT, DOWN, LEFT, UP),
        foods=((2, 1), (3, 1), (4, 1), (5, 1), (9, 9)),
        final_score=4,
    ))

    session.advance_by(1.0)

    assert session.snake_position == (4, 2)
    assert session.snake_body == [(5, 2), (5, 1), (4, 1), (3, 1)]
    assert session.finished
    assert session.moves_played == session.total_moves == 7


def test_moving_into_the_tail_cell_is_not_a_collision():
    # The tail moves away on the same move, as the Game Engine allows.
    session = ReplaySession(make_replay_data(
        moves=(RIGHT, RIGHT, RIGHT, DOWN, LEFT, UP, RIGHT),
        foods=((2, 1), (3, 1), (4, 1), (9, 9)),
        final_score=3,
    ))

    for _ in range(6):
        session.advance()

    assert session.snake_position == (3, 1)
    assert not session.finished
