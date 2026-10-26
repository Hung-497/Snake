# RE-4.2 — Human Play and Bot play

[Functional index](../RE-4-FUNCTIONAL-REQUIREMENTS.md) · [Review state](../review-state.md)

## Human Play

### REQ-007 v1 — Start and steer
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** In Human Play, the snake shall wait until the Player presses
a first direction key, which may point any way, and then move at the Human
Play speed. The arrow keys and WASD shall steer.

**Source and basis:** Directly stated — README "Human Play controls";
`GameSession` (waiting for first direction), `GameView` key sets.
**Why it matters:** The Player decides when the game starts.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-007-1: Before the first direction key, the snake does not move.
- AC-007-2: The first key may be any direction.
- AC-007-3: Arrow keys and W, A, S, D each steer in their direction.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-008 v1 — Two quick turns kept
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The system shall keep up to two turns pressed quickly in a
row and use one per move. A turn that repeats or reverses the last kept
direction shall be ignored.

**Source and basis:** Directly stated — README ("Two quick turns in a row are
both kept"); `HumanPlayer.MAX_QUEUED_TURNS = 2`.
**Why it matters:** Fast players can make a U-turn without losing a key press.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-008-1: Up then Left pressed before the next move are both used, in order.
- AC-008-2: A third quick turn is dropped.
- AC-008-3: With no kept turn, the snake goes straight.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-009 v1 — Pause
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** During a Human Play game, P or Space shall pause and resume.
Losing window focus shall pause the game until the Player resumes it. Paused
time shall not count in the game time.

**Source and basis:** Directly stated — README "Human Play controls";
`GameSession.toggle_pause`, `pause_for_focus_loss`.
**Why it matters:** The Player can step away without losing the game.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-009-1: P or Space during play stops the snake; pressing again resumes.
- AC-009-2: Losing focus pauses the game, and regaining focus does not resume
  it.
- AC-009-3: The saved game time excludes paused time.
- AC-009-4: Direction keys pressed while paused are ignored.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-010 v1 — Result and play again
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** When a Human Play game ends, the system shall show the result
and score until the Player presses Space or Enter to play again or Esc to
return to the menu.

**Source and basis:** Directly stated — README "Human Play controls";
`GameSession.restart`, `GameView` prompts.
**Why it matters:** The Player sees how the game ended.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-010-1: After a game ends, the result ("You won!" or "Game Over!") and
  "Your score: N" stay on screen.
- AC-010-2: Space or Enter starts a new game that waits for a first direction.
- AC-010-3: Esc returns to the menu.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-011 v1 — Leaving an unfinished game
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** A game the Player leaves before it ends shall not be saved in
Records or Replays.

**Source and basis:** Directly stated — README ("A game you leave with Esc
before it ends is not saved"); `GameSession.finish_game` is the only save.
**Why it matters:** Records only hold games that were actually finished.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-011-1: Leaving with Esc mid-game adds no record and changes no replay.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

## Bot play

### REQ-012 v2 — Watch a Bot Mode
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** Play shall offer Rule Based, Search-Based, Hamiltonian,
Q Learning (v2, v3), and DQN (v2, v3). A chosen bot shall play one game after
another by itself until the Player leaves with Back to Menu or Esc.

**Source and basis:** Directly stated — README "Features", "How to Play";
`BotModeCatalogue`, `GameSession` auto-restart.
**Why it matters:** Watching bots is one of the product's goals.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-012-1: Each Bot Mode can be chosen from Play.
- AC-012-2: After a bot's game ends, the next game starts without input.
- AC-012-3: Back to Menu or Esc stops the bot and returns to the menu.

**Open point / scope limit:** Esc added by DEC-007 (Q-4); not built yet, see
[G-21](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#g-21).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-013 v1 — Boards a bot cannot play
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The system shall refuse to start Hamiltonian on a board whose
sides are both odd, and say why, before any game starts.

**Source and basis:** Derived — `BotFactory.supports_board`; `PlayView`
message "Hamiltonian Bot needs at least one even board side."
**Why it matters:** Hamiltonian cannot cover such a board.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-013-1: With the 25 × 25 board chosen, choosing Hamiltonian shows the
  message and starts no game.
- AC-013-2: RunExperiment with Hamiltonian on an odd-by-odd board stops
  before any game, with an error.

**Open point / scope limit:** None.
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.

### REQ-014 v2 — Speed
Status: Approved — baseline v1

**Type:** Functional
**Requirement:** The speed setting shall set the shortest time between moves:
bots 10, 5, or 1 ms and Human Play 150, 100, or 70 ms, for Slow, Normal, and
Fast. A bot shall make at most 50 moves per frame, and Search-Based at most 1,
so a bot may move slower than its delay.

**Source and basis:** Derived — README "How to Play";
`SessionSettings.speed_delay_for`; `GameSession` per-update caps;
`SearchBasedBot.MAX_MOVES_PER_UPDATE`. Wording follows DEC-008 (Q-5).
**Why it matters:** Bots are watchable, people can react, and the README
describes what users really see.
**Milestone / scope:** Current product.

**Acceptance criteria:**
- AC-014-1: `speed_delay_for` gives the delays above for each speed.
- AC-014-2: A Human Play game makes at most one move per update.
- AC-014-3: A bot makes at most 50 moves per update; Search-Based at most 1.
- AC-014-4: The README describes the speeds this way.

**Open point / scope limit:** README not updated yet; see
[D-8](../RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md#documentation-conflicts).
**Approval evidence:** Approved by the owner as part of baseline v1 on
2026-10-26.
