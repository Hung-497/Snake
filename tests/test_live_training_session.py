"""Live Training trains DQN one move at a time, exactly like the headless command."""

import os
from pathlib import Path
import subprocess
import sys

import pytest


pytest.importorskip("torch")
import torch

from snake.engine.GameConfig import GameConfig
from snake.sessions.LiveTrainingSession import LiveTrainingSession


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def make_session(width=6, height=6, seed=7, max_moves=60):
    return LiveTrainingSession(
        GameConfig(width, height, 20), seed=seed, max_moves=max_moves,
    )


def play_until_games(session, games):
    while session.stats().games_played < games:
        session.make_move()


def test_live_training_uses_feature_set_v3():
    session = make_session()

    layer_sizes = [
        layer.out_features for layer in session.bot.network
        if isinstance(layer, torch.nn.Linear)
    ]

    assert session.bot.feature_set == "v3"
    assert session.bot.network[0].in_features == 12
    assert layer_sizes == [64, 64, 3]


def test_a_fresh_session_has_not_played_yet():
    stats = make_session().stats()

    assert stats.games_played == 0
    assert stats.score == 0
    assert stats.best_score == 0
    assert stats.average_score == 0
    assert stats.epsilon == 1.0


def test_one_call_makes_exactly_one_move():
    session = make_session()
    head_before = session.engine.snake_position

    session.make_move()

    assert session.engine.snake_position != head_before
    assert len(session.bot.replay) == 1


def test_a_game_that_reaches_the_move_limit_ends_and_a_new_one_starts():
    session = make_session(width=20, height=20, max_moves=3)
    first_engine = session.engine

    for _ in range(3):
        session.make_move()

    assert session.stats().games_played == 1
    assert session.engine is not first_engine
    assert session.bot.engine is session.engine
    assert session.engine.score == 0
    assert not session.engine.game_over


def test_stats_follow_finished_games():
    session = make_session()

    play_until_games(session, 5)
    stats = session.stats()

    assert stats.games_played == 5
    assert stats.best_score == max(session.scores)
    assert stats.average_score == sum(session.scores) / len(session.scores)
    assert stats.epsilon == session.bot.epsilon < 1.0


def test_live_training_learns_exactly_like_the_headless_command(tmp_path):
    games, seed, max_moves = 3, 7, 60
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    result = subprocess.run(
        [
            sys.executable, "-m", "snake.sessions.TrainDQN",
            "--games", str(games), "--width", "6", "--height", "6",
            "--tile-size", "20", "--seed", str(seed),
            "--max-moves", str(max_moves), "--features", "v3",
        ],
        cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr
    run = next((tmp_path / "learning_data" / "dqn_runs").iterdir())
    headless = torch.load(run / "checkpoint.pt", weights_only=True)["state"]

    session = make_session(seed=seed, max_moves=max_moves)
    play_until_games(session, games)

    # Learning really happened, so matching weights is a meaningful check.
    assert session.bot.optimizer_steps == headless["optimizer_steps"] > 0
    assert session.bot.epsilon == headless["epsilon"]
    live_weights = session.bot.network.state_dict()
    for name, weights in headless["online_weights"].items():
        assert torch.equal(live_weights[name], weights), name
