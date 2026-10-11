# Loaded by pytest before any test module, so the Arcade PATH guard in the
# snake package runs before a test imports Arcade directly.
import snake  # noqa: F401

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def trained_dqn_run_template(tmp_path_factory):
    """Train one tiny DQN run once; tests that only need a model copy it."""
    pytest.importorskip("torch")
    directory = tmp_path_factory.mktemp("dqn_template")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    trained = subprocess.run(
        [
            sys.executable, "-m", "snake.sessions.TrainDQN", "--games", "2",
            "--width", "4", "--height", "4", "--max-moves", "4",
            "--batch-size", "2", "--seed", "9",
        ],
        cwd=directory, env=environment, capture_output=True, text=True, timeout=120,
    )
    assert trained.returncode == 0, trained.stderr
    (run,) = (directory / "learning_data" / "dqn_runs").iterdir()
    return run


@pytest.fixture
def trained_dqn_run(tmp_path, trained_dqn_run_template):
    """A private copy of the shared run inside this test's own folder."""
    run = tmp_path / "learning_data" / "dqn_runs" / trained_dqn_run_template.name
    shutil.copytree(trained_dqn_run_template, run)
    return run
