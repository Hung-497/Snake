# RE-5 — Domain rules and glossary

[Package index](index.md) · [Review state](review-state.md)

## Domain rules

The game's own rules are requirements tagged *Domain rule*:

- No reversing: [REQ-002](functional/RE-4-1-GAME-RULES.md#req-002-v1--movement-without-reversing)
- Eating and growing: [REQ-003](functional/RE-4-1-GAME-RULES.md#req-003-v1--eating-and-growing)
- Game over: [REQ-004](functional/RE-4-1-GAME-RULES.md#req-004-v1--game-over)
- Winning: [REQ-005](functional/RE-4-1-GAME-RULES.md#req-005-v1--winning)

Fair comparison rules:

- Bots are compared only on identical Experiment Conditions
  ([REQ-039](functional/RE-4-5-EVALUATION-REPORTS.md#req-039-v2--bot-report-content)).
- Evaluation never learns
  ([REQ-032](functional/RE-4-5-EVALUATION-REPORTS.md#req-032-v1--evaluate-on-the-studys-games)).

## Glossary

| Term | Meaning |
| --- | --- |
| Player | Whoever controls the snake in a game: a person (Human Play) or a Bot Mode. |
| Human Play | A person playing with the keyboard. A Player, never a Bot Mode. |
| Bot Mode | A program that plays Snake: Rule Based, Search-Based, Hamiltonian, Q Learning, or DQN. |
| Learning Bot Mode | A Bot Mode that improves with training: Q Learning or DQN. |
| Feature Set | The facts a learning bot sees about the board. v2 has 9 features; v3 adds tail reachability (12). |
| Version | A learning Bot Mode with one Feature Set, e.g. Q Learning v3. |
| Q-table | The saved learning of a Q Learning bot (JSON). |
| Training History | The list of training sessions stored in a Q-table. |
| Live Training | DQN training in the app, showing the network. |
| Game limit | The number of games after which a training run stops (Off, 1000, 2000, 5000). |
| Move limit | The number of moves after which a game is stopped (5000 in the study). |
| Evaluate / Evaluation Mode | Measuring a bot on fixed games without learning. |
| Study's games | 24 × 25 board, seeds from 200000, 5000-move limit; 20 or 200 games. |
| Showcase Bot | A read-only trained bot shipped in `starter_data/showcase/`. |
| Baseline | A Bot Mode that does not learn: Rule Based, Search-Based, Hamiltonian. |
| Bot Experiment | A run that plays chosen bots on the same seeds and saves one report. |
| Experiment Conditions | Board size, move limit, and exact seed list of a run. |
| Bot Report | The local pages comparing every saved run, in `reports/`. |
| Run page | The page of one saved report, in `reports/runs/`. |
| Showcase Report | The committed Bot Report of the study, in `docs/results/`. |
| Runtime Data | Files the app creates while used; local and git-ignored. |
| Starter Q-table | The bundled Q-table in `starter_data/` copied once before first use. |
| 95% range | The range that the true average difference between two bots lies in, with 95% confidence. |
