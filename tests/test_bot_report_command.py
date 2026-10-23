"""The Bot Report command is tested through its terminal interface."""

import json
import os
from xml.etree import ElementTree
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
    return (tmp_path / "reports" / "bot_report.md").read_text(encoding="utf-8")


OVERVIEW = "overview"
COMPARISONS = "### Game by game"
PROVENANCE = "### Where each bot came from"


def table_rows(markdown, first_cell, table=OVERVIEW):
    """The cells of each row whose first cell is first_cell, in one kind of table.

    The overview table comes straight after each group's heading; the other
    tables follow their own headings, up to the next heading.
    """
    sections = []
    for section in markdown.split("\n#"):
        heading = "#" + section.splitlines()[0]
        if table == OVERVIEW and heading.startswith("## ") or heading == table:
            sections.append(section)
    rows = []
    for line in "\n".join(sections).splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells[0] == first_cell:
            rows.append(cells)
    return rows


def q_table_identity(sha, feature_set="v3", games=2000, history=None):
    identity = {"table_sha256": sha, "feature_set": feature_set, "game_trained": games}
    if history is not None:
        identity["training_history"] = history
    return identity


def dqn_identity(sha, feature_schema="q_learning_space_state_v3", seed=9000, games=2000):
    return {
        "model_sha256": sha, "feature_schema": feature_schema,
        "base_seed": seed, "game_trained": games,
    }


