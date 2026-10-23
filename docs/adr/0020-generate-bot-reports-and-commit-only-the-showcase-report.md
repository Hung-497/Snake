# Generate Bot Reports and commit only the Showcase Report

- Status: Proposed
- Category: Bots & Training
- Recorded: 2026-10-23
- Discussed in: [#194](https://github.com/Hung-497/Snake/issues/194)
- Extends: [ADR 0017](0017-ship-showcase-bots-and-evaluate-them-on-the-studys-games.md)
- Related: [ADR 0004](0004-run-bot-experiments-headlessly.md), [ADR 0005](0005-separate-runtime-data-from-starter-table.md)

Records Analytics is too brief to judge a trained bot, and `docs/results.md`
was calculated by hand. A headless command now reads saved Bot Experiment
reports and writes a Bot Report: an HTML page with SVG charts for people and a
Markdown file for agents. It compares only runs with identical Experiment
Conditions and includes game-by-game differences with a 95% range. It never
plays games and adds no dependency.

Local Bot Reports are Runtime Data in a git-ignored `reports/` folder. Only the
Showcase Report is committed, under `docs/results/`. It uses full 200-game
study evaluations whose table or model hash matches a Showcase Bot, plus
Baselines evaluated on the same games.

## Considered Options

- Commit every generated report, or let the report replace `docs/results.md`.
- Keep all generated reports local, and publish results only by hand.
- Keep local reports local, and commit only the Showcase Report.

Local `experiments/` folders differ between machines, so committing their
reports would change the published numbers with every run. Showcase Bots are
committed and evaluated on fixed games, so their report is the same everywhere
and safe to publish.

## Consequences

- `docs/results.md` stays the hand-written explanation and links to the
  Showcase Report for numbers and charts.
- A Showcase Bot with no matching study run is shown as not evaluated yet;
  20-game runs are never published.
- Promoting a trained bot to a Showcase Bot stays a manual step.
- Training curves, causes of death, and per-move logs are out of scope,
  because no saved file records them yet.
- GitHub shows the committed `.md`; viewing the `.html` in a browser needs a
  later GitHub Pages step.
