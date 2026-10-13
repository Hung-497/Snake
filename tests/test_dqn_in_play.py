"""Play offers DQN beside the other Bot Modes and opens Live Training for it."""

import pytest

from snake.bots.BotFactory import supports_board
from snake.sessions.HumanPlayer import HUMAN_PLAY
from snake.sessions.ReplaySession import load_replay_session
from snake.storage.ReplayManager import ReplayManager
from snake.ui import Theme
from snake.ui.PlayerLabels import BOT_MODE_LABELS, app_view_for_bot_mode, player_label
from snake.ui.views.MenuView import MENU_ACTIONS


def test_dqn_is_a_bot_mode_labelled_with_its_version():
    assert BOT_MODE_LABELS["dqn"] == "DQN v3"
    assert player_label("dqn") == "DQN v3"
    # Human Play is a Player, never a Bot Mode.
    assert HUMAN_PLAY not in BOT_MODE_LABELS


def test_dqn_v2_is_a_bot_mode_labelled_with_its_version():
    assert BOT_MODE_LABELS["dqn_v2"] == "DQN v2"
    assert player_label("dqn_v2") == "DQN v2"


def test_both_dqn_versions_open_live_training_and_other_bot_modes_open_the_game():
    assert app_view_for_bot_mode("dqn") == "live_training"
    assert app_view_for_bot_mode("dqn_v2") == "live_training"
    for bot_mode in BOT_MODE_LABELS:
        if bot_mode not in ("dqn", "dqn_v2"):
            assert app_view_for_bot_mode(bot_mode) == "game"


@pytest.mark.parametrize("dqn", ["dqn", "dqn_v2"])
def test_each_dqn_version_has_its_own_records_colour(dqn):
    others = [Theme.player_color(player) for player in BOT_MODE_LABELS if player != dqn]
    others.append(Theme.player_color(HUMAN_PLAY))

    assert Theme.player_color(dqn) != Theme.TEXT_MUTED
    assert Theme.player_color(dqn) not in others


def test_both_dqn_versions_play_on_every_board_with_room_to_move():
    for dqn in ("dqn", "dqn_v2"):
        assert supports_board(dqn, 5, 5)
        assert not supports_board(dqn, 1, 1)


def test_the_menu_no_longer_has_a_live_training_button():
    view_names = [view_name for _, view_name, _ in MENU_ACTIONS]

    assert "live_training" not in view_names
    assert "play" in view_names


def test_replay_explains_that_no_dqn_replay_is_saved_yet(tmp_path):
    session, message = load_replay_session(ReplayManager(str(tmp_path)), "dqn")

    assert session is None
    assert message == "No replay saved for dqn yet."