def test_writes_an_overview_table_computed_from_the_games(tmp_path):
    games = games_from([10, 20, 30], outcomes=["collision", "collision", "move_limit"])
    write_report(tmp_path, "one.json", sample_report({"q_learning_v3": games}))

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    assert "24 × 25 board, 5000-move limit, seeds 200000–200002 (3 games)" in markdown
    # Bot, bot file, run date, games, mean, median, best, std dev, win rate,
    # move-limit rate, moves per point (630 moves / 60 points); a report
    # without the bot's identity has an unknown file.
    assert table_rows(markdown, "Q Learning v3")[0] == [
        "Q Learning v3", "unknown", "2026-10-20 12:00", "3", "20.0", "20.0", "30", "8.2",
        "0.0%", "33.3%", "10.5",
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
    page = (tmp_path / "out" / "bot_report.html").read_text(encoding="utf-8")
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


def test_each_bot_file_is_its_own_row_with_a_combined_row(tmp_path):
    for name, sha, scores in (("a.json", "a" * 64, [10, 20]), ("b.json", "b" * 64, [30, 40])):
        report = sample_report({"q_learning_v3": games_from(scores)})
        report["q_learning_v3"] = q_table_identity(sha)
        write_report(tmp_path, name, report)

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    runs = table_rows(markdown, "Q Learning v3")
    assert sorted(row[1] for row in runs) == ["aaaaaaaa", "bbbbbbbb"]
    combined = table_rows(markdown, "Q Learning v3 combined (2 bot files)")
    assert len(combined) == 1
    # The combined row pools both files' games: mean of 10, 20, 30, 40.
    assert combined[0][3:6] == ["4", "25.0", "25.0"]


def test_a_bot_file_evaluated_twice_shows_only_its_newest_run(tmp_path):
    for name, date, scores in (
        ("old.json", "2026-10-01T00:00:00+00:00", [1, 1]),
        ("new.json", "2026-10-05T00:00:00+00:00", [9, 9]),
    ):
        report = sample_report({"q_learning_v3": games_from(scores)}, date=date)
        report["q_learning_v3"] = q_table_identity("c" * 64)
        write_report(tmp_path, name, report)

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    rows = table_rows(markdown, "Q Learning v3")
    assert len(rows) == 1
    assert rows[0][2] == "2026-10-05 00:00"
    assert "2026-10-01" not in markdown
    assert not table_rows(markdown, "Q Learning v3 combined (2 bot files)")


def test_non_learning_bots_evaluated_twice_show_only_the_newest_run(tmp_path):
    for name, date in (("old.json", "2026-10-01T00:00:00+00:00"),
                       ("new.json", "2026-10-05T00:00:00+00:00")):
        write_report(tmp_path, name, sample_report({"rule": games_from([3, 5])}, date=date))

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    rows = table_rows(read_markdown(tmp_path), "Rule Based")
    assert [row[2] for row in rows] == ["2026-10-05 00:00"]


def test_provenance_shows_how_each_bot_file_was_trained(tmp_path):
    report = sample_report({"q_learning_v3": games_from([5, 6]), "dqn": games_from([7, 8])})
    report["q_learning_v3"] = q_table_identity("d" * 64, history=[
        {"source": "train_command", "seed": 12000, "games_at_end": 2000},
    ])
    report["dqn"] = dqn_identity("e" * 64, feature_schema="q_learning_space_state_v2", seed=9000)
    report["code"] = {"git_commit": "1234567890abcdef", "source_sha256": "f" * 64}
    write_report(tmp_path, "one.json", report)

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    assert "## " in markdown and "### Where each bot came from" in markdown
    # Bot, bot file, Feature Set, games trained, trained by, training seeds, code
    assert table_rows(markdown, "Q Learning v3", PROVENANCE)[0] == [
        "Q Learning v3", "dddddddd", "v3", "2000", "Terminal command", "12000", "1234567",
    ]
    # Terminal experiments save every DQN as "dqn"; the Feature Set names it.
    assert table_rows(markdown, "DQN v2", PROVENANCE)[0] == [
        "DQN v2", "eeeeeeee", "v2", "2000", "Terminal command", "9000", "1234567",
    ]


def test_app_trained_bots_are_marked_as_app_training(tmp_path):
    report = sample_report({"dqn": games_from([7, 8])})
    report["dqn"] = dqn_identity("1" * 64, seed=0)
    report["evaluated"] = "app_training"
    write_report(tmp_path, "one.json", report)

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    assert table_rows(read_markdown(tmp_path), "DQN v3", PROVENANCE)[0][4] == "App"


def test_missing_provenance_is_shown_as_unknown(tmp_path):
    report = sample_report({"q_learning": games_from([5, 6]), "rule": games_from([1, 2])})
    report["q_learning"] = {"table_sha256": "2" * 64}
    del report["code"]
    write_report(tmp_path, "one.json", report)

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    # Tables saved before Feature Sets were recorded are v2.
    assert table_rows(markdown, "Q Learning v2", PROVENANCE)[0] == [
        "Q Learning v2", "22222222", "v2", "unknown", "unknown", "unknown", "unknown",
    ]
    assert table_rows(markdown, "Rule Based", PROVENANCE)[0] == [
        "Rule Based", "—", "—", "—", "—", "—", "unknown",
    ]


def test_a_run_that_never_scored_has_no_moves_per_point(tmp_path):
    write_report(tmp_path, "zero.json", sample_report({"rule": games_from([0, 0])}))

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    assert table_rows(read_markdown(tmp_path), "Rule Based")[0][-1] == "—"


def test_each_group_gets_a_score_chart_in_both_files(tmp_path):
    write_report(tmp_path, "short.json", sample_report({
        "rule": games_from([5, 9, 13]), "search_based": games_from([40, 50, 60]),
    }))
    write_report(tmp_path, "long.json", sample_report(
        {"dqn": games_from([80, 90, 100])}, max_moves=20000,
    ))

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    charts = sorted((tmp_path / "reports" / "bot_report_charts").glob("*.svg"))
    assert [chart.name for chart in charts] == ["scores_1.svg", "scores_2.svg"]
    markdown = read_markdown(tmp_path)
    page = (tmp_path / "reports" / "bot_report.html").read_text(encoding="utf-8")
    for chart, labels in zip(charts, (["Rule Based", "Search-Based"], ["DQN"])):
        # Each chart is a complete SVG file that names every bot it shows.
        root = ElementTree.parse(chart).getroot()
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        text = chart.read_text(encoding="utf-8")
        assert all(label in text for label in labels)
        assert f"](bot_report_charts/{chart.name})" in markdown
    assert page.count("<svg") == 2


def test_charts_from_an_earlier_report_are_removed(tmp_path):
    write_report(tmp_path, "a.json", sample_report({"rule": games_from([1, 2])}))
    write_report(tmp_path, "b.json", sample_report({"rule": games_from([3, 4])}, base_seed=7))
    run_bot_report(tmp_path)
    (tmp_path / "experiments" / "b.json").unlink()

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    charts = (tmp_path / "reports" / "bot_report_charts").glob("*.svg")
    assert [chart.name for chart in charts] == ["scores_1.svg"]


def test_bots_are_compared_game_by_game_with_a_95_percent_range(tmp_path):
    write_report(tmp_path, "both.json", sample_report({
        "rule": games_from([5, 7, 9]), "search_based": games_from([40, 50, 60]),
    }))

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    assert "### Game by game" in markdown
    # Differences 35, 43, 51: average 43, range 43 ± 4.303 × 8 / √3.
    assert table_rows(markdown, "Search-Based", COMPARISONS)[0] == [
        "Search-Based", "Rule Based", "3", "43.0", "23.1 to 62.9", "Search-Based scores more",
    ]


def test_a_bot_with_several_files_is_compared_by_its_average_per_seed(tmp_path):
    for name, sha, scores in (("a.json", "a" * 64, [10, 20]), ("b.json", "b" * 64, [30, 40])):
        report = sample_report({"q_learning_v3": games_from(scores), "rule": games_from([25, 25])})
        report["q_learning_v3"] = q_table_identity(sha)
        write_report(tmp_path, name, report)

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    # Per seed, Q Learning v3 averages 20 and 30 over its files; Rule Based
    # scores 25 both times, so the differences are -5 and 5.
    comparison = table_rows(read_markdown(tmp_path), "Q Learning v3", COMPARISONS)[0]
    assert comparison[:4] == ["Q Learning v3", "Rule Based", "2", "0.0"]
    assert comparison[5] == "No reliable difference"


def test_a_group_with_one_bot_has_nothing_to_compare(tmp_path):
    write_report(tmp_path, "one.json", sample_report({"rule": games_from([1, 2])}))

    result = run_bot_report(tmp_path)

    assert result.returncode == 0, result.stderr
    markdown = read_markdown(tmp_path)
    assert "Only one bot was evaluated under these conditions" in markdown
    assert "| Better bot |" not in markdown
