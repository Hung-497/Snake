"""
Tests for the board, tile and speed choices kept for one app session.

SessionSettings holds no Snake rules and no drawing, so these tests need no
graphical display.
"""

import pytest

from snake.sessions.SessionSettings import SessionSettings


def test_defaults_match_the_choices_the_menu_started_with():
    settings = SessionSettings()

    assert settings.selected_board_size_name == "Medium 24 x 25"
    assert settings.selected_tile_size_name == "Medium tiles 25 px"
    assert settings.selected_speed_name == "Fast"


def test_every_current_option_is_offered():
    settings = SessionSettings()

    assert settings.board_size_names() == [
        "Small 16 x 16",
        "Medium 24 x 25",
        "Large 30 x 30",
        "Square 25 x 25",
    ]
    assert settings.tile_size_names() == [
        "Small tiles 20 px",
        "Medium tiles 25 px",
        "Large tiles 30 px",
    ]
    assert settings.speed_names() == ["Slow", "Normal", "Fast"]


def test_the_default_game_config_matches_the_default_choices():
    settings = SessionSettings()

    game_config = settings.build_game_config()

    assert (game_config.width, game_config.height) == (24, 25)
    assert game_config.tile_size == 25
    assert settings.speed_delay == 1


def test_choosing_a_board_size_changes_the_game_config():
    settings = SessionSettings()

    settings.select_board_size("Large 30 x 30")

    assert settings.selected_board_size_name == "Large 30 x 30"
    assert (settings.build_game_config().width, settings.build_game_config().height) == (30, 30)


def test_choosing_a_tile_size_changes_the_game_config():
    settings = SessionSettings()

    settings.select_tile_size("Small tiles 20 px")

    assert settings.selected_tile_size_name == "Small tiles 20 px"
    assert settings.build_game_config().tile_size == 20


def test_choosing_a_speed_changes_the_speed_delay():
    settings = SessionSettings()

    settings.select_speed("Slow")

    assert settings.selected_speed_name == "Slow"
    assert settings.speed_delay == 10


@pytest.mark.parametrize("speed_name, human_delay", [("Slow", 150), ("Normal", 100), ("Fast", 70)])
def test_human_play_uses_a_speed_a_person_can_play(speed_name, human_delay):
    settings = SessionSettings()

    settings.select_speed(speed_name)

    assert settings.speed_delay_for("human") == human_delay


def test_bot_modes_keep_their_own_speed_delay():
    settings = SessionSettings()

    settings.select_speed("Normal")

    assert settings.speed_delay_for("rule") == 5


@pytest.mark.parametrize(
    "select_name, unknown_option",
    [
        ("select_board_size", "Enormous 99 x 99"),
        ("select_tile_size", "Tiny tiles 2 px"),
        ("select_speed", "Ludicrous"),
    ],
)
def test_an_unknown_option_is_rejected(select_name, unknown_option):
    settings = SessionSettings()

    with pytest.raises(ValueError):
        getattr(settings, select_name)(unknown_option)


@pytest.mark.parametrize(
    "speed_delay, speed_name",
    [(10, "Slow"), (5, "Normal"), (1, "Fast"), (150, "Slow"), (100, "Normal"), (70, "Fast")],
)
def test_a_recorded_delay_maps_back_to_its_speed_name(speed_delay, speed_name):
    # Bot Modes and Human Play use different delays for the same speed name.
    assert SessionSettings().speed_name_for_delay(speed_delay) == speed_name


def test_a_delay_the_app_does_not_offer_has_no_speed_name():
    assert SessionSettings().speed_name_for_delay(42) is None
