"""
Tests for reading, filtering and summarising saved game records.

A substitute record boundary stands in for the CSV file in most tests, so
they need neither stored records nor a graphical display. The last tests go
through a real CSV file in a temporary folder, to check that records written
now and records written before the Player column existed both read back.
"""

import csv

import pytest

from snake.storage.RecordManager import RecordManager
from snake.sessions.SessionSettings import SessionSettings
from snake.ui.RecordsBrowser import ALL_BOARDS, ALL_PLAYERS, ALL_SPEEDS, RecordsBrowser


class FakeRecordManager:
    """Returns rows shaped like the CSV reader's, whose values are all text."""

    def __init__(self, records=()):
        self.records = list(records)
        self.read_count = 0

    def read_game_records(self):
        self.read_count += 1
        return list(self.records)


def make_record(player="rule", score=1, total_moves=10, date_time="2026-01-01 10:00:00",
                board=(24, 25), speed_delay=1, game_time="1.0", outcome=""):
    return {
        "date_time": date_time,
        "player": player,
        "games_played": "1",
        "score": str(score),
        "best_score": str(score),
        "average_score": str(score),
        "total_moves": str(total_moves),
        "game_time": game_time,
        "session_time": "1.0",
        "board_width": str(board[0]),
        "board_height": str(board[1]),
        "tile_size": "25",
        "speed_delay": str(speed_delay),
        "outcome": outcome,
    }


def make_browser(records=(), **kwargs):
    browser = RecordsBrowser(record_manager=FakeRecordManager(records), **kwargs)
    browser.load()

    return browser


def test_empty_storage_reports_no_games_and_nothing_to_average():
    browser = make_browser()

    summary = browser.summary()

    assert summary["total_games"] == 0
    assert summary["best_score"] is None
    assert summary["average_score"] is None
    assert summary["average_moves"] is None
    assert browser.visible_records() == []


def test_a_summary_is_worked_out_from_the_stored_records():
    browser = make_browser([
        make_record(score=2, total_moves=10),
        make_record(score=8, total_moves=20),
        make_record(score=5, total_moves=30),
    ])

    summary = browser.summary()

    assert summary["total_games"] == 3
    assert summary["best_score"] == 8
    assert summary["average_score"] == 5.0
    assert summary["average_moves"] == 20.0


def test_the_newest_record_is_shown_first():
    browser = make_browser([
        make_record(date_time="2026-01-01 10:00:00", score=1),
        make_record(date_time="2026-01-02 10:00:00", score=2),
        make_record(date_time="2026-01-03 10:00:00", score=3),
    ])

    shown = browser.visible_records()

    assert [record["score"] for record in shown] == ["3", "2", "1"]


def test_only_the_most_recent_records_are_kept():
    browser = make_browser([make_record(score=number) for number in range(60)])

    assert len(browser.latest_records()) == RecordsBrowser.DISPLAY_LIMIT
    # The oldest ten fell outside the limit.
    assert browser.latest_records()[0]["score"] == "59"
    assert browser.latest_records()[-1]["score"] == "10"


@pytest.mark.parametrize(
    "selected_filter, expected_players",
    [
        (ALL_PLAYERS, ["rule", "q_learning", "q_learning_v2", "hamiltonian", "search_based", "human"]),
        ("rule", ["rule"]),
        ("q_learning", ["q_learning", "q_learning_v2"]),
        ("hamiltonian", ["hamiltonian"]),
        ("search_based", ["search_based"]),
        ("human", ["human"]),
    ],
)
def test_each_filter_selects_the_records_it_should(selected_filter, expected_players):
    browser = make_browser([
        make_record(player="rule"),
        make_record(player="q_learning"),
        make_record(player="q_learning_v2"),
        make_record(player="hamiltonian"),
        make_record(player="search_based"),
        make_record(player="human"),
    ])

    browser.select_filter(selected_filter)

    assert [record["player"] for record in browser.filtered_records()] == expected_players


def test_search_based_appears_in_comparison_and_trends_for_matching_conditions():
    browser = make_browser([
        make_record(player="rule", score=2, outcome="died"),
        make_record(player="search_based", score=4, outcome="won"),
        make_record(player="search_based", score=6, outcome="died"),
        make_record(player="search_based", score=20, board=(4, 4), outcome="won"),
    ])

    rows = {row["player"]: row for row in browser.player_statistics()}
    trends = {row["player"]: row for row in browser.player_trends()}
    assert rows["search_based"]["games"] == 2
    assert rows["search_based"]["average_score"] == 5
    assert rows["search_based"]["win_rate"] == 0.5
    assert "search_based" in trends

    browser.select_filter("search_based")
    assert browser.summary()["total_games"] == 2


