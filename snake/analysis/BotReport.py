"""Turn experiment runs into a Bot Report, written as Markdown and as HTML.

Both files are written from the same BotReport, so they always show the same
numbers. Nothing here depends on the time it runs, so the same runs always
give the same files.
"""

from dataclasses import dataclass
from html import escape
import statistics

from snake.analysis import ReportColors
from snake.analysis.PairedComparison import compare_paired
from snake.analysis.ScoreChart import score_chart_svg
from snake.bots.BotModeCatalogue import BOT_MODES, FAMILY_LABELS


BOT_MODES_BY_KEY = {mode.key: mode for mode in BOT_MODES}
LABELS_BY_VERSION = {(mode.family, mode.version): mode.label for mode in BOT_MODES}

OVERVIEW_HEADINGS = (
    "Bot", "Bot file", "Run date (UTC)", "Games", "Mean", "Median", "Best", "Std dev",
    "Win rate", "Move-limit rate", "Moves per point",
)
COMPARISON_HEADINGS = (
    "Better bot", "Compared with", "Games", "Average difference", "95% range", "Verdict",
)
PROVENANCE_HEADINGS = (
    "Bot", "Bot file", "Feature Set", "Games trained", "Trained by", "Training seeds", "Code",
)
# Shown where a field does not apply, such as a non-learning bot's Feature Set.
NOT_APPLICABLE = "—"
UNKNOWN = "unknown"


@dataclass(frozen=True)
class RunSummary:
    label: str
    # The bot's plain name, the same for its file rows and its combined row.
    bot: str
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
    comparisons: tuple
    provenance: tuple


@dataclass(frozen=True)
class BotReport:
    run_count: int
    skipped_files: int
    groups: tuple
    title: str = "Bot Report"
    # The Showcase Report is committed, so it leaves out anything that depends
    # on the local experiments folder, such as skipped files.
    showcase: bool = False
    not_evaluated: tuple = ()


def build_bot_report(runs, skipped_files, showcase=False, not_evaluated=()):
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
            conditions_title(conditions), summary_rows(newest), comparison_rows(newest),
            tuple(provenance_cells(run) for run in newest),
        ))
    title = "Showcase Report" if showcase else "Bot Report"
    return BotReport(
        run_count, skipped_files, tuple(groups), title, showcase, tuple(not_evaluated),
    )


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
                label, label, short_file(run), run.created_at.strftime("%Y-%m-%d %H:%M"),
                run.games,
            ))
        if len(label_runs) > 1:
            pooled = [game for run in label_runs for game in run.games]
            rows.append(summarize_games(
                f"{label} combined ({len(label_runs)} bot files)", label, NOT_APPLICABLE,
                NOT_APPLICABLE, pooled,
            ))
    return tuple(rows)


def scores_per_seed(runs):
    """A bot's score on each seed, averaged over its bot files.

    Every run in a group played the same seeds in the same order.
    """
    return [
        statistics.mean(run.games[number].score for run in runs)
        for number in range(len(runs[0].games))
    ]


def comparison_rows(runs):
    """Compare every pair of bots in a group, the higher average first."""
    runs_by_label = {}
    for run in runs:
        runs_by_label.setdefault(bot_label(run), []).append(run)
    scores = {label: scores_per_seed(label_runs) for label, label_runs in runs_by_label.items()}
    # Highest average first; equal averages keep alphabetical order.
    labels = sorted(scores, key=lambda label: (-statistics.mean(scores[label]), label))
    rows = []
    for position, first in enumerate(labels):
        for second in labels[position + 1:]:
            comparison = compare_paired(scores[first], scores[second])
            rows.append(comparison_cells(first, second, comparison))
    return tuple(rows)


def comparison_cells(first, second, comparison):
    if comparison.low is None:
        range_text = NOT_APPLICABLE
    else:
        range_text = f"{comparison.low:.1f} to {comparison.high:.1f}"
    verdict = {
        "first is better": f"{first} scores more",
        "second is better": f"{second} scores more",
        "no reliable difference": "No reliable difference",
        "too few games": "Too few games",
    }[comparison.verdict]
    return (
        first, second, str(comparison.game_count), f"{comparison.mean_difference:.1f}",
        range_text, verdict,
    )


def summarize_games(label, bot, bot_file, created_at, games):
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
        bot=bot,
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
    if report.showcase:
        text = SHOWCASE_INTRODUCTION + " " + text
    elif report.skipped_files:
        text += (
            f" {report.skipped_files} report file"
            + (" was" if report.skipped_files == 1 else "s were")
            + " skipped (damaged, incomplete, or an older format)."
        )
    return text


