"""Turn experiment runs into a Bot Report and write its Markdown.

ReportPage writes the HTML from the same BotReport, so both files always show
the same numbers. Nothing here depends on the time it runs, so the same runs
always give the same files.
"""

from dataclasses import dataclass
import statistics

from snake.analysis.PairedComparison import compare_paired
from snake.analysis.ScoreChart import BIN_WIDTH, bin_label, score_bins, score_chart_svg
from snake.bots.BotModeCatalogue import BOT_MODES, FAMILY_LABELS


BOT_MODES_BY_KEY = {mode.key: mode for mode in BOT_MODES}
LABELS_BY_VERSION = {(mode.family, mode.version): mode.label for mode in BOT_MODES}

OVERVIEW_HEADINGS = (
    "Bot", "Bot file", "Run date (UTC)", "Games", "Mean", "Median", "Best", "Std dev",
    "Win rate", "Move-limit rate", "Moves per point",
)
COMPARISON_HEADINGS = (
    "Better bot", "Compared with", "Games", "Average difference", "95% range", "Verdict",
    "Won / tied / lost",
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
    scores: tuple = ()


@dataclass(frozen=True)
class Matchup:
    """Two bots on the same seeds, the one with the higher average first."""

    first: str
    second: str
    game_count: int
    mean_difference: float
    low: float | None
    high: float | None
    verdict: str
    # Games, out of the same seeds, that each bot scored more in, and ties.
    first_wins: int
    ties: int
    second_wins: int


@dataclass(frozen=True)
class ConditionsGroup:
    title: str
    rows: tuple
    matchups: tuple
    provenance: tuple
    # The bot with the most recently saved run in the group, and when (UTC);
    # the committed Showcase Report leaves these out.
    newest_bot: str | None = None
    newest_at: str | None = None

    @property
    def comparisons(self):
        return tuple(comparison_cells(matchup) for matchup in self.matchups)


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

    latest = None if showcase else latest_single_run(runs)
    groups = []
    run_count = 0
    for conditions in sorted(runs_by_conditions):
        newest = newest_runs(runs_by_conditions[conditions])
        run_count += len(newest)
        is_latest_group = latest is not None and latest.conditions == conditions
        groups.append(ConditionsGroup(
            conditions_title(conditions), summary_rows(newest), comparison_rows(newest),
            tuple(provenance_cells(run) for run in newest),
            newest_bot=bot_label(latest) if is_latest_group else None,
            newest_at=latest.created_at.strftime("%Y-%m-%d %H:%M") if is_latest_group else None,
        ))
    title = "Showcase Report" if showcase else "Bot Report"
    return BotReport(
        run_count, skipped_files, tuple(groups), title, showcase, tuple(not_evaluated),
    )


def latest_single_run(runs):
    """The most recently saved run, so a fresh evaluation is easy to find.

    One experiment can evaluate several bots at once; they share its save time,
    so no single bot is the newest and None is returned.
    """
    if not runs:
        return None
    latest_time = max(run.created_at for run in runs)
    latest = [run for run in runs if run.created_at == latest_time]
    return latest[0] if len({bot_label(run) for run in latest}) == 1 else None


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
    matchups = []
    for position, first in enumerate(labels):
        for second in labels[position + 1:]:
            comparison = compare_paired(scores[first], scores[second])
            pairs = list(zip(scores[first], scores[second]))
            matchups.append(Matchup(
                first, second, comparison.game_count, comparison.mean_difference,
                comparison.low, comparison.high, comparison.verdict,
                first_wins=sum(a > b for a, b in pairs),
                ties=sum(a == b for a, b in pairs),
                second_wins=sum(a < b for a, b in pairs),
            ))
    return tuple(matchups)


def range_text(matchup):
    if matchup.low is None:
        return NOT_APPLICABLE
    return f"{matchup.low:.1f} to {matchup.high:.1f}"


def verdict_text(matchup):
    return {
        "first is better": f"{matchup.first} scores more",
        "second is better": f"{matchup.second} scores more",
        "no reliable difference": "No reliable difference",
        "too few games": "Too few games",
    }[matchup.verdict]


def comparison_cells(matchup):
    return (
        matchup.first, matchup.second, str(matchup.game_count),
        f"{matchup.mean_difference:.1f}", range_text(matchup), verdict_text(matchup),
        f"{matchup.first_wins} / {matchup.ties} / {matchup.second_wins}",
    )


def ranking_rows(group):
    """One row per bot, best average first: its combined row when it has one."""
    best_row = {}
    for row in group.rows:
        if row.bot not in best_row or row.label != row.bot:
            best_row[row.bot] = row
    return sorted(best_row.values(), key=lambda row: (-row.mean_score, row.bot))


def bin_count(group):
    """How many score ranges a group's histograms need to reach its best game."""
    return max(row.best_score for row in group.rows) // BIN_WIDTH + 1





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
        scores=tuple(scores),
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
    "Each histogram shows one bot: across is the score a game ended with, in "
    "ranges of 10, and up is how many games ended there. All of a group's "
    "histograms share one scale.",
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
    """Each group's histograms as (file name, SVG), in the order of the groups."""
    return [
        (f"scores_{number}.svg", score_chart_svg(
            chart_title(group), ranking_rows(group), bin_count(group),
        ))
        for number, group in enumerate(report.groups, start=1)
    ]


def score_table(group):
    """How many games landed in each score range, one column per bot."""
    bots = ranking_rows(group)
    count = bin_count(group)
    bins = [score_bins(row.scores, count) for row in bots]
    rows = [
        (bin_label(index), *[str(counts[index]) for counts in bins])
        for index in range(count) if any(counts[index] for counts in bins)
    ]
    return markdown_table(("Score", *[row.bot for row in bots]), rows)


def write_markdown(report, chart_folder):
    """The Markdown report; its charts are linked from chart_folder, next to it."""
    lines = [f"# {report.title}", "", source_sentence(report)]
    for note in reading_notes(report):
        lines += ["", note]
    charts = chart_files(report)
    for group, (chart_name, _) in zip(report.groups, charts):
        lines += ["", f"## {group.title}", ""]
        if group.newest_bot:
            lines += [f"Newest run in this group: {group.newest_bot}, {group.newest_at} UTC.", ""]
        lines += markdown_table(OVERVIEW_HEADINGS, [row_cells(row) for row in group.rows])
        lines += ["", f"![{chart_title(group)}]({chart_folder}/{chart_name})"]
        lines += ["", "### Scores per game", ""]
        lines += score_table(group)
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