def test_a_filter_summary_only_counts_the_records_it_selected():
    browser = make_browser([
        make_record(player="rule", score=2, total_moves=10),
        make_record(player="hamiltonian", score=40, total_moves=900),
    ])

    browser.select_filter("rule")

    assert browser.summary() == {
        "total_games": 1,
        "best_score": 2,
        "average_score": 2.0,
        "average_moves": 10.0,
    }


def test_the_human_filter_summary_only_counts_human_games():
    browser = make_browser([
        make_record(player="human", score=6, total_moves=40),
        make_record(player="rule", score=30, total_moves=500),
        make_record(player="human", score=10, total_moves=80),
    ])

    browser.select_filter("human")

    assert browser.summary() == {
        "total_games": 2,
        "best_score": 10,
        "average_score": 8.0,
        "average_moves": 60.0,
    }


def test_a_filter_with_no_records_is_still_usable():
    browser = make_browser([make_record(player="rule")])

    browser.select_filter("hamiltonian")

    assert browser.summary()["total_games"] == 0
    assert browser.visible_records() == []


def test_records_are_shown_one_page_at_a_time():
    browser = make_browser([make_record(score=number) for number in range(25)], page_size=10)

    first_page = browser.visible_records()
    browser.show_older_records()
    second_page = browser.visible_records()

    assert [record["score"] for record in first_page] == [str(n) for n in range(24, 14, -1)]
    assert [record["score"] for record in second_page] == [str(n) for n in range(14, 4, -1)]
    assert browser.page_number == 2
    assert browser.page_count == 3


def test_paging_stops_at_the_ends():
    browser = make_browser([make_record(score=number) for number in range(15)], page_size=10)

    browser.show_newer_records()
    assert browser.page_number == 1

    browser.show_older_records()
    browser.show_older_records()
    assert browser.page_number == 2


def test_resizing_a_page_keeps_the_current_records_reachable():
    browser = make_browser([make_record(score=number) for number in range(50)], page_size=10)
    for _ in range(4):
        browser.show_older_records()

    browser.set_page_size(20)

    assert browser.page_count == 3
    assert browser.page_number == 3
    assert [record["score"] for record in browser.visible_records()] == [
        str(number) for number in range(9, -1, -1)
    ]


def test_changing_the_filter_returns_to_the_newest_page():
    browser = make_browser([make_record(score=number) for number in range(25)], page_size=10)

    browser.show_older_records()
    browser.select_filter("rule")

    assert browser.page_number == 1


def save_example_game(record_manager, player="rule", score=3, outcome="died"):
    record_manager.save_game_result(player, 1, score, score, score, 10, 1.0, 1.0, 24, 25, 25, 1,
                                    outcome=outcome)


def test_a_new_records_file_stores_the_player_of_each_game(tmp_path):
    records_file = tmp_path / "game_records.csv"
    record_manager = RecordManager(file_name=str(records_file))

    save_example_game(record_manager, player="human", score=7)

    assert records_file.read_text().splitlines()[0].split(",")[1] == "player"
    browser = RecordsBrowser(record_manager=record_manager)
    browser.load()
    assert [(record["player"], record["score"]) for record in browser.latest_records()] == [("human", "7")]


OLD_RECORDS_FILE = (
    "date_time,bot_name,games_played,score,best_score,average_score,total_moves,"
    "game_time,session_time,board_width,board_height,tile_size,speed_delay\n"
    "2026-01-01 10:00:00,rule,1,4,4,4.0,50,1.0,1.0,24,25,25,1\n"
)


def test_records_saved_before_the_player_column_still_load(tmp_path):
    records_file = tmp_path / "game_records.csv"
    records_file.write_text(OLD_RECORDS_FILE)
    browser = RecordsBrowser(record_manager=RecordManager(file_name=str(records_file)))

    browser.load()

    assert [record["player"] for record in browser.latest_records()] == ["rule"]


def test_adding_a_game_to_an_old_records_file_keeps_every_record_readable(tmp_path):
    records_file = tmp_path / "game_records.csv"
    records_file.write_text(OLD_RECORDS_FILE)
    record_manager = RecordManager(file_name=str(records_file))

    save_example_game(record_manager, player="hamiltonian")

    browser = RecordsBrowser(record_manager=record_manager)
    browser.load()
    assert [record["player"] for record in browser.filtered_records()] == ["rule", "hamiltonian"]


