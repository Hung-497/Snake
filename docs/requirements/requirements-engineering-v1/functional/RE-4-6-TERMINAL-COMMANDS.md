# RE-4.6 — Terminal commands

[Functional index](../RE-4-FUNCTIONAL-REQUIREMENTS.md) · [Review state](../review-state.md)

### REQ-044 v1 — Train Q Learning from the terminal
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** `TrainQLearning` shall train Q Learning v2 or v3 for a given
number of games without opening a window, with options for board, seed, move
limit, Q-table path, and a new table, and shall save the table after every
game.

**Source and basis:** Directly stated — README; docs/training.md; ADR 0004;
`TrainQLearning`.
**Why it matters:** Long training runs need no window.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-044-1: `--games 100` trains 100 games and the table's game count rises
  by 100.
- AC-044-2: `--new-table` refuses a path that already exists.
- AC-044-3: A missing or unreadable table stops the command with an error
  before training.
- AC-044-4: The command saves no records or replays.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-045 v1 — Train DQN from the terminal
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** `TrainDQN` shall train DQN with Feature Set v2 or v3, save a
checkpoint every N games and at the end, save an evaluation model at the end,
and resume from a checkpoint into a new run folder without changing the
original.

**Source and basis:** Directly stated — docs/training.md; ADR 0007;
`TrainDQN`, `DQNArtifacts`.
**Why it matters:** Training can be split over several sessions safely.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-045-1: A run writes `checkpoint.pt` every `--checkpoint-every` games and
  `model.pt` at the end, in `learning_data/dqn_runs/<id>/`.
- AC-045-2: `--resume` with options that conflict with the checkpoint is
  refused.
- AC-045-3: The resumed checkpoint file is unchanged.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-046 v1 — Run a Bot Experiment
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** `RunExperiment` shall play chosen bots on the same seeds and
board, check every input before the first game, print each game, save one
report, and print the Bot Report and run page paths.

**Source and basis:** Directly stated — README; docs/bot-experiments.md;
ADR 0004; `RunExperiment`.
**Why it matters:** Bots are compared on exactly the same games.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-046-1: Every chosen bot plays the same seeds.
- AC-046-2: A bad input (games ≤ 0, repeated bot, unsupported board, missing
  table or model) stops the command with exit code 2 and writes nothing.
- AC-046-3: A successful run prints `Saved experiment:`, `Bot Report:`, and
  `Run report:` and exits with 0.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-047 v1 — Evaluate DQN from the terminal
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** `EvaluateDQN` shall evaluate a DQN evaluation model on chosen
seeds and board, save a report, and print the Bot Report and run page paths.

**Source and basis:** Directly stated — docs/training.md; ADR 0007;
`EvaluateDQN`.
**Why it matters:** A terminal-trained DQN can be measured like any other bot.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-047-1: Evaluating a `model.pt` saves one report and prints the paths.
- AC-047-2: A file that is not an evaluation model is refused before any game.

**Open point / scope limit:** It cannot evaluate a training checkpoint, unlike
the app; see [G-13](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-13).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.
