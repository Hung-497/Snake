import random

import pytest

from snake.bots.BotFactory import create_bot_mode
from snake.engine.GameConfig import GameConfig
from snake.sessions.GameSession import GameSession
from snake.engine.GameTypes import Direction
from snake.bots.HamiltonianBot import HamiltonianBot
from snake.bots.QLearningBot import QLearningBot
from snake.bots.RuleBasedBot import RuleBasedBot
from snake.engine.SnakeEngine import SnakeEngine
from snake.ui.PlayerLabels import BOT_MODE_LABELS


MOVE_LIMIT = 5000


def play_game(bot_mode, width, height, seed, q_table_file=None):
    engine = SnakeEngine(
        GameConfig(width=width, height=height, tile_size=20),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        random_source=random.Random(seed),
    )
    bot = create_bot_mode(bot_mode, engine, random_source=random.Random(seed))

    if (q_table_file is not None):
        bot.q_table_file = q_table_file

    moves = 0
    while (not engine.game_over and moves < MOVE_LIMIT):
        direction = bot.choose_action(engine.state)

        if (direction is not None):
            engine.change_direction(direction)

        transition = engine.preview()
        engine.step()
        bot.observe(transition)
        moves += 1

    bot.on_game_end(engine.state)

    return engine, moves


@pytest.mark.parametrize("bot_mode", ["rule", "q_learning", "hamiltonian", "search_based"])
def test_every_bot_mode_completes_a_game_without_a_window(bot_mode, tmp_path):
    engine, moves = play_game(
        bot_mode,
        width=6,
        height=4,
        seed=1,
        q_table_file=str(tmp_path / "q_table.json"),
    )

    assert engine.game_over is True
    assert moves < MOVE_LIMIT
    assert engine.score >= 0


@pytest.mark.parametrize("bot_mode", ["rule", "q_learning", "hamiltonian", "search_based"])
def test_bot_modes_replay_the_same_game_from_the_same_seed(bot_mode, tmp_path):
    first, first_moves = play_game(
        bot_mode, 6, 4, seed=7, q_table_file=str(tmp_path / "a.json")
    )
    second, second_moves = play_game(
        bot_mode, 6, 4, seed=7, q_table_file=str(tmp_path / "b.json")
    )

    assert first_moves == second_moves
    assert first.score == second.score
    assert first.game_won == second.game_won


def test_hamiltonian_still_wins_a_full_board():
    engine, _ = play_game("hamiltonian", 6, 6, seed=1)

    assert engine.game_won is True
    assert engine.score == 6 * 6 - 1


def test_factory_builds_only_the_selected_bot_mode():
    engine = SnakeEngine(
        GameConfig(width=4, height=4, tile_size=20),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        random_source=random.Random(1),
    )

    assert isinstance(create_bot_mode("rule", engine), RuleBasedBot)
    assert isinstance(create_bot_mode("hamiltonian", engine), HamiltonianBot)
    assert create_bot_mode(None, engine) is None
    assert create_bot_mode("replay:rule", engine) is None


def test_search_based_can_start_a_game_and_choose_a_legal_move():
    engine = SnakeEngine(
        GameConfig(width=4, height=4, tile_size=20),
        start_position=(1, 1),
        body=((0, 1),),
        direction=Direction.RIGHT,
        food_position=(3, 3),
    )

    bot = create_bot_mode("search_based", engine)
    action = bot.choose_action(engine.state)

    assert BOT_MODE_LABELS["search_based"] == "Search-Based"
    assert engine.preview(action).moved is True


def test_unselected_bot_modes_cause_no_side_effects(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class FailingRandom:
        def randint(self, start, end):
            raise AssertionError("building a bot must not consume engine randomness")

    engine = SnakeEngine(
        GameConfig(width=3, height=3, tile_size=20),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        food_position=(2, 2),
        random_source=FailingRandom(),
    )

    def fail_to_load(self):
        raise AssertionError("an unselected Bot Mode must not load persistence")

    monkeypatch.setattr(QLearningBot, "load_q_table", fail_to_load)

    # An odd-by-odd board has no valid cycle, so building Hamiltonian here
    # would fail if the factory validated every Bot Mode.
    bot = create_bot_mode("rule", engine)

    assert isinstance(bot, RuleBasedBot)
    assert not (tmp_path / "learning_data").exists()


def test_each_bot_mode_owns_random_source_separate_from_the_engine(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine = SnakeEngine(
        GameConfig(width=4, height=4, tile_size=20),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        random_source=random.Random(1),
    )

    for bot_mode in ("rule", "q_learning", "hamiltonian", "search_based"):
        bot = create_bot_mode(bot_mode, engine)

        assert bot.random_source is not engine.random_source


class FakeReplayManager:
    def start_recording(self, *args, **kwargs):
        pass

    def record_move(self, direction):
        pass

    def record_food(self, food):
        pass

    def save_replay(self, bot_mode, score, game_won):
        pass


class FakeRecordManager:
    def save_game_result(self, *args, **kwargs):
        pass


@pytest.mark.parametrize("bot_mode", ["rule", "q_learning", "hamiltonian", "search_based"])
def test_the_game_session_runs_every_bot_mode_through_the_common_contract(
    bot_mode, tmp_path, monkeypatch
):
    # A working directory of its own, so a learning bot saves nothing real.
    monkeypatch.chdir(tmp_path)

    engine = SnakeEngine(
        GameConfig(width=6, height=4, tile_size=20),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        random_source=random.Random(2),
    )
    session = GameSession(
        engine,
        bot_mode=bot_mode,
        speed_delay=1,
        record_manager=FakeRecordManager(),
        replay_manager=FakeReplayManager(),
    )
    session.start()

    for _ in range(12):
        if (session.game_over):
            break
        session.advance()

    assert session.total_moves > 0
    assert session.score == engine.score


def test_search_based_limits_moves_in_one_fast_game_update():
    engine = SnakeEngine(
        GameConfig(width=30, height=30, tile_size=20),
        start_position=(0, 0),
        food_position=(29, 29),
    )
    session = GameSession(
        engine,
        bot_mode="search_based",
        speed_delay=1,
        record_manager=FakeRecordManager(),
        replay_manager=FakeReplayManager(),
    )
    session.start()

    moves = session.advance_by(1.0)

    assert 1 <= moves <= 4
    assert session.advance_by(0.0) == 0


@pytest.mark.parametrize(
    "width, height, seed",
    [(4, 4, 3), (4, 4, 4), (4, 4, 8), (4, 4, 15), (6, 4, 18), (4, 6, 14), (6, 6, 6)],
)
def test_hamiltonian_clears_the_board_after_an_unfollowable_cycle_step(width, height, seed):
    # A shortcut can land on the tile just behind the head in cycle order.
    # Following the cycle from there would reverse into the body, so the bot
    # has to keep itself alive instead of walking into a wall.
    engine, _ = play_game("hamiltonian", width, height, seed)

    assert engine.game_won is True
    assert engine.score == width * height - 1
