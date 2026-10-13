# Train DQN in the Live Training App View

- Status: Accepted
- Category: Bots & Training
- Recorded: 2026-10-13
- Discussed in: [#137](https://github.com/Hung-497/Snake/issues/137)
- Amends: [ADR 0007](0007-keep-dqn-headless-with-separate-training-and-evaluation-artifacts.md), which kept DQN headless

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
