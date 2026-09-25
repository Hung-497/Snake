# Upgrade old records files in place, keeping a backup

Records Analytics needs a Game Outcome for every new game record, which adds a column to the records CSV. The CSV reader expects every row to match the header, so rows with the new column cannot be appended to a file that has the old header. The first time the app writes to an old records file, it saves a copy as `game_records.csv.bak` and rewrites the file with the new header. Old rows get an empty outcome, which means unknown.

## Considered Options

- Upgrade the existing file once, with a backup
- Start a second file for new records and read both
- Leave old files alone and write outcomes only into new files

Upgrading was chosen so there is still one records file to read and keep. The backup makes the rewrite recoverable. A second file would have to be read alongside the first forever, and leaving old files alone would mean they never get a win rate.

## Consequences

- Earlier column changes, such as renaming `bot_name` to `player`, were read-compatible, so no file was rewritten. Adding a column is the first change that rewrites local Runtime Data.
- Win rates only count games with a known outcome.
