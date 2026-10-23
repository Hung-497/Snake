"""Draw a group's score distributions as a static SVG box plot.

The same SVG is saved as a file for the Markdown report and placed inside the
HTML report. It carries its own light and dark colours, so it reads well
wherever it is shown, and each row has a tooltip with its numbers.
"""

from html import escape


WIDTH = 760
LABEL_WIDTH = 270
RIGHT_MARGIN = 24
TOP = 16
ROW_HEIGHT = 34
AXIS_HEIGHT = 44
BOX_HEIGHT = 14
# The axis shows at most this many steps after zero.
MAX_TICKS = 6

# Colours from the data-visualisation reference palette: one series colour,
# because the row label, not the colour, says which bot a row is.
CHART_STYLE = """
.bot-chart { --surface: #fcfcfb; --text: #0b0b0b; --muted: #52514e;
  --grid: #e4e3df; --series: #2a78d6; }
@media (prefers-color-scheme: dark) {
  .bot-chart { --surface: #1a1a19; --text: #f0efec; --muted: #c3c2b7;
    --grid: #3a3936; --series: #3987e5; }
}
.bot-chart { font: 12px system-ui, sans-serif; }
.bot-chart .background { fill: var(--surface); }
.bot-chart .label { fill: var(--text); }
.bot-chart .axis { fill: var(--muted); }
.bot-chart .grid { stroke: var(--grid); stroke-width: 1; }
.bot-chart .whisker { stroke: var(--muted); stroke-width: 2; }
.bot-chart .box { fill: var(--series); }
.bot-chart .median { stroke: var(--surface); stroke-width: 2; }
.bot-chart .mean { fill: var(--text); stroke: var(--surface); stroke-width: 2; }
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


def score_chart_svg(title, rows):
    """A box plot of each row's scores; rows are RunSummary values."""
    ticks = axis_ticks(max(row.best_score for row in rows))
    axis_end = ticks[-1]
    plot_width = WIDTH - LABEL_WIDTH - RIGHT_MARGIN
    height = TOP + ROW_HEIGHT * len(rows) + AXIS_HEIGHT

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
            f'width="{box_width:.1f}" height="{BOX_HEIGHT}" rx="4"/>',
            f'<line class="median" x1="{x(row.median_score):.1f}" y1="{box_top:.1f}" '
            f'x2="{x(row.median_score):.1f}" y2="{box_top + BOX_HEIGHT:.1f}"/>',
            f'<circle class="mean" cx="{x(row.mean_score):.1f}" cy="{middle:.1f}" r="4"/>',
            "</g>",
        ]
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
