# RE-4.4 — Training

[Functional index](../RE-4-FUNCTIONAL-REQUIREMENTS.md) · [Review state](../review-state.md)

### REQ-023 v1 — Training start screen
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** After choosing Q Learning or DQN and a version, the system
shall show the saved training (games, best score, game limit) or say that
there is none or that it cannot be read. It shall offer Continue training and
Evaluate only for a readable save, Start new training always, and Evaluate
showcase when that version has a Showcase Bot.

**Source and basis:** Directly stated — README "Training and Evaluate in the
App"; ADR 0015, 0017; `TrainingStartView`.
**Why it matters:** The bot developer sees what is saved before choosing.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-023-1: With no save, the screen says "none yet" and offers Start new and,
  where available, Evaluate showcase.
- AC-023-2: With a readable save, it shows games, best, and limit, and offers
  Continue, Evaluate, and Start new.
- AC-023-3: With an unreadable save, it says the save could not be read and
  offers only Start new (and Evaluate showcase).
- AC-023-4: The backup count and total size are shown.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-024 v1 — Start new training
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Start new training shall let the bot developer choose a game
limit (Off, 1000, 2000, 5000), then move any existing save to a dated backup
that never overwrites another backup, and start training from zero.

**Source and basis:** Directly stated — README; ADR 0015;
`TrainingSaves.start_over`, `TRAINING_LIMITS`.
**Why it matters:** Old training is never lost by starting over.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-024-1: Starting new training renames the save to
  `<name>_YYYY-MM-DD_HHMMSS<ext>`; a name clash adds `_2`, `_3`, and so on.
- AC-024-2: No existing backup is changed or deleted.
- AC-024-3: Back on the setup screen changes nothing.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-025 v2 — Continue training and the game limit
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Continue training shall resume from the saved game count and
keep the saved game limit, also after the same save was trained from the
terminal. When the limit is reached, training shall stop and the screen shall
say so.

**Source and basis:** Directly stated — README; ADR 0015;
`GameSession.limit_reached`, `LiveTrainingSession`. Terminal case added by
DEC-010 (Q-7).
**Why it matters:** A training run with a limit ends at a known point.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-025-1: Continuing a save at 500 games with limit 1000 trains 500 more
  games and stops.
- AC-025-2: At the limit, the screen shows "Limit reached: N games".
- AC-025-3: After `TrainQLearning --q-table` on the app table, the app still
  shows and keeps the same limit.
- AC-025-4: That terminal session continues the food seed from the saved
  game count, as the app does.

**Open point / scope limit:** AC-025-3 and AC-025-4 not built yet; see
[G-22](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-22). Raising the
limit of a finished training is deferred (DEC-014, [RE-1](../RE-1-SCOPE.md#deferrals)).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-026 v2 — Q Learning training in the app
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Q Learning shall train in the Game App View on its own app
Q-table for each version, with fixed seeds and a 5000-move limit per game,
shall save the table after every finished game, and shall number games from
the start of the training, not from the start of the visit.

**Source and basis:** Directly stated — README; ADR 0016;
`QLearningTraining.start_q_learning_training`, `QLearningBot.on_game_end`.
**Why it matters:** App training is repeatable and never touches the terminal
commands' tables.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-026-1: App training saves to `learning_data/q_table_app_v2.json` or
  `q_table_app_v3.json` only.
- AC-026-2: After each finished game, the saved game count goes up by one.
- AC-026-3: Training the same table from the same start gives the same games
  as the headless command with the same seed and move limit.
- AC-026-4: Continuing a save at 500 games, the first game of the visit is
  shown and recorded as game 501.

**Open point / scope limit:** Learning from a game left unfinished is not
saved, which is accepted (DEC-011, Q-8). AC-026-4 not built yet; see
[G-23](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-23).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-027 v1 — First use of the shared Q-table
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The first time a Q Learning version is opened, the system
shall copy the shared Q-table to the app table if there is no app table and no
backup of one.

**Source and basis:** Derived — ADR 0016; `TrainingSaves.copy_shared_q_table_once`.
**Why it matters:** App training starts from the existing learning instead of
from nothing.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-027-1: With a shared table and no app table, opening the version creates
  the app table as a copy.
- AC-027-2: With an existing app table or a backup, nothing is copied.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-028 v2 — DQN Live Training
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** DQN shall train in Live Training, showing the board and the
network side by side, with pause (P or Space), moves per frame (S), Live or
Background training (B), network focus (N), zoom and pan (mouse, R), and
leaving (Esc or Back to Menu). It shall save its progress every 25 finished
games and when the bot developer leaves or closes the app.

**Source and basis:** Directly stated — README "Training and Evaluate in the
App"; ADR 0011, 0014; `LiveTrainingView`, `LiveTrainingSession`.
**Why it matters:** The bot developer can see the network learn.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-028-1: Each control does what the README table says.
- AC-028-2: Leaving and opening Live Training again continues from the same
  game count.
- AC-028-3: Closing the window during Live Training saves progress.
- AC-028-4: After game 25, 50, 75, …, the save holds that game count, so a
  crash loses at most the last 24 finished games.
- AC-028-5: Games are numbered from the start of the training (game numbers
  already do this).

**Open point / scope limit:** Saving every 25 games was decided by DEC-004
(Q-1); not built yet, see
[G-18](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-18).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-029 v1 — DQN is optional
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Without PyTorch, the app and commands shall work for every
other feature, and every DQN feature shall show how to install PyTorch instead
of failing.

**Source and basis:** Directly stated — README ("DQN needs the optional
PyTorch dependencies"); ADR 0007; `LiveTraining.missing_dependency_message`.
**Why it matters:** Most users never install the large PyTorch download.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-029-1: Without PyTorch, choosing DQN shows the `uv sync --group dqn`
  message and the app keeps running.
- AC-029-2: Without PyTorch, RunExperiment with `dqn` stops with a clear error
  before any game.
- AC-029-3: Without PyTorch, every non-DQN test passes.

**Open point / scope limit:** See
[G-5](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-5) and
[G-9](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-9).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-030 v1 — Unreadable training saves
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** A training save that cannot be read, or that belongs to a
different Feature Set, shall never be overwritten by training. The system
shall say what is wrong and offer Start new training, which keeps the file as
a backup.

**Source and basis:** Derived — ADR 0009, 0015, 0016; `QLearningTraining`
(refuses an unreadable table); `LiveTrainingCheckpointError`.
**Why it matters:** A damaged file can still be recovered by hand.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-030-1: With an unreadable save, Continue is not offered and the file is
  unchanged.
- AC-030-2: With a save of the wrong Feature Set, the system shows a message
  and does not train or crash.
- AC-030-3: Start new moves the unreadable file to a backup.

**Open point / scope limit:** See
[G-4](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-4).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-031 v1 — Training History
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** A Q-table shall keep a Training History with one entry per
training session: where it ran, its settings, the code version, and its
results.

**Source and basis:** Directly stated — ADR 0010; docs/training.md;
`QLearningBot` history entries.
**Why it matters:** A bot developer can tell how a table was trained.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-031-1: After a session, the table has a new history entry with source,
  seed, board, move limit, code identity, games at start and end, and average
  and best score.
- AC-031-2: A session that finishes no game adds no entry.

**Open point / scope limit:** DQN saves have no code identity; see
[G-14](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-14).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.