# Game Outcome: new games store won or died, and old files are upgraded once
# with a backup (ADR 0006). An empty outcome means unknown.

def test_a_new_records_file_stores_the_outcome_of_each_game(tmp_path):
    record_manager = RecordManager(file_name=str(tmp_path / "game_records.csv"))

    save_example_game(record_manager, outcome="won")
    save_example_game(record_manager, outcome="died")

    assert [record["outcome"] for record in record_manager.read_game_records()] == ["won", "died"]


def test_saving_to_an_old_records_file_backs_it_up_then_upgrades_it(tmp_path):
    records_file = tmp_path / "game_records.csv"
    records_file.write_text(OLD_RECORDS_FILE)
    record_manager = RecordManager(file_name=str(records_file))

    save_example_game(record_manager, player="hamiltonian", outcome="won")

    assert (tmp_path / "game_records.csv.bak").read_text() == OLD_RECORDS_FILE
    header = records_file.read_text().splitlines()[0].split(",")
    assert header[1] == "player"
    assert header[-1] == "outcome"
    records = record_manager.read_game_records()
    assert [(record["player"], record["score"], record["outcome"]) for record in records] == [
        ("rule", "4", ""),
        ("hamiltonian", "3", "won"),
    ]


def test_an_upgraded_records_file_is_not_backed_up_again(tmp_path):
    records_file = tmp_path / "game_records.csv"
    records_file.write_text(OLD_RECORDS_FILE)
    record_manager = RecordManager(file_name=str(records_file))

    save_example_game(record_manager)
    save_example_game(record_manager)

    assert (tmp_path / "game_records.csv.bak").read_text() == OLD_RECORDS_FILE
    assert len(record_manager.read_game_records()) == 3


def test_an_existing_backup_is_never_overwritten(tmp_path):
    records_file = tmp_path / "game_records.csv"
    records_file.write_text(OLD_RECORDS_FILE)
    backup_file = tmp_path / "game_records.csv.bak"
    backup_file.write_text("an earlier backup\n")

    save_example_game(RecordManager(file_name=str(records_file)))

    assert backup_file.read_text() == "an earlier backup\n"


def test_reading_an_old_records_file_gives_unknown_outcomes_and_changes_nothing(tmp_path):
    records_file = tmp_path / "game_records.csv"
    records_file.write_text(OLD_RECORDS_FILE)

    records = RecordManager(file_name=str(records_file)).read_game_records()

    assert [record["outcome"] for record in records] == [""]
    assert records_file.read_text() == OLD_RECORDS_FILE
    assert not (tmp_path / "game_records.csv.bak").exists()


# Game Conditions: only games on the same board size and speed name are compared.
# The records above all use the default Settings choice, 24 x 25 at Fast.

def make_settings(board_size_name="Medium 24 x 25", speed_name="Fast"):
    settings = SessionSettings()
    settings.select_board_size(board_size_name)
    settings.select_speed(speed_name)

    return settings


def scores_selected(browser):
    return [record["score"] for record in browser.filtered_records()]


def test_the_board_and_speed_filters_start_at_the_settings_choice():
    browser = make_browser([
        make_record(score=1, board=(16, 16), speed_delay=10),
        make_record(score=2, board=(16, 16), speed_delay=1),
        make_record(score=3, board=(24, 25), speed_delay=10),
    ], settings=make_settings("Small 16 x 16", "Slow"))

    assert browser.board_filter == "Small 16 x 16"
    assert browser.speed_filter == "Slow"
    assert scores_selected(browser) == ["1"]


def test_human_play_and_bot_games_at_the_same_speed_name_are_compared_together():
    browser = make_browser([
        make_record(player="human", score=1, speed_delay=70),   # Human Play on Fast
        make_record(player="rule", score=2, speed_delay=1),     # a bot on Fast
        make_record(player="human", score=3, speed_delay=100),  # Human Play on Normal
    ])

    browser.select_speed("Fast")

    assert scores_selected(browser) == ["1", "2"]


def test_records_from_other_boards_or_delays_only_appear_under_all():
    browser = make_browser([
        make_record(score=1),
        make_record(score=2, board=(10, 10)),
        make_record(score=3, speed_delay=42),
    ])
    assert scores_selected(browser) == ["1"]

    browser.select_board(ALL_BOARDS)
    assert scores_selected(browser) == ["1", "2"]

    browser.select_speed(ALL_SPEEDS)
    assert scores_selected(browser) == ["1", "2", "3"]


