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


class FakeClock:
    """A clock that moves forward one second every time it is read."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        self.now += 1.0
        return self.now


def test_a_time_budget_makes_moves_until_the_budget_runs_out():
    session = make_session()

    # Start at 1; each move reads the clock once more, so 3 moves reach 4.
    moves = session.make_moves_for(3.0, clock=FakeClock())

    assert moves == 3
    assert len(session.bot.replay) == 3


def test_a_tiny_time_budget_still_makes_one_move_and_stops():
    session = make_session()

    moves = session.make_moves_for(0.0, clock=FakeClock())

    assert moves == 1
    assert len(session.bot.replay) == 1


def test_watching_live_or_in_background_learns_the_same_network():
    one_at_a_time = make_session()
    in_batches = make_session()
    mixed = make_session()

    batch_moves = 0
    while in_batches.stats().games_played < 3:
        batch_moves += in_batches.make_moves_for(25.0, clock=FakeClock())
    for _ in range(batch_moves):
        one_at_a_time.make_move()
    mixed_moves = 0
    while mixed_moves < batch_moves:
        if mixed_moves % 2:
            mixed.make_move()
            mixed_moves += 1
        else:
            mixed_moves += mixed.make_moves_for(
                min(7.0, batch_moves - mixed_moves - 1), clock=FakeClock()
            )

    assert mixed_moves == batch_moves
    for other in (in_batches, mixed):
        assert other.stats() == one_at_a_time.stats()
        assert other.scores == one_at_a_time.scores
        assert other.engine.state == one_at_a_time.engine.state
        live_weights = one_at_a_time.bot.network.state_dict()
        for name, weights in other.bot.network.state_dict().items():
            assert torch.equal(live_weights[name], weights), name
