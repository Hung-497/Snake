# RE-2 — Actors and system boundary

[Package index](index.md) · [Review state](review-state.md)

## Actors

| Actor | Responsibilities | Source |
| --- | --- | --- |
| Player | Plays Snake with the keyboard (Human Play) or watches a Bot Mode play. Changes Settings, browses Records, and watches Replays. | Product definition §5 |
| Bot developer | Trains learning Bot Modes, runs Evaluate and Bot Experiments, and reads Bot Reports. Uses the app and the terminal commands. | Product definition §5 |
| Visitor | Clones the repository, starts the app with the README commands, and reads the committed Showcase Report and results. | Product definition §5 |
| Bot Mode | A non-human Player inside the system. It chooses a move each step from the game state and may learn from the result. | README "The Bots"; `snake/bots/BotMode.py` |

Human Play is a Player, never a Bot Mode.

## System boundary

```text
            ┌──────────────────────── Snake AI ────────────────────────┐
 Player ───►│ App window (Arcade): Menu, Play, Settings, Records,      │
            │ Replay, Training, Live Training, Evaluate                │
 Bot     ──►│ Terminal commands: TrainQLearning, TrainDQN,             │
 developer  │ RunExperiment, EvaluateDQN, AnalyseBots                  │
            │                                                          │
            │ Game Engine · Bot Modes · Sessions · Analysis · Storage  │
            └───────────────┬──────────────────────────┬───────────────┘
                            │                          │
                 Runtime Data (local,         Bundled data (in Git):
                 not in Git): records/,       starter_data/ (Starter
                 replays/, learning_data/,    Q-table, Showcase Bots),
                 experiments/, reports/,      docs/results/ (Showcase
                 settings.json                Report)
```

## External systems

- **Web browser**: opens Bot Report pages (Open report in Evaluate).
- **Git**: read for the code identity stored in reports (commit hash), if
  available.
- **PyTorch** (optional): used only by DQN.
- No network services, accounts, or servers.
