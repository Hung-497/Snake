"""Open Live Training without making the app need PyTorch.

Nothing here imports PyTorch when the module loads, so the App View can use
it while the app still starts on installs without the dqn group (ADR 0007).
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DQNVersion:
    """What one DQN Bot Mode sees, and where its Live Training is saved."""

    feature_set: str
    checkpoint_path: Path


# Each DQN Bot Mode keeps its own DQN Training Checkpoint, apart from the
# headless commands' runs and from the other version (ADR 0013).
DQN_VERSIONS = {
    "dqn": DQNVersion("v3", Path("learning_data") / "dqn_live_training.pt"),
    "dqn_v2": DQNVersion("v2", Path("learning_data") / "dqn_v2_live_training.pt"),
}
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
    """The saved Live Training cannot be read or is for another Feature Set; the file is kept."""


def start_live_training(settings, bot_mode="dqn", checkpoint_path=None, game_limit=None):
    """Continue this DQN's saved Live Training, or start fresh on the Settings board.

    A fresh start stops at game_limit; a continued one keeps its saved limit.

    Raises LiveTrainingCheckpointError when the save does not fit, so it is
    never overwritten by a fresh start.
    """
    from snake.sessions.LiveTrainingSession import LiveTrainingSession
    from snake.storage.RecordManager import RecordManager
    from snake.storage.ReplayManager import ReplayManager

    config = settings.build_game_config()
    # Games are saved as Records with the Settings speed, and the best one as a
    # Replay, like any Play game.
    session_options = {
        "record_manager": RecordManager(),
        "replay_manager": ReplayManager(),
        "speed_delay": settings.speed_delay_for(bot_mode),
        "player": bot_mode,
    }
    if checkpoint_path is None:
        checkpoint_path = DQN_VERSIONS[bot_mode].checkpoint_path
    checkpoint_path = Path(checkpoint_path)
    if checkpoint_path.exists():
        return LiveTrainingSession.load(checkpoint_path, config, **session_options)
    return LiveTrainingSession(
        config, checkpoint_path=checkpoint_path, game_limit=game_limit, **session_options
    )

