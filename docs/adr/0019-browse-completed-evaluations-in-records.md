# Browse completed evaluations in Records

- Status: Accepted
- Category: Game & UI
- Recorded: 2026-10-17
- Discussed in: [#184](https://github.com/Hung-497/Snake/issues/184)
- Extends: [ADR 0017](0017-ship-showcase-bots-and-evaluate-them-on-the-studys-games.md)
- Related: [ADR 0004](0004-run-bot-experiments-headlessly.md)

Add an Evaluate tab to Records that reads completed app Evaluate reports
from `experiments/`. Each row shows the Player, Your bot or Showcase Bot,
game count, average, best, and date in UTC. Board dimensions, seed range,
and move limit remain visible so different evaluation conditions are clear.
Runs are newest first and paged to fit the window.

## Considered Options

- Leave saved reports accessible only through files.
- Add evaluation games to the watched-game CSV.
- Read existing app evaluation JSON reports in a separate Records tab.

The separate tab makes previous measurements accessible without mixing
evaluation games with training or Human Play records. It needs no new
storage format or dependency.

## Consequences

- The Board and Speed filters apply to watched games; evaluation rows show
  their own conditions and do not use those filters.
- Only reports marked as app evaluations are listed. Terminal experiments
  remain separate, and incomplete, unreadable, or unsupported reports are
  skipped with a visible count.
- Reading reports changes no files and does not import PyTorch.
- ADR 0018 is reserved by the open Remember Settings PR (#182).