def test_the_board_speed_and_player_filters_combine_in_the_summary():
    browser = make_browser([
        make_record(player="rule", score=4, board=(30, 30), speed_delay=5),
        make_record(player="q_learning_v2", score=8, board=(30, 30), speed_delay=5),
        make_record(player="q_learning", score=20, board=(30, 30), speed_delay=1),
        make_record(player="q_learning", score=12, board=(16, 16), speed_delay=5),
    ])

    browser.select_board("Large 30 x 30")
    browser.select_speed("Normal")
    browser.select_filter("q_learning")

    assert scores_selected(browser) == ["8"]
    assert browser.summary()["total_games"] == 1


def test_changing_the_board_or_speed_returns_to_the_newest_page():
    browser = make_browser([make_record(score=number) for number in range(25)], page_size=10)

    browser.show_older_records()
    browser.select_board(ALL_BOARDS)
    assert browser.page_number == 1

    browser.show_older_records()
    browser.select_speed(ALL_SPEEDS)
    assert browser.page_number == 1


# Compare: one row of statistics per Player, over every record that matches
# the Board and Speed filters. Expected values are worked out by hand.

def statistics_for(browser, player):
    return next(row for row in browser.player_statistics() if row["player"] == player)


def test_a_player_row_has_best_average_median_moves_and_game_time():
    browser = make_browser([
        make_record(score=2, total_moves=10, game_time="1.0"),
        make_record(score=4, total_moves=20, game_time="2.0"),
        make_record(score=9, total_moves=30, game_time="6.0"),
    ])

    row = statistics_for(browser, "rule")

    assert row["games"] == 3
    assert row["best_score"] == 9
    assert row["average_score"] == 5.0
    assert row["median_score"] == 4
    assert row["average_moves"] == 20.0
    assert row["average_game_time"] == 3.0


def test_the_median_of_an_even_number_of_games_is_the_middle_two_averaged():
    browser = make_browser([make_record(score=score) for score in (11, 1, 5, 3)])

    assert statistics_for(browser, "rule")["median_score"] == 4.0


def test_the_win_rate_only_counts_games_with_a_known_outcome():
    browser = make_browser([
        make_record(outcome="won"),
        make_record(outcome=""),
        make_record(outcome="died"),
        make_record(outcome=""),
    ])

    row = statistics_for(browser, "rule")

    assert row["win_rate"] == 0.5
    assert row["known_outcomes"] == 2


def test_the_win_rate_is_empty_when_no_outcome_is_known():
    browser = make_browser([make_record(outcome=""), make_record(outcome="")])

    row = statistics_for(browser, "rule")

    assert row["win_rate"] is None
    assert row["known_outcomes"] == 0


@pytest.mark.parametrize(
    "older_scores, recent_scores, recent_average, recent_form",
    [
        ([0] * 5, [10] * 20, 10.0, "above"),   # overall 200 / 25 = 8.0
        ([20] * 5, [0] * 20, 0.0, "below"),    # overall 100 / 25 = 4.0
        ([5] * 5, [5] * 20, 5.0, "level"),
    ],
)
def test_recent_form_compares_the_last_20_games_with_the_overall_average(
        older_scores, recent_scores, recent_average, recent_form):
    browser = make_browser([make_record(score=score) for score in older_scores + recent_scores])

    row = statistics_for(browser, "rule")

    assert row["recent_average"] == recent_average
    assert row["recent_form"] == recent_form


def test_a_player_with_fewer_than_20_games_is_level_with_itself():
    browser = make_browser([make_record(score=score) for score in (1, 2, 6)])

    row = statistics_for(browser, "rule")

    assert row["recent_average"] == 3.0
    assert row["recent_form"] == "level"


def test_compare_lists_each_player_with_games_under_the_conditions_in_a_fixed_order():
    browser = make_browser([
        make_record(player="human"),
        make_record(player="q_learning_v2"),
        make_record(player="rule"),
        make_record(player="q_learning_train"),
        make_record(player="hamiltonian", board=(30, 30)),   # another board: left out
    ])
    browser.select_filter("human")   # the Player filter belongs to the Games list only

    rows = browser.player_statistics()

    assert [row["player"] for row in rows] == ["rule", "q_learning", "human"]
    assert statistics_for(browser, "q_learning")["games"] == 2


