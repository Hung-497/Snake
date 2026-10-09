"""Q Learning v3 is its own Bot Mode on Feature Set v3 (ADR 0009)."""

import json
import random

from snake.bots.BotFactory import create_bot_mode, normal_experiment_modes
from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import SnakeEngine
from snake.storage.ReplayManager import ReplayManager
from snake.ui.PlayerLabels import BOT_MODE_LABELS
from snake.ui.RecordsBrowser import player_group
from snake.ui.Theme import player_color, TEXT_MUTED


def make_engine(seed=3):
    return SnakeEngine(
        GameConfig(width=6, height=6, tile_size=20),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        random_source=random.Random(seed),
    )


def play_one_game(bot, engine, move_limit=300):
    moves = 0
    while not engine.game_over and moves < move_limit:
        direction = bot.choose_action(engine.state)
        if direction is not None:
            engine.change_direction(direction)
        transition = engine.preview()
        engine.step()
        bot.observe(transition)
        moves += 1
    bot.on_game_end(engine.state)


def test_q_learning_v3_is_a_labelled_bot_mode_on_feature_set_v3():
    engine = make_engine()
    bot = create_bot_mode("q_learning_v3", engine, random_source=random.Random(4))

    assert BOT_MODE_LABELS["q_learning_v3"] == "Q Learning v3"
    assert bot.feature_set == "v3"
    assert len(bot.features(engine.state)) == 12


def test_q_learning_stays_on_feature_set_v2(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine = make_engine()

    bot = create_bot_mode("q_learning", engine)

    assert bot.feature_set == "v2"
    assert len(bot.features(engine.state)) == 9


def test_q_learning_v3_starts_without_a_table_and_saves_its_own(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    v2_table = tmp_path / "learning_data" / "q_table_space_state_v2.json"
    v2_table.parent.mkdir()
    v2_table.write_text('{"q_table": {}, "epsilon": 0.5, "game_trained": 7}')
    engine = make_engine()
    bot = create_bot_mode("q_learning_v3", engine, random_source=random.Random(4))

    play_one_game(bot, engine)

    saved = json.loads(
        (tmp_path / "learning_data" / "q_table_space_state_v3.json").read_text()
    )
    assert saved["feature_set"] == "v3"
    assert saved["game_trained"] == 1
    assert all(len(key.split("_")) == 12 for key in saved["q_table"])
    assert v2_table.read_text() == '{"q_table": {}, "epsilon": 0.5, "game_trained": 7}'


def test_q_learning_v3_loads_its_saved_table(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    first_engine = make_engine()
    first = create_bot_mode("q_learning_v3", first_engine, random_source=random.Random(4))
    play_one_game(first, first_engine)

    again = create_bot_mode("q_learning_v3", make_engine(), random_source=random.Random(4))

    assert again.game_trained == 1
    assert again.q_table == first.q_table


def test_q_learning_v3_keeps_its_own_records_replay_and_colour(tmp_path):
    replays = ReplayManager.__new__(ReplayManager)
    replays.folder_name = str(tmp_path)

    assert player_group("q_learning_v3") == "q_learning_v3"
    assert player_group("q_learning_v2") == "q_learning"
    assert replays.get_replay_file_path("q_learning_v3").endswith("q_learning_v3_best.json")
    assert player_color("q_learning_v3") not in (TEXT_MUTED, player_color("q_learning"))


def test_q_learning_v3_is_not_in_the_default_bot_experiment():
    assert "q_learning_v3" not in normal_experiment_modes()
    assert "q_learning" in normal_experiment_modes()
