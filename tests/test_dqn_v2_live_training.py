"""DQN v2 trains in Live Training like DQN v3, with Feature Set v2 and its own save."""

import os
from pathlib import Path
import subprocess
import sys

import pytest


pytest.importorskip("torch")
import torch

from snake.engine.GameConfig import GameConfig
from snake.sessions.LiveTraining import (
    DQN_VERSIONS, LiveTrainingCheckpointError, start_live_training,
)
from snake.sessions.LiveTrainingSession import LiveTrainingSession
from snake.sessions.SessionSettings import SessionSettings
from snake.storage.DQNArtifacts import load_artifact
from snake.storage.RecordManager import RecordManager


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG = GameConfig(6, 6, 20)


def make_session(player="dqn_v2", checkpoint_path=None, seed=7, max_moves=60):
    return LiveTrainingSession(
        CONFIG, seed=seed, max_moves=max_moves,
        checkpoint_path=checkpoint_path, player=player,
    )


def play_games(session, games):
    target = session.stats().games_played + games
    while session.stats().games_played < target:
        session.make_move()


def assert_same_weights(first, second):
    second_weights = second.bot.network.state_dict()
    for name, weights in first.bot.network.state_dict().items():
        assert torch.equal(second_weights[name], weights), name


def test_each_dqn_version_has_its_feature_set_and_its_own_save():
    assert DQN_VERSIONS["dqn"].feature_set == "v3"
    assert DQN_VERSIONS["dqn_v2"].feature_set == "v2"
    # DQN v3 keeps the save it always had.
    assert DQN_VERSIONS["dqn"].checkpoint_path == Path("learning_data") / "dqn_live_training.pt"
    assert DQN_VERSIONS["dqn_v2"].checkpoint_path != DQN_VERSIONS["dqn"].checkpoint_path


def test_a_dqn_v2_session_has_a_nine_input_network():
    session = make_session()

    assert session.bot.feature_set == "v2"
    assert session.bot.network[0].in_features == 9


def test_a_dqn_v2_snapshot_has_layers_of_9_64_64_3():
    session = make_session()
    session.make_move()

    snapshot = session.network_snapshot()

    assert [len(layer) for layer in snapshot.activations] == [9, 64, 64, 3]
    assert [len(matrix[0]) for matrix in snapshot.weights] == [9, 64, 64]


def test_dqn_v2_learns_exactly_like_the_headless_command_with_feature_set_v2(tmp_path):
    games, seed, max_moves = 3, 7, 60
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    result = subprocess.run(
        [
            sys.executable, "-m", "snake.sessions.TrainDQN",
            "--games", str(games), "--width", "6", "--height", "6",
            "--tile-size", "20", "--seed", str(seed),
            "--max-moves", str(max_moves), "--features", "v2",
        ],
        cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr
    run = next((tmp_path / "learning_data" / "dqn_runs").iterdir())
    headless = torch.load(run / "checkpoint.pt", weights_only=True)["state"]

    session = make_session(seed=seed, max_moves=max_moves)
    play_games(session, games)

    assert session.bot.optimizer_steps == headless["optimizer_steps"] > 0
    assert session.bot.epsilon == headless["epsilon"]
    live_weights = session.bot.network.state_dict()
    for name, weights in headless["online_weights"].items():
        assert torch.equal(live_weights[name], weights), name


def test_a_dqn_v2_save_records_feature_set_v2(tmp_path):
    path = tmp_path / "dqn_v2_live_training.pt"
    session = make_session(checkpoint_path=path)
    play_games(session, 1)

    session.save()

    metadata = load_artifact(path, "dqn_training_checkpoint")["metadata"]
    assert metadata["feature_schema"] == "q_learning_space_state_v2"


def test_dqn_v2_continues_its_save_on_another_board(tmp_path):
    path = tmp_path / "dqn_v2_live_training.pt"
    session = make_session(checkpoint_path=path)
    play_games(session, 2)
    session.save()

    continued = LiveTrainingSession.load(path, GameConfig(16, 16, 20), player="dqn_v2")

    assert continued.bot.feature_set == "v2"
    assert continued.stats().games_played == 2
    assert (continued.engine.board_width, continued.engine.board_height) == (16, 16)
    assert_same_weights(session, continued)
    play_games(continued, 1)
    assert continued.stats().games_played == 3


@pytest.mark.parametrize("saved, opened", [("dqn", "dqn_v2"), ("dqn_v2", "dqn")])
def test_neither_dqn_version_loads_the_others_save(tmp_path, saved, opened):
    path = tmp_path / "save.pt"
    session = make_session(player=saved, checkpoint_path=path)
    play_games(session, 1)
    session.save()
    saved_bytes = path.read_bytes()

    with pytest.raises(LiveTrainingCheckpointError, match="Feature Set"):
        LiveTrainingSession.load(path, CONFIG, player=opened)

    assert path.read_bytes() == saved_bytes


def test_opening_each_dqn_version_uses_its_own_save(tmp_path, monkeypatch):
    # Opening Live Training saves Records, Replays and saves in the current folder.
    monkeypatch.chdir(tmp_path)
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")

    v3 = start_live_training(settings, "dqn")
    play_games(v3, 2)
    v3.save()
    v2 = start_live_training(settings, "dqn_v2")

    # DQN v2 starts fresh instead of loading DQN v3's save.
    assert v2.bot.feature_set == "v2"
    assert v2.stats().games_played == 0
    play_games(v2, 1)
    v2.save()

    assert (tmp_path / DQN_VERSIONS["dqn"].checkpoint_path).exists()
    assert (tmp_path / DQN_VERSIONS["dqn_v2"].checkpoint_path).exists()
    assert start_live_training(settings, "dqn").stats().games_played == 2
    assert start_live_training(settings, "dqn_v2").stats().games_played == 1


def test_dqn_v2_games_add_records_and_a_best_replay_under_dqn_v2(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")
    settings.select_speed("Normal")

    session = start_live_training(settings, "dqn_v2")
    play_games(session, 2)

    rows = RecordManager().read_game_records()
    assert [row["player"] for row in rows] == ["dqn_v2", "dqn_v2"]
    assert rows[0]["speed_delay"] == str(settings.speed_delay_for("dqn_v2"))
    assert (tmp_path / "replays" / "dqn_v2_best.json").exists()
    assert not (tmp_path / "replays" / "dqn_best.json").exists()
