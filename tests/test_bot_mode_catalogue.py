"""Every fact about a Bot Mode is written once, in the Bot Mode catalogue."""

from pathlib import Path

from snake.bots.BotFactory import BOT_MODE_CLASSES
from snake.bots.BotModeCatalogue import (
    BOT_MODES, SPARE_COLORS, BotColors, BotMode, bot_mode, bot_mode_colors,
)
from snake.sessions.LiveTraining import DQN_VERSIONS
from snake.sessions.RunExperiment import BOT_NAMES
from snake.sessions.TrainQLearning import FEATURE_SET_BY_BOT_MODE
from snake.sessions.TrainingSaves import APP_Q_TABLES, SAVE_PATHS, SHARED_Q_TABLES, SHOWCASE_BOTS
from snake.ui.PlayerLabels import (
    BOT_MODE_LABELS, LEARNING_FAMILIES, LIVE_TRAINING_BOT_MODES, app_view_for_bot_mode,
)


LEARNING_DATA = Path("learning_data")
SHOWCASE = Path("starter_data") / "showcase"


def test_the_catalogue_lists_every_bot_mode_once_in_play_order():
    assert [mode.key for mode in BOT_MODES] == [
        "rule", "q_learning", "hamiltonian", "search_based", "q_learning_v3", "dqn", "dqn_v2",
    ]


def test_the_older_tables_are_read_from_the_catalogue():
    assert BOT_MODE_LABELS == {
        "rule": "Rule Based", "q_learning": "Q Learning v2", "hamiltonian": "Hamiltonian",
        "search_based": "Search-Based", "q_learning_v3": "Q Learning v3",
        "dqn": "DQN v3", "dqn_v2": "DQN v2",
    }
    assert {key: family.versions for key, family in LEARNING_FAMILIES.items()} == {
        "q_learning": {"v2": "q_learning", "v3": "q_learning_v3"},
        "dqn": {"v2": "dqn_v2", "v3": "dqn"},
    }
    assert LIVE_TRAINING_BOT_MODES == ("dqn", "dqn_v2")
    assert FEATURE_SET_BY_BOT_MODE == {"q_learning": "v2", "q_learning_v3": "v3"}
    assert {key: (v.feature_set, v.checkpoint_path) for key, v in DQN_VERSIONS.items()} == {
        "dqn": ("v3", LEARNING_DATA / "dqn_live_training.pt"),
        "dqn_v2": ("v2", LEARNING_DATA / "dqn_v2_live_training.pt"),
    }
    assert APP_Q_TABLES == {
        "q_learning": LEARNING_DATA / "q_table_app_v2.json",
        "q_learning_v3": LEARNING_DATA / "q_table_app_v3.json",
    }
    assert SHARED_Q_TABLES == {
        "q_learning": LEARNING_DATA / "q_table_space_state_v2.json",
        "q_learning_v3": LEARNING_DATA / "q_table_space_state_v3.json",
    }
    assert SAVE_PATHS == {**APP_Q_TABLES, **{key: v.checkpoint_path for key, v in DQN_VERSIONS.items()}}
    assert {key: (bot.path, bot.seed) for key, bot in SHOWCASE_BOTS.items()} == {
        "q_learning": (SHOWCASE / "q_table_v2_seed12000.json", 12000),
        "q_learning_v3": (SHOWCASE / "q_table_v3_seed15000.json", 15000),
        "dqn": (SHOWCASE / "dqn_v3_seed9000.pt", 9000),
    }


def test_play_opens_live_training_only_for_dqn():
    assert [app_view_for_bot_mode(mode.key) for mode in BOT_MODES] == [
        "game", "game", "game", "game", "game", "live_training", "live_training",
    ]


def test_the_terminal_names_match_the_app_except_for_any_dqn_model():
    # RunExperiment's dqn evaluates whichever DQN model it is given, v2 or v3.
    assert BOT_NAMES == {**BOT_MODE_LABELS, "dqn": "DQN"}


def test_every_bot_mode_the_factory_builds_is_in_the_catalogue():
    assert set(BOT_MODE_CLASSES) <= {mode.key for mode in BOT_MODES}


def test_each_learning_bot_mode_sees_its_own_feature_set_version():
    for mode in BOT_MODES:
        if mode.family is None:
            assert mode.version is None and mode.save_path is None
        else:
            assert mode.version in ("v2", "v3")
            assert mode.save_path is not None
    assert bot_mode("dqn").label == "DQN v3"


def test_a_bot_mode_without_colours_gets_the_next_spare_pair():
    modes = (
        BotMode("rule", "Rule Based", colors=BotColors("#F2B84B", "#9A6B00")),
        BotMode("dqn_v4", "DQN v4"),
        BotMode("dqn_v5", "DQN v5"),
    )

    colors = bot_mode_colors(modes)

    assert colors["rule"] == BotColors("#F2B84B", "#9A6B00")
    assert colors["dqn_v4"] == SPARE_COLORS[0]
    assert colors["dqn_v5"] == SPARE_COLORS[1]
