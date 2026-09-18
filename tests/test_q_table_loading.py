import json

import pytest

from QLearningBot import QLearningBot


VALID_STATE = "0_0_0_0_1_0_2_2_2"
VALID_ACTION_VALUES = {
    "Straight": 1.5,
    "Turn_Left": 2,
    "Turn_Right": -0.5,
}


def make_loader(tmp_path, contents=None):
    path = tmp_path / "q_table.json"
    if contents is not None:
        path.write_text(contents)

    bot = QLearningBot.__new__(QLearningBot)
    bot.q_table_file = str(path)
    bot.q_table = {}
    bot.epsilon = 1.0
    bot.game_trained = 0
    bot.actions = ["Straight", "Turn_Left", "Turn_Right"]
    return bot


def saved_data(q_table=None, epsilon=0.4, game_trained=12):
    return {
        "q_table": q_table if q_table is not None else {},
        "epsilon": epsilon,
        "game_trained": game_trained,
    }


@pytest.mark.parametrize("contents", [None, ""])
def test_missing_or_empty_file_keeps_defaults(tmp_path, contents):
    bot = make_loader(tmp_path, contents)

    bot.load_q_table()

    assert bot.q_table == {}
    assert bot.epsilon == 1.0
    assert bot.game_trained == 0


@pytest.mark.parametrize("contents", ["not json", json.dumps([])])
def test_invalid_file_structure_keeps_complete_defaults(tmp_path, contents):
    bot = make_loader(tmp_path, contents)

    bot.load_q_table()

    assert bot.q_table == {}
    assert bot.epsilon == 1.0
    assert bot.game_trained == 0


@pytest.mark.parametrize(
    "bad_q_table",
    [
        {"not_a_state": VALID_ACTION_VALUES},
        {VALID_STATE: {"Straight": 1.0}},
    ],
)
def test_malformed_q_table_does_not_partially_apply(tmp_path, bad_q_table):
    data = saved_data(
        {
            VALID_STATE: VALID_ACTION_VALUES,
            **bad_q_table,
        },
        epsilon=0.2,
        game_trained=99,
    )
    bot = make_loader(tmp_path, json.dumps(data))

    bot.load_q_table()

    assert bot.q_table == {}
    assert bot.epsilon == 1.0
    assert bot.game_trained == 0


def test_valid_q_table_restores_all_saved_values(tmp_path):
    data = saved_data({VALID_STATE: VALID_ACTION_VALUES})
    bot = make_loader(tmp_path, json.dumps(data))

    bot.load_q_table()

    assert bot.q_table == {
        (0, 0, 0, 0, 1, 0, 2, 2, 2): VALID_ACTION_VALUES,
    }
    assert bot.epsilon == pytest.approx(0.4)
    assert bot.game_trained == 12
