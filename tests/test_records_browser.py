"""
Tests for reading, filtering and summarising saved game records.

A substitute record boundary stands in for the CSV file in most tests, so
they need neither stored records nor a graphical display. The last tests go
through a real CSV file in a temporary folder, to check that records written
now and records written before the Player column existed both read back.
"""

import pytest

from snake.storage.RecordManager import RecordManager
from snake.ui.RecordsBrowser import ALL_PLAYERS, RecordsBrowser


class FakeRecordManager:
    """Returns rows shaped like the CSV reader's, whose values are all text."""

    def __init__(self, records=()):
        self.records = list(records)
        self.read_count = 0

    def read_game_records(self):
        self.read_count += 1
        return list(self.records)


def make_record(player="rule", score=1, total_moves=10, date_time="2026-01-01 10:00:00"):
    return {
        "date_time": date_time,
        "player": player,
        "games_played": "1",
        "score": str(score),
        "best_score": str(score),
        "average_score": str(score),
        "total_moves": str(total_moves),
        "game_time": "1.0",
        "session_time": "1.0",
        "board_width": "24",
        "board_height": "25",
        "tile_size": "25",
        "speed_delay": "1",
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
        (ALL_PLAYERS, ["rule", "q_learning", "q_learning_v2", "hamiltonian", "human"]),
        ("rule", ["rule"]),
        ("q_learning", ["q_learning", "q_learning_v2"]),
        ("hamiltonian", ["hamiltonian"]),
        ("human", ["human"]),
    ],
)
def test_each_filter_selects_the_records_it_should(selected_filter, expected_players):
    browser = make_browser([
        make_record(player="rule"),
        make_record(player="q_learning"),
        make_record(player="q_learning_v2"),
        make_record(player="hamiltonian"),
        make_record(player="human"),
    ])

    browser.select_filter(selected_filter)

    assert [record["player"] for record in browser.filtered_records()] == expected_players


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


def save_example_game(record_manager, player="rule", score=3):
    record_manager.save_game_result(player, 1, score, score, score, 10, 1.0, 1.0, 24, 25, 25, 100)


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
