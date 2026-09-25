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
# Records Games tab controls: title, Board and Speed row, tabs, Player
# filters, summary, paging and Back. Whole record rows fill the rest.
RECORDS_FIXED_HEIGHT = 494
RECORD_ROW_HEIGHT = 48


def layout_step(window_width):
    """Choose one of the two readable type layouts for this window."""
    return "compact" if window_width < COMPACT_WIDTH else "regular"


def record_rows_per_page(window_height):
    """Leave room for Records controls and fit whole two-line rows below them."""
    return max(1, (window_height - RECORDS_FIXED_HEIGHT) // RECORD_ROW_HEIGHT)


# Records Analytics charts are this wide, which fits the minimum window width.
CHART_WIDTH = 620
# Height used on each tab by everything except its chart, and the chart's limits.
# On Compare, the Player table grows by one row per Player, so its rows are
# counted separately from everything else on the tab.
COMPARE_FIXED_HEIGHT = 392
COMPARE_ROW_HEIGHT = 27
COMPARE_CHART_HEIGHTS = (100, 300)
# On Trends, the fixed height includes one legend row; the legend wraps after
# this many Players, and each further row is counted separately.
TRENDS_FIXED_HEIGHT = 380
TREND_LEGEND_PER_ROW = 4
TREND_LEGEND_ROW_HEIGHT = 27
TREND_CHART_HEIGHTS = (160, 400)


def compare_chart_height(window_height, player_rows):
    """
    The Compare bar chart fills the height left under the Player table, or
    None when too little is left to read it, so the tab never runs off the
    window.
    """
    shortest, tallest = COMPARE_CHART_HEIGHTS
    height_left = window_height - COMPARE_FIXED_HEIGHT - player_rows * COMPARE_ROW_HEIGHT

    if (height_left < shortest):
        return None

    return min(tallest, height_left)


def trend_legend_rows(player_count):
    """How many rows the Trends legend needs, so it never runs off the window's sides."""
    return max(1, -(-player_count // TREND_LEGEND_PER_ROW))   # rounds up


def trend_chart_height(window_height, legend_rows):
    """The Trends chart fills the height left under the tabs and its legend."""
    shortest, tallest = TREND_CHART_HEIGHTS
    extra_legend_height = (legend_rows - 1) * TREND_LEGEND_ROW_HEIGHT
    return max(shortest, min(tallest, window_height - TRENDS_FIXED_HEIGHT - extra_legend_height))


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
