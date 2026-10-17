"""The evaluation list reads real report structure and leaves stored data alone."""

from copy import deepcopy
import json

import pytest

from snake.engine.GameConfig import GameConfig
from snake.sessions.ExperimentReport import build_report, summarize_games
from snake.storage.EvaluationReports import read_evaluation_reports
from snake.ui.EvaluationBrowser import EvaluationBrowser


def sample_report(source="app_training", date="2026-10-17T00:00:00+00:00"):
    games = [{"seed": 200000, "score": 12, "moves": 20, "outcome": "collision"}]
    result = {"games": games, "summary": summarize_games(games, 1.0)}
    report = build_report(GameConfig(24, 25, 25), 200000, 1, 5000, ["q_learning_v3"],
                          {"q_learning_v3": result})
    report.update(evaluated=source, created_at=date)
    return report


def write_report(directory, name, report):
    path = directory / name
    path.write_text(json.dumps(report))
    return path


def test_lists_both_sources_newest_first_and_preserves_files(tmp_path):
    older = write_report(tmp_path, "old.json", sample_report())
    newer = write_report(tmp_path, "new.json", sample_report("showcase", "2026-10-18T00:00:00Z"))
    before = {path: path.read_bytes() for path in (older, newer)}

    results, skipped = read_evaluation_reports(tmp_path)

    assert skipped == 0
    assert [result.source for result in results] == ["Showcase Bot", "Your bot"]
    assert results[0].player == "q_learning_v3"
    assert results[0].game_count == 1
    assert results[0].average_score == 12
    assert results[0].best_score == 12
    assert (results[0].board_width, results[0].board_height) == (24, 25)
    assert (results[0].base_seed, results[0].max_moves) == (200000, 5000)
    assert before == {path: path.read_bytes() for path in before}


def test_terminal_reports_are_separate_and_no_directory_is_created(tmp_path):
    missing = tmp_path / "missing"
    assert read_evaluation_reports(missing) == ([], 0)
    assert not missing.exists()
    report = sample_report()
    del report["evaluated"]
    write_report(tmp_path, "terminal.json", report)
    assert read_evaluation_reports(tmp_path) == ([], 0)


@pytest.mark.parametrize("field,value", [
    ("schema_version", 999), ("evaluated", "unknown"), ("game_count", 0),
    ("game_count", 2), ("selected_bot_modes", []), ("board", None),
    ("base_seed", "200000"), ("max_moves", True), ("created_at", "broken"),
    ("bots", []),
])
def test_damaged_or_unsupported_reports_do_not_hide_valid_results(tmp_path, field, value):
    report = sample_report()
    report[field] = value
    write_report(tmp_path, "bad.json", report)
    write_report(tmp_path, "good.json", sample_report())
    results, skipped = read_evaluation_reports(tmp_path)
    assert len(results) == 1
    assert skipped == 1


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, "12"])
def test_invalid_averages_are_rejected(tmp_path, value):
    report = sample_report()
    report["bots"]["q_learning_v3"]["summary"]["mean_score"] = value
    write_report(tmp_path, "bad.json", report)
    assert read_evaluation_reports(tmp_path) == ([], 1)


def test_malformed_json_and_read_errors_are_counted(tmp_path, monkeypatch):
    (tmp_path / "bad.json").write_text("{broken")
    unreadable = write_report(tmp_path, "unreadable.json", sample_report())
    original_open = type(unreadable).open

    def open_file(path, *args, **kwargs):
        if path == unreadable:
            raise PermissionError("Cannot read")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(type(unreadable), "open", open_file)
    assert read_evaluation_reports(tmp_path) == ([], 2)


def test_dates_are_sorted_by_actual_time_and_displayed_in_utc(tmp_path):
    write_report(tmp_path, "a.json", sample_report(date="2026-10-17T02:00:00+03:00"))
    write_report(tmp_path, "b.json", sample_report(date="2026-10-17T00:00:00Z"))
    results, skipped = read_evaluation_reports(tmp_path)
    assert skipped == 0
    assert results[0].created_at.isoformat() == "2026-10-17T00:00:00+00:00"
    assert results[1].created_at.isoformat() == "2026-10-16T23:00:00+00:00"


def test_paging_reaches_all_runs_and_keeps_position_when_resized(tmp_path):
    for day in range(1, 10):
        report = deepcopy(sample_report())
        report["created_at"] = f"2026-10-{day:02}T00:00:00Z"
        write_report(tmp_path, f"{day}.json", report)
    browser = EvaluationBrowser(tmp_path, page_size=2)
    browser.load()
    assert browser.page_count == 5
    assert [result.created_at.day for result in browser.visible_results()] == [9, 8]
    browser.older()
    assert [result.created_at.day for result in browser.visible_results()] == [7, 6]
    browser.set_page_size(3)
    assert browser.page_count == 3
    for _ in range(10):
        browser.older()
    assert [result.created_at.day for result in browser.visible_results()] == [3, 2, 1]
    for _ in range(10):
        browser.newer()
    assert browser.page_index == 0