SHOWCASE_INTRODUCTION = (
    "The Showcase Bots shipped with the app and the non-learning Baselines, each "
    "measured in Evaluation Mode on the same 200 study games."
)
# Hamiltonian never dies, but filling the study board takes far more moves
# than the study allows, so its study score is how far it gets, not a loss.
MOVE_LIMIT_NOTE = (
    "Hamiltonian follows one route over the whole board, so it never collides, "
    "but filling the board takes far more than the study's 5000 moves. Its games "
    "stop at the move limit while the snake is still alive: its score shows how "
    "far that safe route gets in 5000 moves, not whether it can win."
)
NOT_EVALUATED_SENTENCE = (
    "These have no full study evaluation on the shipped file yet, so they are "
    "not shown above:"
)

READING_NOTES = (
    "Every number is computed from the saved games. The Move-limit rate is the "
    "share of games stopped by the move limit rather than ended by a win or a "
    "collision. Moves per point is how many moves the bot needed for each point "
    "of score; a high value with a high Move-limit rate suggests circling "
    "instead of chasing food.",
    "Game by game compares two bots on the same seeds, so the luck of where the "
    "food appears cancels out. Each seed gives one difference in score, and the "
    "Average difference is their mean. The 95% range shows how far that average "
    "could move if the bots were tested on other seeds: when the whole range is "
    "above zero, the first bot reliably scores more; when it includes zero, the "
    "games cannot show a difference. A bot with several bot files uses its "
    "average score on each seed.",
    "In each chart the line runs from the lowest to the best score, the box holds "
    "the middle half of the games, the line inside the box is the median, and the "
    "dot is the mean.",
    "A bot file is the saved Q-table or DQN model, shown by the start of its "
    "hash. When the same bot file was evaluated more than once, only its newest "
    "run is shown. A combined row pools the games of every bot file of that bot.",
)


def reading_notes(report):
    return READING_NOTES + ((MOVE_LIMIT_NOTE,) if report.showcase else ())


ONE_BOT_SENTENCE = "Only one bot was evaluated under these conditions, so there is nothing to compare."


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


def write_markdown(report, chart_folder):
    """The Markdown report; its charts are linked from chart_folder, next to it."""
    lines = [f"# {report.title}", "", source_sentence(report)]
    for note in reading_notes(report):
        lines += ["", note]
    charts = chart_files(report)
    for group, (chart_name, _) in zip(report.groups, charts):
        lines += ["", f"## {group.title}", ""]
        lines += markdown_table(OVERVIEW_HEADINGS, [row_cells(row) for row in group.rows])
        lines += ["", f"![{chart_title(group)}]({chart_folder}/{chart_name})"]
        lines += ["", "### Game by game", ""]
        if group.comparisons:
            lines += markdown_table(COMPARISON_HEADINGS, group.comparisons)
        else:
            lines.append(ONE_BOT_SENTENCE)
        lines += ["", "### Where each bot came from", ""]
        lines += markdown_table(PROVENANCE_HEADINGS, group.provenance)
    if report.not_evaluated:
        lines += ["", "## Not evaluated yet", "", NOT_EVALUATED_SENTENCE, ""]
        lines += [f"- {name}" for name in report.not_evaluated]
    return "\n".join(lines) + "\n"


