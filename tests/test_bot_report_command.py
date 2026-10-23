"""The Bot Report command is tested through its terminal interface."""

import json
import os
from pathlib import Path
import subprocess
import sys

from snake.engine.GameConfig import GameConfig
from snake.sessions.ExperimentReport import build_report, summarize_games


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_bot_report(tmp_path, *options):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "snake.sessions.AnalyseBots", *options],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )


def games_from(scores, base_seed=200000, outcomes=None):
    outcomes = outcomes or ["collision"] * len(scores)
    return [
        {"seed": base_seed + number, "score": score, "moves": 10 * (score + 1), "outcome": outcome}
        for number, (score, outcome) in enumerate(zip(scores, outcomes))
    ]


def sample_report(bots, base_seed=200000, max_moves=5000, date="2026-10-20T12:00:00+00:00"):
    """A real-shaped report; bots maps a Bot Mode to its list of games."""
    game_count = len(next(iter(bots.values())))
    results = {
        bot_mode: {"games": games, "summary": summarize_games(games, 1.0)}
        for bot_mode, games in bots.items()
    }
    report = build_report(GameConfig(24, 25, 25), base_seed, game_count, max_moves,
                          list(bots), results)
    report["created_at"] = date
    return report


def write_report(tmp_path, name, report):
    directory = tmp_path / "experiments"
    directory.mkdir(exist_ok=True)
    path = directory / name
    path.write_text(json.dumps(report) if isinstance(report, dict) else report)
    return path


def read_markdown(tmp_path):
    return (tmp_path / "reports" / "bot_report.md").read_text()


def test_writes_an_overview_table_computed_from_the_games(tmp_path):
    games = games_from([10, 20, 30], outcomes=["collision", "collision", "move_limit"])
    write_report(tmp_path, "one.json", sample_report({"q_learning_v3": games}))

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    assert "24 × 25 board, 5000-move limit, seeds 200000–200002 (3 games)" in markdown
    row = next(line for line in markdown.splitlines() if line.startswith("| Q Learning v3"))
    cells = [cell.strip() for cell in row.strip("|").split("|")]
    # Bot, run date, games, mean, median, best, std dev, win rate, move-limit rate
    assert cells == [
        "Q Learning v3", "2026-10-20 12:00", "3", "20.0", "20.0", "30", "8.2", "0.0%", "33.3%",
    ]
    assert "bot_report.html" in result.stdout


def test_every_bot_in_a_report_gets_its_own_row(tmp_path):
    write_report(tmp_path, "both.json", sample_report({
        "rule": games_from([5, 7]),
        "hamiltonian": games_from([40, 60], outcomes=["won", "won"]),
    }))

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    assert "| Rule Based |" in markdown
    hamiltonian = next(line for line in markdown.splitlines() if line.startswith("| Hamiltonian"))
    assert "| 100.0% |" in hamiltonian


def test_runs_with_different_experiment_conditions_are_never_mixed(tmp_path):
    write_report(tmp_path, "short.json", sample_report({"dqn": games_from([50, 52])}))
    write_report(tmp_path, "long.json", sample_report(
        {"dqn": games_from([80, 90])}, max_moves=20000,
    ))
    write_report(tmp_path, "other_seeds.json", sample_report(
        {"dqn": games_from([30, 31], base_seed=7)}, base_seed=7,
    ))

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    sections = markdown.split("\n## ")[1:]
    assert len(sections) == 3
    by_heading = {section.splitlines()[0]: section for section in sections}
    short = by_heading["24 × 25 board, 5000-move limit, seeds 200000–200001 (2 games)"]
    long = by_heading["24 × 25 board, 20000-move limit, seeds 200000–200001 (2 games)"]
    other = by_heading["24 × 25 board, 5000-move limit, seeds 7–8 (2 games)"]
    assert "| 51.0 |" in short and "85.0" not in short
    assert "| 85.0 |" in long and "51.0" not in long
    assert "| 30.5 |" in other


def test_damaged_old_or_incomplete_reports_are_skipped_and_counted(tmp_path):
    write_report(tmp_path, "good.json", sample_report({"rule": games_from([4, 6])}))
    write_report(tmp_path, "broken.json", "{not json")
    old = sample_report({"rule": games_from([1, 1])})
    old["schema_version"] = 2
    write_report(tmp_path, "old.json", old)
    incomplete = sample_report({"rule": games_from([1, 1])})
    incomplete["bots"]["rule"]["games"].pop()
    write_report(tmp_path, "incomplete.json", incomplete)

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    assert "3 report files were skipped" in markdown
    assert "3 skipped" in result.stdout
    assert "| 5.0 |" in markdown


def test_no_usable_reports_gives_a_clear_error_and_writes_nothing(tmp_path):
    write_report(tmp_path, "broken.json", "[]")

    result = run_bot_report(tmp_path)

    assert result.returncode == 1
    assert "No usable Bot Experiment reports" in result.stderr
    assert "1 skipped" in result.stderr
    assert not (tmp_path / "reports").exists()


def test_a_missing_experiments_folder_gives_the_same_error(tmp_path):
    result = run_bot_report(tmp_path)

    assert result.returncode == 1
    assert "No usable Bot Experiment reports" in result.stderr
    assert not (tmp_path / "reports").exists()


def test_same_inputs_give_identical_files_and_inputs_are_unchanged(tmp_path):
    path = write_report(tmp_path, "one.json", sample_report({"rule": games_from([3, 9])}))
    before = path.read_bytes()

    run_bot_report(tmp_path)
    first = {name: (tmp_path / "reports" / name).read_bytes()
             for name in ("bot_report.md", "bot_report.html")}
    run_bot_report(tmp_path)

    for name, content in first.items():
        assert (tmp_path / "reports" / name).read_bytes() == content
    assert path.read_bytes() == before


def test_html_is_complete_and_shows_the_same_rows(tmp_path):
    write_report(tmp_path, "both.json", sample_report({
        "search_based": games_from([12, 14]), "q_learning": games_from([20, 22]),
    }))

    result = run_bot_report(tmp_path, "--output", "out")

    assert result.returncode == 0, result.stderr
    page = (tmp_path / "out" / "bot_report.html").read_text()
    assert page.startswith("<!doctype html>")
    assert page.rstrip().endswith("</html>")
    assert "Search-Based" in page and "Q Learning v2" in page
    assert "<td>13.0</td>" in page and "<td>21.0</td>" in page


def test_the_command_does_not_import_pytorch(tmp_path):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys, snake.sessions.AnalyseBots; print('torch' in sys.modules)"],
        cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=60,
    )

    assert result.stdout.strip() == "False", result.stderr
