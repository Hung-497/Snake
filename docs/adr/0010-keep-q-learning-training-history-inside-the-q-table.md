# Keep Q Learning Training History Inside the Q-table

- Status: Accepted
- Category: Bots & Training
- Recorded: 2026-10-11
- Discussed in: [#103](https://github.com/Hung-497/Snake/issues/103)
- Related: [ADR 0007](0007-keep-dqn-headless-with-separate-training-and-evaluation-artifacts.md), the DQN run folder this compares against

A Q-table recorded only its values, epsilon, and game count, so when two tables trained for the same number of games scored differently, nothing showed how either was trained. Each Q-table now carries its own Training History: one entry per training session, from `TrainQLearning` or app play in Training Mode, written at the first save and updated on every save so an interrupted session is still described. Unlike DQN, which keeps metadata in a run folder because a run has several files, a Q-table is a single JSON file, so the history lives inside it and travels with every copy.

## Considered Options

- A history list inside the Q-table JSON.
- A separate history file next to the table.
- A run folder per training session, as DQN uses.

## Consequences

- Older tables load unchanged; the first session recorded on a table that already has games starts with an `unrecorded` entry for those games.
- Bot Experiment reports copy the table's Training History, so a result stays explained even if the table later changes or is lost.
