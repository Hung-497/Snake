"""Play offers DQN beside the other Bot Modes and opens Live Training for it."""

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


def test_dqn_opens_live_training_and_other_bot_modes_open_the_game():
    assert app_view_for_bot_mode("dqn") == "live_training"
    for bot_mode in BOT_MODE_LABELS:
        if bot_mode != "dqn":
            assert app_view_for_bot_mode(bot_mode) == "game"


def test_dqn_has_its_own_records_colour():
    others = [Theme.player_color(player) for player in BOT_MODE_LABELS if player != "dqn"]
    others.append(Theme.player_color(HUMAN_PLAY))

    assert Theme.player_color("dqn") != Theme.TEXT_MUTED
    assert Theme.player_color("dqn") not in others


def test_the_menu_no_longer_has_a_live_training_button():
    view_names = [view_name for _, view_name, _ in MENU_ACTIONS]

    assert "live_training" not in view_names
    assert "play" in view_names


def test_replay_explains_that_no_dqn_replay_is_saved_yet(tmp_path):
    session, message = load_replay_session(ReplayManager(str(tmp_path)), "dqn")

    assert session is None
    assert message == "No replay saved for dqn yet."
