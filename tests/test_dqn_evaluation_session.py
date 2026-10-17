"""Evaluate measures a DQN's Live Training exactly like RunExperiment (ADR 0017)."""

import json

import pytest


pytest.importorskip("torch")

from snake.engine.GameConfig import GameConfig
from snake.sessions.EvaluationSession import EvaluationGames, start_dqn_evaluation
from snake.sessions.LiveTrainingSession import LiveTrainingSession
from snake.sessions.RunExperiment import main as run_experiment
from snake.storage.DQNArtifacts import evaluation_model_data, save_torch_data


SMALL_GAMES = EvaluationGames(GameConfig(10, 10, 20), base_seed=200000, max_moves=200)


def trained_checkpoint(tmp_path, player="dqn"):
    """A short Live Training save, and an evaluation model with the same weights."""
    checkpoint_path = tmp_path / "live.pt"
    session = LiveTrainingSession(
        GameConfig(10, 10, 20), seed=7, max_moves=200,
        checkpoint_path=checkpoint_path, player=player,
    )
    while session.stats().games_played < 3:
        session.make_move()
    session.save()
    model_path = tmp_path / "model.pt"
    save_torch_data(
        model_path, evaluation_model_data(session.bot, _saved_metadata(checkpoint_path))
    )
    return checkpoint_path, model_path


def _saved_metadata(checkpoint_path):
    from snake.storage.DQNArtifacts import load_artifact
    return load_artifact(checkpoint_path, "dqn_training_checkpoint")["metadata"]


def evaluate(checkpoint_path, report_directory, bot_mode="dqn", game_count=3):
    session = start_dqn_evaluation(
        bot_mode, game_count, model_path=checkpoint_path, games=SMALL_GAMES,
        report_directory=report_directory,
    )
    while not session.finished:
        session.make_move()
    return session


def read_report(directory):
    [path] = directory.glob("*.json")
    return json.loads(path.read_text())


def test_evaluate_plays_the_same_games_as_run_experiment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    checkpoint_path, model_path = trained_checkpoint(tmp_path)

    evaluate(checkpoint_path, tmp_path / "app")
    run_experiment([
        "--bots", "dqn", "--dqn-model", str(model_path), "--games", "3",
        "--seed", "200000", "--width", "10", "--height", "10", "--tile-size", "20",
        "--max-moves", "200",
    ])

    app_report = read_report(tmp_path / "app")
    command_report = read_report(tmp_path / "experiments")
    assert app_report["bots"]["dqn"]["games"] == command_report["bots"]["dqn"]["games"]


def test_the_report_identifies_the_evaluated_checkpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    checkpoint_path, _ = trained_checkpoint(tmp_path)

    evaluate(checkpoint_path, tmp_path / "app")

    report = read_report(tmp_path / "app")
    identity = report["dqn"]
    assert report["evaluated"] == "app_training"
    assert identity["feature_set"] == "v3"
    assert identity["game_trained"] == 3
    assert identity["model_path"] == str(checkpoint_path)
    assert len(identity["model_sha256"]) == 64
    assert report["evaluation_board"] == report["board"]
    assert report["training_board"]["width"] == 10


def test_evaluating_never_changes_the_checkpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    checkpoint_path, _ = trained_checkpoint(tmp_path)
    before = checkpoint_path.read_bytes()

    evaluate(checkpoint_path, tmp_path / "app")

    assert checkpoint_path.read_bytes() == before


def test_report_omits_score_history_but_checkpoint_keeps_it(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    checkpoint_path, _ = trained_checkpoint(tmp_path)
    before = _saved_metadata(checkpoint_path)
    assert before["live_training_scores"]

    evaluate(checkpoint_path, tmp_path / "app")

    identity = read_report(tmp_path / "app")["dqn"]
    assert "live_training_scores" not in identity
    for field in ("base_seed", "learning_settings", "feature_schema", "run_id"):
        assert identity[field] == before[field]
    assert _saved_metadata(checkpoint_path) == before


def test_dqn_v2_evaluates_its_own_feature_set(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    checkpoint_path, _ = trained_checkpoint(tmp_path, player="dqn_v2")

    evaluate(checkpoint_path, tmp_path / "app", bot_mode="dqn_v2")

    assert read_report(tmp_path / "app")["dqn_v2"]["feature_set"] == "v2"


def test_a_save_for_the_other_dqn_version_is_refused(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    checkpoint_path, _ = trained_checkpoint(tmp_path, player="dqn_v2")

    with pytest.raises(ValueError):
        evaluate(checkpoint_path, tmp_path / "app", bot_mode="dqn")


def test_a_missing_checkpoint_cannot_be_evaluated(tmp_path):
    with pytest.raises(ValueError):
        evaluate(tmp_path / "missing.pt", tmp_path / "app")
