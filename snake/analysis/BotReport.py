"""Turn experiment runs into a Bot Report, written as Markdown and as HTML.

Both files are written from the same BotReport, so they always show the same
numbers. Nothing here depends on the time it runs, so the same runs always
give the same files.
"""

from dataclasses import dataclass
from html import escape
import statistics

from snake.analysis.ScoreChart import score_chart_svg
from snake.bots.BotModeCatalogue import BOT_MODES, FAMILY_LABELS


BOT_MODES_BY_KEY = {mode.key: mode for mode in BOT_MODES}
LABELS_BY_VERSION = {(mode.family, mode.version): mode.label for mode in BOT_MODES}

OVERVIEW_HEADINGS = (
    "Bot", "Bot file", "Run date (UTC)", "Games", "Mean", "Median", "Best", "Std dev",
    "Win rate", "Move-limit rate", "Moves per point",
)
PROVENANCE_HEADINGS = (
    "Bot", "Bot file", "Feature Set", "Games trained", "Trained by", "Training seeds", "Code",
)
# Shown where a field does not apply, such as a non-learning bot's Feature Set.
NOT_APPLICABLE = "—"
UNKNOWN = "unknown"
# The Markdown links to each group's chart in this folder, next to it.
CHART_FOLDER = "bot_report_charts"


@dataclass(frozen=True)
class RunSummary:
    label: str
    bot_file: str
    created_at: str
    game_count: int
    mean_score: float
    median_score: float
    best_score: int
    score_std_dev: float
    win_rate: float
    move_limit_rate: float
    min_score: int
    lower_quartile: float
    upper_quartile: float
    # None when no game scored, as there is no point to divide by.
    moves_per_point: float | None


@dataclass(frozen=True)
class ConditionsGroup:
    title: str
    rows: tuple
    provenance: tuple


@dataclass(frozen=True)
class BotReport:
    run_count: int
    skipped_files: int
    groups: tuple


def build_bot_report(runs, skipped_files):
    """Group runs by Experiment Conditions and summarise each run from its games."""
    runs_by_conditions = {}
    for run in runs:
        runs_by_conditions.setdefault(run.conditions, []).append(run)

    groups = []
    run_count = 0
    for conditions in sorted(runs_by_conditions):
        newest = newest_runs(runs_by_conditions[conditions])
        run_count += len(newest)
        groups.append(ConditionsGroup(
            conditions_title(conditions), summary_rows(newest),
            tuple(provenance_cells(run) for run in newest),
        ))
    return BotReport(run_count, skipped_files, tuple(groups))


def bot_label(run):
    """The app's name for the bot, using its Feature Set when the report has one.

    Terminal experiments save any DQN model as "dqn", so the Feature Set, not
    the name, says whether it was DQN v2 or v3.
    """
    mode = BOT_MODES_BY_KEY.get(run.bot_mode)
    if mode is None:
        return run.bot_mode
    if mode.family is None or run.bot_file is None or run.bot_file.feature_set is None:
        return mode.label
    feature_set = run.bot_file.feature_set
    return LABELS_BY_VERSION.get(
        (mode.family, feature_set), f"{FAMILY_LABELS[mode.family]} {feature_set}",
    )


def is_learning(run):
    mode = BOT_MODES_BY_KEY.get(run.bot_mode)
    return run.bot_file is not None or (mode is not None and mode.family is not None)


def file_key(run):
    """Runs with the same key played the same bot; only the newest is kept.

    A non-learning bot has no file, so each of its runs shares one key.
    """
    return (bot_label(run), run.bot_file.sha256 if run.bot_file else None)


def newest_runs(runs):
    newest = {}
    for run in runs:
        key = file_key(run)
        if key not in newest or run.created_at > newest[key].created_at:
            newest[key] = run
    return sorted(
        newest.values(),
        key=lambda run: (bot_label(run), run.created_at, file_key(run)[1] or ""),
    )


def short_file(run):
    if run.bot_file is not None:
        return run.bot_file.sha256[:8]
    return UNKNOWN if is_learning(run) else NOT_APPLICABLE


