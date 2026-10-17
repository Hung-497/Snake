"""Where each learning Bot Mode saves its app training, and how to start it over.

The Start and Set up training App Views use these for DQN and Q Learning
alike. Nothing here imports PyTorch when the module loads, so the app still
starts without the dqn group (ADR 0007).
"""

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import re
import shutil

from snake.bots.BotModeCatalogue import BOT_MODES, SHOWCASE_DIRECTORY, ShowcaseBot  # noqa: F401


# The game limits a new training can stop at; Off trains until you leave.
TRAINING_LIMITS = {
    "Off": None,
    "1000 games": 1000,
    "2000 games": 2000,
    "5000 games": 5000,
}
# Q Learning in the app trains its own table, so the app never changes the
# table the headless commands use (ADR 0016).
APP_Q_TABLES = {
    mode.key: mode.save_path for mode in BOT_MODES if mode.family == "q_learning"
}
# The headless commands' tables, copied once to start the app's tables.
SHARED_Q_TABLES = {
    mode.key: mode.shared_q_table for mode in BOT_MODES if mode.shared_q_table is not None
}
# Every learning Bot Mode the app trains, and where its training is saved.
SAVE_PATHS = {mode.key: mode.save_path for mode in BOT_MODES if mode.save_path is not None}
# The best of each bot's three Study 1 training runs, by their 200-game
# results in docs/results.md. The app only reads these files.
SHOWCASE_BOTS = {mode.key: mode.showcase for mode in BOT_MODES if mode.showcase is not None}


@dataclass(frozen=True)
class SavedTraining:
    """How far a saved training got, and the game limit it stops at.

    Every field is None when the save cannot be read.
    """

    games: int | None
    best_score: int | None
    game_limit: int | None


@dataclass(frozen=True)
class BackupSummary:
    count: int = 0
    total_bytes: int = 0
    unreadable_count: int = 0


def backup_summary(bot_mode, save_path=None):
    """Count this mode's dated backups and bytes, without loading or deleting them."""
    path = Path(SAVE_PATHS[bot_mode] if save_path is None else save_path)
    pattern = re.compile(
        re.escape(path.stem) + r"_\d{4}-\d{2}-\d{2}_\d{6}(?:_\d+)?" + re.escape(path.suffix)
    )
    count = total_bytes = unreadable_count = 0
    try:
        backups = list(path.parent.glob(f"{path.stem}_*{path.suffix}"))
    except OSError:
        return BackupSummary(unreadable_count=1)
    for backup in backups:
        if not pattern.fullmatch(backup.name):
            continue
        try:
            if not backup.is_file():
                continue
            total_bytes += backup.stat().st_size
            count += 1
        except OSError:
            unreadable_count += 1
    return BackupSummary(count, total_bytes, unreadable_count)


def valid_game_limit(limit):
    """A saved game limit, or None for no limit or a broken value."""
    return limit if type(limit) is int and limit > 0 else None


def saved_training(bot_mode, save_path=None):
    """What this Bot Mode's saved training holds, or None when there is no save.

    A save that cannot be read still counts, with every field unknown, so the
    player can still choose to start over.
    """
    save_path = Path(SAVE_PATHS[bot_mode] if save_path is None else save_path)
    if not save_path.exists():
        return None
    if bot_mode in APP_Q_TABLES:
        return _saved_q_table(save_path)
    return _saved_dqn_checkpoint(save_path)


def _saved_dqn_checkpoint(save_path):
    try:
        from snake.storage.DQNArtifacts import load_artifact
        data = load_artifact(save_path, "dqn_training_checkpoint")
        games = data["state"]["game_trained"]
        scores = data["metadata"].get("live_training_scores")
    except (ImportError, ValueError, KeyError, TypeError):
        return SavedTraining(None, None, None)
    best_score = max(scores) if isinstance(scores, list) and scores else None
    return SavedTraining(games, best_score, valid_game_limit(data["metadata"].get("game_limit")))


def _saved_q_table(save_path):
    try:
        with open(save_path, "r") as file:
            data = json.load(file)
        games = data["game_trained"]
        history = data.get("training_history", [])
        # Each Training History entry keeps its session's best score (ADR 0010).
        best_scores = [entry["best_score"] for entry in history if "best_score" in entry]
        last_entry = history[-1] if history else {}
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return SavedTraining(None, None, None)
    best_score = max(best_scores) if best_scores else None
    return SavedTraining(games, best_score, valid_game_limit(last_entry.get("game_limit")))


def start_over(bot_mode, save_path=None, now=datetime.now):
    """Move this Bot Mode's save aside as a dated backup, so training starts at game 0.

    Returns the backup's path, or None when there was no save. A backup is
    never overwritten, so an earlier long run is not lost by starting over again.
    """
    save_path = Path(SAVE_PATHS[bot_mode] if save_path is None else save_path)
    if not save_path.exists():
        return None
    stamp = now().strftime("%Y-%m-%d_%H%M%S")
    backup_path = save_path.with_name(f"{save_path.stem}_{stamp}{save_path.suffix}")
    copy_number = 2
    while backup_path.exists():
        backup_path = save_path.with_name(
            f"{save_path.stem}_{stamp}_{copy_number}{save_path.suffix}"
        )
        copy_number += 1
    save_path.rename(backup_path)
    return backup_path


def copy_shared_q_table_once(bot_mode, app_path=None, shared_path=None):
    """Start the app's Q-table as a copy of the headless commands' table.

    Copies only the very first time: when neither the app table nor a backup
    of it exists. After starting over, the app table stays empty instead.
    Returns True when it copied.
    """
    if bot_mode not in APP_Q_TABLES:
        return False
    app_path = Path(APP_Q_TABLES[bot_mode] if app_path is None else app_path)
    shared_path = Path(SHARED_Q_TABLES[bot_mode] if shared_path is None else shared_path)
    backups = app_path.parent.glob(f"{app_path.stem}_*{app_path.suffix}")
    if app_path.exists() or not shared_path.exists() or any(backups):
        return False
    app_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(shared_path, app_path)
    return True
