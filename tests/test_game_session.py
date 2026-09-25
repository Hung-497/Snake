"""
Tests for the repeated-game session that the Game App View drives.

The session is given substitute Game Engine and storage boundaries here, so
these tests need no graphical display. They deliberately do not check Snake
rules, which belong to the Game Engine, and they never check drawing.
"""

import pytest

from snake.engine.GameTypes import Direction
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import EngineState, SnakeEngine
from snake.sessions.GameSession import GameSession
from snake.sessions.ReplaySession import ReplaySession
from snake.storage.ReplayManager import ReplayManager


class FakeEngine:
    """A stand-in Game Engine that ends the game after a fixed number of moves."""

    def __init__(self, moves_until_game_over=3, game_won=False):
        self.board_width = 10
        self.board_height = 10
        self.tile_size = 25
        self.moves_until_game_over = moves_until_game_over
        self.ends_as_a_win = game_won

        self.score = 0
        self.game_over = False
        self.game_won = False
        self.food_position = (5, 5)
        self.moves_made = 0
        self.reset_count = 0
        self.directions_taken = []
        self.direction = Direction.RIGHT

    @property
    def state(self):
        return EngineState(
            board_width=self.board_width,
            board_height=self.board_height,
            tile_size=self.tile_size,
            snake_position=(1, 1),
            snake_body=(),
            direction=self.direction,
            food_position=self.food_position,
            score=self.score,
            game_over=self.game_over,
            game_won=self.game_won,
        )

    def change_direction(self, direction):
        self.directions_taken.append(direction)
        self.direction = direction

    def choose_start_direction(self, direction):
        # The fake snake has no body, so it may start facing any way.
        self.direction = direction
        return True

    def preview(self, direction=None):
        return f"transition-{self.moves_made}"

    def step(self):
        self.moves_made += 1
        self.score += 1

        if (self.moves_made >= self.moves_until_game_over):
            self.game_over = True
            self.game_won = self.ends_as_a_win

    def reset(self):
        self.reset_count += 1
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.moves_made = 0


class FakeBot:
    def __init__(self, direction=Direction.RIGHT):
        self.direction = direction
        self.calls = []

    def choose_action(self, state):
        self.calls.append("choose_action")
        return self.direction

    def observe(self, transition):
        self.calls.append(f"observe:{transition}")

    def on_game_end(self, result):
        self.calls.append("on_game_end")


class FakeRecordManager:
    def __init__(self):
        self.saved_results = []

    def save_game_result(self, *result):
        self.saved_results.append(result)


class FakeReplayManager:
    def __init__(self):
        self.recordings_started = 0
        self.saved_replays = []
        self.moves = []
        self.foods = []

    def start_recording(self, *args, **kwargs):
        self.recordings_started += 1

    def record_move(self, direction):
        self.moves.append(direction)

    def record_food(self, food_position):
        self.foods.append(food_position)

    def save_replay(self, bot_name, score, game_won=False):
        self.saved_replays.append((bot_name, score, game_won))


def make_session(engine=None, bot=None, speed_delay=10, **kwargs):
    engine = FakeEngine() if engine is None else engine
    bot = FakeBot() if bot is None else bot
    session = GameSession(
        engine,
        bot_mode="rule",
        speed_delay=speed_delay,
        record_manager=FakeRecordManager(),
        replay_manager=FakeReplayManager(),
        bot=bot,
        **kwargs,
    )
    session.start()

    return session


def test_starting_the_session_starts_recording_a_replay():
    session = make_session()

    assert session.replay_manager.recordings_started == 1


def test_one_move_asks_the_bot_then_steps_the_engine_then_reports_back():
    bot = FakeBot()
    session = make_session(bot=bot)

    session.advance()

    assert session.engine.directions_taken == [Direction.RIGHT]
    assert session.engine.moves_made == 1
    # The bot sees the transition the step committed, not a fresh calculation.
    assert bot.calls == ["choose_action", "observe:transition-0"]


def test_moves_happen_at_the_chosen_speed():
    session = make_session(speed_delay=10)  # 10 ms between moves

    session.advance_by(0.005)
    assert session.engine.moves_made == 0

    session.advance_by(0.005)
    assert session.engine.moves_made == 1


