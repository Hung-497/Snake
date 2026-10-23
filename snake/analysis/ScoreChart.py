"""Draw a group's score distributions as a static SVG box plot.

The same SVG is saved as a file for the Markdown report and placed inside the
HTML report. It uses the app's dark board colours and each bot's own colour,
so it looks the same wherever it is shown, and each row has a tooltip with its
numbers.
"""

from html import escape

from snake.analysis import ReportColors


WIDTH = 760
LABEL_WIDTH = 270
RIGHT_MARGIN = 24
TOP = 16
ROW_HEIGHT = 34
AXIS_HEIGHT = 44
# The key under the axis that says what each mark means.
KEY_HEIGHT = 30
KEY_ICON_WIDTH = 28
KEY_GAP = 26
# A rough width per character of the 12px key text, to place the next item.
KEY_CHARACTER_WIDTH = 6.6
BOX_HEIGHT = 14
# The axis shows at most this many steps after zero.
MAX_TICKS = 6

# Each box takes its bot's colour from the app; the row label still names
# the bot, so colour is never the only way to tell rows apart.
CHART_STYLE = f"""
.bot-chart {{ --surface: {ReportColors.SURFACE_RAISED}; --text: {ReportColors.TEXT};
  --muted: {ReportColors.TEXT_MUTED}; --grid: {ReportColors.BORDER};
  font: 12px Inter, ui-sans-serif, system-ui, sans-serif; }}
.bot-chart .background {{ fill: var(--surface); }}
.bot-chart .label {{ fill: var(--text); }}
.bot-chart .key {{ fill: var(--muted); }}
.bot-chart .axis {{ fill: var(--muted); }}
.bot-chart .grid {{ stroke: var(--grid); stroke-width: 1; }}
.bot-chart .whisker {{ stroke: var(--muted); stroke-width: 2; }}
.bot-chart .box {{ fill: var(--muted); }}
.bot-chart .median {{ stroke: var(--surface); stroke-width: 2; }}
.bot-chart .mean {{ fill: var(--surface); stroke: var(--text); stroke-width: 2; }}
"""


def axis_ticks(highest_score):
    """Round tick values from zero to just past the highest score.

    The step is 1, 2, or 5 times a power of ten: the smallest that needs at
    most MAX_TICKS steps.
    """
    power = 1
    while True:
        for step in (power, 2 * power, 5 * power):
            steps = max(1, -(-highest_score // step))
            if steps <= MAX_TICKS:
                return [step * number for number in range(steps + 1)]
        power *= 10


def key_icon(kind, left, middle):
    """A small copy of one chart mark, drawn the same way as in the rows."""
    right = left + KEY_ICON_WIDTH
    box_top = middle - BOX_HEIGHT / 2
    if kind == "whisker":
        return [f'<line class="whisker" x1="{left}" y1="{middle}" x2="{right}" y2="{middle}"/>']
    box = (f'<rect class="box" x="{left}" y="{box_top}" width="{KEY_ICON_WIDTH}" '
           f'height="{BOX_HEIGHT}" rx="4"/>')
    if kind == "box":
        return [box]
    if kind == "median":
        centre = left + KEY_ICON_WIDTH / 2
        return [box, f'<line class="median" x1="{centre}" y1="{box_top}" '
                     f'x2="{centre}" y2="{box_top + BOX_HEIGHT}"/>']
    return [f'<circle class="mean" cx="{left + KEY_ICON_WIDTH / 2}" cy="{middle}" r="4"/>']


KEY_ITEMS = (
    ("whisker", "Lowest to best score"),
    ("box", "Middle half of games"),
    ("median", "Median"),
    ("mean", "Mean"),
)


def chart_key(middle):
    parts = []
    left = 24
    for kind, text in KEY_ITEMS:
        parts += key_icon(kind, left, middle)
        text_left = left + KEY_ICON_WIDTH + 8
        parts.append(f'<text class="key" x="{text_left}" y="{middle + 4}">{text}</text>')
        left = round(text_left + len(text) * KEY_CHARACTER_WIDTH + KEY_GAP)
    return parts


def score_chart_svg(title, rows):
    """A box plot of each row's scores; rows are RunSummary values."""
    ticks = axis_ticks(max(row.best_score for row in rows))
    axis_end = ticks[-1]
    plot_width = WIDTH - LABEL_WIDTH - RIGHT_MARGIN
    height = TOP + ROW_HEIGHT * len(rows) + AXIS_HEIGHT + KEY_HEIGHT

    def x(score):
        return LABEL_WIDTH + plot_width * score / axis_end

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="bot-chart" '
        f'viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" '
        f'role="img" aria-label="{escape(title)}">',
        f"<title>{escape(title)}</title>",
        f"<style>{CHART_STYLE}</style>",
        f'<rect class="background" width="{WIDTH}" height="{height}" rx="4"/>',
    ]
    plot_bottom = TOP + ROW_HEIGHT * len(rows)
    for score in ticks:
        tick_x = f"{x(score):.1f}"
        parts.append(
            f'<line class="grid" x1="{tick_x}" y1="{TOP}" x2="{tick_x}" y2="{plot_bottom}"/>'
        )
        parts.append(
            f'<text class="axis" x="{tick_x}" y="{plot_bottom + 16}" '
            f'text-anchor="middle">{score}</text>'
        )
    parts.append(
        f'<text class="axis" x="{LABEL_WIDTH + plot_width / 2:.1f}" y="{plot_bottom + 34}" '
        f'text-anchor="middle">Score per game</text>'
    )

    for number, row in enumerate(rows):
        middle = TOP + ROW_HEIGHT * number + ROW_HEIGHT / 2
        box_top = middle - BOX_HEIGHT / 2
        tooltip = (
            f"{row.label}: lowest {row.min_score}, middle half {row.lower_quartile:g}–"
            f"{row.upper_quartile:g}, median {row.median_score:g}, mean {row.mean_score:.1f}, "
            f"best {row.best_score}"
        )
        box_width = max(x(row.upper_quartile) - x(row.lower_quartile), 2)
        # Several bot files of one bot share a name; the file tells them apart.
        label = row.label
        if len(row.bot_file) == 8:
            label = f"{row.label} · {row.bot_file}"
        parts += [
            f"<g><title>{escape(tooltip)}</title>",
            f'<rect x="0" y="{middle - ROW_HEIGHT / 2:.1f}" width="{WIDTH}" '
            f'height="{ROW_HEIGHT}" fill="transparent"/>',
            f'<text class="label" x="{LABEL_WIDTH - 12}" y="{middle + 4:.1f}" '
            f'text-anchor="end">{escape(label)}</text>',
            f'<line class="whisker" x1="{x(row.min_score):.1f}" y1="{middle:.1f}" '
            f'x2="{x(row.best_score):.1f}" y2="{middle:.1f}"/>',
            f'<rect class="box" x="{x(row.lower_quartile):.1f}" y="{box_top:.1f}" '
            f'width="{box_width:.1f}" height="{BOX_HEIGHT}" rx="4" '
            f'style="fill: {ReportColors.bot_color(row.bot)}"/>',
            f'<line class="median" x1="{x(row.median_score):.1f}" y1="{box_top:.1f}" '
            f'x2="{x(row.median_score):.1f}" y2="{box_top + BOX_HEIGHT:.1f}"/>',
            f'<circle class="mean" cx="{x(row.mean_score):.1f}" cy="{middle:.1f}" r="4"/>',
            "</g>",
        ]
    parts += chart_key(height - KEY_HEIGHT / 2)
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
