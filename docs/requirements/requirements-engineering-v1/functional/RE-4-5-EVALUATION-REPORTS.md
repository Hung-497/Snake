# RE-4.5 — Evaluation and Bot Reports

[Functional index](../RE-4-FUNCTIONAL-REQUIREMENTS.md) · [Review state](../review-state.md)

## Evaluate in the app

### REQ-032 v1 — Evaluate on the study's games
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Evaluate shall measure the app training or a Showcase Bot
without learning, on 20 or 200 of the study's games: a 24 × 25 board, seeds
starting at 200000, and a 5000-move limit, whatever the Settings are.

**Source and basis:** Directly stated — README "Training and Evaluate in the
App"; ADR 0017; `EvaluationSession.STUDY_GAMES`, `GAME_COUNTS`.
**Why it matters:** Every evaluation uses the same games, so results can be
compared.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-032-1: A 20-game run uses seeds 200000–200019; a 200-game run uses
  200000–200199.
- AC-032-2: The board is 24 × 25 even when Settings has another size.
- AC-032-3: The evaluated Q-table or DQN file is unchanged afterwards.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-033 v1 — Fast or watched evaluation
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** W shall switch Evaluate between fast play and watching the
board, and both shall play exactly the same games.

**Source and basis:** Directly stated — README; `EvaluateView`.
**Why it matters:** The bot developer can watch without changing the result.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-033-1: A run played fast and one played one move at a time give the same
  scores and moves.
- AC-033-2: W toggles the board view during and after the run.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-034 v1 — Save only a finished evaluation
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** A finished evaluation shall save one Bot Experiment report in
`experiments/`. Leaving before the last game shall save nothing.

