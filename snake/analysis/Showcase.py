"""Choose the runs that belong in the committed Showcase Report (ADR 0020).

Only full study evaluations count: the study's board, move limit, and all 200
seeds. A learning run counts only when its bot file is the shipped Showcase
Bot, checked by hash, and the non-learning Bot Modes join as Baselines.
"""

import hashlib
from pathlib import Path

from snake.analysis.ExperimentRuns import ExperimentConditions
from snake.bots.BotModeCatalogue import BOT_MODES
from snake.sessions.EvaluationSession import GAME_COUNTS, STUDY_GAMES


STUDY_CONDITIONS = ExperimentConditions(
    STUDY_GAMES.config.width,
    STUDY_GAMES.config.height,
    STUDY_GAMES.max_moves,
    tuple(range(STUDY_GAMES.base_seed, STUDY_GAMES.base_seed + max(GAME_COUNTS))),
)
BASELINE_BOT_MODES = tuple(mode for mode in BOT_MODES if mode.family is None)
SHOWCASE_BOT_MODES = tuple(mode for mode in BOT_MODES if mode.showcase is not None)


def file_sha256(path):
    """The hash of a shipped file, or None when it is missing."""
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def select_showcase_runs(runs):
    """Return the qualifying runs and labels of those with no study run yet."""
    showcase_hashes = {
        mode.key: file_sha256(mode.showcase.path) for mode in SHOWCASE_BOT_MODES
    }
    baseline_keys = {mode.key for mode in BASELINE_BOT_MODES}
    selected = []
    for run in runs:
        if run.conditions != STUDY_CONDITIONS:
            continue
        if run.bot_mode in baseline_keys:
            selected.append(run)
        elif run.bot_file is not None and run.bot_file.sha256 in showcase_hashes.values():
            selected.append(run)

    found_hashes = {run.bot_file.sha256 for run in selected if run.bot_file}
    found_baselines = {run.bot_mode for run in selected}
    not_evaluated = [
        f"{mode.label} Showcase Bot ({mode.showcase.label})"
        for mode in SHOWCASE_BOT_MODES
        if showcase_hashes[mode.key] is None or showcase_hashes[mode.key] not in found_hashes
    ]
    not_evaluated += [
        f"{mode.label} Baseline"
        for mode in BASELINE_BOT_MODES if mode.key not in found_baselines
    ]
    return selected, tuple(not_evaluated)
