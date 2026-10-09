"""DQN trains and evaluates on Feature Set v3; v2 stays the default (ADR 0009)."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


pytest.importorskip("torch")
import torch
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SMALL_RUN = ("--width", "4", "--height", "4", "--max-moves", "8", "--seed", "7")


def run_module(tmp_path, module, *options):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    return subprocess.run(
        [sys.executable, "-m", module, *options],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )


def train(tmp_path, *options):
    return run_module(tmp_path, "snake.sessions.TrainDQN", *options)


def only_run(tmp_path):
    (run,) = (tmp_path / "learning_data" / "dqn_runs").iterdir()
    return run


def first_layer_inputs(weights):
    return weights["0.weight"].shape[1]


def test_v3_training_saves_twelve_input_artifacts_marked_v3(tmp_path):
    result = train(tmp_path, "--games", "2", "--features", "v3", *SMALL_RUN)

    assert result.returncode == 0, result.stderr
    run = only_run(tmp_path)
    checkpoint = torch.load(run / "checkpoint.pt", weights_only=True)
    model = torch.load(run / "model.pt", weights_only=True)
    for artifact in (checkpoint, model):
        assert artifact["metadata"]["feature_schema"] == "q_learning_space_state_v3"
        assert artifact["metadata"]["dqn_details"]["network"]["input_size"] == 12
    assert first_layer_inputs(model["online_weights"]) == 12
    assert all(len(experience[0]) == 12 for experience in checkpoint["state"]["replay"])


def test_training_without_features_option_stays_v2(tmp_path):
    result = train(tmp_path, "--games", "1", *SMALL_RUN)

    assert result.returncode == 0, result.stderr
    model = torch.load(only_run(tmp_path) / "model.pt", weights_only=True)
    assert model["metadata"]["feature_schema"] == "q_learning_space_state_v2"
    assert first_layer_inputs(model["online_weights"]) == 9


def test_resume_keeps_the_checkpoint_feature_set(tmp_path):
    assert train(tmp_path, "--games", "1", "--features", "v3", *SMALL_RUN).returncode == 0
    source = only_run(tmp_path) / "checkpoint.pt"

    conflict = train(tmp_path, "--resume", str(source), "--games", "1", "--features", "v2")
    resumed = train(tmp_path, "--resume", str(source), "--games", "1")

    assert conflict.returncode != 0
    assert "--features conflicts with the checkpoint" in conflict.stderr
    assert resumed.returncode == 0, resumed.stderr
    runs = list((tmp_path / "learning_data" / "dqn_runs").iterdir())
    assert len(runs) == 2
    for run in runs:
        model = torch.load(run / "model.pt", weights_only=True)
        assert model["metadata"]["feature_schema"] == "q_learning_space_state_v3"


def test_v3_model_is_evaluated_with_v3_features(tmp_path):
    assert train(tmp_path, "--games", "1", "--features", "v3", *SMALL_RUN).returncode == 0
    model_path = str(only_run(tmp_path) / "model.pt")

    evaluation = run_module(
        tmp_path, "snake.sessions.EvaluateDQN", "--model", model_path,
        "--games", "2", "--width", "5", "--height", "5", "--max-moves", "20",
    )
    experiment = run_module(
        tmp_path, "snake.sessions.RunExperiment", "--bots", "dqn",
        "--dqn-model", model_path, "--games", "2", "--width", "5", "--height", "5",
        "--max-moves", "20",
    )

    assert evaluation.returncode == 0, evaluation.stderr
    assert experiment.returncode == 0, experiment.stderr
    for report_path in (tmp_path / "experiments").glob("*.json"):
        report = json.loads(report_path.read_text())
        assert report["dqn"]["feature_schema"] == "q_learning_space_state_v3"


def test_unknown_feature_set_in_a_model_is_rejected(tmp_path):
    assert train(tmp_path, "--games", "1", *SMALL_RUN).returncode == 0
    model_path = only_run(tmp_path) / "model.pt"
    model = torch.load(model_path, weights_only=True)
    model["metadata"]["feature_schema"] = "q_learning_space_state_v9"
    torch.save(model, model_path)

    result = run_module(
        tmp_path, "snake.sessions.EvaluateDQN", "--model", str(model_path),
        "--width", "5", "--height", "5",
    )

    assert result.returncode != 0
    assert "Feature Set" in result.stderr
    assert not (tmp_path / "experiments").exists()
