# Architecture Decision Log

This folder records the important decisions behind the Snake project, one file
per decision. Each Architecture Decision Record (ADR) says what was decided,
which options were considered, and what follows from the choice. Read the ADRs
for an area before changing it.

## Decisions by category

### Game & UI

The app window, its screens, and how they look and move.

| ADR | Decision | Status | Recorded | Related |
| --- | --- | --- | --- | --- |
| [0001](0001-use-arcade-for-the-presentation-layer.md) | Use Arcade for the presentation layer | Accepted | 2026-09-18 | Amended by 0002 |
| [0002](0002-resizable-window-with-a-scaled-board.md) | Make the window resizable and scale the board to fit it | Accepted | 2026-09-25 | Amends 0001, amended by 0014 |
| [0003](0003-keep-motion-in-the-presentation-layer.md) | Keep motion in the presentation layer, and do not animate snake movement | Accepted | 2026-09-25 | |
| [0014](0014-split-live-training-in-half-and-fill-the-board-half.md) | Split Live Training in half and let the board fill its half | Accepted | 2026-10-16 | Amends 0002 and 0011 |

### Bots & Training

How the bots learn, are saved, and are compared.

| ADR | Decision | Status | Recorded | Related |
| --- | --- | --- | --- | --- |
| [0004](0004-run-bot-experiments-headlessly.md) | Run Bot Experiments headlessly and keep their records separate | Accepted | 2026-09-25 | |
| [0007](0007-keep-dqn-headless-with-separate-training-and-evaluation-artifacts.md) | Keep DQN headless with separate training and evaluation artifacts | Accepted | 2026-09-26 | Extended by 0009, amended by 0011 and 0012 |
| [0009](0009-version-learned-artifacts-by-feature-set.md) | Version Learned Artifacts by Feature Set | Accepted | 2026-10-09 | Extends 0007 |
| [0010](0010-keep-q-learning-training-history-inside-the-q-table.md) | Keep Q Learning Training History Inside the Q-table | Accepted | 2026-10-11 | Related to 0007 |
| [0011](0011-train-dqn-in-the-live-training-app-view.md) | Train DQN in the Live Training App View | Accepted | 2026-10-13 | Amends 0007, amended by 0012, 0013, 0014 and 0015 |
| [0012](0012-offer-dqn-in-play-with-one-network-for-all-boards.md) | Offer DQN in Play with one network for all boards | Accepted | 2026-10-13 | Amends 0007 and 0011, amended by 0013 |
| [0013](0013-choose-a-feature-set-version-for-learning-bot-modes.md) | Choose a Feature Set version for learning Bot Modes | Accepted | 2026-10-13 | Amends 0011 and 0012 |
| [0015](0015-let-live-training-start-over-and-keep-a-backup.md) | Let Live Training start over with a game limit and keep the old save as a backup | Accepted | 2026-10-16 | Amends 0011, extended by 0016 |
| [0016](0016-train-q-learning-in-play-on-its-own-app-q-table.md) | Train Q Learning in Play on its own app Q-table | Accepted | 2026-10-16 | Amends 0005, extends 0015 |
| [0017](0017-ship-showcase-bots-and-evaluate-them-on-the-studys-games.md) | Ship Showcase Bots and evaluate them on the study's games | Accepted | 2026-10-16 | Extends 0005, related to 0004 |

### Saved Data

Game records, replays, and the bundled Starter Q-table.

| ADR | Decision | Status | Recorded | Related |
| --- | --- | --- | --- | --- |
| [0005](0005-separate-runtime-data-from-starter-table.md) | Separate Runtime Data from the Starter Q-table | Accepted | 2026-09-25 | Amended by 0016, extended by 0017 |
| [0006](0006-upgrade-old-records-files-in-place.md) | Upgrade old records files in place, keeping a backup | Accepted | 2026-09-26 | |

### Project Setup

Dependencies, tools, and continuous integration.

| ADR | Decision | Status | Recorded | Related |
| --- | --- | --- | --- | --- |
| [0008](0008-manage-dependencies-with-uv.md) | Manage Dependencies with uv | Accepted | 2026-10-09 | Related to 0007 |

## Decisions by status

| Status | ADRs |
| --- | --- |
| Accepted | 0001–0017 |
| Proposed | none |
| Rejected | none |
| Deprecated | none |
| Superseded | none |

## What the fields mean

Every ADR starts with a short list under its title.

- **Status** is one of:
  - **Proposed**: written down but not yet agreed.
  - **Accepted**: the project follows this decision.
  - **Rejected**: considered and turned down. The file is kept so the idea is
    not proposed again without its history.
  - **Deprecated**: no longer applies, and nothing replaces it.
  - **Superseded**: replaced by a newer ADR, which the status names, for
    example `Superseded by ADR 0012`.
- **Category** is one of the four sections above.
- **Recorded** is the date the ADR was first committed to this repository. The
  date each decision was made was not written down separately, so it is left
  out. The issue linked under **Discussed in** shows where it was worked out.
- **Updated** appears when an accepted ADR later gained a clarification.
- **Amends / Amended by** link two ADRs when the newer one changes one part of
  the older one and the rest still stands.
- **Extends / Extended by** link two ADRs when the newer one builds on the
  older one without changing it.
- **Supersedes / Superseded by** link two ADRs when the newer one replaces the
  older one completely.
- **Related** points to an ADR that is useful background.

## Adding a decision

1. Copy the outline below into a new file named with the next unused number
   and a short verb phrase, such as `0011-save-window-size.md`. Numbers are
   never reused.
2. Use **Proposed** while the decision is still being discussed, and change it
   to **Accepted** once it is agreed.
3. Add a row to its category table and update the status table above, in the
   same commit.

```markdown
# Short verb phrase that names the decision

- Status: Proposed
- Category: Game & UI | Bots & Training | Saved Data | Project Setup
- Recorded: YYYY-MM-DD
- Discussed in: link to the issue

The problem, and what was decided.

## Considered Options

- Each option that was considered

Why the chosen option won.

## Consequences

- What follows from the decision
```

## When a decision changes

Do not rewrite an accepted ADR's decision. Instead:

- **To clarify it** without changing the decision, add a dated `## Update`
  section at the end and an **Updated** line at the top, as ADR 0003 does.
- **To change one part of it**, write a new ADR that **Amends** it, and add
  **Amended by** to the old one, as ADR 0002 does for ADR 0001.
- **To replace it**, write a new ADR that **Supersedes** it, and set the old
  one's status to `Superseded by ADR NNNN`.
- **If it no longer applies** and nothing replaces it, set its status to
  **Deprecated**.

Update the tables in this file in the same commit.
