# Offer DQN in Play with one network for all boards

- Status: Accepted
- Category: Bots & Training
- Recorded: 2026-10-13
- Discussed in: the modes redesign after [#137](https://github.com/Hung-497/Snake/issues/137); the spec issue follows
- Amends: [ADR 0007](0007-keep-dqn-headless-with-separate-training-and-evaluation-artifacts.md), which kept DQN out of Play and Replay, and [ADR 0011](0011-train-dqn-in-the-live-training-app-view.md), which gave Live Training its own menu entry and one board per save

Live Training trained DQN behind its own menu button that did not say which bot it trained, while Play offered the Q Learning Bot Modes, which already learn while watched, but not DQN. The app now has one place for every Bot Mode: Play lists DQN beside the others, and choosing it opens the Live Training App View, so learning Bot Modes follow one rule: they learn while you watch them. The separate Live Training menu entry goes away. DQN games count like any Play game: they add Records and keep a best Replay, and Replay offers DQN with the board only. PyTorch stays optional: without it, DQN still appears in Play and explains how to install the `dqn` group.

One DQN keeps learning on whatever board is chosen, as the Q-table does, because Feature Set v3 does not depend on the board size. The save records the board it was last trained on.

## Considered Options

- Keep Live Training as its own menu entry and rename it to say DQN
- Split watching from training: Play only watches, and a Train screen trains Q Learning, Q Learning v3, and DQN
- Offer DQN in Play, opening Live Training, with learning Bot Modes learning whenever watched
- For board changes: one DQN for all boards, one DQN per board size, or refusing a save from another board

Offering DQN in Play won because it removes a menu entry and matches how the Q Learning Bot Modes already behave; a Play/Train split would have changed Q Learning's established app behavior and its Training History. One network for all boards won because refusing other boards made DQN a dead end in Play, and one network per board would split learning four ways for no gain, since the features are board-independent.

## Consequences

- DQN Records use the Speed chosen in Settings, like every other Bot Mode, so they share the Board and Speed filters and Compare. Live Training's own speed keys and Background mode change only how fast games are shown, never what the bot does.
- A DQN Replay plays the saved moves on the board; the network graph is not saved, so it is not shown.
- Bot Experiments still include DQN only when selected with an explicit DQN Evaluation Model, as ADR 0007 decided.
- The Live Training save keeps the DQN Training Checkpoint format, so `TrainDQN --resume` still continues it, on the board it was last trained on.
