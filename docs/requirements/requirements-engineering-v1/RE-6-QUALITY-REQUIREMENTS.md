# RE-6 — Quality requirements

[Package index](index.md) · [Review state](review-state.md)

## Reproducibility

### REQ-048 v1 — Same inputs, same games
Status: Approved — baseline v1

**Type:** Non-functional—Quality
**Tags:** Reproducibility
**Requirement:** Evaluating the same bot file on the same board, seeds, and
move limit shall give the same games and scores every time, in the app and in
the terminal.

**Source and basis:** Directly stated — product definition §7, §9; ADR 0004,
0017.
**Why it matters:** Fair comparison depends on it (goal 4).
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-048-1: Two evaluations of one bot file on the same conditions give
  identical scores and moves.
- AC-048-2: App Evaluate and RunExperiment give the same games for the same
  Q-table and seeds.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-049 v1 — Bot randomness never moves the food
Status: Approved — baseline v1

**Type:** Non-functional—Quality
**Tags:** Reproducibility
**Requirement:** A bot's own randomness (for example, exploring while
learning) shall come from a separate random source, so it never changes where
food appears.

**Source and basis:** Derived — `BotMode` (each bot gets its own
`random_source`); `test_bot_mode_headless.py`.
**Why it matters:** Two bots on the same seed see the same food.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-049-1: With the same engine seed, food positions are identical whether
  the bot explores or not.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-050 v1 — Reports are deterministic
Status: Approved — baseline v1

**Type:** Non-functional—Quality
**Tags:** Reproducibility
**Requirement:** Building the Bot Report twice from the same report files shall
give identical files, and the committed Showcase Report shall contain nothing
local (no dates of building, no local paths).

**Source and basis:** Directly stated — issue #200 acceptance criteria;
ADR 0020.
**Why it matters:** The committed report changes only when results change.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-050-1: Two builds from the same `experiments/` give byte-identical
  pages.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

## Data safety

### REQ-051 v1 — An interrupted save never breaks a file
Status: Approved — baseline v1

**Type:** Non-functional—Quality
**Tags:** Reliability
**Requirement:** If saving is interrupted (crash, kill, power loss), every
saved file shall be either the old version or the new one, never a broken
mix. This covers training saves, replays, settings, records, reports, and
report pages.

**Source and basis:** Derived — product definition §7 ("an interrupted save
never leaves a broken file"); `JsonFile.save_json_atomically`.
**Why it matters:** One crash must not destroy hours of training or history.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-051-1: Interrupting a save of each file type leaves the previous version
  readable.

**Open point / scope limit:** Met for Q-tables, replays, settings, and DQN
files; not met for records, reports, and pages. See
[G-2](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-2) and
[G-3](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-3).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-052 v2 — Training progress is never lost
Status: Approved — baseline v1

**Type:** Non-functional—Quality
**Tags:** Reliability
**Requirement:** No action in the app or the commands shall overwrite or
delete a training save or a backup without first keeping a backup. A crash
shall lose at most the current game of Q Learning training and at most the
last 24 finished games of DQN training.

**Source and basis:** Directly stated — product definition §7; ADR 0015.
Crash limits decided by DEC-004 (Q-1).
**Why it matters:** Training takes hours and cannot be recreated exactly.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-052-1: Start new, `--new-table`, and `--resume` never overwrite an
  existing save or backup.
- AC-052-2: Killing the app during training and opening it again continues
  from the last saved game within these limits.

**Open point / scope limit:** DQN limit not met yet; see
[G-18](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-18).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-053 v1 — Damaged files never crash the app
Status: Approved — baseline v1

**Type:** Non-functional—Quality
**Tags:** Robustness
**Requirement:** A missing, damaged, or older-format Runtime Data file shall
never crash the app or a command. The system shall show what is wrong, keep
the file, and keep working.

**Source and basis:** Derived — README (Settings, Records, Replays
behaviour); ADR 0006, 0019, 0020.
**Why it matters:** Runtime Data lives on the user's disk and can be damaged.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-053-1: A damaged replay, records file, Q-table, DQN save, settings file,
  or report produces a message, not a crash.
- AC-053-2: The damaged file is not changed.

**Open point / scope limit:** Not met in several places; see
[G-1](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-1),
[G-4](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-4),
[G-6](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-6).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-054 v1 — Save failures are reported
Status: Approved — baseline v1

**Type:** Non-functional—Quality
**Tags:** Robustness
**Requirement:** When a save fails (disk full, read-only folder, file locked),
the app shall tell the user and keep running.

**Source and basis:** Proposed — follows the Settings behaviour (ADR 0018) for
every other save; accepted by the owner for every save (DEC-005, Q-2).
**Why it matters:** A full disk should not crash the app mid-training.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-054-1: With `records/` read-only, finishing a game shows a message and
  the next game starts.
- AC-054-2: With `experiments/` read-only, a finished evaluation shows a
  message instead of crashing.

**Open point / scope limit:** Only Settings does this today; see
[G-19](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-19).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

## Usability and responsiveness

### REQ-055 v1 — The window stays responsive
Status: Approved — baseline v1

**Type:** Non-functional—Quality
**Tags:** Responsiveness
**Requirement:** While bots play, train, or are evaluated, the window shall
keep responding to keys and buttons. Fast work shall be split into short
pieces per frame (Evaluate: 0.05 s; Live Training Background: 50 ms).

**Source and basis:** Derived — `EvaluateView`, `LiveTrainingView`.
**Why it matters:** The bot developer can always pause or leave.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-055-1: During fast Evaluate and Background training, Back to Menu works
  within one frame.

**Open point / scope limit:** Rebuilding the report and loading a large DQN
save run in one frame and may freeze the window; see
[G-15](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-15).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-056 v1 — Easy first run
Status: Approved — baseline v1

**Type:** Non-functional—Quality
**Tags:** Usability
**Requirement:** A visitor shall be able to start the app on macOS, Windows,
or Linux with the README Quick Start commands only.

**Source and basis:** Directly stated — product definition §9; README "Quick
Start".
**Why it matters:** Visitors from a CV or portfolio try it quickly.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-056-1: On a clean computer with Git and uv, `git clone`, `uv sync`, and
  `uv run python SnakeApp.py` open the app.

**Open point / scope limit:** Checked by hand on macOS only (product
definition §10).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

## Maintainability

### REQ-057 v1 — Testable without a window
Status: Approved — baseline v1

**Type:** Non-functional—Quality
**Tags:** Testability
**Requirement:** The game rules, Bot Modes, sessions, storage, and analysis
shall run and be tested without opening a window, and the automated tests
shall pass on macOS, Windows, and Linux for every change to `main`.

**Source and basis:** Directly stated — product definition §7, §9;
README "Run the Tests"; `.github/workflows/tests.yml`.
**Why it matters:** Changes can be checked automatically.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-057-1: `uv run pytest` passes in CI on all three systems.
- AC-057-2: No module under `snake/engine`, `bots`, `sessions`, `storage`, or
  `analysis` needs a display to import.

**Open point / scope limit:** App Views have no automated tests; see
[G-16](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-16).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.
