# Give each evaluation its own run page

- Status: Accepted
- Category: Bots & Training
- Recorded: 2026-10-23
- Discussed in: [#204](https://github.com/Hung-497/Snake/pull/204)
- Extends: [ADR 0020](0020-generate-bot-reports-and-commit-only-the-showcase-report.md), which generates the Bot Report this links to
- Related: [ADR 0017](0017-ship-showcase-bots-and-evaluate-them-on-the-studys-games.md), whose Evaluate opens the run page

After evaluating a new bot, the user wants to see how it did against every
other bot without hunting through the full Bot Report. Every finished Evaluate
in the app, `RunExperiment`, and `EvaluateDQN` now rebuilds the local Bot Report
and writes a run page for every saved Bot Experiment report, in
`reports/runs/`, named after the report's file. The step that saved a report
knows its file, so Open report and the commands' printed path go straight to
that run's page. Nothing is chosen by which run is newest.

For each bot in its run, a run page shows the bot's average food per game, best
game, and share of games stopped by the move limit; how far it leads or trails
every other bot on the same games, with the games it won and whether the
difference is reliable; and its histogram next to the leader's. It does not
rank the bots: Hamiltonian always stops at the move limit and the hand-written
bots always crash, so one place in an order of averages hides how each bot got
its score.

## Considered Options

- Mark the bot with the newest run in the full Bot Report and open its face-off
  against the leader.
- Keep one Bot Report and open it with a link that names the run, such as
  `bot_report.html#run=…`, for a script to focus on.
- Write a run page for every saved report and open the one the evaluation just
  saved.

Save times are a guess: one experiment saves several bots at the same moment,
and reports copied in from another machine arrive with no local step that knows
they are new. Windows often drops the `#` part of a file link that a program
opens, and copied reports would still need a list to find them. A page per
saved report needs no guess, works for copied reports the next time the report
is rebuilt, and stays a plain file that opens the same everywhere.

## Consequences

- Run pages are Runtime Data, like the local Bot Report: they are rebuilt with
  it from every saved report, so they always compare with every bot evaluated
  so far, and pages of deleted reports are removed. The committed Showcase
  Report has none.
- The full Bot Report stays neutral: its face-off always opens on the two best
  bots, and a Recent evaluations list links to the five latest run pages by
  date. The date only orders that list.
- A run page compares that run's own games, seed by seed, even when its bot has
  other bot files or later runs; the other bots are compared as the Bot Report
  compares them.
- Run pages are HTML only. Agents read the full report's Markdown, which lists
  the recent runs with their run pages.
- A bot that no other bot played the same games with says so and names the
  games other bots were evaluated on. Comparing a 20-game run with the first 20
  study games is left out, because ADR 0020 compares only identical Experiment
  Conditions.
