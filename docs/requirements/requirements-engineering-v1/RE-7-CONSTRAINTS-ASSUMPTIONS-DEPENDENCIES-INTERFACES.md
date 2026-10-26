# RE-7 — Constraints, assumptions, dependencies, and interfaces

[Package index](index.md) · [Review state](review-state.md)

## Constraints

### REQ-058 v1 — Python 3.13 managed with uv
Status: Approved — baseline v1

**Type:** Constraint
**Requirement:** The project shall run on Python 3.13 and manage its
dependencies only with uv, with exact versions locked in `uv.lock`.

**Source and basis:** Directly stated — ADR 0008; `.python-version`;
`pyproject.toml`.
**Why it matters:** Everyone runs the same versions.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-058-1: CI runs `uv sync --locked` and fails if `uv.lock` is out of date.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-059 v1 — Arcade only in the presentation layer
Status: Approved — baseline v1

**Type:** Constraint
**Requirement:** The window shall use Arcade 3, and only the presentation
layer (`SnakeApp.py`, `snake/ui/`) may depend on it.

**Source and basis:** Directly stated — ADR 0001, 0003; imports in `snake/`.
**Why it matters:** The rest can be tested and run without a display
(REQ-057).
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-059-1: No file outside `SnakeApp.py` and `snake/ui/` imports `arcade`
  (inspection).

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-060 v1 — DQN uses optional, CPU-only PyTorch
Status: Approved — baseline v1

**Type:** Constraint
**Requirement:** PyTorch shall be an optional dependency group, installed as
a CPU-only build, and used only by DQN.

**Source and basis:** Directly stated — ADR 0007; `pyproject.toml`
(`dqn` group, CPU index on Linux).
**Why it matters:** Most users never need the large download.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-060-1: `uv sync` without `--group dqn` installs no PyTorch.
- AC-060-2: On Linux, PyTorch comes from the CPU-only index.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-061 v1 — Local only, Runtime Data out of Git
Status: Approved — baseline v1

**Type:** Constraint
**Requirement:** The product shall work offline with no accounts or servers.
Runtime Data shall stay local and git-ignored; only bundled data
(`starter_data/`) and the Showcase Report (`docs/results/`) are committed.

**Source and basis:** Directly stated — product definition §8; ADR 0005,
0020; `.gitignore`.
**Why it matters:** Personal results never end up in the repository.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-061-1: `records/`, `replays/`, `learning_data/`, `experiments/`,
  `reports/`, and `settings.json` are git-ignored.
- AC-061-2: The app makes no network requests (inspection).

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-062 v1 — Licences
Status: Approved — baseline v1

**Type:** Constraint
**Requirement:** The project shall be released under the MIT License, and the
bundled Inter font shall keep its own SIL Open Font License.

**Source and basis:** Directly stated — README "License"; `LICENSE`;
`assets/fonts/Inter-LICENSE.txt`.
**Why it matters:** Others may reuse the code legally.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-062-1: `LICENSE` and `assets/fonts/Inter-LICENSE.txt` exist (inspection).

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

## Assumptions

- **A-1** The computer has a desktop and an OpenGL graphics driver (product
  definition §10).
- **A-2** One copy of the app or one command uses the Snake folder at a time
  (product definition §10). Nothing prevents two copies; see
  [G-17](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-17).

## Dependencies

- Arcade 3 (window, drawing, input).
- PyTorch 2 and NumPy 2 (optional, DQN only).
- pytest and Ruff (development only).
- A web browser (Open report).
- Git (optional; code identity in reports).

## Interfaces

| Interface | Kind | Where specified |
| --- | --- | --- |
| Keyboard and mouse | User | REQ-007–REQ-010, REQ-021, REQ-028, REQ-033 |
| Terminal commands and exit codes | User | REQ-044–REQ-047, REQ-041, REQ-043 |
| `records/game_records.csv` | File | REQ-018, REQ-022 |
| `replays/<player>_best.json` | File | REQ-020–REQ-022 |
| `learning_data/` Q-tables and DQN saves | File | REQ-024–REQ-031, REQ-044, REQ-045 |
| `experiments/experiment_<id>.json` | File | REQ-034, REQ-046, REQ-047 |
| `reports/` and `docs/results/` pages | File | REQ-038–REQ-043 |
| `settings.json` | File | REQ-016 |

Field-level file formats are not specified here; they belong to the design
(DDS) data dictionary.

## Feasibility

**Input choice:** the owner chose to proceed with the available evidence
(2026-10-26).

| Area | Evidence | Assessment |
| --- | --- | --- |
| Technical | The product is built and its tests pass in CI on three systems. | Feasible: every functional requirement except REQ-054 is already implemented, at least in part. |
| Operational | Local single-user app, started with uv. | Feasible; window checked by hand on macOS only. |
| Economic | Personal project; no budget. | Not applicable. |
| Schedule | No deadline. | Not applicable. |
| External | MIT licence; OFL font; PyTorch BSD-style licence. | No known conflict. |

**Recommendation:** proceed. The open work is closing the gaps in RE-9, not
building new capability.
