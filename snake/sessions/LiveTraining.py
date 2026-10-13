"""Open Live Training without making the app need PyTorch.

Nothing here imports PyTorch when the module loads, so the App View can use
it while the app still starts on installs without the dqn group (ADR 0007).
"""

from pathlib import Path


# Live Training keeps its own DQN Training Checkpoint, apart from the
# headless commands' runs.
DEFAULT_CHECKPOINT_PATH = Path("learning_data") / "dqn_live_training.pt"
MISSING_PYTORCH_MESSAGE = (
    "Live Training needs PyTorch, which is not installed.\n"
    "Install it with: uv sync --group dqn"
)


def missing_dependency_message():
    """Return why Live Training cannot start, or None when it can."""
    try:
        import torch  # noqa: F401
    except ImportError:
        return MISSING_PYTORCH_MESSAGE
    return None


class LiveTrainingCheckpointError(ValueError):
    """The saved Live Training cannot continue on this board; the file is kept."""


def start_live_training(settings, checkpoint_path=DEFAULT_CHECKPOINT_PATH):
    """Continue the saved Live Training, or start fresh on the Settings board.

    Raises LiveTrainingCheckpointError when the save does not fit, so it is
    never overwritten by a fresh start.
    """
    from snake.sessions.LiveTrainingSession import PLAYER, LiveTrainingSession
    from snake.storage.RecordManager import RecordManager
    from snake.storage.ReplayManager import ReplayManager

    config = settings.build_game_config()
    # Games are saved as Records with the Settings speed, and the best one as a
    # Replay, like any Play game.
    records = {
        "record_manager": RecordManager(),
        "replay_manager": ReplayManager(),
        "speed_delay": settings.speed_delay_for(PLAYER),
    }
    checkpoint_path = Path(checkpoint_path)
    if checkpoint_path.exists():
        return LiveTrainingSession.load(checkpoint_path, config, **records)
    return LiveTrainingSession(config, checkpoint_path=checkpoint_path, **records)