def summary_rows(runs):
    """One row per run, then a combined row for a bot with several bot files."""
    rows = []
    runs_by_label = {}
    for run in runs:
        runs_by_label.setdefault(bot_label(run), []).append(run)
    for label in sorted(runs_by_label):
        label_runs = runs_by_label[label]
        for run in label_runs:
            rows.append(summarize_games(
                label, short_file(run), run.created_at.strftime("%Y-%m-%d %H:%M"), run.games,
            ))
        if len(label_runs) > 1:
            pooled = [game for run in label_runs for game in run.games]
            rows.append(summarize_games(
                f"{label} combined ({len(label_runs)} bot files)", NOT_APPLICABLE,
                NOT_APPLICABLE, pooled,
            ))
    return tuple(rows)


def summarize_games(label, bot_file, created_at, games):
    scores = [game.score for game in games]
    outcomes = [game.outcome for game in games]
    # The middle half of games lies between the lower and upper quartile.
    if len(scores) > 1:
        lower_quartile, _, upper_quartile = statistics.quantiles(
            scores, n=4, method="inclusive",
        )
    else:
        lower_quartile = upper_quartile = scores[0]
    total_score = sum(scores)
    return RunSummary(
        label=label,
        bot_file=bot_file,
        created_at=created_at,
        game_count=len(scores),
        mean_score=statistics.mean(scores),
        median_score=statistics.median(scores),
        best_score=max(scores),
        score_std_dev=statistics.pstdev(scores),
        win_rate=outcomes.count("won") / len(outcomes),
        move_limit_rate=outcomes.count("move_limit") / len(outcomes),
        min_score=min(scores),
        lower_quartile=lower_quartile,
        upper_quartile=upper_quartile,
        moves_per_point=(
            sum(game.moves for game in games) / total_score if total_score else None
        ),
    )


def provenance_cells(run):
    code = run.code_version or UNKNOWN
    if not is_learning(run):
        return (bot_label(run), *[NOT_APPLICABLE] * 5, code)
    bot_file = run.bot_file
    if bot_file is None:
        return (bot_label(run), *[UNKNOWN] * 5, code)
    return (
        bot_label(run),
        short_file(run),
        bot_file.feature_set or UNKNOWN,
        UNKNOWN if bot_file.games_trained is None else str(bot_file.games_trained),
        bot_file.trained_by or UNKNOWN,
        ", ".join(str(seed) for seed in bot_file.training_seeds) or UNKNOWN,
        code,
    )


def conditions_title(conditions):
    seeds = conditions.seeds
    games = f"{len(seeds)} game" + ("" if len(seeds) == 1 else "s")
    if list(seeds) == list(range(seeds[0], seeds[0] + len(seeds))):
        seed_text = f"seeds {seeds[0]}–{seeds[-1]}" if len(seeds) > 1 else f"seed {seeds[0]}"
    else:
        seed_text = f"{len(seeds)} listed seeds starting at {seeds[0]}"
    return (
        f"{conditions.width} × {conditions.height} board, "
        f"{conditions.max_moves}-move limit, {seed_text} ({games})"
    )


def row_cells(row):
    return (
        row.label, row.bot_file, row.created_at, str(row.game_count), f"{row.mean_score:.1f}",
        f"{row.median_score:.1f}", str(row.best_score), f"{row.score_std_dev:.1f}",
        f"{row.win_rate:.1%}", f"{row.move_limit_rate:.1%}",
        NOT_APPLICABLE if row.moves_per_point is None else f"{row.moves_per_point:.1f}",
    )


def source_sentence(report):
    runs = f"{report.run_count} run" + ("" if report.run_count == 1 else "s")
    groups = len(report.groups)
    text = f"Built from {runs} in {groups} group" + ("" if groups == 1 else "s") + (
        " of Experiment Conditions. Runs are only compared inside the same group."
    )
    if report.skipped_files:
        text += (
            f" {report.skipped_files} report file"
            + (" was" if report.skipped_files == 1 else "s were")
            + " skipped (damaged, incomplete, or an older format)."
        )
    return text


