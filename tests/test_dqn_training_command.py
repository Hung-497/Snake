"""DQN Training Mode is exercised through its headless command."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


pytest.importorskip("torch")
import torch
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_training(tmp_path, *options):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "snake.sessions.TrainDQN", *options],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )


def read_runs(tmp_path):
    runs = list((tmp_path / "learning_data" / "dqn_runs").iterdir())
    return [(run, json.loads((run / "training.json").read_text())) for run in runs]


def test_fresh_training_saves_progress_checkpoint_and_evaluation_model(tmp_path):
    result = run_training(
        tmp_path, "--games", "2", "--width", "4", "--height", "4",
        "--max-moves", "8", "--seed", "7", "--checkpoint-every", "1",
    )

    assert result.returncode == 0, result.stderr
    runs = list((tmp_path / "learning_data" / "dqn_runs").iterdir())
    assert len(runs) == 1
    run = runs[0]
    assert (run / "checkpoint.pt").exists()
    assert (run / "model.pt").exists()
    record = json.loads((run / "training.json").read_text())
    assert record["game_count"] == 2
    assert [game["seed"] for game in record["games"]] == [7, 8]
    assert all(0 <= game["moves"] <= 8 for game in record["games"])
    assert all(game["outcome"] in {"won", "collision", "move_limit"} for game in record["games"])
    checkpoint = torch.load(run / "checkpoint.pt", weights_only=True)
    model = torch.load(run / "model.pt", weights_only=True)
    assert checkpoint["schema_version"] == model["schema_version"] == 2
    expected_details = {
        "device": "cpu",
        "network": {
            "input_size": 9,
            "hidden_sizes": [64, 64],
            "output_size": 3,
            "activation": "ReLU",
        },
        "optimizer": {"name": "Adam", "learning_rate": 0.001},
        "experience_replay": {
            "capacity": 10000,
            "batch_size": 32,
            "warmup_size": 32,
            "sampling": "uniform",
        },
        "target_network": {"update_interval_optimizer_steps": 100},
    }
    assert record["dqn_details"] == expected_details
    assert checkpoint["metadata"]["dqn_details"] == expected_details
    assert model["metadata"]["dqn_details"] == expected_details
    assert set(checkpoint["state"]) == {
        "online_weights", "target_weights", "optimizer", "epsilon",
        "game_trained", "optimizer_steps", "replay", "engine_random_state",
        "bot_random_state", "replay_random_state", "torch_random_state",
    }


def test_fresh_runs_are_unique_and_reproduce_fixed_seed_games(tmp_path):
    options = (
        "--games", "2", "--width", "4", "--height", "4",
        "--max-moves", "8", "--seed", "13", "--batch-size", "2",
    )

    first = run_training(tmp_path, *options)
    second = run_training(tmp_path, *options)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    runs = read_runs(tmp_path)
    assert len(runs) == 2
    assert runs[0][0].name != runs[1][0].name
    assert runs[0][1]["run_id"] != runs[1][1]["run_id"]
    assert runs[0][1]["games"] == runs[1][1]["games"]


def test_periodic_checkpoint_exists_before_an_interrupted_run_can_export_model(tmp_path):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    process = subprocess.Popen(
        [
            sys.executable, "-m", "snake.sessions.TrainDQN",
            "--games", "1000", "--width", "4", "--height", "4",
            "--max-moves", "8", "--seed", "17", "--batch-size", "2",
            "--checkpoint-every", "1",
        ],
        cwd=tmp_path,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    saw_periodic_save = False
    try:
        for line in process.stdout:
            if "DQN game 1/1000:" in line:
                saw_periodic_save = True
                process.terminate()
                break
        process.wait(timeout=10)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)

    assert saw_periodic_save, process.stderr.read()
    runs = list((tmp_path / "learning_data" / "dqn_runs").iterdir())
    assert len(runs) == 1
    assert (runs[0] / "checkpoint.pt").exists()
    assert not (runs[0] / "model.pt").exists()
    checkpoint = torch.load(runs[0] / "checkpoint.pt", weights_only=True)
    assert checkpoint["state"]["game_trained"] >= 1


def test_resume_matches_uninterrupted_training_and_keeps_source_unchanged(tmp_path):
    shared = ("--width", "4", "--height", "4", "--max-moves", "8",
              "--seed", "11", "--batch-size", "2", "--checkpoint-every", "1")
    full_dir = tmp_path / "full"
    split_dir = tmp_path / "split"
    full_dir.mkdir()
    split_dir.mkdir()

    full = run_training(full_dir, "--games", "4", *shared)
    first = run_training(split_dir, "--games", "2", *shared)
    assert full.returncode == 0, full.stderr
    assert first.returncode == 0, first.stderr
    source = next((split_dir / "learning_data" / "dqn_runs").iterdir()) / "checkpoint.pt"
    source_bytes = source.read_bytes()
    resumed = run_training(split_dir, "--resume", str(source), "--games", "2")
    assert resumed.returncode == 0, resumed.stderr
    assert source.read_bytes() == source_bytes

    full_run = next((full_dir / "learning_data" / "dqn_runs").iterdir())
    split_runs = list((split_dir / "learning_data" / "dqn_runs").iterdir())
    assert len(split_runs) == 2
    resumed_run = next(path for path in split_runs if path != source.parent)
    full_record = json.loads((full_run / "training.json").read_text())
    first_record = json.loads((source.parent / "training.json").read_text())
    resumed_record = json.loads((resumed_run / "training.json").read_text())
    assert resumed_record["source_checkpoint"] == str(source)
    assert resumed_record["starting_game_count"] == 2
    assert resumed_record["game_count"] == 4
    assert full_record["games"] == first_record["games"] + resumed_record["games"]

    full_checkpoint = torch.load(full_run / "checkpoint.pt", weights_only=True)
    resumed_checkpoint = torch.load(resumed_run / "checkpoint.pt", weights_only=True)
    for name in full_checkpoint["state"]["online_weights"]:
        assert torch.equal(
            full_checkpoint["state"]["online_weights"][name],
            resumed_checkpoint["state"]["online_weights"][name],
        )
    assert full_checkpoint["state"]["epsilon"] == resumed_checkpoint["state"]["epsilon"]
    assert full_checkpoint["state"]["optimizer_steps"] == resumed_checkpoint["state"]["optimizer_steps"]


def test_resume_rejects_incomplete_checkpoint_before_creating_a_run(tmp_path):
    trained = run_training(
        tmp_path, "--games", "1", "--width", "4", "--height", "4",
        "--max-moves", "4",
    )
    assert trained.returncode == 0, trained.stderr
    runs = tmp_path / "learning_data" / "dqn_runs"
    checkpoint_path = next(runs.iterdir()) / "checkpoint.pt"
    checkpoint = torch.load(checkpoint_path, weights_only=True)
    del checkpoint["state"]["replay_random_state"]
    invalid_path = tmp_path / "incomplete.pt"
    torch.save(checkpoint, invalid_path)

    resumed = run_training(tmp_path, "--resume", str(invalid_path), "--games", "1")
    assert resumed.returncode != 0
    assert "Invalid DQN checkpoint" in resumed.stderr
    assert len(list(runs.iterdir())) == 1


def test_versioned_checkpoint_validation_rejects_metadata_and_shape_changes(tmp_path):
    trained = run_training(
        tmp_path, "--games", "1", "--width", "4", "--height", "4",
        "--max-moves", "4",
    )
    assert trained.returncode == 0, trained.stderr
    runs = tmp_path / "learning_data" / "dqn_runs"
    source = next(runs.iterdir()) / "checkpoint.pt"

    unsupported = torch.load(source, weights_only=True)
    unsupported["schema_version"] = 999
    unsupported_path = tmp_path / "unsupported.pt"
    torch.save(unsupported, unsupported_path)

    missing_details = torch.load(source, weights_only=True)
    del missing_details["metadata"]["dqn_details"]
    missing_details_path = tmp_path / "missing_details.pt"
    torch.save(missing_details, missing_details_path)

    wrong_shape = torch.load(source, weights_only=True)
    wrong_shape["state"]["online_weights"]["0.weight"] = (
        wrong_shape["state"]["online_weights"]["0.weight"][:, :8]
    )
    wrong_shape_path = tmp_path / "wrong_shape.pt"
    torch.save(wrong_shape, wrong_shape_path)

    cases = (
        (unsupported_path, "Unsupported DQN artifact version"),
        (missing_details_path, "Invalid DQN architecture or training details"),
        (wrong_shape_path, "Invalid DQN network weights"),
    )
    for artifact_path, expected_error in cases:
        resumed = run_training(
            tmp_path, "--resume", str(artifact_path), "--games", "1"
        )
        assert resumed.returncode != 0
        assert expected_error in resumed.stderr

    assert len(list(runs.iterdir())) == 1


def test_training_rejects_a_board_without_food_before_creating_a_run(tmp_path):
    result = run_training(
        tmp_path, "--games", "1", "--width", "1", "--height", "1",
    )
    assert result.returncode != 0
    assert "at least two cells" in result.stderr
    assert not (tmp_path / "learning_data").exists()


def test_training_rejects_invalid_replay_settings_before_creating_a_run(tmp_path):
    result = run_training(
        tmp_path, "--games", "1", "--width", "4", "--height", "4",
        "--batch-size", "10001",
    )

    assert result.returncode != 0
    assert "cannot exceed replay capacity" in result.stderr
    assert not (tmp_path / "learning_data").exists()
