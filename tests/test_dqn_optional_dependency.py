"""Ordinary app and experiment imports must not require optional PyTorch."""

import json
import os
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def environment_with_blocked_torch(tmp_path, error_type="AssertionError"):
    blocker = tmp_path / "blocked_dependency"
    blocker.mkdir()
    (blocker / "torch.py").write_text(
        f"raise {error_type}('ordinary Snake code imported optional PyTorch')\n",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join((str(blocker), str(PROJECT_ROOT)))
    return environment


def test_normal_app_import_does_not_require_pytorch(tmp_path):
    result = subprocess.run(
        [sys.executable, "-c", "import SnakeApp"],
        cwd=tmp_path,
        env=environment_with_blocked_torch(tmp_path),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_non_dqn_experiment_runs_when_pytorch_is_unavailable(tmp_path):
    result = subprocess.run(
        [
            sys.executable, "-m", "snake.sessions.RunExperiment",
            "--bots", "rule", "--width", "3", "--height", "3",
            "--max-moves", "2",
        ],
        cwd=tmp_path,
        env=environment_with_blocked_torch(tmp_path),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "experiments").exists()


def test_default_experiment_selection_excludes_dqn_without_pytorch(tmp_path):
    learning_data = tmp_path / "learning_data"
    learning_data.mkdir()
    (learning_data / "q_table_space_state_v2.json").write_text(
        '{"q_table": {}, "epsilon": 0.8, "game_trained": 3}\n'
    )
    result = subprocess.run(
        [
            sys.executable, "-m", "snake.sessions.RunExperiment",
            "--games", "1", "--width", "4", "--height", "4",
            "--max-moves", "2",
        ],
        cwd=tmp_path,
        env=environment_with_blocked_torch(tmp_path),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    report = next((tmp_path / "experiments").glob("*.json"))
    assert json.loads(report.read_text())["selected_bot_modes"] == [
        "rule", "q_learning", "hamiltonian", "search_based",
    ]


def test_explicit_dqn_selection_reports_missing_optional_dependency(tmp_path):
    model = tmp_path / "model.pt"
    model.write_bytes(b"placeholder")
    result = subprocess.run(
        [
            sys.executable, "-m", "snake.sessions.RunExperiment",
            "--bots", "dqn", "--dqn-model", str(model), "--games", "1",
            "--width", "4", "--height", "4", "--max-moves", "2",
        ],
        cwd=tmp_path,
        env=environment_with_blocked_torch(tmp_path, "ImportError"),
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "DQN requires optional PyTorch" in result.stderr
    assert not (tmp_path / "experiments").exists()
