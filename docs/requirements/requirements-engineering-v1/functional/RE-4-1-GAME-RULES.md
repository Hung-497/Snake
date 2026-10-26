# RE-4.1 — Game rules

[Functional index](../RE-4-FUNCTIONAL-REQUIREMENTS.md) · [Review state](../review-state.md)

### REQ-001 v1 — Start of a game
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** When a game starts, the system shall place a one-cell snake on
a random cell of the board, facing right, with one food on a free cell and a
score of 0.

**Source and basis:** Derived — product definition §6.1;
`snake/engine/SnakeEngine.py` (start state, food placement).
**Why it matters:** Every Player starts from the same kind of position.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-001-1: A new game has exactly one snake cell inside the board, the score
  is 0, and the snake faces right.
- AC-001-2: The food is inside the board and not on the snake.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-002 v1 — Movement without reversing
Status: Approved — baseline v1

**Type:** Functional
**Tags:** Domain rule
**Requirement:** Each step, the snake shall move one cell in its current
direction. A change to the opposite direction shall be refused, except for the
first direction of a snake that has no body yet.

**Source and basis:** Directly stated — README "Human Play controls" ("A key
that would turn the snake straight back into itself is ignored");
`SnakeEngine.change_direction`, `choose_start_direction`.
**Why it matters:** A snake turning back into itself would end the game for no
reason.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-002-1: A snake facing right that is told to go left keeps going right.
- AC-002-2: A snake with no body may start in any direction, including left.
- AC-002-3: After one step, the head is one cell further in the current
  direction.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-003 v1 — Eating and growing
Status: Approved — baseline v1

**Type:** Functional
**Tags:** Domain rule
**Requirement:** When the snake moves onto the food, the snake shall grow by
one cell, the score shall rise by 1, and new food shall appear on a random
free cell.

**Source and basis:** Derived — product definition §6.1;
`SnakeEngine.step`, `place_food`.
**Why it matters:** This is how the score is earned.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-003-1: Moving onto food increases the snake length by 1 and the score
  by 1.
- AC-003-2: The new food is on a free cell.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-004 v1 — Game over
Status: Approved — baseline v1

**Type:** Functional
**Tags:** Domain rule
**Requirement:** The game shall end when the snake moves outside the board or
into its own body. Moving into the cell the tail is leaving in the same step
shall be allowed.

**Source and basis:** Derived — product definition §6.1;
`SnakeEngine.preview` collision rules.
**Why it matters:** This is the rule every Player must avoid.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-004-1: A move outside the board ends the game, and the snake stays where
  it was.
- AC-004-2: A move into a body cell ends the game.
- AC-004-3: A move into the tail cell when no food is eaten does not end the
  game.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-005 v1 — Winning
Status: Approved — baseline v1

**Type:** Functional
**Tags:** Domain rule
**Requirement:** The game shall be won when the snake fills every cell of the
board.

**Source and basis:** Derived — product definition §6.1; `SnakeEngine`
(win when body + head equals the number of cells).
**Why it matters:** The Hamiltonian bot is measured by winning.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-005-1: Eating the last free cell ends the game as won, and no new food
  appears.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-006 v1 — Preview a move
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The system shall let a Player ask what a move would do
(where the head goes, whether it eats or collides) without changing the game,
and the real move shall then give the same result.

**Source and basis:** Derived — README "Project Structure" (engine);
`SnakeEngine.preview`, `step`.
**Why it matters:** Bots check safety with it; a preview that disagreed with
the real move would make bots die.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-006-1: For any state and direction, `step` produces the transition that
  `preview` reported.
- AC-006-2: Calling `preview` changes no game state and uses no randomness.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.
