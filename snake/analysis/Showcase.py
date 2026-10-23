"""Choose the runs that belong in the committed Showcase Report (ADR 0020).

Only full study evaluations count: the study's board, move limit, and all 200
seeds. A learning run counts only when its bot file is the shipped Showcase
Bot, checked by hash, and the non-learning Bot Modes join as Baselines.
"""

from dataclasses import replace
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


def file_hashes(path):
    """Every hash a run of this shipped file may report; empty when it is missing.

    Git on Windows may check out a JSON Q-table with CRLF line endings, which
    changes its bytes but not its table, so both line endings count. A DQN
    model is binary and is only ever its own hash.
    """
    try:
        content = Path(path).read_bytes()
    except OSError:
        return set()
    versions = {content}
    if Path(path).suffix == ".json":
        unix = content.replace(b"\r\n", b"\n")
        versions |= {unix, unix.replace(b"\n", b"\r\n")}
    return {hashlib.sha256(version).hexdigest() for version in versions}


def select_showcase_runs(runs):
    """Return the qualifying runs and labels of those with no study run yet."""
    showcase_hashes = {
        mode.key: file_hashes(mode.showcase.path) for mode in SHOWCASE_BOT_MODES
    }
    modes_by_hash = {
        sha: mode for mode in SHOWCASE_BOT_MODES for sha in showcase_hashes[mode.key]
    }
    baseline_keys = {mode.key for mode in BASELINE_BOT_MODES}
    selected = []
    for run in runs:
        if run.conditions != STUDY_CONDITIONS:
            continue
        if run.bot_mode in baseline_keys:
            selected.append(run)
        elif run.bot_file is not None and run.bot_file.sha256 in modes_by_hash:
            selected.append(with_showcase_seed(run, modes_by_hash[run.bot_file.sha256]))

    found_hashes = {run.bot_file.sha256 for run in selected if run.bot_file}
    found_baselines = {run.bot_mode for run in selected}
    not_evaluated = [
        f"{mode.label} Showcase Bot ({mode.showcase.label})"
        for mode in SHOWCASE_BOT_MODES if not showcase_hashes[mode.key] & found_hashes
    ]
    not_evaluated += [
        f"{mode.label} Baseline"
        for mode in BASELINE_BOT_MODES if mode.key not in found_baselines
    ]
    return selected, tuple(not_evaluated)


def with_showcase_seed(run, mode):
    """Older reports did not record a table's training seed; the catalogue does."""
    if run.bot_file.training_seeds:
        return run
    return replace(run, bot_file=replace(run.bot_file, training_seeds=(mode.showcase.seed,)))