def test_compare_uses_every_matching_record_not_just_the_newest_shown():
    browser = make_browser([make_record(score=1) for _ in range(60)], display_limit=50)

    assert statistics_for(browser, "rule")["games"] == 60


def test_compare_is_empty_when_no_records_match():
    browser = make_browser([make_record(board=(30, 30))])

    assert browser.player_statistics() == []


# Trends: each Player's last 100 matching games in play order, smoothed with a
# moving average over the 10 games up to each point.

def trend_for(browser, player):
    return next(trend["points"] for trend in browser.player_trends() if trend["player"] == player)


def test_a_short_history_is_averaged_over_the_games_so_far():
    browser = make_browser([make_record(score=score) for score in (1, 2, 3, 4, 5)])

    assert trend_for(browser, "rule") == [1.0, 1.5, 2.0, 2.5, 3.0]


def test_each_trend_point_averages_at_most_the_last_10_games():
    browser = make_browser([make_record(score=score) for score in range(12)])

    points = trend_for(browser, "rule")

    assert len(points) == 12
    assert points[9:] == [4.5, 5.5, 6.5]   # games 0-9, 1-10, 2-11


def test_a_trend_only_covers_the_last_100_games():
    browser = make_browser([make_record(score=score) for score in range(105)])

    points = trend_for(browser, "rule")

    assert len(points) == 100
    assert points[0] == 5.0     # game 5 is the first of the last 100
    assert points[-1] == 99.5   # games 95-104


def test_trends_follow_the_conditions_and_group_q_learning_names():
    browser = make_browser([
        make_record(player="q_learning", score=2),
        make_record(player="rule", score=8, board=(30, 30)),   # another board: left out
        make_record(player="q_learning_v2", score=4),
        make_record(player="human", score=6, speed_delay=70),
    ])

    trends = browser.player_trends()

    assert [trend["player"] for trend in trends] == ["q_learning", "human"]
    assert trend_for(browser, "q_learning") == [2.0, 3.0]


def test_trends_are_empty_when_no_records_match():
    browser = make_browser([make_record(board=(30, 30))])

    assert browser.player_trends() == []


def test_a_failed_upgrade_leaves_the_old_records_file_as_it_was(tmp_path, monkeypatch):
    records_file = tmp_path / "game_records.csv"
    records_file.write_text(OLD_RECORDS_FILE)
    backup_file = tmp_path / "game_records.csv.bak"
    backup_file.write_text("an earlier backup of a different file\n")
    real_writer = csv.writer

    class WriterThatFailsOnOldRows:
        """Writes the header, then fails on the first old row, like a full disk."""

        def __init__(self, file):
            self.writer = real_writer(file)

        def writerow(self, row):
            if (row[0] == "2026-01-01 10:00:00"):
                raise OSError("disk full")
            self.writer.writerow(row)

    monkeypatch.setattr("snake.storage.RecordManager.csv.writer", WriterThatFailsOnOldRows)

    with pytest.raises(OSError):
        save_example_game(RecordManager(file_name=str(records_file)))

    assert records_file.read_text() == OLD_RECORDS_FILE
    assert sorted(path.name for path in tmp_path.iterdir()) == ["game_records.csv",
                                                                "game_records.csv.bak"]


def test_unreadable_records_are_left_out_of_the_numbers_but_still_listed():
    missing_moves = make_record(score=7)
    missing_moves["total_moves"] = None   # a short row read from a damaged file
    browser = make_browser([
        make_record(score=4, total_moves=10, game_time="2.0"),
        make_record(score=9, game_time=""),
        make_record(score=5, game_time="abc"),
        missing_moves,
    ])
    browser.records[1]["score"] = "not a number"

    row = statistics_for(browser, "rule")

    assert (row["games"], row["best_score"], row["average_game_time"]) == (1, 4, 2.0)
    assert trend_for(browser, "rule") == [4.0]
    assert browser.summary() == {
        "total_games": 1,
        "best_score": 4,
        "average_score": 4.0,
        "average_moves": 10.0,
    }
    assert len(browser.latest_records()) == 4


def test_a_player_with_only_unreadable_records_is_left_out():
    browser = make_browser([make_record(player="human", game_time=""), make_record(score=3)])

    assert [row["player"] for row in browser.player_statistics()] == ["rule"]
    assert [trend["player"] for trend in browser.player_trends()] == ["rule"]
