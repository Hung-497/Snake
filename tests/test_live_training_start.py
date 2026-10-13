"""Opening Live Training from the app."""

import pytest


pytest.importorskip("torch")

from snake.sessions.LiveTraining import missing_dependency_message, start_live_training
from snake.sessions.SessionSettings import SessionSettings


def test_nothing_is_missing_when_pytorch_is_installed():
    assert missing_dependency_message() is None


def test_live_training_trains_on_the_board_chosen_in_settings():
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")

    session = start_live_training(settings)

    assert session.config == settings.build_game_config()
    assert (session.engine.board_width, session.engine.board_height) == (16, 16)
    assert session.stats().games_played == 0
