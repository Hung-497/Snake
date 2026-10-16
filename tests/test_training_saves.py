"""Continuing a learning Bot Mode's saved app training, or starting it over from game 0."""

from datetime import datetime
import json

import pytest

from snake.sessions.TrainingSaves import (
    TRAINING_LIMITS, SavedTraining, copy_shared_q_table_once, saved_training, start_over,
)


NOW = datetime(2026, 10, 16, 20, 11, 3)


def test_every_training_limit_is_offered_with_off_first():
    assert TRAINING_LIMITS == {
        "Off": None, "1000 games": 1000, "2000 games": 2000, "5000 games": 5000,
    }


def test_there_is_no_saved_training_without_a_save(tmp_path):
    assert saved_training("dqn", save_path=tmp_path / "live.pt") is None


def test_a_saved_training_shows_its_games_and_best_score(tmp_path):
    pytest.importorskip("torch")
    from snake.engine.GameConfig import GameConfig
    from snake.sessions.LiveTrainingSession import LiveTrainingSession

    checkpoint_path = tmp_path / "live.pt"
    session = LiveTrainingSession(GameConfig(6, 6, 20), checkpoint_path=checkpoint_path,
                                  game_limit=2000)
    session.bot.game_trained = 3
    session.scores = [4, 9, 2]
    session.save()

    assert saved_training("dqn", save_path=checkpoint_path) == SavedTraining(3, 9, 2000)


def test_an_unreadable_save_still_counts_as_saved_training(tmp_path):
    checkpoint_path = tmp_path / "live.pt"
    checkpoint_path.write_bytes(b"not a checkpoint")

    # Live Training explains the problem when it opens; the choice stays offered.
    assert saved_training("dqn", save_path=checkpoint_path) == SavedTraining(None, None, None)


def test_starting_over_keeps_the_old_save_as_a_dated_backup(tmp_path):
    checkpoint_path = tmp_path / "live.pt"
    checkpoint_path.write_bytes(b"old training")

    backup_path = start_over("dqn", save_path=checkpoint_path, now=lambda: NOW)

    assert backup_path == tmp_path / "live_2026-10-16_201103.pt"
    assert backup_path.read_bytes() == b"old training"
    # With no save left, the next Live Training starts at game 0.
    assert not checkpoint_path.exists()


def test_starting_over_twice_in_one_second_keeps_both_backups(tmp_path):
    checkpoint_path = tmp_path / "live.pt"
    checkpoint_path.write_bytes(b"first")
    first = start_over("dqn", save_path=checkpoint_path, now=lambda: NOW)
    checkpoint_path.write_bytes(b"second")

    second = start_over("dqn", save_path=checkpoint_path, now=lambda: NOW)

    assert first != second
    assert first.read_bytes() == b"first"
    assert second.read_bytes() == b"second"


def test_starting_over_without_a_save_does_nothing(tmp_path):
    assert start_over("dqn", save_path=tmp_path / "live.pt", now=lambda: NOW) is None
    assert list(tmp_path.iterdir()) == []


def write_q_table(path, game_trained, training_history=None):
    data = {"q_table": {}, "epsilon": 0.05, "game_trained": game_trained}
    if training_history is not None:
        data["training_history"] = training_history
    path.write_text(json.dumps(data))


def test_a_saved_q_table_shows_its_games_best_score_and_limit(tmp_path):
    save_path = tmp_path / "q_table_app_v2.json"
    write_q_table(save_path, 2500, [
        {"source": "train_command", "best_score": 87},
        {"source": "app", "best_score": 60, "game_limit": 3000},
    ])

    assert saved_training("q_learning", save_path=save_path) == SavedTraining(2500, 87, 3000)


def test_a_q_table_without_training_history_shows_only_its_games(tmp_path):
    save_path = tmp_path / "q_table_app_v2.json"
    write_q_table(save_path, 2000)

    assert saved_training("q_learning", save_path=save_path) == SavedTraining(2000, None, None)


def test_the_limit_comes_from_the_latest_training_session(tmp_path):
    # A later terminal session on the same table set no limit.
    save_path = tmp_path / "q_table_app_v2.json"
    write_q_table(save_path, 2500, [
        {"source": "app", "best_score": 60, "game_limit": 1000},
        {"source": "train_command", "best_score": 70},
    ])

    assert saved_training("q_learning", save_path=save_path).game_limit is None


def test_an_unreadable_q_table_still_counts_as_saved_training(tmp_path):
    save_path = tmp_path / "q_table_app_v2.json"
    save_path.write_text("{ not json")

    assert saved_training("q_learning", save_path=save_path) == SavedTraining(None, None, None)


def test_the_app_q_table_starts_as_a_copy_of_the_shared_table(tmp_path):
    shared_path = tmp_path / "q_table_space_state_v2.json"
    app_path = tmp_path / "q_table_app_v2.json"
    write_q_table(shared_path, 2000)

    assert copy_shared_q_table_once("q_learning", app_path=app_path, shared_path=shared_path)
    assert app_path.read_text() == shared_path.read_text()


def test_an_existing_app_q_table_is_never_replaced_by_the_shared_one(tmp_path):
    shared_path = tmp_path / "q_table_space_state_v2.json"
    app_path = tmp_path / "q_table_app_v2.json"
    write_q_table(shared_path, 2000)
    write_q_table(app_path, 5)

    assert not copy_shared_q_table_once("q_learning", app_path=app_path, shared_path=shared_path)
    assert json.loads(app_path.read_text())["game_trained"] == 5


def test_after_starting_over_the_shared_table_is_not_copied_again(tmp_path):
    shared_path = tmp_path / "q_table_space_state_v2.json"
    app_path = tmp_path / "q_table_app_v2.json"
    write_q_table(shared_path, 2000)
    write_q_table(app_path, 5)
    start_over("q_learning", save_path=app_path, now=lambda: NOW)

    # The new training has not finished a game yet, so it has no table.
    assert not copy_shared_q_table_once("q_learning", app_path=app_path, shared_path=shared_path)
    assert not app_path.exists()


def test_nothing_is_copied_without_a_shared_table_or_for_dqn(tmp_path):
    app_path = tmp_path / "q_table_app_v3.json"

    assert not copy_shared_q_table_once(
        "q_learning_v3", app_path=app_path, shared_path=tmp_path / "missing.json"
    )
    assert not copy_shared_q_table_once("dqn")
    assert not app_path.exists()