C = ReportColors
# The app's dark board, as a page: a faint cell grid behind raised panels, and
# each bot in its Records Analytics colour.
HTML_STYLE = f"""
:root {{ color-scheme: dark; --surface: {C.SURFACE}; --raised: {C.SURFACE_RAISED};
  --border: {C.BORDER}; --grid: #0F2036; --text: {C.TEXT}; --muted: {C.TEXT_MUTED};
  --head: {C.SNAKE_HEAD}; --body: #2EAA82; --food: {C.FOOD}; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; color: var(--text); background-color: var(--surface);
  background-image: linear-gradient(var(--grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size: 28px 28px;
  font: 15px/1.6 Inter, ui-sans-serif, system-ui, sans-serif;
  font-variant-numeric: tabular-nums; }}
main {{ max-width: 1080px; margin: 0 auto; padding: 48px 20px 64px; }}
h1 {{ font-size: clamp(34px, 6vw, 52px); line-height: 1.05; letter-spacing: -0.02em;
  margin: 0 0 14px; font-weight: 700; }}
h2 {{ font-size: 22px; line-height: 1.3; margin: 0 0 18px; font-weight: 650;
  letter-spacing: -0.01em; }}
h3 {{ font-size: 15px; font-weight: 600; margin: 28px 0 10px; color: var(--muted); }}
.lede {{ max-width: 68ch; color: var(--muted); font-size: 17px; margin: 0 0 18px; }}
p {{ max-width: 72ch; }}
details.notes {{ max-width: 72ch; border: 1px solid var(--border); border-radius: 10px;
  background: var(--raised); padding: 4px 18px; margin-bottom: 8px; }}
details.notes summary {{ cursor: pointer; padding: 10px 0; font-weight: 600; }}
details.notes p {{ color: var(--muted); margin: 0 0 14px; }}
summary:focus-visible {{ outline: 2px solid var(--head); outline-offset: 4px;
  border-radius: 4px; }}
section.group {{ margin-top: 56px; }}
ol.ranking {{ list-style: none; display: flex; flex-wrap: wrap; align-items: center;
  gap: 10px 0; padding: 0; margin: 0 0 22px; }}
ol.ranking li {{ position: relative; min-width: 118px; padding: 10px 14px 9px;
  margin-right: 12px; border-radius: 8px; background: var(--raised);
  border: 1px solid var(--border); border-top: 3px solid var(--bot); }}
ol.ranking li + li::before {{ content: ""; position: absolute; left: -13px; top: 50%;
  width: 13px; height: 6px; margin-top: -3px; background: var(--body); }}
ol.ranking li.head {{ background: var(--head); border-color: var(--head);
  color: {C.SURFACE}; padding-left: 24px; }}
ol.ranking li.head::after {{ content: ""; position: absolute; top: 12px; left: 9px;
  width: 5px; height: 5px; border-radius: 50%; background: {C.SURFACE};
  box-shadow: 0 9px 0 {C.SURFACE}; }}
ol.ranking .food {{ width: 12px; height: 12px; border-radius: 50%; background: var(--food);
  margin-right: 14px; min-width: 0; padding: 0; border: 0; }}
ol.ranking .name {{ display: block; font-weight: 600; font-size: 14px; white-space: nowrap; }}
ol.ranking .score {{ display: block; font-size: 22px; font-weight: 700; line-height: 1.2; }}
ol.ranking li.head .score, ol.ranking li.head .name {{ color: {C.SURFACE}; }}
.panel {{ background: var(--raised); border: 1px solid var(--border); border-radius: 10px;
  overflow-x: auto; }}
.chart {{ margin: 0 0 18px; overflow-x: auto; border-radius: 10px; }}
.chart svg {{ display: block; width: 100%; min-width: 620px; height: auto; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ padding: 9px 14px; text-align: right; white-space: nowrap;
  border-bottom: 1px solid var(--border); }}
tbody tr:last-child td {{ border-bottom: 0; }}
th {{ color: var(--muted); font-weight: 500; font-size: 13px; }}
th.text, td.text {{ text-align: left; }}
td.bot {{ text-align: left; font-weight: 500; }}
td.text:not(.bot) {{ color: var(--muted); }}
.swatch {{ display: inline-block; width: 10px; height: 10px; border-radius: 3px;
  margin-right: 9px; background: var(--bot); vertical-align: 0; }}
td.unsure {{ color: var(--muted); font-style: italic; }}
.empty {{ color: var(--muted); }}
.picker {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px;
  margin: 0 0 12px; color: var(--muted); }}
.picker select {{ font: inherit; color: var(--text); background: var(--raised);
  border: 1px solid var(--border); border-radius: 8px; padding: 7px 10px; }}
.picker select:focus-visible {{ outline: 2px solid var(--head); outline-offset: 2px; }}
tr[hidden] {{ display: none; }}
ul.missing {{ padding-left: 20px; color: var(--muted); }}
@media (max-width: 600px) {{ main {{ padding: 32px 16px 48px; }}
  ol.ranking li {{ min-width: 0; margin-right: 8px; }}
  ol.ranking li + li::before {{ display: none; }} }}
"""

# Columns that name a bot, per table, get the bot's colour swatch; text
# columns align left and numbers right.
BOT_COLUMNS = {"overview": (0,), "comparisons": (0, 1), "provenance": (0,)}
TEXT_COLUMNS = {"overview": (0, 1, 2), "comparisons": (0, 1, 5), "provenance": (0, 1, 4)}


def bot_cell(name, colors):
    color = colors.get(name, C.TEXT_MUTED)
    return (f'<td class="bot" style="--bot: {color}"><span class="swatch"></span>'
            f"{escape(name)}</td>")


def html_table(headings, rows, colors, table):
    bot_columns, text_columns = BOT_COLUMNS[table], TEXT_COLUMNS[table]
    parts = ['<div class="panel"><table>']
    parts.append("<thead><tr>" + "".join(
        f'<th class="text">{escape(heading)}</th>' if column in text_columns
        else f"<th>{escape(heading)}</th>"
        for column, heading in enumerate(headings)
    ) + "</tr></thead><tbody>")
    for cells in rows:
        row = []
        # A comparison row names its pair, so the picker can show just that pair.
        opening = (f'<tr data-pair="{escape(cells[0])}|{escape(cells[1])}">'
                   if table == "comparisons" else "<tr>")
        for column, cell in enumerate(cells):
            if column in bot_columns:
                row.append(bot_cell(cell, colors))
            elif cell in ("No reliable difference", "Too few games"):
                row.append(f'<td class="text unsure">{escape(cell)}</td>')
            elif column in text_columns:
                row.append(f'<td class="text">{escape(cell)}</td>')
            else:
                row.append(f"<td>{escape(cell)}</td>")
        parts.append(opening + "".join(row) + "</tr>")
    parts.append("</tbody></table></div>")
    return parts


