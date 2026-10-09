# Version Learned Artifacts by Feature Set

Feature Set v3 changes what Q Learning and DQN observe, so a Q-table or DQN model trained on one Feature Set gives wrong action values on another. Every Q-table and DQN artifact records its Feature Set and refuses to load under a different one; Q-tables without the marker are treated as v2. Q Learning v3 is a separate Bot Mode (`q_learning_v3`) with its own table, records, and best replay, while DQN stays one Bot Mode whose model file decides the Feature Set, because DQN models already carried that metadata and are only used headlessly.

## Considered Options

- One `q_learning` Bot Mode that switches Feature Set by the loaded table.
- Separate Bot Modes for both Q Learning and DQN.
- A separate Bot Mode for Q Learning only, with DQN chosen by model file.

The last option lets one Bot Experiment compare `q_learning` with `q_learning_v3` and keeps their records and replays apart, without adding a DQN Bot Mode that the app does not use.

## Consequences

- Feature Set v2 stays the baseline: the existing Q-table, Starter Q-table, and DQN models keep working unchanged.
- `q_learning_v3` is not part of the default Bot Experiment set and has no Starter Q-table; a v3 table is created explicitly for training.
- `TrainDQN` keeps v2 as its default Feature Set; v3 is chosen explicitly, and resumed runs use the checkpoint's Feature Set.