def test_a_finished_game_is_recorded_and_the_bot_is_told():
    bot = FakeBot()
    session = make_session(engine=FakeEngine(moves_until_game_over=2), bot=bot)

    session.advance()
    session.advance()

    assert session.games_played == 1
    assert session.best_score == 2
    assert session.replay_manager.saved_replays == [("rule", 2, False)]
    assert len(session.record_manager.saved_results) == 1
    saved_result = session.record_manager.saved_results[0]
    assert saved_result[0] == "rule"       # bot name
    assert saved_result[2] == 2            # score
    assert "on_game_end" in bot.calls


def test_a_won_game_is_reported_as_a_win():
    session = make_session(engine=FakeEngine(moves_until_game_over=1, game_won=True))

    session.advance()

    assert session.game_won
    assert session.replay_manager.saved_replays == [("rule", 1, True)]


def test_the_next_game_starts_after_the_result_pause():
    session = make_session(engine=FakeEngine(moves_until_game_over=1), speed_delay=10)

    session.advance()
    assert session.engine.reset_count == 0

    session.advance_by(1.0)

    assert session.engine.reset_count == 1
    assert session.score == 0
    assert session.games_played == 1
    assert session.replay_manager.recordings_started == 2


def test_the_best_score_keeps_the_highest_score_of_the_session():
    session = make_session(engine=FakeEngine(moves_until_game_over=3), speed_delay=10)

    session.advance_by(1.0)   # first game, score 3
    session.engine.moves_until_game_over = 1
    session.advance_by(1.0)   # the result pause ends and the next game starts
    session.advance_by(1.0)   # second game, score 1

    assert session.games_played == 2
    assert session.best_score == 3


def test_a_stopped_session_makes_no_further_moves():
    session = make_session(speed_delay=10)

    session.stop()
    session.advance_by(1.0)

    assert session.engine.moves_made == 0


def test_one_update_cannot_make_an_unlimited_number_of_moves():
    # A long frame must not freeze the window by catching up forever.
    session = make_session(engine=FakeEngine(moves_until_game_over=10_000), speed_delay=1)

    moves_made = session.advance_by(60.0)

    assert 0 < moves_made <= GameSession.MOVES_PER_UPDATE_LIMIT


def test_the_score_average_prunes_before_it_is_calculated():
    # Only the last hundred scores count, and the oldest goes before the average.
    session = make_session(engine=FakeEngine(moves_until_game_over=2))
    session.recent_scores = [1] * 100

    session.advance()
    session.advance()

    average_score = session.record_manager.saved_results[0][4]
    assert average_score == pytest.approx(1.01)


def test_the_move_average_prunes_before_it_is_calculated(capsys):
    # Only the last ten games count towards the average number of moves.
    session = make_session(engine=FakeEngine(moves_until_game_over=1))
    session.total_moves_history = [10] * 10
    session.total_moves = 19

    session.advance()

    assert "Avg total move: 11.0" in capsys.readouterr().out


def test_a_session_drives_a_real_game_engine():
    # The same loop, with the real Game Engine instead of a stand-in.
    engine = SnakeEngine(
        GameConfig(width=3, height=1, tile_size=25),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        food_position=(1, 0),
    )
    session = GameSession(
        engine,
        bot_mode=None,
        speed_delay=1,
        record_manager=FakeRecordManager(),
        replay_manager=FakeReplayManager(),
    )
    session.start()

    session.advance()

    assert engine.snake_position == (1, 0)
    assert engine.snake_body == ((0, 0),)
    assert engine.score == 1
    assert session.score == 1


# Human Play: a person steers, so the session waits for them instead of
# playing on by itself. The session builds its own Human Play controller here.

class FakeClock:
    """A clock the test moves by hand, in seconds."""

    def __init__(self):
        self.seconds = 0.0

    def __call__(self):
        return self.seconds


def make_human_session(engine=None, speed_delay=100, now=None):
    engine = FakeEngine() if engine is None else engine
    session = GameSession(
        engine,
        bot_mode="human",
        speed_delay=speed_delay,
        record_manager=FakeRecordManager(),
        replay_manager=FakeReplayManager(),
        now=FakeClock() if now is None else now,
    )
    session.start()

    return session


