# RE-3 — Usage scenarios

[Package index](index.md) · [Review state](review-state.md)

Each scenario is a user journey across features. Its criteria live with the
linked requirements.

## UJ-1 Play a game myself

Player opens Play → Play Yourself, presses a direction, steers, pauses, and
sees the result, then plays again or returns to the menu. The game is saved
in Records, and the best one becomes a Replay.
Requirements: REQ-001–REQ-011, REQ-018, REQ-020.

## UJ-2 Watch a bot play

Player chooses a Bot Mode and watches it play one game after another at the
chosen speed, then goes back to the menu.
Requirements: REQ-012–REQ-014, REQ-018, REQ-020.

## UJ-3 Change Settings

Player changes speed, board size, or tile size; the choices apply at once and
are restored the next time the app starts.
Requirements: REQ-015–REQ-017.

## UJ-4 Look back at games

Player compares Players in Records, looks at trends and recent games, and
watches the best Replay of a Player.
Requirements: REQ-019–REQ-022, REQ-037.

## UJ-5 Train a learning bot in the app

Bot developer chooses Q Learning or DQN and a version, then continues the
saved training or starts new training with a game limit. Training saves its
progress; starting over keeps the old training as a backup.
Requirements: REQ-023–REQ-031.

## UJ-6 Train → Evaluate → see the report

Bot developer trains a learning bot, evaluates it on the study's games, and
opens the run page that compares it with every other bot that played the same
games, without running any extra command.
Requirements: REQ-026, REQ-028, REQ-032–REQ-035, REQ-038–REQ-040, REQ-048.

## UJ-7 Compare bots from the terminal

Bot developer runs a Bot Experiment on chosen bots and seeds; the report is
saved and the Bot Report and run page paths are printed.
Requirements: REQ-044–REQ-047, REQ-038–REQ-041, REQ-043.

## UJ-8 Publish the study results

Bot developer rebuilds the committed Showcase Report from the full study
evaluations of the Showcase Bots and the Baselines.
Requirements: REQ-036, REQ-042, REQ-050.

## UJ-9 First run by a visitor

Visitor clones the repository, runs the Quick Start commands, and can play,
watch bots, and evaluate a Showcase Bot without training anything.
Requirements: REQ-032, REQ-036, REQ-056, REQ-058.
