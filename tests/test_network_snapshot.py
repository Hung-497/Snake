"""Live Training reports what the network saw and decided, without changing training."""

import pytest


pytest.importorskip("torch")
import torch

from snake.engine.GameConfig import GameConfig
from snake.sessions.LiveTrainingSession import LiveTrainingSession


def make_session(seed=7):
    return LiveTrainingSession(GameConfig(6, 6, 20), seed=seed, max_moves=60)


def test_there_is_no_snapshot_before_the_first_move():
    assert make_session().network_snapshot() is None


def test_the_snapshot_has_one_activation_list_per_layer():
    session = make_session()
    session.make_move()

    snapshot = session.network_snapshot()

    assert [len(layer) for layer in snapshot.activations] == [12, 64, 64, 3]
    assert snapshot.activations[0] == list(session.bot.current_features)
    # Hidden neurons use ReLU, so they are never negative.
    assert all(value >= 0 for layer in snapshot.activations[1:3] for value in layer)
    with torch.no_grad():
        expected = session.bot.network(
            torch.tensor(session.bot.current_features, dtype=torch.float32)
        )
    assert torch.allclose(torch.tensor(snapshot.activations[-1]), expected)


def test_the_snapshot_has_the_weights_between_each_pair_of_layers():
    session = make_session()
    session.make_move()

    snapshot = session.network_snapshot()

    # weights[layer][to_neuron][from_neuron], as in torch's Linear layers.
    shapes = [(len(matrix), len(matrix[0])) for matrix in snapshot.weights]
    assert shapes == [(64, 12), (64, 64), (3, 64)]
    first_layer = session.bot.network[0].weight.detach()
    assert snapshot.weights[0][5][3] == pytest.approx(float(first_layer[5][3]))


def test_the_snapshot_names_the_chosen_action():
    session = make_session()
    session.make_move()

    snapshot = session.network_snapshot()

    assert snapshot.actions == ["Straight", "Turn_Left", "Turn_Right"]
    assert snapshot.chosen_action == session.bot.current_action


def test_without_exploration_no_move_is_marked_as_exploration():
    session = make_session()
    session.bot.epsilon = 0.0

    for _ in range(40):
        session.make_move()
        assert session.network_snapshot().explored is False


def test_random_exploration_moves_are_marked():
    session = make_session()
    explored = []

    for _ in range(40):
        session.make_move()
        explored.append(session.network_snapshot().explored)

    # Epsilon starts at 1, so some random safe moves differ from the best one.
    assert any(explored)
    assert not all(explored)


def test_taking_snapshots_does_not_change_training():
    watched = make_session()
    unwatched = make_session()

    for _ in range(200):
        watched.make_move()
        watched.network_snapshot()
        unwatched.make_move()

    assert watched.stats() == unwatched.stats()
    assert watched.engine.state == unwatched.engine.state
    unwatched_weights = unwatched.bot.network.state_dict()
    for name, weights in watched.bot.network.state_dict().items():
        assert torch.equal(unwatched_weights[name], weights), name
