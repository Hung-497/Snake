# Ship Showcase Bots and evaluate them on the study's games

- Status: Accepted
- Category: Bots & Training
- Recorded: 2026-10-16
- Extends: [ADR 0005](0005-separate-runtime-data-from-starter-table.md), which bundles only the Starter Q-table
- Related: [ADR 0004](0004-run-bot-experiments-headlessly.md), whose Bot Experiment reports Evaluate also writes

Seeing a strong learning bot meant training it first, and the app had no fair way to measure a trained bot, so the scores in `docs/results.md` could only be checked in the terminal. The app now ships one finished Showcase Bot per learning Bot Mode, read-only in `starter_data/showcase/`, and adds an Evaluate App View that measures either the user's own app training or the Showcase Bot. Evaluate always uses the study's games: a 24 × 25 board, a 5000-move limit, and 20 or 200 games on evaluation seeds starting at 200000, ignoring the board chosen in Settings.

## Considered Options

- Ship nothing, and leave measuring to `RunExperiment`
- Ship the typical (middle) run of each bot, or the best of its three study runs
- Evaluate on the Settings board, or always on the study's games

The best run won because a showcase should show what the bot can do; its label says it is the best of three runs, so it is not mistaken for a typical result. The study's games won because a score is only worth measuring if it can be compared: the same Showcase Bot then reproduces its `docs/results.md` score exactly, and every app training is measured on the same games.

## Consequences

- About 250 KB of models are committed: the Q Learning v2 and v3 tables and the DQN v2 and v3 as DQN Evaluation Models. The app only reads them and never trains them; starting new training still starts from scratch.
- Evaluate plays in Evaluation Mode, so it never changes a save. It runs fast with a key to watch the current game, and both give the same result.
- Only a finished Evaluate run is saved, as a Bot Experiment report in `experiments/`, and its games stay out of Records. Leaving halfway saves nothing.
- Evaluating a DQN needs PyTorch, like Live Training. No replay files are shipped.
