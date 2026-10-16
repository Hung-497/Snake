"""Open Live Training without making the app need PyTorch.

Nothing here imports PyTorch when the module loads, so the App View can use
it while the app still starts on installs without the dqn group (ADR 0007).
"""

from dataclasses import dataclass
from datetime import datetime
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


@dataclass(frozen=True)
class SavedTraining:
    """How far a saved Live Training got; both are None when the save cannot be read."""

    games: int | None
    best_score: int | None


class LiveTrainingCheckpointError(ValueError):
    """The saved Live Training cannot be read or is for another Feature Set; the file is kept."""


def start_live_training(settings, bot_mode="dqn", checkpoint_path=None):
    """Continue this DQN's saved Live Training, or start fresh on the Settings board.

    Raises LiveTrainingCheckpointError when the save does not fit, so it is
    never overwritten by a fresh start.
    """
    from snake.sessions.LiveTrainingSession import LiveTrainingSession
    from snake.storage.RecordManager import RecordManager
    from snake.storage.ReplayManager import ReplayManager

    config = settings.build_game_config()
    # Games are saved as Records with the Settings speed, and the best one as a
    # Replay, like any Play game.
    records = {
        "record_manager": RecordManager(),
        "replay_manager": ReplayManager(),
        "speed_delay": settings.speed_delay_for(bot_mode),
        "player": bot_mode,
    }
    if checkpoint_path is None:
        checkpoint_path = DQN_VERSIONS[bot_mode].checkpoint_path
    checkpoint_path = Path(checkpoint_path)
    if checkpoint_path.exists():
        return LiveTrainingSession.load(checkpoint_path, config, **records)
    return LiveTrainingSession(config, checkpoint_path=checkpoint_path, **records)


def saved_training(bot_mode, checkpoint_path=None):
    """What this DQN's saved Live Training holds, or None when there is no save.

    A save that cannot be read still counts, with unknown games and best
    score, so the player can still choose to start over.
    """
    if checkpoint_path is None:
        checkpoint_path = DQN_VERSIONS[bot_mode].checkpoint_path
    checkpoint_path = Path(checkpoint_path)
    if not checkpoint_path.exists():
        return None
    try:
        from snake.storage.DQNArtifacts import load_artifact
        data = load_artifact(checkpoint_path, "dqn_training_checkpoint")
        games = data["state"]["game_trained"]
        scores = data["metadata"].get("live_training_scores")
    except (ImportError, ValueError, KeyError, TypeError):
        return SavedTraining(None, None)
    best_score = max(scores) if isinstance(scores, list) and scores else None
    return SavedTraining(games, best_score)


def start_over(bot_mode, checkpoint_path=None, now=datetime.now):
    """Move this DQN's save aside as a dated backup, so Live Training starts at game 0.

    Returns the backup's path, or None when there was no save. A backup is
    never overwritten, so an earlier long run is not lost by starting over again.
    """
    if checkpoint_path is None:
        checkpoint_path = DQN_VERSIONS[bot_mode].checkpoint_path
    checkpoint_path = Path(checkpoint_path)
    if not checkpoint_path.exists():
        return None
    stamp = now().strftime("%Y-%m-%d_%H%M%S")
    backup_path = checkpoint_path.with_name(f"{checkpoint_path.stem}_{stamp}{checkpoint_path.suffix}")
    copy_number = 2
    while backup_path.exists():
        backup_path = checkpoint_path.with_name(
            f"{checkpoint_path.stem}_{stamp}_{copy_number}{checkpoint_path.suffix}"
        )
        copy_number += 1
    checkpoint_path.rename(backup_path)
    return backup_path
