# Let Live Training start over and keep the old save as a backup

- Status: Accepted
- Category: Bots & Training
- Recorded: 2026-10-16
- Amends: [ADR 0011](0011-train-dqn-in-the-live-training-app-view.md), whose Live Training always continues its save

Live Training always continued a DQN's saved training, so the only way to watch a DQN learn from game 0 again was to delete its DQN Training Checkpoint by hand. When the chosen DQN already has a save, Play now opens a Start Live Training App View first. It shows how many games the save holds and its best score, and offers "Continue training" or "Start new training". Starting new moves the save aside as a dated backup next to it, such as `learning_data/dqn_live_training_2026-10-16_201103.pt`, and Live Training then starts fresh. A DQN with no save goes straight to Live Training as before.

## Considered Options

- Keep only continuing, and document deleting the file by hand
- A key inside Live Training that starts over after a second press to confirm
- A choice before Live Training opens, offered only when a save exists

The choice before opening was chosen because it is visible: nobody has to know a key, and the saved games and best score are shown before deciding. Moving the save aside instead of deleting it means a long run is never lost by one click.

## Consequences

- No Live Training save is ever deleted by the app. Backups never overwrite each other, so they collect in `learning_data/` as Runtime Data until the user removes them.
- Records and Replays are not reset. Games from the new training are saved under the same Player name, after the old run's games.
- Reading the save's summary needs PyTorch. A save that cannot be read still offers both choices, and Live Training explains the problem if the user continues.
