"""The Bot Experiment command is tested through its terminal interface."""

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

import pytest

from snake.bots.BotFactory import normal_experiment_modes


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_experiment(tmp_path, *options):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "snake.sessions.RunExperiment", *options],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )


def test_explicit_rule_only_experiment_needs_no_q_table(tmp_path):
    result = run_experiment(
        tmp_path, "--bots", "rule", "--width", "3", "--height", "3",
        "--max-moves", "5",
    )

    assert result.returncode == 0, result.stderr
    report_path = next((tmp_path / "experiments").glob("*.json"))
    report = json.loads(report_path.read_text())
    assert report["schema_version"] == 3
    assert report["selected_bot_modes"] == ["rule"]
    assert set(report["bots"]) == {"rule"}
    assert "q_learning" not in report
    assert not (tmp_path / "learning_data").exists()


def test_search_based_only_experiment_runs_without_other_bot_requirements(tmp_path):
    result = run_experiment(
        tmp_path, "--bots", "search_based", "--width", "3", "--height", "3",
        "--games", "2", "--seed", "7", "--max-moves", "5",
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(next((tmp_path / "experiments").glob("*.json")).read_text())
    assert report["selected_bot_modes"] == ["search_based"]
    assert list(report["bots"]) == ["search_based"]
    assert [game["seed"] for game in report["bots"]["search_based"]["games"]] == [7, 8]
    assert "mean_score" in report["bots"]["search_based"]["summary"]
    assert "Search-Based:" in result.stdout
    assert "Search-Based game 1/2:" in result.stdout
    assert "q_learning" not in report
    assert not (tmp_path / "learning_data").exists()
    assert not (tmp_path / "records").exists()
    assert not (tmp_path / "replays").exists()


def test_search_based_reaches_distant_food_instead_of_circling_until_move_limit(tmp_path):
    result = run_experiment(
        tmp_path, "--bots", "search_based", "--width", "24", "--height", "25",
        "--games", "1", "--seed", "7", "--max-moves", "120",
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(next((tmp_path / "experiments").glob("*.json")).read_text())
    assert report["bots"]["search_based"]["games"][0]["score"] >= 2


def test_search_based_does_not_repeat_a_survival_loop_on_another_seed(tmp_path):
    result = run_experiment(
        tmp_path, "--bots", "search_based", "--width", "24", "--height", "25",
        "--games", "1", "--seed", "14", "--max-moves", "120",
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(next((tmp_path / "experiments").glob("*.json")).read_text())
    assert report["bots"]["search_based"]["games"][0]["score"] >= 6


def test_selected_bots_share_seeds_and_keep_the_requested_order(tmp_path):
    result = run_experiment(
        tmp_path, "--bots", "hamiltonian", "rule", "--games", "2",
        "--width", "4", "--height", "4", "--seed", "7", "--max-moves", "5",
    )

    assert result.returncode == 0, result.stderr
    report_path = next((tmp_path / "experiments").glob("*.json"))
    report = json.loads(report_path.read_text())
    assert report["selected_bot_modes"] == ["hamiltonian", "rule"]
    assert list(report["bots"]) == ["hamiltonian", "rule"]
    for bot in report["bots"].values():
        assert [game["seed"] for game in bot["games"]] == [7, 8]


@pytest.mark.parametrize("selection,error_text", [
    (("hamiltonian",), "Hamiltonian"),
    (("q_learning",), "Q-table"),
    (("unknown",), "invalid choice"),
    (("rule", "rule"), "must not repeat"),
])
def test_invalid_selected_comparison_stops_before_any_report(
    tmp_path, selection, error_text,
):
    result = run_experiment(
        tmp_path, "--bots", *selection, "--width", "3", "--height", "3",
        "--max-moves", "5",
    )

    assert result.returncode != 0
    assert error_text in result.stderr
    assert not (tmp_path / "experiments").exists()


def test_one_game_experiment_saves_result_without_changing_game_data(tmp_path):
    learning_directory = tmp_path / "learning_data"
    learning_directory.mkdir()
    table_path = learning_directory / "q_table_space_state_v2.json"
    original_table = json.dumps({
        "q_table": {}, "epsilon": 0.8, "game_trained": 3,
    })
    table_path.write_text(original_table)

    records_directory = tmp_path / "records"
    records_directory.mkdir()
    record_path = records_directory / "game_records.csv"
    record_path.write_text("existing game records\n")
    replays_directory = tmp_path / "replays"
    replays_directory.mkdir()
    replay_path = replays_directory / "rule_best.json"
    replay_path.write_text("existing replay\n")

    result = run_experiment(
        tmp_path, "--width", "4", "--height", "4",
        "--seed", "7", "--max-moves", "20",
    )

    assert result.returncode == 0, result.stderr
    result_paths = list((tmp_path / "experiments").glob("*.json"))
    assert len(result_paths) == 1
    saved = json.loads(result_paths[0].read_text())
    assert saved["schema_version"] == 3
    assert saved["board"] == {"width": 4, "height": 4, "tile_size": 25}
    assert saved["game_count"] == 1
    assert saved["base_seed"] == 7
    assert saved["seeds"] == [7]
    assert saved["max_moves"] == 20
    assert saved["selected_bot_modes"] == list(normal_experiment_modes())
    assert set(saved["bots"]) == {"rule", "q_learning", "hamiltonian", "search_based"}
    for bot_result in saved["bots"].values():
        assert len(bot_result["games"]) == 1
        game = bot_result["games"][0]
        assert type(game["score"]) is int
        assert 0 <= game["moves"] <= 20
        assert game["outcome"] in {"won", "collision", "move_limit"}
    assert str(result_paths[0].relative_to(tmp_path)) in result.stdout
    assert table_path.read_text() == original_table
    assert record_path.read_text() == "existing game records\n"
    assert replay_path.read_text() == "existing replay\n"


@pytest.mark.parametrize("contents", [None, "not json", json.dumps({"q_table": []})])
def test_experiment_rejects_missing_or_malformed_selected_table(tmp_path, contents):
    table_path = tmp_path / "selected_table.json"
    if contents is not None:
        table_path.write_text(contents)

    result = run_experiment(
        tmp_path, "--width", "4", "--height", "4",
        "--max-moves", "5", "--q-table", str(table_path),
    )

    assert result.returncode != 0
    assert "Q-table" in result.stderr
    assert not (tmp_path / "experiments").exists()
    if contents is None:
        assert not table_path.exists()
    else:
        assert table_path.read_text() == contents


@pytest.mark.parametrize("board", [("3", "3"), ("1", "4")])
def test_unsupported_board_is_rejected_before_result_creation(tmp_path, board):
    result = run_experiment(
        tmp_path, "--width", board[0], "--height", board[1],
        "--max-moves", "5",
    )

    assert result.returncode != 0
    assert "Hamiltonian" in result.stderr
    assert not (tmp_path / "experiments").exists()


@pytest.mark.parametrize("option", ["--width", "--height", "--tile-size", "--max-moves"])
def test_invalid_board_or_move_limit_is_rejected(tmp_path, option):
    result = run_experiment(tmp_path, option, "0")

    assert result.returncode != 0
    assert "positive integer" in result.stderr
    assert not (tmp_path / "experiments").exists()


def test_invalid_game_count_is_rejected_without_writing_a_result(tmp_path):
    result = run_experiment(tmp_path, "--games", "0")

    assert result.returncode != 0
    assert "--games must be a positive integer" in result.stderr
    assert not (tmp_path / "experiments").exists()


def test_repeated_experiments_keep_both_results(tmp_path):
    table_path = tmp_path / "selected_table.json"
    table_path.write_text(json.dumps({
        "q_table": {}, "epsilon": 1.0, "game_trained": 2,
    }))
    options = (
        "--games", "3", "--width", "4", "--height", "4", "--seed", "7", "--max-moves", "5",
        "--q-table", str(table_path),
    )

    first = run_experiment(tmp_path, *options)
    second = run_experiment(tmp_path, *options)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    result_paths = list((tmp_path / "experiments").glob("*.json"))
    assert len(result_paths) == 2
    first_report = json.loads(result_paths[0].read_text())
    second_report = json.loads(result_paths[1].read_text())
    assert first_report["seeds"] == second_report["seeds"] == [7, 8, 9]
    for bot_mode in ("rule", "q_learning", "hamiltonian", "search_based"):
        assert first_report["bots"][bot_mode]["games"] == second_report["bots"][bot_mode]["games"]
    assert not (tmp_path / "learning_data").exists()


def test_multiple_games_use_the_same_seed_list_for_every_bot(tmp_path):
    table_path = tmp_path / "selected_table.json"
    original_table = json.dumps({
        "q_table": {}, "epsilon": 0.8, "game_trained": 3,
    })
    table_path.write_text(original_table)
    records = tmp_path / "records"
    records.mkdir()
    (records / "game_records.csv").write_text("watched games\n")
    replays = tmp_path / "replays"
    replays.mkdir()
    (replays / "best.json").write_text("watched replay\n")

    result = run_experiment(
        tmp_path, "--games", "3", "--seed", "7", "--width", "4",
        "--height", "4", "--max-moves", "2", "--q-table", str(table_path),
    )

    assert result.returncode == 0, result.stderr
    report_path = next((tmp_path / "experiments").glob("*.json"))
    report = json.loads(report_path.read_text())
    assert report["game_count"] == 3
    assert report["base_seed"] == 7
    assert report["seeds"] == [7, 8, 9]
    assert report["bot_seed_offset"] == 1
    for bot in report["bots"].values():
        assert [game["seed"] for game in bot["games"]] == [7, 8, 9]
        assert all(0 <= game["moves"] <= 2 for game in bot["games"])
        assert all(game["outcome"] in {"won", "collision", "move_limit"} for game in bot["games"])
    assert table_path.read_text() == original_table
    assert (records / "game_records.csv").read_text() == "watched games\n"
    assert (replays / "best.json").read_text() == "watched replay\n"


def test_report_summarizes_known_games_and_identifies_the_workload(tmp_path):
    table_path = tmp_path / "selected_table.json"
    original_table = json.dumps({
        "q_table": {}, "epsilon": 0.8, "game_trained": 3,
    })
    table_path.write_text(original_table)

    result = run_experiment(
        tmp_path, "--games", "3", "--seed", "7", "--width", "4",
        "--height", "4", "--max-moves", "2", "--q-table", str(table_path),
    )

    assert result.returncode == 0, result.stderr
    report_path = next((tmp_path / "experiments").glob("*.json"))
    report = json.loads(report_path.read_text())
    assert [game["score"] for game in report["bots"]["rule"]["games"]] == [1, 1, 0]
    assert [game["score"] for game in report["bots"]["q_learning"]["games"]] == [1, 0, 0]
    assert [game["score"] for game in report["bots"]["hamiltonian"]["games"]] == [1, 1, 0]

    summary = report["bots"]["rule"]["summary"]
    assert summary["mean_score"] == pytest.approx(2 / 3)
    assert summary["median_score"] == 1
    assert summary["best_score"] == 1
    assert summary["score_std_dev"] == pytest.approx((2 / 9) ** 0.5)
    assert summary["wins"] == 0
    assert summary["win_rate"] == 0
    assert summary["move_limits"] == 3
    assert summary["collisions"] == 0
    assert summary["total_moves"] == 6
    assert summary["mean_moves"] == 2
    assert summary["median_moves"] == 2
    assert summary["min_moves"] == 2
    assert summary["max_moves"] == 2
    assert summary["elapsed_seconds"] > 0
    assert summary["games_per_second"] > 0

    assert datetime.fromisoformat(report["created_at"]).tzinfo is not None
    assert report["python_version"] == platform.python_version()
    assert report["code"]["git_commit"]
    assert len(report["code"]["source_sha256"]) == 64
    assert "perf_counter" in report["timing_basis"]
    assert report["q_learning"]["table_path"] == str(table_path)
    assert report["q_learning"]["table_sha256"] == hashlib.sha256(
        original_table.encode()
    ).hexdigest()
    assert report["q_learning"]["epsilon"] == 0.8
    assert report["q_learning"]["game_trained"] == 3
    assert report["q_learning"]["evaluation_mode"] is True
    assert "Rule Based:" in result.stdout
    assert "Q Learning:" in result.stdout
    assert "Hamiltonian:" in result.stdout
    assert "Search-Based:" in result.stdout
    assert str(report_path.relative_to(tmp_path)) in result.stdout
    assert table_path.read_text() == original_table
