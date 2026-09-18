import random

import pytest

from BotFactory import create_bot_mode
from GameConfig import GameConfig
from GameTypes import Direction
from HamiltonianBot import HamiltonianBot
from QLearningBot import QLearningBot
from RuleBasedBot import RuleBasedBot
from SnakeEngine import SnakeEngine


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


@pytest.mark.parametrize("bot_mode", ["rule", "q_learning", "hamiltonian"])
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


@pytest.mark.parametrize("bot_mode", ["rule", "q_learning", "hamiltonian"])
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

    for bot_mode in ("rule", "q_learning", "hamiltonian"):
        bot = create_bot_mode(bot_mode, engine)

        assert bot.random_source is not engine.random_source


class FakeCanvas:
    def create_rectangle(self, *args, **kwargs):
        pass

    def create_oval(self, *args, **kwargs):
        pass

    def delete(self, tag):
        pass


class FakeWindow:
    width = 6
    height = 4
    tile_size = 20

    def __init__(self):
        self.window = self
        self.canvas = FakeCanvas()
        self.scheduled_callbacks = []

    def clear_canvas(self):
        pass

    def update_score_label(self, score, games_played, best_score):
        pass

    def draw_game_over(self, score):
        pass

    def draw_game_won(self, score):
        pass

    def after(self, delay, callback):
        self.scheduled_callbacks.append((delay, callback))
        return len(self.scheduled_callbacks)


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
    def save_game_result(self, *args):
        pass


@pytest.mark.parametrize("bot_mode", ["rule", "q_learning", "hamiltonian"])
def test_game_runs_every_bot_mode_through_the_common_contract(bot_mode, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    from Game import Game

    monkeypatch.setattr("Game.ReplayManager", FakeReplayManager)
    monkeypatch.setattr("Game.RecordManager", FakeRecordManager)

    engine = SnakeEngine(
        GameConfig(width=6, height=4, tile_size=20),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        random_source=random.Random(2),
    )
    game = Game(FakeWindow(), bot_mode=bot_mode, speed_delay=1, engine=engine)

    for _ in range(12):
        if (game.game_over):
            break
        game.update()

    assert game.total_moves > 0
    assert game.score == engine.score