**Source and basis:** Directly stated — README ("A completed run saves a JSON
report; leaving early saves no report"); `EvaluationSession`.
**Why it matters:** Reports never hold half a study.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-034-1: After the last game, exactly one new
  `experiments/experiment_<id>.json` exists.
- AC-034-2: Leaving after some games creates no file.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-035 v1 — Open the run page
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** After a finished evaluation, Open report (or R) shall open
the run page of that evaluation in the web browser.

**Source and basis:** Directly stated — README; ADR 0021;
`EvaluationSession.run_report_path`, `EvaluateView`.
**Why it matters:** The result is one click away (UJ-6).
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-035-1: The opened page is `reports/runs/<report name>.html` of the
  report just saved.
- AC-035-2: The button and R are shown only when the page exists.

**Open point / scope limit:** See
[G-12](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-12).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-036 v2 — Showcase Bots
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The app shall ship read-only Showcase Bots for Q Learning v2,
Q Learning v3, and DQN v3, labelled as the best of three study runs, which can
be evaluated but never trained or changed. Before evaluating one, the app
shall check that the file is the shipped Showcase Bot and refuse a changed
file.

**Source and basis:** Directly stated — README; ADR 0017;
`BotModeCatalogue`, `starter_data/showcase/`.
**Why it matters:** A visitor can see a trained bot without training one.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-036-1: Evaluate showcase is offered for those three versions and not for
  DQN v2.
- AC-036-2: The Showcase Bot files are unchanged after an evaluation.
- AC-036-3: With a changed Showcase Bot file, Evaluate showcase shows a
  message, plays no game, and saves no report.

**Open point / scope limit:** The hash check was decided by DEC-012 (Q-9);
not built yet, see [G-24](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-24).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-037 v1 — Finished evaluations in Records
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Records → Evaluate shall list finished app evaluations,
newest first, in pages, each with Your bot or Showcase Bot, version, game
count, average, best, UTC date, and board, seeds, and move limit. It shall say
how many reports were skipped as unreadable.

**Source and basis:** Directly stated — README; ADR 0019;
`EvaluationReports`, `RecordsView`.
**Why it matters:** Earlier evaluations can be found again in the app.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-037-1: A finished app evaluation appears at the top of the list.
- AC-037-2: Newer and Older page through the list.
- AC-037-3: With a damaged report, the tab shows "Skipped N unreadable or
  unsupported reports."

**Open point / scope limit:** Terminal reports are not listed, as ADR 0019
decided (DEC-013, Q-11). See also
[G-11](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-11).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

## Bot Reports

### REQ-038 v1 — Rebuild the report after every evaluation
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Every finished evaluation — Evaluate in the app,
RunExperiment, or EvaluateDQN — shall rebuild the local Bot Report and the run
pages, with no extra command.

**Source and basis:** Directly stated — README "Train and Compare Bots";
ADR 0020, 0021; `LocalReport.write_local_report` callers.
**Why it matters:** Results are never out of date after an evaluation (UJ-6).
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-038-1: After each of the three, `reports/bot_report.html` includes the
  new run.
- AC-038-2: The terminal commands print the `Bot Report:` and `Run report:`
  paths.
- AC-038-3: Training alone (app or terminal) writes no report.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-039 v2 — Bot Report content
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The Bot Report shall group runs by Experiment Conditions
(board, move limit, and exact seed list) and never mix groups. For each group
it shall show one row per bot file, compare every pair of bots seed by seed
with a 95% range, draw score histograms, and offer a face-off between any two
bots, opening on the top two. A version's own training and its Showcase Bot
shall count as different bots. It shall also list the 5 most recent runs.

**Source and basis:** Directly stated — ADR 0020; docs/bot-experiments.md;
`BotReport`, `PairedComparison`, `ReportPage`.
**Why it matters:** A comparison says how sure it is, not only who has the
higher average (goal 4).
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-039-1: Runs on different seeds or boards appear in different groups.
- AC-039-2: Within a group, only the newest run of each bot file is used.
- AC-039-3: Each pair shows a mean difference and a 95% range, or "too few
  games".
- AC-039-4: The face-off opens on the two highest-ranked bots.
- AC-039-5: After evaluating your Q Learning v3 training and the Q Learning v3
  Showcase Bot on the same games, the report compares them with each other.

**Open point / scope limit:** Separate labels were decided by DEC-006 (Q-3);
not built yet, see [G-20](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-20).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-040 v1 — Run pages
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Each saved report shall get its own run page that shows, for
each of its bots, the average, best game, and move-limit share (never a rank),
its games compared with every other bot that played the same games, and its
histogram next to the leader's.

**Source and basis:** Directly stated — ADR 0021; `RunReport`, `RunPage`.
**Why it matters:** One evaluation can be read on its own.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-040-1: `reports/runs/<report name>.html` exists for every usable report.
- AC-040-2: A bot alone on its games gets "No other bot has played these games
  yet" and the list of other conditions.
- AC-040-3: The page shows no rank.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-041 v1 — Damaged or missing reports
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The Bot Report shall skip damaged, incomplete, or older-format
report files and say how many it skipped. With no usable reports, the command
shall print a clear message, exit with an error, and write nothing.

**Source and basis:** Directly stated — issue #200 acceptance criteria;
`ExperimentRuns`, `AnalyseBots`.
**Why it matters:** One bad file does not break every report.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-041-1: A damaged report is skipped, counted, and the others are reported.
- AC-041-2: With no usable report, AnalyseBots prints "No usable Bot
  Experiment reports…" and exits with code 1.

**Open point / scope limit:** Old run pages stay when no usable report is
left; see [G-8](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-8).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-042 v1 — Showcase Report
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** `AnalyseBots --showcase` shall write the committed Showcase
Report in `docs/results/` from full 200-game study evaluations of the
Showcase Bots (matched by file hash) and the Baselines only, with no run pages
and no Recent list.

**Source and basis:** Directly stated — ADR 0020; `Showcase`, `AnalyseBots`.
**Why it matters:** The published results hold nothing local or unverified.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-042-1: A run of your own training is not included.
- AC-042-2: A Showcase Bot without a matching run is listed as not evaluated
  yet.
- AC-042-3: The Showcase Report has no Recent list and no skipped count.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-043 v1 — Rebuild the report by hand
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** `AnalyseBots` shall rebuild the local Bot Report and run pages
from `experiments/` without playing any game.

**Source and basis:** Directly stated — README; `AnalyseBots`.
**Why it matters:** Reports can be rebuilt after deleting or copying reports.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-043-1: The command finishes without playing games and prints the paths
  written.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.
