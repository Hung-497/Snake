# Decisions and dispositions

[Package index](index.md) · [Review state](review-state.md)

| ID | Date | Decision | Affects |
| --- | --- | --- | --- |
| DEC-001 | 2026-10-26 | Owner: the requirements describe the existing product (reverse engineering), using the product definition, documents, and code as sources. | All |
| DEC-002 | 2026-10-26 | Owner: remembering the window size is not a product-level exclusion; it is a detail of Settings. | Product definition §11, REQ-016 |
| DEC-003 | 2026-10-26 | Owner: proceed with the available feasibility evidence. | RE-7 Feasibility |
| DEC-004 | 2026-10-26 | Owner (Q-1): DQN Live Training saves every 25 games. Chosen over 50 because saves are small (under 1 MB) and the terminal already checkpoints every 25. | REQ-028 v2, REQ-052 v2 |
| DEC-005 | 2026-10-26 | Owner (Q-2): every failed save shows a message and the app keeps running. | REQ-054 |
| DEC-006 | 2026-10-26 | Owner (Q-3): a version's own training and its Showcase Bot are different bots in the Bot Report. | REQ-039 v2 |
| DEC-007 | 2026-10-26 | Owner (Q-4): Esc returns to the menu in every App View. | REQ-012 v2, REQ-021 v2 |
| DEC-008 | 2026-10-26 | Owner (Q-5): keep the speeds and describe the real behaviour in the README. | REQ-014 v2 |
| DEC-009 | 2026-10-26 | Owner (Q-6): one best replay per Player, whatever the board size. | REQ-020 |
| DEC-010 | 2026-10-26 | Owner (Q-7): terminal training on the app Q-table keeps the game limit and continues the food seed. | REQ-025 v2 |
| DEC-011 | 2026-10-26 | Owner (Q-8): Q Learning numbers games from the start of the training, like DQN; learning from an unfinished game is still not saved. | REQ-026 v2 |
| DEC-012 | 2026-10-26 | Owner (Q-9): check the Showcase Bot file's hash and refuse a changed file. | REQ-036 v2 |
| DEC-013 | 2026-10-26 | Owner (Q-11): Records → Evaluate lists app evaluations only (ADR 0019). | REQ-037 |
| DEC-014 | 2026-10-26 | Owner (Q-10): keep Continue as is; raising the limit of a finished training is deferred. Workaround: limit Off. | REQ-025 v2, RE-1 |
| DEC-015 | 2026-10-26 | Owner: approved baseline v1 (REQ-001 – REQ-062 at their current revisions). | All, RE-11 |
| DEC-016 | 2026-10-26 | Owner: publish the requirements in `docs/requirements/`. Source citations to local files that are not in the repository were replaced with the README, ADRs, code, or tests they come from. No requirement statement or criterion changed, so baseline v1 stays approved. | REQ-006, REQ-049, REQ-057, REQ-059, RE-2 |
