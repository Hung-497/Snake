"""
Tests for working out where the Board Area sits in the window.

This is pure arithmetic over plain numbers: no window, no Arcade, no display.
It is the one place that decides where the board goes and how a grid cell
becomes a pixel, so everything about that lives here.
"""

import pytest

from WindowLayout import HUD_HEIGHT, layout_board


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 960


def make_layout(board_width=4, board_height=3, tile_size=20, window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT):
    return layout_board(window_width, window_height, board_width, board_height, tile_size)


def test_the_board_takes_its_size_from_the_board_and_the_tile_size():
    layout = make_layout(board_width=4, board_height=3, tile_size=20)

    assert (layout.width, layout.height) == (80, 60)


def test_the_board_is_centred_in_the_space_below_the_score_line():
    layout = make_layout(board_width=4, board_height=3, tile_size=20)

    assert layout.left == (WINDOW_WIDTH - 80) / 2
    assert layout.bottom == (WINDOW_HEIGHT - HUD_HEIGHT - 60) / 2


def test_a_cell_becomes_the_pixel_corner_arcade_draws_from():
    layout = make_layout(board_width=4, board_height=3, tile_size=20)

    assert layout.cell_to_pixels((0, 0)) == (410, 460)
    assert layout.cell_to_pixels((1, 1)) == (430, 440)


def test_the_top_row_of_the_grid_is_drawn_highest_on_the_screen():
    # Grid rows count downwards, while Arcade's y axis counts upwards.
    layout = make_layout(board_width=4, board_height=3, tile_size=20)

    _, top_row_y = layout.cell_to_pixels((0, 0))
    _, bottom_row_y = layout.cell_to_pixels((0, 2))

    assert top_row_y > bottom_row_y


def test_the_last_cell_sits_inside_the_board():
    layout = make_layout(board_width=4, board_height=3, tile_size=20)

    x, y = layout.cell_to_pixels((3, 2))

    assert x + layout.tile_size == layout.left + layout.width
    assert y == layout.bottom


def test_a_bigger_tile_size_makes_a_bigger_board_from_the_same_cells():
    small = make_layout(tile_size=20)
    large = make_layout(tile_size=40)

    assert (large.width, large.height) == (small.width * 2, small.height * 2)


def test_the_board_stays_centred_when_the_window_changes():
    narrow = make_layout(window_width=700)
    wide = make_layout(window_width=1100)

    assert narrow.left == (700 - narrow.width) / 2
    assert wide.left == (1100 - wide.width) / 2


@pytest.mark.parametrize("board", [(16, 16), (24, 25), (30, 30), (25, 25)])
def test_every_supported_board_is_centred(board):
    board_width, board_height = board

    layout = layout_board(WINDOW_WIDTH, WINDOW_HEIGHT, board_width, board_height, 25)

    assert layout.left == (WINDOW_WIDTH - layout.width) / 2
    assert layout.bottom == (WINDOW_HEIGHT - HUD_HEIGHT - layout.height) / 2
