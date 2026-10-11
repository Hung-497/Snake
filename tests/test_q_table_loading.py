import json

import pytest

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine


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


V2_KEY = "0_0_0_0_1_0_2_2_2"
V3_LENGTH_KEY = "0_0_0_0_1_0_2_2_2_1_0_1"


def build_bot(table_path):
    """Build a Q Learning bot through its constructor, requiring the saved table."""
    engine = SnakeEngine(GameConfig(4, 4, 25), start_position=None)
    return QLearningBot(engine, q_table_file=str(table_path), require_saved_table=True)


@pytest.mark.parametrize(
    "field, value",
    [
        ("epsilon", 1.5),
        ("epsilon", -0.1),
        ("epsilon", float("nan")),
        ("epsilon", float("inf")),
        ("epsilon", True),
        ("game_trained", -1),
        ("game_trained", True),
        ("game_trained", 1.5),
        ("q_table", {"0_0_0_0_1_0_2_2_3": VALID_ACTION_VALUES}),
        ("q_table", {V3_LENGTH_KEY: VALID_ACTION_VALUES}),
        ("q_table", {"0_0_0_0_1_0_2_2": VALID_ACTION_VALUES}),
    ],
)
def test_a_table_with_a_malformed_field_is_refused_and_left_unchanged(tmp_path, field, value):
    table_path = tmp_path / "q_table.json"
    table = {"q_table": {V2_KEY: VALID_ACTION_VALUES}, "epsilon": 0.4, "game_trained": 12}
    table[field] = value
    # json writes NaN and Infinity, which the loader reads back as floats.
    table_path.write_text(json.dumps(table))
    before = table_path.read_text()

    with pytest.raises(ValueError, match="missing or malformed"):
        build_bot(table_path)

    assert table_path.read_text() == before


def test_a_valid_table_of_each_feature_set_loads_through_the_constructor(tmp_path):
    for feature_set, key in (("v2", V2_KEY), ("v3", V3_LENGTH_KEY)):
        table_path = tmp_path / f"{feature_set}.json"
        table_path.write_text(json.dumps({
            "feature_set": feature_set,
            "q_table": {key: VALID_ACTION_VALUES},
            "epsilon": 0.4,
            "game_trained": 12,
        }))
        engine = SnakeEngine(GameConfig(4, 4, 25), start_position=None)

        bot = QLearningBot(
            engine, q_table_file=str(table_path), require_saved_table=True,
            feature_set=feature_set,
        )

        assert bot.game_trained == 12
        assert bot.epsilon == 0.4
        assert len(bot.q_table) == 1
