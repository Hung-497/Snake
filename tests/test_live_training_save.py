"""Live Training keeps its progress in its own DQN Training Checkpoint."""

import os
from pathlib import Path
import random
import subprocess
import sys

import pytest


pytest.importorskip("torch")
import torch

from snake.bots.DQNBot import DEFAULT_DQN_SETTINGS, DQNBot
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine
from snake.sessions.LiveTraining import LiveTrainingCheckpointError, start_live_training
from snake.sessions.LiveTrainingSession import LiveTrainingSession
from snake.sessions.SessionSettings import SessionSettings
from snake.storage.DQNArtifacts import (
    checkpoint_data, common_metadata, load_artifact, save_torch_data,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG = GameConfig(6, 6, 20)


def make_session(checkpoint_path, seed=7):
    return LiveTrainingSession(CONFIG, seed=seed, max_moves=60, checkpoint_path=checkpoint_path)


def play_games(session, games):
    target = session.stats().games_played + games
    while session.stats().games_played < target:
        session.make_move()


def assert_same_training(first, second):
    assert first.stats() == second.stats()
    assert first.scores == second.scores
    assert first.engine.state == second.engine.state
    second_weights = second.bot.network.state_dict()
    for name, weights in first.bot.network.state_dict().items():
        assert torch.equal(second_weights[name], weights), name


def test_saving_writes_a_dqn_training_checkpoint(tmp_path):
    path = tmp_path / "learning_data" / "dqn_live_training.pt"
    session = make_session(path)
    play_games(session, 2)

    session.save()

    checkpoint = load_artifact(path, "dqn_training_checkpoint")
    assert checkpoint["metadata"]["feature_schema"] == "q_learning_space_state_v3"
    assert checkpoint["metadata"]["training_board"]["width"] == 6
    assert checkpoint["state"]["game_trained"] == 2
    assert list(tmp_path.rglob("*.pt")) == [path]


def test_continuing_from_a_save_matches_never_stopping(tmp_path):
    path = tmp_path / "dqn_live_training.pt"
    never_stopped = make_session(path)
    play_games(never_stopped, 3)
    never_stopped.save()

    continued = LiveTrainingSession.load(path, CONFIG)
    play_games(never_stopped, 3)
    play_games(continued, 3)

    assert_same_training(continued, never_stopped)


def test_stats_are_kept_across_a_save(tmp_path):
    path = tmp_path / "dqn_live_training.pt"
    session = make_session(path)
    play_games(session, 4)
    session.save()

    continued = LiveTrainingSession.load(path, CONFIG)

    assert continued.stats().games_played == 4
    assert continued.stats().best_score == session.stats().best_score
    assert continued.stats().average_score == session.stats().average_score
    assert continued.stats().epsilon == session.stats().epsilon


def test_a_game_left_halfway_keeps_its_learning_and_starts_fresh(tmp_path):
    path = tmp_path / "dqn_live_training.pt"
    session = make_session(path)
    play_games(session, 1)
    for _ in range(40):
        session.make_move()
    session.save()

    continued = LiveTrainingSession.load(path, CONFIG)

    assert continued.stats().games_played == 1
    assert continued.engine.score == 0 and continued.moves_this_game == 0
    assert len(continued.bot.replay) == len(session.bot.replay)
    saved_weights = session.bot.network.state_dict()
    for name, weights in continued.bot.network.state_dict().items():
        assert torch.equal(saved_weights[name], weights), name


def test_a_save_continues_on_another_board(tmp_path):
    path = tmp_path / "dqn_live_training.pt"
    session = make_session(path)
    play_games(session, 3)
    session.save()

    continued = LiveTrainingSession.load(path, GameConfig(16, 16, 20))

    # The same DQN keeps learning: Feature Set v3 does not depend on the board size.
    assert continued.stats().games_played == 3
    assert continued.stats().epsilon == session.stats().epsilon
    assert len(continued.bot.replay) == len(session.bot.replay)
    saved_weights = session.bot.network.state_dict()
    for name, weights in continued.bot.network.state_dict().items():
        assert torch.equal(saved_weights[name], weights), name
    assert (continued.engine.board_width, continued.engine.board_height) == (16, 16)
    play_games(continued, 1)
    assert continued.stats().games_played == 4


def test_saving_after_a_board_change_records_the_new_board(tmp_path):
    path = tmp_path / "dqn_live_training.pt"
    make_session(path).save()
    continued = LiveTrainingSession.load(path, GameConfig(16, 16, 20))
    play_games(continued, 1)

    continued.save()

    board = load_artifact(path, "dqn_training_checkpoint")["metadata"]["training_board"]
    assert (board["width"], board["height"]) == (16, 16)


def test_opening_live_training_on_another_board_continues_the_save(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "dqn_live_training.pt"
    session = make_session(path)
    play_games(session, 2)
    session.save()
    settings = SessionSettings()
    settings.select_board_size("Large 30 x 30")

    continued = start_live_training(settings, checkpoint_path=path)

    assert continued.stats().games_played == 2
    assert (continued.engine.board_width, continued.engine.board_height) == (30, 30)


def test_a_save_for_another_feature_set_is_reported(tmp_path):
    path = tmp_path / "dqn_live_training.pt"
    engine = SnakeEngine(CONFIG, start_position=None, random_source=random.Random(0))
    bot = DQNBot(engine, random.Random(1), random.Random(2), feature_set="v2")
    metadata = common_metadata(CONFIG, DEFAULT_DQN_SETTINGS, 0, 60, "v2-run", None, "v2")
    metadata["checkpoint_every"] = 25
    save_torch_data(path, checkpoint_data(bot, engine, metadata))

    with pytest.raises(LiveTrainingCheckpointError, match="Feature Set v2"):
        LiveTrainingSession.load(path, CONFIG)


def test_opening_live_training_starts_fresh_then_continues(tmp_path, monkeypatch):
    # Opening Live Training saves Records in the current folder.
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "dqn_live_training.pt"
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")

    first = start_live_training(settings, checkpoint_path=path)
    assert first.stats().games_played == 0
    play_games(first, 1)
    first.save()

    second = start_live_training(settings, checkpoint_path=path)
    assert second.stats().games_played == 1


def test_the_headless_command_can_resume_a_live_training_save(tmp_path):
    path = tmp_path / "dqn_live_training.pt"
    session = make_session(path)
    play_games(session, 2)
    session.save()
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)

    result = subprocess.run(
        [sys.executable, "-m", "snake.sessions.TrainDQN", "--games", "1",
         "--resume", str(path)],
        cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=120,
    )

    assert result.returncode == 0, result.stderr
    assert "DQN game 1/1" in result.stdout
