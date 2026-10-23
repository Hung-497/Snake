"""Evaluate plays the same games and writes the same report as RunExperiment (ADR 0017)."""

import json

import pytest

from snake.engine.GameConfig import GameConfig
from snake.sessions.EvaluationSession import (
    GAME_COUNTS, STUDY_GAMES, EvaluationGames, start_q_learning_evaluation,
)
from snake.sessions.RunExperiment import main as run_experiment
from snake.sessions.TrainQLearning import main as train_q_learning


# Small games keep the tests quick; the study's own games are checked as constants.
SMALL_GAMES = EvaluationGames(GameConfig(12, 12, 20), base_seed=200000, max_moves=300)


@pytest.fixture
def trained_table(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    table_path = tmp_path / "table.json"
    train_q_learning([
        "--new-table", "--q-table", str(table_path), "--games", "5",
        "--width", "12", "--height", "12", "--max-moves", "300",
    ])
    return table_path


def evaluate(table_path, game_count=3, games=SMALL_GAMES, report_directory=None):
    return start_q_learning_evaluation(
        "q_learning", game_count, table_path=table_path, games=games,
        report_directory=report_directory,
    )


def play_one_move_at_a_time(session):
    while not session.finished:
        session.make_move()


def read_reports(directory):
    return [json.loads(path.read_text()) for path in sorted(directory.glob("*.json"))]


def test_the_study_games_are_the_ones_from_the_results():
    assert STUDY_GAMES.config == GameConfig(24, 25, 25)
    assert STUDY_GAMES.base_seed == 200000
    assert STUDY_GAMES.max_moves == 5000
    assert GAME_COUNTS == (20, 200)


def test_evaluate_plays_the_same_games_as_run_experiment(trained_table, tmp_path):
    session = evaluate(trained_table, report_directory=tmp_path / "app")
    play_one_move_at_a_time(session)

    run_experiment([
        "--bots", "q_learning", "--q-table", str(trained_table), "--games", "3",
        "--seed", "200000", "--width", "12", "--height", "12", "--tile-size", "20",
        "--max-moves", "300",
    ])

    [app_report] = read_reports(tmp_path / "app")
    [command_report] = read_reports(tmp_path / "experiments")
    assert app_report["bots"]["q_learning"]["games"] == command_report["bots"]["q_learning"]["games"]
    assert app_report.keys() >= command_report.keys()
    for key in ("board", "seeds", "base_seed", "max_moves", "bot_seed_offset", "game_count"):
        assert app_report[key] == command_report[key]
    assert app_report["q_learning"]["table_sha256"] == command_report["q_learning"]["table_sha256"]


def test_fast_and_one_move_at_a_time_give_the_same_games(trained_table, tmp_path):
    one_at_a_time = evaluate(trained_table, report_directory=tmp_path / "one")
    play_one_move_at_a_time(one_at_a_time)
    fast = evaluate(trained_table, report_directory=tmp_path / "fast")
    while not fast.finished:
        fast.make_moves_for(10.0)

    [one_report] = read_reports(tmp_path / "one")
    [fast_report] = read_reports(tmp_path / "fast")
    assert one_report["bots"]["q_learning"]["games"] == fast_report["bots"]["q_learning"]["games"]


def test_a_finished_evaluation_writes_one_report_and_says_where(trained_table, tmp_path):
    session = evaluate(trained_table, report_directory=tmp_path / "reports")

    play_one_move_at_a_time(session)
    session.make_move()

    [report_path] = (tmp_path / "reports").glob("*.json")
    assert session.report_path == report_path
    assert read_reports(tmp_path / "reports")[0]["evaluated"] == "app_training"


def test_stopping_early_writes_no_report(trained_table, tmp_path):
    session = evaluate(trained_table, report_directory=tmp_path / "reports")

    for _ in range(5):
        session.make_move()

    assert not session.finished
    assert session.report_path is None
    assert not (tmp_path / "reports").exists()


def test_evaluating_never_changes_the_table(trained_table, tmp_path):
    before = trained_table.read_bytes()

    play_one_move_at_a_time(evaluate(trained_table, report_directory=tmp_path / "reports"))

    assert trained_table.read_bytes() == before


def test_progress_counts_games_average_best_and_move_limits(trained_table, tmp_path):
    # A 3-move limit cuts every game off before the snake can die.
    games = EvaluationGames(GameConfig(12, 12, 20), base_seed=200000, max_moves=3)
    session = evaluate(trained_table, game_count=2, games=games,
                       report_directory=tmp_path / "reports")

    assert session.progress().games_done == 0
    play_one_move_at_a_time(session)

    progress = session.progress()
    [report] = read_reports(tmp_path / "reports")
    scores = [game["score"] for game in report["bots"]["q_learning"]["games"]]
    assert (progress.games_done, progress.game_count) == (2, 2)
    assert progress.move_limits == 2
    assert progress.best_score == max(scores)
    assert progress.average_score == sum(scores) / 2


def test_a_missing_or_broken_table_cannot_be_evaluated(tmp_path):
    with pytest.raises(ValueError):
        evaluate(tmp_path / "missing.json")


def test_a_finished_evaluation_rebuilds_the_local_bot_report(trained_table, tmp_path):
    session = evaluate(trained_table, report_directory=tmp_path / "experiments")
    assert session.bot_report_path is None

    play_one_move_at_a_time(session)

    page = tmp_path / "reports" / "bot_report.html"
    assert session.bot_report_path.resolve() == page.resolve()
    assert "Q Learning v2" in page.read_text(encoding="utf-8")
