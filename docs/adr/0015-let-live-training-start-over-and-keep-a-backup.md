# Let Live Training start over with a game limit and keep the old save as a backup

- Status: Accepted
- Category: Bots & Training
- Recorded: 2026-10-16
- Amends: [ADR 0011](0011-train-dqn-in-the-live-training-app-view.md), whose Live Training always continues its save
- Extended by: [ADR 0016](0016-train-q-learning-in-play-on-its-own-app-q-table.md), which gives Q Learning in Play the same choices
- Amended by: [ADR 0017](0017-ship-showcase-bots-and-evaluate-them-on-the-studys-games.md), whose start screen also opens with no save, to reach the Showcase Bot

Live Training always continued a DQN's saved training and never stopped, so the only way to watch a DQN learn from game 0 again was to delete its DQN Training Checkpoint by hand. When the chosen DQN already has a save, Play now opens a Start Live Training App View first. It shows how many games the save holds, its best score and its game limit, and offers "Continue training" or "Start new training".

"Start new training", or choosing a DQN with no save, opens a Set up training App View where the user picks a game limit: Off, 1000, 2000 or 5000 games. Pressing "Start training" moves any old save aside as a dated backup next to it, such as `learning_data/dqn_live_training_2026-10-16_201103.pt`, and Live Training starts from game 0. It stops once the training has played that many games in total.

## Considered Options

- Keep only continuing, and document deleting the file by hand
- A key inside Live Training that starts over after a second press to confirm
- A choice before Live Training opens, offered only when a save exists

A game limit in Settings was also considered, and rejected because the limit belongs to one training, not to the app session.

The choice before opening was chosen because it is visible: nobody has to know a key, and the saved games and best score are shown before deciding. Moving the save aside instead of deleting it means a long run is never lost by one click.

## Consequences

- No Live Training save is ever deleted by the app. Backups never overwrite each other, so they collect in `learning_data/` as Runtime Data until the user removes them.
- Records and Replays are not reset. Games from the new training are saved under the same Player name, after the old run's games.
- The game limit is saved in the DQN Training Checkpoint, so continuing stops at the same limit. Saves from before game limits have none. The limit is not a Settings option, because it belongs to one training rather than to the app session.
- No seed is offered: Live Training keeps seed 0, the same default as `TrainDQN`, so a new Live Training and a default headless run learn the same network.
- Reading the save's summary needs PyTorch. Without it, Play opens Live Training straight away, which explains how to install it. A save that cannot be read offers only "Start new training", which keeps it as a backup, so it is never overwritten.
