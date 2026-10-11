# Training the Learning Bots

Q Learning and DQN are the two Bot Modes that learn from play. Both can be
trained from the terminal without opening the app window. Run every command
below from the project root.

- To compare trained bots with the others, see [Bot Experiments](bot-experiments.md).
- For the results of past training runs, see [Results](results.md).
- The decisions behind this setup are [ADR 0005](adr/0005-separate-runtime-data-from-starter-table.md)
  (Starter Q-table), [ADR 0007](adr/0007-keep-dqn-headless-with-separate-training-and-evaluation-artifacts.md)
  (DQN files), [ADR 0009](adr/0009-version-learned-artifacts-by-feature-set.md)
  (Feature Sets), and [ADR 0010](adr/0010-keep-q-learning-training-history-inside-the-q-table.md)
  (Training History).

## Set up the Starter Q-table

The project bundles a Starter Q-table at
`starter_data/q_table_space_state_v2.json`. Headless training and Bot
Experiments need a local saved Q-table. From the project root, copy the starter
once before using either command:

```bash
mkdir -p learning_data
cp -n starter_data/q_table_space_state_v2.json learning_data/q_table_space_state_v2.json
```

The `-n` option preserves an existing local table. On Windows, create the
`learning_data` folder and copy the starter with File Explorer only when the
local table does not already exist. Later training updates the local copy; the
Starter Q-table stays unchanged. The app can also start Q Learning without a
saved table, beginning new local progress instead of loading the starter.

## Q Learning

### Train

```bash
uv run python -m snake.sessions.TrainQLearning --games 100 --width 24 --height 25 --seed 7 --max-moves 5000
```

This resumes the existing saved Q-table and saves learning progress back to it
after each game. A missing or malformed table stops the command with an error;
training does not start a new table unless you ask for one with `--new-table`
(see [Q Learning v3](#q-learning-v3)). The command prints score and learning
progress in the terminal. It does not add game records or replays.

`--games` is required. The default board is 24 × 25, the default Tile Size is
25, the default seed is 0, and the default move limit is 5000 per game.
`--q-table path/to/table.json` trains a different table.

### Training History

Each Q-table keeps a Training History: a `training_history` list inside the
table with one entry per training session, from this command or from app play
(one entry per visit to the Game view that finishes at least one game). An
entry records the seed, board, move limit, learning settings, code version, and
the games, epsilon, and scores at the start and end of the session. It is
updated after every game, so a run stopped part-way is still described. Tables
saved before this feature have no history and still load. The first time one
is trained again, an `unrecorded` entry counts the games it already had, so the
history always adds up to the table's game count. A table whose history is
broken is refused. Bot Experiment reports copy the evaluated table's Training
History.

### Q Learning v3

Q Learning v3 is a separate Bot Mode that uses Feature Set v3. On top of the
nine v2 features, it checks whether each move keeps the tail reachable, and it
counts open space as the tail moves away instead of treating the whole body as
a wall. It keeps its own table, `learning_data/q_table_space_state_v3.json`,
plus its own records and best replay, so it never changes the v2 table. Every
Q-table records its Feature Set, and a table saved under another Feature Set is
refused.

There is no v3 Starter Q-table. Start an empty v3 table explicitly:

```bash
uv run python -m snake.sessions.TrainQLearning --bot q_learning_v3 --new-table --games 100 --seed 7
```

`--new-table` never overwrites an existing table. Leave it out to continue
training the saved v3 table, and add `--q-table path/to/table.json` to keep
several v3 tables apart, for example one per training seed. `--new-table` also
starts an empty v2 table when `--bot` is left out; give it its own
`--q-table` path, because the default v2 table already exists after setup.

## DQN

DQN is an optional, CPU-only Deep Q Learning experiment. Its action values come
from a neural network instead of a Q-table. It runs only from the terminal; the
app does not offer it.

### Install PyTorch

The normal Snake app and default Bot Experiments do not need PyTorch. Install
it only when you want to train or evaluate DQN:

```bash
uv sync --group dqn
```

A plain `uv sync` removes PyTorch again. The DQN commands below use
`uv run --group dqn`, which reinstalls it when it is missing.

On Windows, PyTorch also needs Microsoft's Visual C++ Redistributable. Most
Windows PCs already have it, but a fresh Windows (or Windows Server) install
may not, and importing torch then fails with `WinError 1114` while loading
`c10.dll`. Install it from <https://aka.ms/vs/17/release/vc_redist.x64.exe>.

### Train a new model

```bash
uv run --group dqn python -m snake.sessions.TrainDQN --games 100 --width 24 --height 25 --seed 7 --max-moves 5000
```

Each run gets its own `learning_data/dqn_runs/<run-id>/` folder:

- `training.json` records each game and loss.
- `checkpoint.pt` contains the full resumable state: both networks, optimizer,
  epsilon, game count, replay buffer, and random states. It is updated every
  25 games by default and at completion; use `--checkpoint-every` to change
  that interval.
- `model.pt` contains the trained network and identifying metadata for
  evaluation.

`--batch-size` changes the number of replay experiences used per update.

### Network and learning settings

The network is a feed-forward `9 → 64 → 64 → 3` network: the nine Q Learning
features enter two 64-unit ReLU layers, and the three outputs are the values
of Straight, Turn Left, and Turn Right. Training uses Adam with a learning rate
of 0.001, uniform experience replay with a 10,000-transition capacity and a
batch size of 32, and no extra warm-up beyond collecting one complete batch.
The target network copies the online network every 100 optimizer steps. These
values, the explicit CPU device, and the network shape are stored in every new
version 2 checkpoint and evaluation model. Version 1 files created by the
earlier DQN implementation remain loadable.

### Train on Feature Set v3

To train DQN on Feature Set v3 (the twelve features Q Learning v3 uses), add
`--features v3`. The network then takes twelve inputs instead of nine:

```bash
uv run --group dqn python -m snake.sessions.TrainDQN --features v3 --games 100 --width 24 --height 25 --seed 7 --max-moves 5000
```

Without `--features`, training uses v2. Checkpoints and evaluation models
record their Feature Set, so resuming a run keeps it, and evaluation and Bot
Experiments read it from the model. A model with an unknown Feature Set is
rejected.

### Resume training

Continue for **additional** games from a checkpoint:

```bash
uv run --group dqn python -m snake.sessions.TrainDQN --resume learning_data/dqn_runs/<run-id>/checkpoint.pt --games 100
```

Resume restores the saved board, seed, move limit, learning settings, and
random state. It writes a new run folder and leaves the source checkpoint
untouched. Supplied settings that conflict with the checkpoint are rejected.

### Evaluate a model

To evaluate a fixed model on the same board or another board, use `model.pt`:

```bash
uv run --group dqn python -m snake.sessions.EvaluateDQN --model learning_data/dqn_runs/<run-id>/model.pt --games 10 --width 24 --height 25 --seed 7
```

Evaluation does not explore, learn, or alter the saved model. It writes a
version 3 report in `experiments/`, including the model hash and both training
and evaluation boards. A training checkpoint cannot be used as an evaluation
model. DQN uses the same Feature Set, three relative actions, safe-action
selection, reward, discount, and epsilon rules as tabular Q Learning.

To compare a DQN model with other Bot Modes on the same seeds, use a
[Bot Experiment](bot-experiments.md#include-dqn).
