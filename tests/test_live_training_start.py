"""Opening Live Training from the app."""

import pytest


pytest.importorskip("torch")

from snake.sessions.LiveTraining import missing_dependency_message, start_live_training
from snake.sessions.SessionSettings import SessionSettings


def test_nothing_is_missing_when_pytorch_is_installed():
    assert missing_dependency_message() is None


def test_live_training_trains_on_the_board_chosen_in_settings(tmp_path, monkeypatch):
    # Opening Live Training saves Records in the current folder.
    monkeypatch.chdir(tmp_path)
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")

    session = start_live_training(settings, checkpoint_path=tmp_path / "live.pt")

    assert session.config == settings.build_game_config()
    assert (session.engine.board_width, session.engine.board_height) == (16, 16)
    assert session.stats().games_played == 0


def test_new_live_training_uses_the_chosen_game_limit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    session = start_live_training(
        SessionSettings(), checkpoint_path=tmp_path / "live.pt", game_limit=1000,
    )

    assert session.game_limit == 1000


def test_continuing_keeps_the_game_limit_saved_with_the_training(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    checkpoint_path = tmp_path / "live.pt"
    start_live_training(SessionSettings(), checkpoint_path=checkpoint_path, game_limit=2000).save()

    continued = start_live_training(SessionSettings(), checkpoint_path=checkpoint_path)

    assert continued.game_limit == 2000


def test_a_save_from_before_game_limits_has_no_limit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    checkpoint_path = tmp_path / "live.pt"
    start_live_training(SessionSettings(), checkpoint_path=checkpoint_path).save()

    continued = start_live_training(SessionSettings(), checkpoint_path=checkpoint_path)

    assert continued.game_limit is None
