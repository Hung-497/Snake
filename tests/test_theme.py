"""
Tests for theme arithmetic and bundled font discovery.

Colour, size and spacing tokens are deliberately not asserted here: checking
that a token holds a particular value only proves it was typed twice. What is
worth testing is the mixing used to ease a control between its states.
"""

from pathlib import Path

from arcade.types import Color

from snake.ui.Theme import FONT_DIR, SPACE_TIGHT, blend_color, filter_button_width


def test_bundled_fonts_are_found_after_theme_move():
    font_directory = Path(FONT_DIR)
    assert (font_directory / "Inter-Regular.ttf").is_file()
    assert (font_directory / "Inter-SemiBold.ttf").is_file()


BLACK = Color(0, 0, 0, 255)
WHITE = Color(255, 255, 255, 255)


def test_no_mixing_gives_the_first_colour():
    assert blend_color(BLACK, WHITE, 0) == BLACK


def test_full_mixing_gives_the_second_colour():
    assert blend_color(BLACK, WHITE, 1) == WHITE


def test_half_mixing_lands_between_the_two():
    mixed = blend_color(BLACK, WHITE, 0.5)

    assert mixed.r == mixed.g == mixed.b == 128


def test_mixing_further_than_the_target_stops_at_the_target():
    # A long frame must not overshoot into a colour nobody chose.
    assert blend_color(BLACK, WHITE, 4.0) == WHITE


def test_mixing_backwards_stays_at_the_start():
    assert blend_color(BLACK, WHITE, -2.0) == BLACK


def test_mixing_keeps_the_colour_fully_opaque():
    assert blend_color(BLACK, WHITE, 0.3).a == 255


def test_each_channel_moves_independently():
    orange = Color(255, 128, 0, 255)
    blue = Color(0, 128, 255, 255)

    mixed = blend_color(orange, blue, 0.5)

    assert (mixed.r, mixed.g, mixed.b) == (128, 128, 128)


def test_six_player_filters_fit_when_compact_and_widen_after_resize():
    compact_width = filter_button_width(700)
    regular_width = filter_button_width(900)

    assert compact_width * 6 + SPACE_TIGHT * 5 <= 700
    assert regular_width > compact_width
