# Remember Settings between app launches

- Status: Accepted
- Category: Saved Data
- Recorded: 2026-10-16
- Discussed in: [#180](https://github.com/Hung-497/Snake/issues/180)
- Extends: [ADR 0005](0005-separate-runtime-data-from-starter-table.md)
- Related: [ADR 0002](0002-resizable-window-with-a-scaled-board.md)

Save the selected board size, Tile Size, and speed automatically when a
Settings dropdown changes, and restore them at app startup. Store them in
an ignored `settings.json` file in the Snake project root, independently of
the terminal's launch folder. Window size continues to start at 900 x 960.

## Considered Options

- Keep preferences only for the current app session.
- Save the three choices in a small JSON file in the project.
- Add a preferences directory outside the project or a database.

The JSON file follows the project's existing local Runtime Data design and
needs no new dependency. SessionSettings still owns the supported choices;
SettingsFile owns the file format, loading, and atomic writing.

## Consequences

- The file has a schema version and stores board dimensions and tile pixels
  rather than dropdown labels. The speed stores its existing name.
- Missing, unreadable, malformed, or unsupported files use defaults without
  being rewritten at startup. Invalid individual choices keep their default
  while other valid choices are restored.
- Saves reuse `save_json_atomically`. A failed save keeps the current choice
  usable for the session and shows a message in Settings.
- Tests use temporary paths; normal play and tests never commit preferences.
