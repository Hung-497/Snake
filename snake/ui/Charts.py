import arcade
import arcade.gui

from snake.ui import Theme
from snake.ui.PlayerLabels import player_label


# Space around the plot for the axis labels, in pixels.
LEFT_MARGIN = 44
RIGHT_MARGIN = 12
TOP_MARGIN = 20
BOTTOM_MARGIN = 24
# A bar is never wider than this, even with only one Player.
WIDEST_BAR = 56
# The best-score line reaches this far past each side of its bar.
BEST_LINE_OVERHANG = 6


class ScoreBarChart(arcade.gui.UIWidget):
    """
    The Compare tab's bar chart: one bar per Player for its average score,
    with a line across it at its best score.

    It only draws the statistics rows it is given; RecordsBrowser works them
    out. Everything is drawn relative to the chart's own corner.
    """

    def __init__(self, rows, width, height, font_size):
        super().__init__(width=width, height=height)
        self.rows = rows
        self.font_size = font_size

    def do_render(self, surface):
        self.prepare_render(surface)

        left, right = LEFT_MARGIN, self.width - RIGHT_MARGIN
        bottom, top = BOTTOM_MARGIN, self.height - TOP_MARGIN
        # Scale to the best score, so every best-score line fits.
        highest = max(max(row["best_score"] for row in self.rows), 1)

        draw_value_axis(left, right, bottom, top, highest, self.font_size)

        slot_width = (right - left) / len(self.rows)
        bar_width = min(WIDEST_BAR, slot_width * 0.5)

        for index, row in enumerate(self.rows):
            color = Theme.player_color(row["player"])
            center = left + slot_width * (index + 0.5)
            average_top = bottom + row["average_score"] / highest * (top - bottom)
            best_height = bottom + row["best_score"] / highest * (top - bottom)

            arcade.draw_lrbt_rectangle_filled(center - bar_width / 2, center + bar_width / 2,
                                              bottom, max(average_top, bottom + 1), color)
            arcade.draw_line(center - bar_width / 2 - BEST_LINE_OVERHANG, best_height,
                             center + bar_width / 2 + BEST_LINE_OVERHANG, best_height,
                             Theme.TEXT, 2)
            draw_chart_text(f"{row['average_score']:.1f} / {row['best_score']}",
                            center, max(average_top, best_height) + 4,
                            Theme.TEXT, self.font_size)
            draw_chart_text(player_label(row["player"]), center, bottom - self.font_size - 8,
                            Theme.TEXT_MUTED, self.font_size)


class TrendChart(arcade.gui.UIWidget):
    """
    The Trends tab's chart: one smoothed score line per Player.

    Lines are aligned on the right, so every Player's latest game sits at the
    right edge even when Players have played different numbers of games.
    """

    def __init__(self, trends, width, height, font_size):
        super().__init__(width=width, height=height)
        self.trends = trends
        self.font_size = font_size

    def do_render(self, surface):
        self.prepare_render(surface)

        left, right = LEFT_MARGIN, self.width - RIGHT_MARGIN
        bottom, top = BOTTOM_MARGIN, self.height - TOP_MARGIN
        longest = max(len(trend["points"]) for trend in self.trends)
        highest = max(max(max(trend["points"]) for trend in self.trends), 1)

        draw_value_axis(left, right, bottom, top, highest, self.font_size)
        span_text = "Latest game" if longest == 1 else f"Last {longest} games, oldest to latest"
        draw_chart_text(span_text, (left + right) / 2,
                        bottom - self.font_size - 8, Theme.TEXT_MUTED, self.font_size)

        # With one game there is no width to spread over, so it sits at the right.
        step = (right - left) / (longest - 1) if longest > 1 else 0

        for trend in self.trends:
            color = Theme.player_color(trend["player"])
            points = trend["points"]
            first_slot = longest - len(points)
            line = [
                (left + (first_slot + index) * step if longest > 1 else right,
                 bottom + value / highest * (top - bottom))
                for index, value in enumerate(points)
            ]

            if (len(line) == 1):
                arcade.draw_circle_filled(line[0][0], line[0][1], 4, color)
            else:
                arcade.draw_line_strip(line, color, 2)


def draw_value_axis(left, right, bottom, top, highest, font_size):
    """The baseline and value axis, labelled 0 at the bottom and the highest value at the top."""
    arcade.draw_line(left, bottom, right, bottom, Theme.BORDER, 1)
    arcade.draw_line(left, bottom, left, top, Theme.BORDER, 1)
    draw_chart_text("0", left - 6, bottom - font_size / 2, Theme.TEXT_MUTED, font_size,
                    anchor_x="right")
    draw_chart_text(f"{highest:.0f}", left - 6, top - font_size / 2, Theme.TEXT_MUTED,
                    font_size, anchor_x="right")


def draw_chart_text(text, x, y, color, font_size, anchor_x="center"):
    # A chart only draws when the Records App View is rebuilt, so a Text made
    # here is not recreated every frame.
    arcade.Text(text, x, y, color, font_size=font_size, font_name=Theme.FONT_REGULAR,
                anchor_x=anchor_x).draw()