def test_human_play_makes_no_moves_before_the_first_direction():
    session = make_human_session()

    session.advance_by(5.0)

    assert session.engine.moves_made == 0
    assert session.status == "waiting_to_start"


def test_the_first_direction_starts_human_play_and_is_used_on_the_first_move():
    session = make_human_session(speed_delay=100)

    session.press_direction(Direction.UP)
    session.advance_by(0.1)

    assert session.status == "playing"
    assert session.engine.direction == Direction.UP
    assert session.engine.moves_made == 1


def test_two_quick_turns_are_used_on_the_next_two_moves_and_a_third_is_dropped():
    session = make_human_session(engine=FakeEngine(moves_until_game_over=10), speed_delay=100)
    session.press_direction(Direction.UP)
    session.advance_by(0.1)

    session.press_direction(Direction.LEFT)
    session.press_direction(Direction.DOWN)
    session.press_direction(Direction.RIGHT)
    session.advance_by(0.1)
    session.advance_by(0.1)
    session.advance_by(0.1)

    assert session.engine.directions_taken == [Direction.LEFT, Direction.DOWN]
    assert session.engine.moves_made == 4


@pytest.mark.parametrize("ignored_direction", [Direction.UP, Direction.DOWN])
def test_a_turn_that_repeats_or_reverses_the_snake_is_ignored(ignored_direction):
    # The snake is moving up, so Up repeats it and Down reverses it.
    session = make_human_session(engine=FakeEngine(moves_until_game_over=10), speed_delay=100)
    session.press_direction(Direction.UP)
    session.advance_by(0.1)

    session.press_direction(ignored_direction)
    session.advance_by(0.1)

    assert session.engine.directions_taken == []


def test_a_finished_human_game_waits_for_a_restart_instead_of_starting_another():
    session = make_human_session(engine=FakeEngine(moves_until_game_over=1), speed_delay=100)
    session.press_direction(Direction.UP)
    session.advance_by(0.1)

    session.advance_by(5.0)

    assert session.status == "showing_result"
    assert session.engine.reset_count == 0


def test_restarting_human_play_starts_a_new_game_that_waits_for_a_first_direction():
    session = make_human_session(engine=FakeEngine(moves_until_game_over=1), speed_delay=100)
    session.press_direction(Direction.UP)
    session.advance_by(0.1)

    session.restart()
    session.advance_by(5.0)

    assert session.engine.reset_count == 1
    assert session.status == "waiting_to_start"
    assert session.engine.moves_made == 0
    assert session.replay_manager.recordings_started == 2


def test_a_finished_human_game_is_saved_once_under_human_with_its_speed():
    session = make_human_session(engine=FakeEngine(moves_until_game_over=2), speed_delay=100)
    session.press_direction(Direction.UP)
    session.advance_by(0.2)
    session.advance_by(5.0)

    assert session.replay_manager.saved_replays == [("human", 2, False)]
    assert len(session.record_manager.saved_results) == 1
    saved_result = session.record_manager.saved_results[0]
    assert saved_result[0] == "human"      # player
    assert saved_result[-1] == 100         # speed delay


def test_leaving_human_play_before_the_game_ends_saves_nothing():
    session = make_human_session(engine=FakeEngine(moves_until_game_over=10), speed_delay=100)
    session.press_direction(Direction.UP)
    session.advance_by(0.3)

    session.stop()
    session.advance_by(5.0)

    assert session.replay_manager.saved_replays == []
    assert session.record_manager.saved_results == []


def start_human_game(speed_delay=100):
    """A Human Play session that has made one move and is now playing."""
    session = make_human_session(engine=FakeEngine(moves_until_game_over=20), speed_delay=speed_delay)
    session.press_direction(Direction.UP)
    session.advance_by(0.1)

    return session


def test_pausing_human_play_stops_moves_and_resuming_makes_no_catch_up_moves():
    session = start_human_game(speed_delay=100)

    session.toggle_pause()
    session.advance_by(5.0)
    assert session.status == "paused"
    assert session.engine.moves_made == 1

    session.toggle_pause()
    session.advance_by(0.1)
    assert session.status == "playing"
    assert session.engine.moves_made == 2


