"""
Where things sit in the window.

This is the one place that turns a window size into positions, and the only
place that turns a grid cell into pixels. It is plain arithmetic: no Arcade,
no window object, nothing that needs a display. Keeping it separate means the
renderer and the App Views cannot disagree about where the board is.
"""

from dataclasses import dataclass


# Room at the top of the window for the score line.
HUD_HEIGHT = 60
MIN_WINDOW_WIDTH = 700
MIN_WINDOW_HEIGHT = 700
MIN_READABLE_TILE_SIZE = 16
COMPACT_WIDTH = 800
RECORDS_FIXED_HEIGHT = 390
RECORD_ROW_HEIGHT = 48


def layout_step(window_width):
    """Choose one of the two readable type layouts for this window."""
    return "compact" if window_width < COMPACT_WIDTH else "regular"


def record_rows_per_page(window_height):
    """Leave room for Records controls and fit whole two-line rows below them."""
    return max(1, (window_height - RECORDS_FIXED_HEIGHT) // RECORD_ROW_HEIGHT)


def minimum_window_size(board_width, board_height, preferred_tile_size):
    """The window must fit both the app floor and a readable board."""
    readable_tile_size = min(preferred_tile_size, MIN_READABLE_TILE_SIZE)
    return (
        max(MIN_WINDOW_WIDTH, board_width * readable_tile_size),
        max(MIN_WINDOW_HEIGHT, board_height * readable_tile_size + HUD_HEIGHT),
    )


def view_label_positions(window_width, window_height, result_score_gap):
    """Positions for the score line and the two result lines."""
    center_x = window_width / 2
    center_y = window_height / 2
    return {
        "score": (center_x, window_height - HUD_HEIGHT + 4),
        "bot_mode": (16, window_height - HUD_HEIGHT + 35),
        "result": (center_x, center_y),
        "result_score": (center_x, center_y - result_score_gap),
    }


@dataclass(frozen=True)
class BoardLayout:
    """The Board Area: where the board is drawn, in pixels."""

    left: float
    bottom: float
    width: float
    height: float
    tile_size: int

    def cell_to_pixels(self, cell):
        """
        The pixel corner Arcade draws a grid cell from.

        Grid rows count downwards from the top of the board, while Arcade's y
        axis counts upwards from the bottom of the window, so the row is
        flipped here.
        """
        column, row = cell

        x = self.left + column * self.tile_size
        y = self.bottom + self.height - (row + 1) * self.tile_size

        return x, y


def layout_board(window_width, window_height, board_width, board_height, tile_size, hud_height=HUD_HEIGHT):
    """Fit the preferred Tile Size into the window, then centre the Board Area."""
    fitted_tile_size = max(
        1,
        min(tile_size, window_width // board_width,
            (window_height - hud_height) // board_height),
    )
    board_pixel_width = board_width * fitted_tile_size
    board_pixel_height = board_height * fitted_tile_size

    return BoardLayout(
        left=(window_width - board_pixel_width) / 2,
        bottom=(window_height - hud_height - board_pixel_height) / 2,
        width=board_pixel_width,
        height=board_pixel_height,
        tile_size=fitted_tile_size,
    )