def ranking_rows(group):
    """One row per bot, best mean first: its combined row when it has one."""
    best_row = {}
    for row in group.rows:
        if row.bot not in best_row or row.label != row.bot:
            best_row[row.bot] = row
    return sorted(best_row.values(), key=lambda row: (-row.mean_score, row.bot))


def ranking_snake(group):
    """The group's ranking drawn as a snake: the leader is the head, nearest the food."""
    parts = ['<ol class="ranking" aria-label="Bots ranked by mean score, best first">',
             '<li class="food" aria-hidden="true"></li>']
    for place, row in enumerate(ranking_rows(group)):
        head = ' class="head"' if place == 0 else ""
        parts.append(
            f'<li{head} style="--bot: {C.bot_color(row.bot)}">'
            f'<span class="name">{escape(row.bot)}</span>'
            f'<span class="score">{row.mean_score:.1f}</span></li>'
        )
    parts.append("</ol>")
    return parts


def compare_picker(group):
    """Two dropdowns that narrow the Game by game table, starting on the top two bots."""
    bots = [row.bot for row in ranking_rows(group)]

    def select(kind, chosen):
        options = ['<option value="">Any bot</option>'] + [
            f'<option value="{escape(bot)}"{" selected" if bot == chosen else ""}>'
            f"{escape(bot)}</option>"
            for bot in bots
        ]
        name = "First bot" if kind == "a" else "Second bot"
        return (f'<select class="pick-{kind}" aria-label="{name}">'
                + "".join(options) + "</select>")

    return [
        '<div class="picker">Compare', select("a", bots[0]), "with", select("b", bots[1]),
        "</div>",
    ]


# Narrows each Game by game table to the chosen pair; without it every row shows.
PICKER_SCRIPT = """
document.querySelectorAll(".picker").forEach(function (picker) {
  var a = picker.querySelector(".pick-a"), b = picker.querySelector(".pick-b");
  var rows = picker.nextElementSibling.querySelectorAll("tr[data-pair]");
  function update() {
    rows.forEach(function (row) {
      var pair = row.dataset.pair.split("|");
      var fits = [a.value, b.value].every(function (bot) {
        return bot === "" || pair.indexOf(bot) >= 0;
      });
      row.hidden = !fits || (a.value !== "" && a.value === b.value);
    });
  }
  a.addEventListener("change", update);
  b.addEventListener("change", update);
  update();
});
"""


def write_html(report):
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{escape(report.title)}</title>",
        f"<style>{HTML_STYLE}</style>",
        "</head>",
        "<body>",
        "<main>",
        f"<h1>{escape(report.title)}</h1>",
        f'<p class="lede">{escape(source_sentence(report))}</p>',
        '<details class="notes"><summary>How to read this report</summary>',
    ]
    parts += [f"<p>{escape(note)}</p>" for note in reading_notes(report)]
    parts.append("</details>")
    for group, (_, chart) in zip(report.groups, chart_files(report)):
        colors = {row.label: C.bot_color(row.bot) for row in group.rows}
        parts += ['<section class="group">', f"<h2>{escape(group.title)}</h2>"]
        parts += ranking_snake(group)
        parts.append(f'<div class="chart">{chart}</div>')
        parts += html_table(OVERVIEW_HEADINGS, [row_cells(row) for row in group.rows],
                            colors, "overview")
        parts.append("<h3>Game by game</h3>")
        if group.comparisons:
            parts += compare_picker(group)
            parts += html_table(COMPARISON_HEADINGS, group.comparisons, colors, "comparisons")
        else:
            parts.append(f'<p class="empty">{escape(ONE_BOT_SENTENCE)}</p>')
        parts.append("<h3>Where each bot came from</h3>")
        parts += html_table(PROVENANCE_HEADINGS, group.provenance, colors, "provenance")
        parts.append("</section>")
    if report.not_evaluated:
        parts += ['<section class="group">', "<h2>Not evaluated yet</h2>",
                  f"<p>{escape(NOT_EVALUATED_SENTENCE)}</p>", '<ul class="missing">']
        parts += [f"<li>{escape(name)}</li>" for name in report.not_evaluated]
        parts += ["</ul>", "</section>"]
    parts += ["</main>", f"<script>{PICKER_SCRIPT}</script>", "</body>", "</html>"]
    return "\n".join(parts) + "\n"
