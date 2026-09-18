"""
Tests for the repeated-game session that the Game App View drives.

The session is given substitute Game Engine and storage boundaries here, so
these tests need no graphical display. They deliberately do not check Snake
rules, which belong to the Game Engine, and they never check drawing.
"""

import pytest

from GameTypes import Direction
from GameConfig import GameConfig
from SnakeEngine import EngineState, SnakeEngine
from GameSession import GameSession


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

    @property
    def state(self):
        return EngineState(
            board_width=self.board_width,
            board_height=self.board_height,
            tile_size=self.tile_size,
            snake_position=(1, 1),
            snake_body=(),
            direction=Direction.RIGHT,
            food_position=self.food_position,
            score=self.score,
            game_over=self.game_over,
            game_won=self.game_won,
        )

    def change_direction(self, direction):
        self.directions_taken.append(direction)

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
