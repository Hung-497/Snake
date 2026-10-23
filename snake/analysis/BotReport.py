"""Turn experiment runs into a Bot Report, written as Markdown and as HTML.

Both files are written from the same BotReport, so they always show the same
numbers. Nothing here depends on the time it runs, so the same runs always
give the same files.
"""

from dataclasses import dataclass
from html import escape
import statistics

from snake.bots.BotModeCatalogue import BOT_MODES


# Terminal experiments save any DQN model as "dqn", so its Feature Set is not
# known from the name alone.
BOT_LABELS = {**{mode.key: mode.label for mode in BOT_MODES}, "dqn": "DQN"}

TABLE_HEADINGS = (
    "Bot", "Run date (UTC)", "Games", "Mean", "Median", "Best", "Std dev",
    "Win rate", "Move-limit rate",
)


@dataclass(frozen=True)
class RunSummary:
    label: str
    created_at: str
    game_count: int
    mean_score: float
    median_score: float
    best_score: int
    score_std_dev: float
    win_rate: float
    move_limit_rate: float


@dataclass(frozen=True)
class ConditionsGroup:
    title: str
    rows: tuple


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
    for conditions in sorted(runs_by_conditions):
        rows = sorted(
            (summarize_run(run) for run in runs_by_conditions[conditions]),
            key=lambda row: (row.label, row.created_at, row.mean_score),
        )
        groups.append(ConditionsGroup(conditions_title(conditions), tuple(rows)))
    return BotReport(len(runs), skipped_files, tuple(groups))


def summarize_run(run):
    scores = [game.score for game in run.games]
    outcomes = [game.outcome for game in run.games]
    return RunSummary(
        label=BOT_LABELS.get(run.bot_mode, run.bot_mode),
        created_at=run.created_at.strftime("%Y-%m-%d %H:%M"),
        game_count=len(scores),
        mean_score=statistics.mean(scores),
        median_score=statistics.median(scores),
        best_score=max(scores),
        score_std_dev=statistics.pstdev(scores),
        win_rate=outcomes.count("won") / len(outcomes),
        move_limit_rate=outcomes.count("move_limit") / len(outcomes),
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
        row.label, row.created_at, str(row.game_count), f"{row.mean_score:.1f}",
        f"{row.median_score:.1f}", str(row.best_score), f"{row.score_std_dev:.1f}",
        f"{row.win_rate:.1%}", f"{row.move_limit_rate:.1%}",
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


def write_markdown(report):
    lines = ["# Bot Report", "", source_sentence(report), ""]
    lines += [
        "Every number is computed from the saved games. The Move-limit rate is "
        "the share of games stopped by the move limit rather than ended by a win "
        "or a collision.",
    ]
    for group in report.groups:
        lines += ["", f"## {group.title}", ""]
        lines.append("| " + " | ".join(TABLE_HEADINGS) + " |")
        lines.append("|" + "|".join(" --- " for _ in TABLE_HEADINGS) + "|")
        for row in group.rows:
            lines.append("| " + " | ".join(row_cells(row)) + " |")
    return "\n".join(lines) + "\n"


HTML_STYLE = """
:root { color-scheme: light dark; --text: #1f2328; --muted: #59636e;
  --background: #ffffff; --line: #d1d9e0; --header: #f6f8fa; }
@media (prefers-color-scheme: dark) {
  :root { --text: #e6edf3; --muted: #9198a1; --background: #0d1117;
    --line: #3d444d; --header: #151b23; }
}
body { margin: 0 auto; max-width: 1000px; padding: 24px 16px; color: var(--text);
  background: var(--background); font: 15px/1.5 system-ui, sans-serif; }
p { color: var(--muted); }
.table-scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
th, td { border-bottom: 1px solid var(--line); padding: 6px 10px; text-align: right;
  white-space: nowrap; }
th { background: var(--header); }
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align: left; }
"""


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
    for group in report.groups:
        parts.append(f"<h2>{escape(group.title)}</h2>")
        parts.append('<div class="table-scroll"><table>')
        parts.append(
            "<thead><tr>"
            + "".join(f"<th>{escape(heading)}</th>" for heading in TABLE_HEADINGS)
            + "</tr></thead><tbody>"
        )
        for row in group.rows:
            parts.append(
                "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row_cells(row)) + "</tr>"
            )
        parts.append("</tbody></table></div>")
    parts += ["</body>", "</html>"]
    return "\n".join(parts) + "\n"
