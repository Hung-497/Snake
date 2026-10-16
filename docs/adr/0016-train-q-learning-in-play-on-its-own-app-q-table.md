# Train Q Learning in Play on its own app Q-table

- Status: Accepted
- Category: Bots & Training
- Recorded: 2026-10-16
- Amends: [ADR 0005](0005-separate-runtime-data-from-starter-table.md), whose app play wrote into the same local Q-table as training and experiments
- Extends: [ADR 0015](0015-let-live-training-start-over-and-keep-a-backup.md), which let only DQN start over with a game limit
- Related: [ADR 0010](0010-keep-q-learning-training-history-inside-the-q-table.md), whose Training History now also records the game limit

Q Learning in Play trained the same Q-table that `TrainQLearning` and Bot Experiments use, with unseeded games, no move limit, and no way to start over or stop. Starting over in the app would have changed the table a study depends on. Q Learning in Play now trains its own app table per Feature Set, `learning_data/q_table_app_v2.json` and `q_table_app_v3.json`, and goes through the same Start and Set up training App Views as DQN: continue the saved training, or start new with a game limit, keeping the old table as a dated backup.

## Considered Options

- Keep training the shared table, and back it up when starting over in the app
- Give the app its own table, copied once from the shared table
- Give the app its own table that always starts empty

An app table copied once won. The app can never change the table the headless commands use, and the first copy means Play still shows the trained bot at first instead of an empty one. The copy happens only when neither the app table nor a backup of it exists, so starting over really starts from an empty table.

## Consequences

- App training uses the headless command's defaults: seed 0 for the food, seed 1 for the bot, and a 5000-move limit per game. A new app training learns exactly the same table as `TrainQLearning --new-table` with those defaults, and a test checks it. A continued training seeds from its game count, so it does not replay its first games' food.
- Q Learning games in Play now stop at 5000 moves, as in training. A stopped game is saved with an empty outcome, like a Live Training game stopped at its move limit.
- The game limit is saved in the session's Training History entry, so continuing stops at the same limit. Entries from the headless commands have no limit.
- Training in the app no longer reaches the shared table. To continue an app training in the terminal, pass `--q-table learning_data/q_table_app_v2.json`.
- An app table that cannot be read is never overwritten: Play offers only "Start new training", which keeps it as a backup.
