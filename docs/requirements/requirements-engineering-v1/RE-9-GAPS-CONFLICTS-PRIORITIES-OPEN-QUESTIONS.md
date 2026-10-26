# RE-9 — Gaps, conflicts, priorities, and open questions

[Package index](index.md) · [Review state](review-state.md)

Found by checking the requirements against the code at `07c9afe`. Priority:
**High** = can lose data or crash; **Medium** = wrong or inconsistent
behaviour; **Low** = cosmetic or rare.

## Owner decisions

Each question was a product decision: the code worked one way, and the owner
chose what the product should do. All are answered (2026-10-26). A decision
that changes behaviour creates a gap below until the code follows it.

| Question | Owner decision | Requirement | Work |
| --- | --- | --- | --- |
| <a id="q-1"></a>Q-1 DQN Live Training loses the whole session on a crash. | Save every 25 games (DEC-004). | REQ-028 v2, REQ-052 v2 | G-18 |
| <a id="q-2"></a>Q-2 Save failures crash the app; only Settings shows a message. | Show a message and keep running, for every save (DEC-005). | REQ-054 | G-19 |
| <a id="q-3"></a>Q-3 Your training and the Showcase Bot of a version are merged in the Bot Report. | Separate them so they can be compared (DEC-006). | REQ-039 v2 | G-20 |
| <a id="q-4"></a>Q-4 Esc does not leave a bot game or replay playback. | Esc returns to the menu in every App View (DEC-007). | REQ-012 v2, REQ-021 v2 | G-21 |
| <a id="q-5"></a>Q-5 The speed setting barely changes Search-Based. | Describe the real behaviour in the README (DEC-008). | REQ-014 v2 | D-8 |
| <a id="q-6"></a>Q-6 The best replay ignores board size and speed. | Keep one best replay per Player (DEC-009). | REQ-020 | None |
| <a id="q-7"></a>Q-7 Terminal training on the app Q-table erases the app game limit. | Keep the limit and continue the food seed (DEC-010). | REQ-025 v2 | G-22 |
| <a id="q-8"></a>Q-8 Q Learning numbers games per visit, DQN in total. | Both number games in total; keep the learning rule on leaving (DEC-011). | REQ-026 v2 | G-23 |
| <a id="q-9"></a>Q-9 The app does not check the Showcase Bot file. | Check the hash and refuse a changed file (DEC-012). | REQ-036 v2 | G-24 |
| <a id="q-10"></a>Q-10 A finished limited training cannot be extended. | Keep as is; extending is deferred (DEC-014). | REQ-025 v2 | RE-1 Deferrals |
| <a id="q-11"></a>Q-11 Terminal reports are not listed in Records → Evaluate. | Keep as ADR 0019 decided (DEC-013). | REQ-037 | None |

## Verification gaps

The requirement is clear, but the code does not fully meet it. These need a
fix, not a decision.

