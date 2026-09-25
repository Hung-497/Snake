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
    """Work out the Board Area for a board of this size in a window of this size."""
    board_pixel_width = board_width * tile_size
    board_pixel_height = board_height * tile_size

    return BoardLayout(
        left=(window_width - board_pixel_width) / 2,
        bottom=(window_height - hud_height - board_pixel_height) / 2,
        width=board_pixel_width,
        height=board_pixel_height,
        tile_size=tile_size,
    )
