"""Choosing to continue a saved Live Training or to start it over from game 0."""

from datetime import datetime

import pytest

from snake.sessions.LiveTraining import SavedTraining, saved_training, start_over


NOW = datetime(2026, 10, 16, 20, 11, 3)


def test_there_is_no_saved_training_without_a_save(tmp_path):
    assert saved_training("dqn", checkpoint_path=tmp_path / "live.pt") is None


def test_a_saved_training_shows_its_games_and_best_score(tmp_path):
    pytest.importorskip("torch")
    from snake.engine.GameConfig import GameConfig
    from snake.sessions.LiveTrainingSession import LiveTrainingSession

    checkpoint_path = tmp_path / "live.pt"
    session = LiveTrainingSession(GameConfig(6, 6, 20), checkpoint_path=checkpoint_path)
    session.bot.game_trained = 3
    session.scores = [4, 9, 2]
    session.save()

    assert saved_training("dqn", checkpoint_path=checkpoint_path) == SavedTraining(3, 9)


def test_an_unreadable_save_still_counts_as_saved_training(tmp_path):
    checkpoint_path = tmp_path / "live.pt"
    checkpoint_path.write_bytes(b"not a checkpoint")

    # Live Training explains the problem when it opens; the choice stays offered.
    assert saved_training("dqn", checkpoint_path=checkpoint_path) == SavedTraining(None, None)


def test_starting_over_keeps_the_old_save_as_a_dated_backup(tmp_path):
    checkpoint_path = tmp_path / "live.pt"
    checkpoint_path.write_bytes(b"old training")

    backup_path = start_over("dqn", checkpoint_path=checkpoint_path, now=lambda: NOW)

    assert backup_path == tmp_path / "live_2026-10-16_201103.pt"
    assert backup_path.read_bytes() == b"old training"
    # With no save left, the next Live Training starts at game 0.
    assert not checkpoint_path.exists()


def test_starting_over_twice_in_one_second_keeps_both_backups(tmp_path):
    checkpoint_path = tmp_path / "live.pt"
    checkpoint_path.write_bytes(b"first")
    first = start_over("dqn", checkpoint_path=checkpoint_path, now=lambda: NOW)
    checkpoint_path.write_bytes(b"second")

    second = start_over("dqn", checkpoint_path=checkpoint_path, now=lambda: NOW)

    assert first != second
    assert first.read_bytes() == b"first"
    assert second.read_bytes() == b"second"


def test_starting_over_without_a_save_does_nothing(tmp_path):
    assert start_over("dqn", checkpoint_path=tmp_path / "live.pt", now=lambda: NOW) is None
    assert list(tmp_path.iterdir()) == []
