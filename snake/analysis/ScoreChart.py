"""Draw a group's scores as one histogram per bot, in a static SVG.

The Markdown report links to this file, so it shows on GitHub. Across is the
score a game ended with, in ranges of BIN_WIDTH; up is how many games ended
there. Every panel shares one scale, and the SVG follows the viewer's light or
dark setting. Each bar has a tooltip with its count.
"""

from html import escape

from snake.analysis import ReportColors


WIDTH = 760
# Space around the whole chart, so names and the last ticks are never cut off.
MARGIN = 16
COLUMNS = 3
GAP = 20
PANEL_HEIGHT = 214
# Inside a panel: the name at the top, then the plot with room for both axes.
NAME_HEIGHT = 26
AXIS_LEFT = 34
AXIS_BOTTOM = 34
TITLE_HEIGHT = 20
# The axis shows at most this many steps after zero.
MAX_TICKS = 6
# Histograms count games in score ranges of this width.
BIN_WIDTH = 10

CHART_STYLE = f"""
.bot-chart {{ --surface: #FFFFFF; --text: #14171C; --muted: {ReportColors.LIGHT_TEXT_MUTED};
  --grid: #E6E9EE; font: 12px ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }}
@media (prefers-color-scheme: dark) {{
  .bot-chart {{ --surface: #161A1F; --text: #ECEEF2; --muted: #A3AAB6; --grid: #2A3038; }}
}}
.bot-chart .background {{ fill: var(--surface); }}
.bot-chart .name {{ fill: var(--text); font-weight: 600; font-size: 13px; }}
.bot-chart .axis {{ fill: var(--muted); }}
.bot-chart .grid {{ stroke: var(--grid); stroke-width: 1; }}
.bot-chart .baseline {{ stroke: var(--muted); stroke-width: 1; }}
"""


def score_bins(scores, count):
    """How many games ended in each score range of BIN_WIDTH, from 0 upwards."""
    bins = [0] * count
    for score in scores:
        bins[score // BIN_WIDTH] += 1
    return bins


def bin_label(index):
    return f"{index * BIN_WIDTH} to {index * BIN_WIDTH + BIN_WIDTH - 1}"


def axis_ticks(highest):
    """Round tick values from zero to just past the highest value.

    The step is 1, 2, or 5 times a power of ten: the smallest that needs at
    most MAX_TICKS steps.
    """
    power = 1
    while True:
        for step in (power, 2 * power, 5 * power):
            steps = max(1, -(-highest // step))
            if steps <= MAX_TICKS:
                return [step * number for number in range(steps + 1)]
        power *= 10


def bot_style(number, label):
    """Each bot's bars in its own colour, deeper on a light page."""
    light = ReportColors.bot_color(label, light=True)
    dark = ReportColors.bot_color(label)
    return (f".bot-chart .bars-{number} {{ fill: {light}; }}\n"
            f"@media (prefers-color-scheme: dark) {{ .bot-chart .bars-{number} {{ fill: {dark}; }} }}\n")


def score_chart_svg(title, rows, bin_count):
    """Histograms of each row's scores; rows are RunSummary values, best first."""
    bins = [score_bins(row.scores, bin_count) for row in rows]
    y_ticks = axis_ticks(max(max(counts) for counts in bins))
    x_ticks = axis_ticks(bin_count * BIN_WIDTH)
    x_end = x_ticks[-1]
    panel_width = (WIDTH - 2 * MARGIN - GAP * (COLUMNS - 1)) / COLUMNS
    row_count = -(-len(rows) // COLUMNS)
    height = MARGIN + TITLE_HEIGHT + row_count * PANEL_HEIGHT + (row_count - 1) * GAP + MARGIN

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="bot-chart" '
        f'viewBox="0 0 {WIDTH} {height:.0f}" width="{WIDTH}" height="{height:.0f}" '
        f'role="img" aria-label="{escape(title)}">',
        f"<title>{escape(title)}</title>",
        "<style>" + CHART_STYLE
        + "".join(bot_style(number, row.bot) for number, row in enumerate(rows)) + "</style>",
        f'<rect class="background" width="{WIDTH}" height="{height:.0f}" rx="8"/>',
    ]
    for number, (row, counts) in enumerate(zip(rows, bins)):
        left = MARGIN + (number % COLUMNS) * (panel_width + GAP)
        top = MARGIN + (number // COLUMNS) * (PANEL_HEIGHT + GAP)
        plot_left = left + AXIS_LEFT
        plot_right = left + panel_width - 4
        # Room above the plot for the "Games" axis title, clear of the top tick.
        plot_top = top + NAME_HEIGHT + 22
        plot_bottom = top + PANEL_HEIGHT - AXIS_BOTTOM

        def x(score):
            return plot_left + (plot_right - plot_left) * score / x_end

        def y(games):
            return plot_bottom - (plot_bottom - plot_top) * games / y_ticks[-1]

        parts.append(f'<text class="name" x="{left:.1f}" y="{top + 16:.1f}">'
                     f"{escape(row.bot)}</text>")
        parts.append(f'<text class="axis" x="{left:.1f}" y="{plot_top - 12:.1f}">Games</text>')
        for games in y_ticks:
            parts.append(f'<line class="grid" x1="{plot_left:.1f}" x2="{plot_right:.1f}" '
                         f'y1="{y(games):.1f}" y2="{y(games):.1f}"/>')
            parts.append(f'<text class="axis" x="{plot_left - 6:.1f}" y="{y(games) + 4:.1f}" '
                         f'text-anchor="end">{games}</text>')
        for index, games in enumerate(counts):
            if not games:
                continue
            bar_left = x(index * BIN_WIDTH) + 1
            bar_width = max(x((index + 1) * BIN_WIDTH) - x(index * BIN_WIDTH) - 2, 1)
            parts.append(
                f'<rect class="bars-{number}" x="{bar_left:.1f}" y="{y(games):.1f}" '
                f'width="{bar_width:.1f}" height="{plot_bottom - y(games):.1f}" rx="2">'
                f"<title>{escape(row.bot)}: {games} games scored {bin_label(index)}</title></rect>"
            )
        parts.append(f'<line class="baseline" x1="{plot_left:.1f}" x2="{plot_right:.1f}" '
                     f'y1="{plot_bottom:.1f}" y2="{plot_bottom:.1f}"/>')
        for score in x_ticks:
            # The last tick ends at the edge rather than centring past it.
            anchor = "end" if score == x_end else "middle"
            parts.append(f'<text class="axis" x="{x(score):.1f}" y="{plot_bottom + 15:.1f}" '
                         f'text-anchor="{anchor}">{score}</text>')
        parts.append(f'<text class="axis" x="{(plot_left + plot_right) / 2:.1f}" '
                     f'y="{plot_bottom + 30:.1f}" text-anchor="middle">Score (food eaten)</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
