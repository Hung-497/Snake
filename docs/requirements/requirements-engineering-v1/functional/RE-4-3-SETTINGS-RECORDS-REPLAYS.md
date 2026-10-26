# RE-4.3 — Settings, Records, and Replays

[Functional index](../RE-4-FUNCTIONAL-REQUIREMENTS.md) · [Review state](../review-state.md)

## Settings

### REQ-015 v1 — Settings choices
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Settings shall offer game speed (Slow, Normal, Fast; default
Fast), board size (16 × 16, 24 × 25, 30 × 30, 25 × 25; default 24 × 25), and
tile size (20, 25, 30 px; default 25), and new games shall use them.

**Source and basis:** Derived — README "How to Play"; `SessionSettings`.
**Why it matters:** The Player chooses how the game looks and plays.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-015-1: Settings shows the three choices with these options and defaults.
- AC-015-2: A game started after a change uses the new board size and speed.

**Open point / scope limit:** Evaluate ignores Settings on purpose (REQ-032).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-016 v1 — Remember settings
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The system shall save the Settings choices when they change
and restore them when the app starts. A missing or unreadable file shall give
the defaults, an unsupported choice shall fall back to its own default only,
and a failed save shall show a message while the choice still applies until
the app closes.

**Source and basis:** Directly stated — README "How to Play"; ADR 0018;
`SettingsFile`, `SettingsView`.
**Why it matters:** The Player does not have to set the game up again.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-016-1: After changing the board size and restarting the app, the new
  board size is selected.
- AC-016-2: With an unreadable `settings.json`, the app starts with the
  defaults and does not rewrite the file.
- AC-016-3: With one unsupported value, only that choice uses its default.
- AC-016-4: When saving fails, Settings shows "Could not save settings.
  Choices apply until the app closes."

**Open point / scope limit:** The window size is not remembered.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-017 v1 — Resizable window
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The app shall use one resizable window and scale the board
down to fit it.

**Source and basis:** Directly stated — README "How to Play"; ADR 0002;
`WindowLayout`.
**Why it matters:** The app works on small screens.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-017-1: Making the window smaller than the board shrinks the board so it
  stays fully visible.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

## Records

### REQ-018 v1 — Save every finished game
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Each game finished in the app, by a bot or in Human Play,
shall be saved as one record with the Player, date and time, score, moves,
game time, board, tile size, speed, and outcome.

**Source and basis:** Directly stated — README "Where Your Data Is Saved";
`RecordManager.save_game_result`.
**Why it matters:** Records and comparisons are built from these.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-018-1: Finishing a game adds exactly one row to
  `records/game_records.csv`.
- AC-018-2: The row names the Player (`human` for Human Play) and the outcome
  (`won` or `died`).

**Open point / scope limit:** A damaged best replay currently stops the record
from being saved; see [G-1](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-1).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-019 v1 — Browse Records
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Records shall compare Players (Compare), show score trends
(Trends), and list recent games (Games), filtered by board size and speed,
starting from the current Settings, and shall say so when there are no
matching games.

**Source and basis:** Directly stated — README "Features"; `RecordsView`,
`RecordsBrowser`.
**Why it matters:** The Player can see which Player does best.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-019-1: Compare shows one row per Player with games, best, average,
  median, win rate, moves, time, and recent change.
- AC-019-2: Trends shows the last 100 games per Player, each point averaging
  up to 10 games.
- AC-019-3: Games lists the newest 50 matching games, newest first, in pages.
- AC-019-4: With no records, the view shows "No games recorded yet."; with no
  match, "No games match these filters."

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

## Replays

### REQ-020 v1 — Keep each Player's best game
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The system shall keep one best replay per Player and replace
it only with a game that has a higher score. Hamiltonian shall keep only games
it wins.

**Source and basis:** Directly stated — README "Where Your Data Is Saved";
`ReplayManager.save_replay`.
**Why it matters:** The Player can watch each Player at its best.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-020-1: A game with a higher score than the saved replay replaces it.
- AC-020-2: A game with an equal or lower score does not.
- AC-020-3: A Hamiltonian game that does not win is not saved as a replay.

**Open point / scope limit:** One best replay per Player, whatever the board
size and speed (DEC-009, Q-6).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-021 v2 — Watch a replay
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Replay shall let the Player choose a Player (and a version
for Q Learning and DQN) and watch its best game, with pause (P or Space),
restart (R), three Replay Speeds (S), and leaving (Esc or Back to Menu), and
shall show a message when there is no replay or it cannot be read.

**Source and basis:** Directly stated — README "Human Play controls";
`ReplayView`, `ReplayPlaybackView`, `ReplaySession`.
**Why it matters:** The Player can study how a game was played.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-021-1: The replay plays back the saved moves and ends with the saved
  score.
- AC-021-2: P or Space pauses, R restarts, and S cycles Slow, Normal, Fast.
- AC-021-3: With no replay, the view says that none is saved yet; with a
  damaged one, it shows why it cannot be played.
- AC-021-4: Esc during playback returns to the menu.

**Open point / scope limit:** Esc added by DEC-007 (Q-4); not built yet, see
[G-21](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-21).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-022 v1 — Read older saved files
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The system shall still read records and replays saved by
older versions: an older records file shall be upgraded in place after a
backup copy is made, and older replays shall be converted when loaded.

**Source and basis:** Derived — ADR 0006; `RecordManager.upgrade_old_file`;
`ReplayManager` migration.
**Why it matters:** Updating the app does not lose a Player's history.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-022-1: A records file without an `outcome` column is backed up to `.bak`
  and upgraded; its rows keep their values.
- AC-022-2: A records file with a `bot_name` column is read as `player`.
- AC-022-3: An older pixel-based replay plays back correctly.

**Open point / scope limit:** Very old 9-column records files may be misread;
see [G-10](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-10).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.