| ID | Gap | Requirement | Priority |
| --- | --- | --- | --- |
| <a id="g-1"></a>G-1 | A damaged best-replay file crashes the app at the end of a game, and that game's record is lost (`ReplayManager.should_replace_replay` reads it with no error handling). | REQ-018, REQ-053 | High |
| <a id="g-2"></a>G-2 | `records/game_records.csv` is appended directly, so an interrupted write can leave a broken row. | REQ-051 | High |
| <a id="g-3"></a>G-3 | Reports, report pages, and charts are written directly, and the rebuild deletes old pages first, so an interruption leaves broken or missing files. | REQ-051 | Medium |
| <a id="g-4"></a>G-4 | Continue with a Q-table whose game count is readable but whose content is invalid (wrong Feature Set, bad values) crashes the Game App View. | REQ-030, REQ-053 | High |
| <a id="g-5"></a>G-5 | A PyTorch install that fails with `OSError` (e.g. a missing Windows DLL) crashes the app; only `ImportError` is handled. | REQ-029 | Medium |
| <a id="g-6"></a>G-6 | Records can crash on a damaged CSV (bad encoding, NUL bytes, a row with one field). | REQ-053 | Medium |
| <a id="g-7"></a>G-7 | An evaluation whose report save or rebuild fails crashes the app (see Q-2). | REQ-053, REQ-054 | High |
| <a id="g-8"></a>G-8 | When no usable report is left, old run pages and the old Bot Report are not removed. | REQ-041 | Low |
| <a id="g-9"></a>G-9 | `EvaluateDQN` without PyTorch fails with a traceback (exit 1); `RunExperiment` gives a clear error (exit 2). | REQ-029 | Low |
| <a id="g-10"></a>G-10 | Very old 9-column records files get misaligned columns when upgraded. | REQ-022 | Low |
| <a id="g-11"></a>G-11 | Records → Evaluate trusts a report's summary, while the Bot Report recomputes it from the games, so the two can disagree. | REQ-037 | Low |
| <a id="g-12"></a>G-12 | If the run page could not be written, Evaluate still says "Open report (R)". | REQ-035 | Low |
| <a id="g-13"></a>G-13 | The terminal cannot evaluate a DQN training checkpoint, so an app DQN evaluation cannot be repeated from the terminal; `EvaluateDQN` also duplicates the report code. | REQ-047, REQ-048 | Low |
| <a id="g-14"></a>G-14 | DQN saves have no code identity, unlike Q-tables. | REQ-031 | Low |
| <a id="g-15"></a>G-15 | Rebuilding the Bot Report after an evaluation, and loading a DQN save on the Play click, run inside one frame and can freeze the window. | REQ-055 | Low |
| <a id="g-16"></a>G-16 | No automated test covers any App View (keys, buttons, messages, save on leave); only the manual smoke checklist does. | REQ-057 | Medium |
| <a id="g-17"></a>G-17 | Nothing stops two copies of the app writing the same files; temporary file names would collide. | A-2 | Low |
| <a id="g-18"></a>G-18 | DQN Live Training saves only on leave or close, not every 25 games. | REQ-028, REQ-052 | High |
| <a id="g-19"></a>G-19 | Only Settings reports a failed save; every other save crashes the app. | REQ-054 | High |
| <a id="g-20"></a>G-20 | Your training and the Showcase Bot of a version share one label in the Bot Report and run pages. | REQ-039 | Medium |
| <a id="g-21"></a>G-21 | Esc does nothing in a bot game or replay playback. | REQ-012, REQ-021 | Medium |
| <a id="g-22"></a>G-22 | Terminal training on the app Q-table drops the game limit and restarts the food seed. | REQ-025 | Medium |
| <a id="g-23"></a>G-23 | Q Learning app training numbers games from the start of the visit. | REQ-026 | Low |
| <a id="g-24"></a>G-24 | Evaluate showcase does not check the Showcase Bot file's hash. | REQ-036 | Low |

## Documentation conflicts

The code and a document disagree; the requirement follows the code.

| ID | Document | Says | Code does |
| --- | --- | --- | --- |
| D-1 | `docs/training.md` | DQN runs only from the terminal. | Live Training exists in the app. |
| D-2 | `docs/training.md` | The app starts Q Learning without a table. | The app copies the shared table once (REQ-027). |
| D-3 | `docs/training.md` | TrainQLearning prints score and learning progress. | It prints one final line. |
| D-4 | Smoke checklist #31, #36 | Reopening Live Training starts fresh; Play lists DQN directly. | It continues; DQN goes through Choose a version. |
| D-5 | `LiveTrainingCheckpointError` | "Delete <path> to start over." | The app offers Start new. |
| D-6 | Human Play prompt | "Press an arrow key to start". | WASD works too. |
| D-7 | Records | Games tab uses local time. | Evaluate tab says UTC. |
| D-8 | README | Bots move every 10, 5, or 1 ms. | Bots are capped per frame; Search-Based moves once per frame (REQ-014 v2). |
| D-9 | `docs/bot-experiments.md` | Pages of deleted reports are removed. | Not when no usable report is left (G-8). |

## Priorities

1. **High** — can lose data or crash: G-1, G-2, G-4, G-7, G-18, G-19.
2. **Medium** — wrong or inconsistent behaviour: G-3, G-5, G-6, G-16, G-20,
   G-21, G-22.
3. **Low** and documentation conflicts (D-1 – D-9) when convenient.
