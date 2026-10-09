"""Q-tables record the Feature Set they were trained on (ADR 0009)."""

import json

import pytest

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine


ACTION_VALUES = {"Straight": 1.0, "Turn_Left": 0.5, "Turn_Right": -1.0}


def make_engine():
    return SnakeEngine(GameConfig(6, 6), start_position=(2, 2), food_position=(4, 2))


def write_table(path, feature_set=None):
    data = {
        "q_table": {"0_0_0_1_0_0_2_2_2": ACTION_VALUES},
        "epsilon": 0.3,
        "game_trained": 5,
    }
    if feature_set is not None:
        data["feature_set"] = feature_set
    path.write_text(json.dumps(data))


def test_saved_q_table_records_feature_set_v2(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "table.json"
    bot = QLearningBot(make_engine(), q_table_file=str(path))

    bot.save_q_table()

    assert json.loads(path.read_text())["feature_set"] == "v2"


def test_q_table_without_feature_set_loads_as_v2(tmp_path):
    path = tmp_path / "table.json"
    write_table(path)

    bot = QLearningBot(make_engine(), evaluation_mode=True, q_table_file=str(path))

    assert bot.q_table == {(0, 0, 0, 1, 0, 0, 2, 2, 2): ACTION_VALUES}
    assert bot.game_trained == 5


@pytest.mark.parametrize("feature_set", ["v3", "v9", 2])
def test_q_table_with_another_feature_set_is_refused(tmp_path, feature_set):
    path = tmp_path / "table.json"
    write_table(path, feature_set)

    with pytest.raises(ValueError, match="Feature Set"):
        QLearningBot(make_engine(), evaluation_mode=True, q_table_file=str(path))


def test_refused_q_table_is_not_partially_applied(tmp_path):
    path = tmp_path / "table.json"
    write_table(path, "v3")
    bot = QLearningBot(make_engine(), q_table_file=str(path))

    assert bot.q_table == {}
    assert bot.game_trained == 0