READING_NOTES = (
    "Every number is computed from the saved games. The Move-limit rate is the "
    "share of games stopped by the move limit rather than ended by a win or a "
    "collision. Moves per point is how many moves the bot needed for each point "
    "of score; a high value with a high Move-limit rate suggests circling "
    "instead of chasing food.",
    "In each chart the line runs from the lowest to the best score, the box holds "
    "the middle half of the games, the line inside the box is the median, and the "
    "dot is the mean.",
    "A bot file is the saved Q-table or DQN model, shown by the start of its "
    "hash. When the same bot file was evaluated more than once, only its newest "
    "run is shown. A combined row pools the games of every bot file of that bot.",
)


def markdown_table(headings, rows):
    lines = ["| " + " | ".join(headings) + " |"]
    lines.append("|" + "|".join(" --- " for _ in headings) + "|")
    lines += ["| " + " | ".join(cells) + " |" for cells in rows]
    return lines


def chart_title(group):
    return f"Scores per game: {group.title}"


def chart_files(report):
    """Each group's chart as (file name, SVG), in the order of the groups."""
    return [
        (f"scores_{number}.svg", score_chart_svg(chart_title(group), group.rows))
        for number, group in enumerate(report.groups, start=1)
    ]


def write_markdown(report):
    lines = ["# Bot Report", "", source_sentence(report)]
    for note in READING_NOTES:
        lines += ["", note]
    charts = chart_files(report)
    for group, (chart_name, _) in zip(report.groups, charts):
        lines += ["", f"## {group.title}", ""]
        lines += markdown_table(OVERVIEW_HEADINGS, [row_cells(row) for row in group.rows])
        lines += ["", f"![{chart_title(group)}]({CHART_FOLDER}/{chart_name})"]
        lines += ["", "### Where each bot came from", ""]
        lines += markdown_table(PROVENANCE_HEADINGS, group.provenance)
    return "\n".join(lines) + "\n"


HTML_STYLE = """
:root { color-scheme: light dark; --text: #1f2328; --muted: #59636e;
  --background: #ffffff; --line: #d1d9e0; --header: #f6f8fa; }
@media (prefers-color-scheme: dark) {
  :root { --text: #e6edf3; --muted: #9198a1; --background: #0d1117;
    --line: #3d444d; --header: #151b23; }
}
body { margin: 0 auto; max-width: 1100px; padding: 24px 16px; color: var(--text);
  background: var(--background); font: 15px/1.5 system-ui, sans-serif; }
p { color: var(--muted); }
.table-scroll, .chart { overflow-x: auto; }
.chart { margin: 16px 0; }
table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
th, td { border-bottom: 1px solid var(--line); padding: 6px 10px; text-align: right;
  white-space: nowrap; }
th { background: var(--header); }
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align: left; }
"""


def html_table(headings, rows):
    parts = ['<div class="table-scroll"><table>']
    parts.append(
        "<thead><tr>" + "".join(f"<th>{escape(heading)}</th>" for heading in headings)
        + "</tr></thead><tbody>"
    )
    for cells in rows:
        parts.append("<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in cells) + "</tr>")
    parts.append("</tbody></table></div>")
    return parts


def write_html(report):
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Bot Report</title>",
        f"<style>{HTML_STYLE}</style>",
        "</head>",
        "<body>",
        "<h1>Bot Report</h1>",
        f"<p>{escape(source_sentence(report))}</p>",
    ]
    parts += [f"<p>{escape(note)}</p>" for note in READING_NOTES]
    for group, (_, chart) in zip(report.groups, chart_files(report)):
        parts.append(f"<h2>{escape(group.title)}</h2>")
        parts += html_table(OVERVIEW_HEADINGS, [row_cells(row) for row in group.rows])
        parts.append(f'<div class="chart">{chart}</div>')
        parts.append("<h3>Where each bot came from</h3>")
        parts += html_table(PROVENANCE_HEADINGS, group.provenance)
    parts += ["</body>", "</html>"]
    return "\n".join(parts) + "\n"
