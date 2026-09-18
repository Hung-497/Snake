"""
Tests for reading, filtering and summarising saved game records.

A substitute record boundary stands in for the CSV file, so these tests need
neither stored records nor a graphical display. Nothing here changes how the
records are stored; the browser only reads what RecordManager returns.
"""

import pytest

from RecordsBrowser import ALL_BOTS, RecordsBrowser


class FakeRecordManager:
    """Returns rows shaped like the CSV reader's, whose values are all text."""

    def __init__(self, records=()):
        self.records = list(records)
        self.read_count = 0

    def read_game_records(self):
        self.read_count += 1
        return list(self.records)


def make_record(bot_name="rule", score=1, total_moves=10, date_time="2026-01-01 10:00:00"):
    return {
        "date_time": date_time,
        "bot_name": bot_name,
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
    "selected_filter, expected_bot_names",
    [
        (ALL_BOTS, ["rule", "q_learning", "q_learning_v2", "hamiltonian"]),
        ("rule", ["rule"]),
        ("q_learning", ["q_learning", "q_learning_v2"]),
        ("hamiltonian", ["hamiltonian"]),
    ],
)
def test_each_filter_selects_the_records_it_should(selected_filter, expected_bot_names):
    browser = make_browser([
        make_record(bot_name="rule"),
        make_record(bot_name="q_learning"),
        make_record(bot_name="q_learning_v2"),
        make_record(bot_name="hamiltonian"),
    ])

    browser.select_filter(selected_filter)

    assert [record["bot_name"] for record in browser.filtered_records()] == expected_bot_names


def test_a_filter_summary_only_counts_the_records_it_selected():
    browser = make_browser([
        make_record(bot_name="rule", score=2, total_moves=10),
        make_record(bot_name="hamiltonian", score=40, total_moves=900),
    ])

    browser.select_filter("rule")

    assert browser.summary() == {
        "total_games": 1,
        "best_score": 2,
        "average_score": 2.0,
        "average_moves": 10.0,
    }


def test_a_filter_with_no_records_is_still_usable():
    browser = make_browser([make_record(bot_name="rule")])

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


def test_changing_the_filter_returns_to_the_newest_page():
    browser = make_browser([make_record(score=number) for number in range(25)], page_size=10)

    browser.show_older_records()
    browser.select_filter("rule")

    assert browser.page_number == 1
