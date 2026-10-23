"""Turn one saved Bot Experiment into a Run Report: its bots against every other bot.

A run page is written for every saved report each time the local Bot Report is
rebuilt, so it always compares with every bot evaluated so far. It reads the
Bot Report's groups, so both pages show the same numbers.
"""

from dataclasses import dataclass

from snake.analysis.BotReport import (
    ConditionsGroup, RunSummary, bot_label, newest_runs, ranking_rows, scores_per_seed,
    short_file, summarize_games,
)
from snake.analysis.PairedComparison import compare_paired


@dataclass(frozen=True)
class Rival:
    """Another bot on the same games, seen from the run's bot.

    A positive difference means the run's bot ate more food per game.
    """

    label: str
    difference: float
    low: float | None
    high: float | None
    wins: int
    game_count: int
    # "reliable", "too close to call", or "too few games".
    reliability: str


@dataclass(frozen=True)
class RunBot:
    label: str
    # This run's own games, even when the bot has other runs in the group.
    summary: RunSummary
    # Every other bot in the group, best average first.
    rivals: tuple = ()


@dataclass(frozen=True)
class RunReport:
    # The saved report's file name without ".json".
    source: str
    group: ConditionsGroup
    bots: tuple
    # (title, how many bots) of every group that played other games, so a bot
    # with nothing to compare can be evaluated on games other bots played.
    other_games: tuple = ()


def build_run_reports(runs, report):
    """One Run Report per saved report file, in file name order."""
    groups = {group.conditions: group for group in report.groups}
    runs_by_conditions = {}
    runs_by_source = {}
    for run in runs:
        runs_by_conditions.setdefault(run.conditions, []).append(run)
        if run.source is not None:
            runs_by_source.setdefault(run.source, []).append(run)
    run_reports = []
    for source in sorted(runs_by_source):
        source_runs = runs_by_source[source]
        # Every bot in one report played the same games.
        conditions = source_runs[0].conditions
        group = groups[conditions]
        scores = bot_scores(runs_by_conditions[conditions])
        ranked = [row.bot for row in ranking_rows(group)]
        bots = tuple(
            RunBot(bot_label(run), run_summary(run), rivals(run, scores, ranked))
            for run in sorted(source_runs, key=lambda run: ranked.index(bot_label(run)))
        )
        other_games = tuple(
            (other.title, len(ranking_rows(other))) for other in report.groups if other is not group
        )
        run_reports.append(RunReport(source, group, bots, other_games))
    return run_reports


def run_summary(run):
    label = bot_label(run)
    return summarize_games(
        label, label, short_file(run), run.created_at.strftime("%Y-%m-%d %H:%M"), run.games,
    )


def bot_scores(runs):
    """Each bot's score on each seed, as the Bot Report compares them.

    It uses each bot file's newest run, averaged over a bot's files.
    """
    runs_by_label = {}
    for run in newest_runs(runs):
        runs_by_label.setdefault(bot_label(run), []).append(run)
    return {label: scores_per_seed(label_runs) for label, label_runs in runs_by_label.items()}


def rivals(run, scores, ranked):
    """This run's own games against every other bot, seed by seed."""
    label = bot_label(run)
    own = [game.score for game in run.games]
    return tuple(rival(own, other, scores[other]) for other in ranked if other != label)


# How sure a comparison is, as the run's bot's row says it.
RELIABILITY_WORDS = {
    "first is better": "reliable",
    "second is better": "reliable",
    "no reliable difference": "too close to call",
    "too few games": "too few games",
}


def rival(own, other, other_scores):
    comparison = compare_paired(own, other_scores)
    return Rival(
        other, comparison.mean_difference, comparison.low, comparison.high,
        sum(mine > theirs for mine, theirs in zip(own, other_scores)), comparison.game_count,
        RELIABILITY_WORDS[comparison.verdict],
    )


def partner_row(group, bot):
    """The bot to show next to this one: the leader, or the second best for the leader."""
    others = [row for row in ranking_rows(group) if row.bot != bot.label]
    return others[0]


def alone_sentence(bot):
    return (f"No other bot has played these games yet, so there is nothing to compare "
            f"{bot.label} with.")


def headline(bot):
    return f"{bot.label} eats {bot.summary.mean_score:.1f} food per game on average."


def headline_detail(bot):
    """How the bot played, so bots that play in different ways are not mixed up."""
    summary = bot.summary
    games = f"{summary.game_count} game" + ("" if summary.game_count == 1 else "s")
    return (f"{games} · best game {summary.best_score} · stopped by the move limit in "
            f"{summary.move_limit_rate:.1%} of games")