def test_direction_presses_while_paused_are_ignored():
    session = start_human_game(speed_delay=100)
    session.toggle_pause()

    session.press_direction(Direction.LEFT)
    session.toggle_pause()
    session.advance_by(0.1)

    assert session.engine.directions_taken == []


def test_losing_focus_pauses_human_play_and_never_resumes_it():
    session = start_human_game()

    session.focus_lost()
    assert session.status == "paused"

    session.focus_lost()
    session.advance_by(5.0)
    assert session.status == "paused"
    assert session.engine.moves_made == 1


def test_pausing_does_nothing_while_waiting_to_start():
    session = make_human_session()

    session.toggle_pause()
    session.focus_lost()

    assert session.status == "waiting_to_start"


def test_pausing_does_nothing_while_the_result_is_showing():
    session = make_human_session(engine=FakeEngine(moves_until_game_over=1), speed_delay=100)
    session.press_direction(Direction.UP)
    session.advance_by(0.1)

    session.toggle_pause()
    session.focus_lost()

    assert session.status == "showing_result"


def test_a_long_frame_makes_only_one_human_move_and_drops_the_rest():
    # A frozen window must not make the snake jump many cells at once.
    session = make_human_session(engine=FakeEngine(moves_until_game_over=50), speed_delay=100)
    session.press_direction(Direction.UP)

    session.advance_by(2.0)
    assert session.engine.moves_made == 1

    session.advance_by(0.05)
    assert session.engine.moves_made == 1

    session.advance_by(0.05)
    assert session.engine.moves_made == 2


def test_human_game_time_leaves_out_waiting_and_paused_time():
    clock = FakeClock()
    session = make_human_session(engine=FakeEngine(moves_until_game_over=2), speed_delay=100, now=clock)

    clock.seconds = 30.0            # 30 s before the first key
    session.press_direction(Direction.UP)
    clock.seconds = 31.0
    session.advance_by(0.1)
    session.toggle_pause()
    clock.seconds = 331.0           # 5 minutes paused
    session.toggle_pause()
    clock.seconds = 332.0
    session.advance_by(0.1)

    saved_result = session.record_manager.saved_results[0]
    assert saved_result[6] == 2.0   # game time: 30 -> 332, minus the pause
    assert saved_result[7] == 32.0  # session time: 0 -> 332, minus the pause


def test_the_first_direction_can_turn_the_snake_around_before_it_moves():
    # The snake starts facing right, but a person pressing Left means Left.
    session = make_human_session(speed_delay=100)

    session.press_direction(Direction.LEFT)
    session.advance_by(0.1)

    assert session.status == "playing"
    assert session.engine.direction == Direction.LEFT
    assert session.engine.moves_made == 1


def test_a_human_replay_records_a_direction_for_every_move():
    # A replay plays back one saved direction per move, straight moves included.
    session = make_human_session(engine=FakeEngine(moves_until_game_over=10), speed_delay=100)
    session.press_direction(Direction.UP)
    session.advance_by(0.1)
    session.advance_by(0.1)
    session.press_direction(Direction.LEFT)
    session.advance_by(0.1)

    assert session.replay_manager.moves == [Direction.UP, Direction.UP, Direction.LEFT]


def test_a_human_game_replays_along_the_path_it_was_played(tmp_path):
    engine = SnakeEngine(
        GameConfig(width=6, height=6, tile_size=20),
        start_position=(3, 3),
        direction=Direction.RIGHT,
        food_position=(0, 5),
    )
    replay_manager = ReplayManager(folder_name=str(tmp_path))
    session = GameSession(
        engine,
        bot_mode="human",
        speed_delay=100,
        record_manager=FakeRecordManager(),
        replay_manager=replay_manager,
        now=FakeClock(),
    )
    session.start()

    session.press_direction(Direction.LEFT)   # turn around before the first move
    session.advance_by(0.1)                   # to (2, 3)
    session.press_direction(Direction.UP)
    for _ in range(4):                        # up to (2, 0), then into the wall
        session.advance_by(0.1)
    assert session.status == "showing_result"

    replay = ReplaySession(replay_manager.load_replay("human"))
    for _ in range(4):
        replay.advance()

    assert replay.snake_position == (2, 0)
