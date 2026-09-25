# Separate Runtime Data from the Starter Q-table

The app, training command, and Bot Experiments write results into project folders. Keep those generated Q-tables, watched-game records, replays, and experiment results as local Runtime Data rather than tracked files. Bundle a separate Starter Q-table from the committed Q-table snapshot so a fresh clone has an explicit starting point without making that starter writable during normal use.

## Considered Options

- Keep active saved data tracked alongside the code.
- Move saved data to a user data directory outside the repository.
- Keep the current project folders for ignored Runtime Data and bundle the starter separately.

The last option preserves existing local data and paths while preventing normal runs from changing tracked files.

## Consequences

- A fresh clone starts with no watched-game records or saved replays. Training and experiments require an explicitly initialized local Q-table.
- Existing local data is preserved when tracking is removed. Past Git history is not rewritten.
