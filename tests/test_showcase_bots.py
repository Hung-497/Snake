"""Showcase Bots: finished study bots shipped read-only with the app (ADR 0017)."""

import hashlib
import json
import random
from pathlib import Path

import pytest

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.sessions.EvaluationSession import EvaluationGames, start_q_learning_evaluation
from snake.sessions.ExperimentReport import make_engine
from snake.sessions.TrainingSaves import SAVE_PATHS, SHOWCASE_BOTS
from snake.sessions.TrainQLearning import FEATURE_SET_BY_BOT_MODE


PROJECT_ROOT = Path(__file__).resolve().parents[1]
Q_LEARNING_MODES = ("q_learning", "q_learning_v3")


def showcase_file(bot_mode):
    return PROJECT_ROOT / SHOWCASE_BOTS[bot_mode].path


@pytest.mark.parametrize("bot_mode", Q_LEARNING_MODES)
def test_every_q_learning_bot_mode_ships_a_showcase_bot(bot_mode):
    assert showcase_file(bot_mode).is_file()


@pytest.mark.parametrize("bot_mode", Q_LEARNING_MODES)
def test_a_q_learning_showcase_bot_loads_in_evaluation_mode_with_its_feature_set(bot_mode):
    feature_set = FEATURE_SET_BY_BOT_MODE[bot_mode]

    bot = QLearningBot(
        make_engine(GameConfig(24, 25, 25), 0), random_source=random.Random(1),
        evaluation_mode=True, q_table_file=str(showcase_file(bot_mode)), feature_set=feature_set,
    )

    assert bot.feature_set == feature_set
    assert bot.game_trained == 2000


def test_each_showcase_bot_is_labelled_as_the_best_of_three_study_runs():
    assert SHOWCASE_BOTS["q_learning"].label == "Best of 3 study runs (seed 12000)"
    assert SHOWCASE_BOTS["q_learning_v3"].label == "Best of 3 study runs (seed 15000)"


def test_showcase_bots_live_apart_from_every_training_save():
    showcase_folders = {Path(bot.path).parent for bot in SHOWCASE_BOTS.values()}

    assert showcase_folders == {Path("starter_data") / "showcase"}
    assert not {Path(path) for path in SAVE_PATHS.values()} & {
        Path(bot.path) for bot in SHOWCASE_BOTS.values()
    }


def test_evaluating_a_showcase_bot_never_changes_it_and_says_so(tmp_path):
    path = showcase_file("q_learning")
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    session = start_q_learning_evaluation(
        "q_learning", 2, table_path=path, evaluated="showcase",
        games=EvaluationGames(GameConfig(12, 12, 20), base_seed=200000, max_moves=200),
        report_directory=tmp_path,
    )
    while not session.finished:
        session.make_move()

    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
    [report_path] = tmp_path.glob("*.json")
    assert json.loads(report_path.read_text())["evaluated"] == "showcase"
