"""
Tests for turning grid cells into pixels.

The renderer is the only place in the app where a cell becomes a pixel, so the
conversion is checked here with a stand-in window and no graphical display.
"""

from BoardRenderer import BoardRenderer


class FakeWindow:
    """Only the size matters for working out where the board sits."""

    width = 900
    height = 960


def make_renderer():
    return BoardRenderer(FakeWindow(), hud_height=60)


def test_the_board_is_centred_in_the_space_below_the_score_line():
    renderer = make_renderer()

    left, bottom, board_pixel_width, board_pixel_height = renderer.board_area(4, 3, 20)

    assert (board_pixel_width, board_pixel_height) == (80, 60)
    assert left == (900 - 80) / 2
    assert bottom == (960 - 60 - 60) / 2


def test_a_cell_becomes_the_pixel_corner_arcade_draws_from():
    renderer = make_renderer()

    assert renderer.cell_to_pixels((0, 0), 4, 3, 20) == (410, 460)
    assert renderer.cell_to_pixels((1, 1), 4, 3, 20) == (430, 440)


def test_the_top_row_of_the_grid_is_drawn_highest_on_the_screen():
    # Grid rows count downwards, while Arcade's y axis counts upwards.
    renderer = make_renderer()

    _, top_row_y = renderer.cell_to_pixels((0, 0), 4, 3, 20)
    _, bottom_row_y = renderer.cell_to_pixels((0, 2), 4, 3, 20)

    assert top_row_y > bottom_row_y


def test_the_tile_size_only_changes_the_pixels_not_the_cells():
    small_tiles = make_renderer().cell_to_pixels((2, 1), 4, 3, 20)
    large_tiles = make_renderer().cell_to_pixels((2, 1), 4, 3, 40)

    assert small_tiles != large_tiles
