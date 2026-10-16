# Train DQN in the Live Training App View

- Status: Accepted
- Category: Bots & Training
- Recorded: 2026-10-13
- Updated: 2026-10-13, Live Training sets its own larger window minimum
- Discussed in: [#137](https://github.com/Hung-497/Snake/issues/137)
- Amends: [ADR 0007](0007-keep-dqn-headless-with-separate-training-and-evaluation-artifacts.md), which kept DQN headless
- Amended by: [ADR 0012](0012-offer-dqn-in-play-with-one-network-for-all-boards.md), which opens Live Training from Play and keeps one DQN for all boards
- Amended by: [ADR 0013](0013-choose-a-feature-set-version-for-learning-bot-modes.md), which adds a Feature Set v2 DQN
- Amended by: [ADR 0014](0014-split-live-training-in-half-and-fill-the-board-half.md), which splits the window in half and scales the board to fill its half

ADR 0007 kept DQN out of the app, so the only way to train it was the headless command and the network was never visible while it learned. The app now has one opt-in App View, Live Training, that trains a Feature Set v3 DQN Bot Mode in the window and shows the board as it learns. PyTorch stays optional: the app still starts without it, and Live Training explains how to install the `dqn` dependency group instead of failing.

## Considered Options

- Keep DQN headless and only show a trained DQN Evaluation Model in the app
- Train in the app, in a Live Training App View that loads PyTorch only when it opens
- Make PyTorch required so the app can import DQN at startup

Training in the app was chosen because watching the network learn is the point of the feature; a finished model hides how it got there. Loading PyTorch only when Live Training opens keeps the part of ADR 0007 that still matters: ordinary play needs no PyTorch.

## Consequences

- DQN stays out of BotFactory and the Play, Replay, and Bot Experiment selections. Live Training is the only place the app trains DQN.
- Live Training makes each move through the same single training move as the headless commands, with the same seeds and CPU settings as DQN training, so watching never changes what is learned. A test checks it reaches the same network as the headless command.
- The Live Training App View reaches DQN only through a module that imports PyTorch when called, never when loaded, and the optional-dependency tests keep app startup free of PyTorch.
- The rest of ADR 0007 still holds, including the separate DQN Training Checkpoint and DQN Evaluation Model.

## Update

2026-10-13: Live Training draws the network graph beside the board, which does not fit in the app's 700 x 700 minimum window from ADR 0002. While Live Training is open, it grows the window to fit the graph and the board at the Tile Size from Settings, never past the screen the window is on, and raises the minimum to fit the graph and a readable board. Leaving it restores the usual minimum, so every other App View keeps ADR 0002's small-window support.
