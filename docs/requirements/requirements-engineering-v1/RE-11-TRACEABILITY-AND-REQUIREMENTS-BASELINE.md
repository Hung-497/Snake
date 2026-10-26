# RE-11 — Traceability and requirements baseline

[Package index](index.md) · [Review state](review-state.md)

## Requirement catalogue

Source = product definition section. Scenario = RE-3 user journey.
Verification is in [RE-8](RE-8-VERIFICATION-METHODS.md).

| ID | Title | Type | Source | Scenario |
| --- | --- | --- | --- | --- |
| REQ-001 | Start of a game | Functional | §6.1 | UJ-1, UJ-2 |
| REQ-002 | Movement without reversing | Functional | §6.1 | UJ-1 |
| REQ-003 | Eating and growing | Functional | §6.1 | UJ-1, UJ-2 |
| REQ-004 | Game over | Functional | §6.1 | UJ-1, UJ-2 |
| REQ-005 | Winning | Functional | §6.1 | UJ-2 |
| REQ-006 | Preview a move | Functional | §6.1 | UJ-2 |
| REQ-007 | Start and steer | Functional | §6.2 | UJ-1 |
| REQ-008 | Two quick turns kept | Functional | §6.2 | UJ-1 |
| REQ-009 | Pause | Functional | §6.2 | UJ-1 |
| REQ-010 | Result and play again | Functional | §6.2 | UJ-1 |
| REQ-011 | Leaving an unfinished game | Functional | §6.2 | UJ-1 |
| REQ-012 | Watch a Bot Mode | Functional | §6.2 | UJ-2 |
| REQ-013 | Boards a bot cannot play | Functional | §6.2 | UJ-2, UJ-7 |
| REQ-014 | Speed | Functional | §6.2, §6.6 | UJ-1, UJ-2 |
| REQ-015 | Settings choices | Functional | §6.6 | UJ-3 |
| REQ-016 | Remember settings | Functional | §6.6 | UJ-3 |
| REQ-017 | Resizable window | Functional | §6.6 | UJ-3 |
| REQ-018 | Save every finished game | Functional | §6.5 | UJ-1, UJ-2 |
| REQ-019 | Browse Records | Functional | §6.5 | UJ-4 |
| REQ-020 | Keep each Player's best game | Functional | §6.5 | UJ-1, UJ-2, UJ-4 |
| REQ-021 | Watch a replay | Functional | §6.5 | UJ-4 |
| REQ-022 | Read older saved files | Functional | §6.5 | UJ-4 |
| REQ-023 | Training start screen | Functional | §6.3 | UJ-5 |
| REQ-024 | Start new training | Functional | §6.3 | UJ-5 |
| REQ-025 | Continue training and the game limit | Functional | §6.3 | UJ-5 |
| REQ-026 | Q Learning training in the app | Functional | §6.3 | UJ-5, UJ-6 |
| REQ-027 | First use of the shared Q-table | Functional | §6.3 | UJ-5 |
| REQ-028 | DQN Live Training | Functional | §6.3 | UJ-5, UJ-6 |
| REQ-029 | DQN is optional | Functional | §8 | UJ-5, UJ-9 |
| REQ-030 | Unreadable training saves | Functional | §6.3, §7 | UJ-5 |
| REQ-031 | Training History | Functional | §6.3 | UJ-5 |
| REQ-032 | Evaluate on the study's games | Functional | §6.4 | UJ-6, UJ-9 |
| REQ-033 | Fast or watched evaluation | Functional | §6.4 | UJ-6 |
| REQ-034 | Save only a finished evaluation | Functional | §6.4 | UJ-6 |
| REQ-035 | Open the run page | Functional | §6.4 | UJ-6 |
| REQ-036 | Showcase Bots | Functional | §6.4 | UJ-8, UJ-9 |
| REQ-037 | Finished evaluations in Records | Functional | §6.5 | UJ-4, UJ-6 |
| REQ-038 | Rebuild the report after every evaluation | Functional | §6.8 | UJ-6, UJ-7 |
| REQ-039 | Bot Report content | Functional | §6.8 | UJ-6, UJ-7 |
| REQ-040 | Run pages | Functional | §6.8 | UJ-6, UJ-7 |
| REQ-041 | Damaged or missing reports | Functional | §6.8 | UJ-7 |
| REQ-042 | Showcase Report | Functional | §6.8 | UJ-8 |
| REQ-043 | Rebuild the report by hand | Functional | §6.8 | UJ-7 |
| REQ-044 | Train Q Learning from the terminal | Functional | §6.7 | UJ-7 |
| REQ-045 | Train DQN from the terminal | Functional | §6.7 | UJ-7 |
| REQ-046 | Run a Bot Experiment | Functional | §6.7 | UJ-7 |
| REQ-047 | Evaluate DQN from the terminal | Functional | §6.7 | UJ-7 |
| REQ-048 | Same inputs, same games | Quality | §7, §9 | UJ-6, UJ-7 |
| REQ-049 | Bot randomness never moves the food | Quality | §7 | UJ-7 |
| REQ-050 | Reports are deterministic | Quality | §7 | UJ-8 |
| REQ-051 | An interrupted save never breaks a file | Quality | §7 | all |
| REQ-052 | Training progress is never lost | Quality | §7 | UJ-5 |
| REQ-053 | Damaged files never crash the app | Quality | §7 | all |
| REQ-054 | Save failures are reported | Quality | §7 (Proposed, DEC-005) | all |
| REQ-055 | The window stays responsive | Quality | §7 | UJ-5, UJ-6 |
| REQ-056 | Easy first run | Quality | §7, §9 | UJ-9 |
| REQ-057 | Testable without a window | Quality | §7, §9 | — |
| REQ-058 | Python 3.13 managed with uv | Constraint | §8 | UJ-9 |
| REQ-059 | Arcade only in the presentation layer | Constraint | §8 | — |
| REQ-060 | DQN uses optional, CPU-only PyTorch | Constraint | §8 | UJ-9 |
| REQ-061 | Local only, Runtime Data out of Git | Constraint | §8 | — |
| REQ-062 | Licences | Constraint | §11 | — |

## Coverage of the product definition

| Product definition | Requirements |
| --- | --- |
| §4 Goal 1 Play | REQ-001 – REQ-011 |
| §4 Goal 2 Watch | REQ-012 – REQ-014, REQ-020, REQ-021 |
| §4 Goal 3 Learn | REQ-023 – REQ-031, REQ-044, REQ-045 |
| §4 Goal 4 Compare fairly | REQ-032 – REQ-043, REQ-046 – REQ-050 |
| §4 Goal 5 Keep results | REQ-018, REQ-022, REQ-051 – REQ-054 |
| §10 Assumptions | RE-7 A-1, A-2 |

## Baseline

**Baseline v1: approved** by the owner on 2026-10-26 (DEC-015).

| Member | Version |
| --- | --- |
| [Product definition](../product-definition.md) | version 1 |
| REQ-001 – REQ-062 | v2: REQ-012, 014, 021, 025, 026, 028, 036, 039, 052; v1: the rest |
| Content identity (after DEC-016) | SHA-256 `17ae3dcbdaac6b67…` of the product definition, `functional/*.md`, RE-6, and RE-7, joined in that order |

Limitations kept with this baseline:

- The owner is the only stakeholder consulted (RE-10).
- 24 verification gaps and 9 documentation conflicts are open (RE-9); approval
  states what the product must do, not that it already does it.
- One capability is deferred (RE-1).

Any later change to a requirement follows requirements management: record the
change and its reason, check which other requirements it affects, raise the
revision, and approve a new baseline. Baseline v1 stays as it is.
