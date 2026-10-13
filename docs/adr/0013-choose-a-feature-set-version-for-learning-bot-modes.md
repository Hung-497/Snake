# Choose a Feature Set version for learning Bot Modes

- Status: Accepted
- Category: Bots & Training
- Recorded: 2026-10-13
- Discussed in: the version grouping after [#151](https://github.com/Hung-497/Snake/issues/151); the spec issue follows
- Amends: [ADR 0011](0011-train-dqn-in-the-live-training-app-view.md), which trained only a Feature Set v3 DQN, and [ADR 0012](0012-offer-dqn-in-play-with-one-network-for-all-boards.md), which kept one DQN for all boards

Play and Replay listed Q Learning and Q Learning v3 as unrelated buttons, and DQN existed only for Feature Set v3, so the difference between the versions was hard to see. Play and Replay now show one button per learning family, Q Learning and DQN, and choosing one opens a small screen to pick Feature Set v2 or v3, each with one line saying what that version sees. DQN gains a Feature Set v2 version, and Live Training draws its network with 9 inputs instead of 12. There is now one DQN per Feature Set, each still learning on every board size.

Player names saved in Records, Replays, and saves do not change: `q_learning` (v2), `q_learning_v3`, and `dqn` (v3) keep their names, and the new DQN is `dqn_v2`. Only the labels change, so every learning Player shows its version: Q Learning v2, Q Learning v3, DQN v2, and DQN v3. Records keep one filter per Player, so the versions can be compared.

## Considered Options

- Rename every Player to one pattern, such as `q_learning_v2` and `dqn_v3`
- Keep the saved names, add `dqn_v2`, and show the version in every label
- Pick the version on its own screen, expand the family button in place, or use one v2/v3 switch for all of Play

Keeping the saved names won because renaming would mean migrating existing Q Learning Records, Replays, and Q-tables for no change in behavior. A separate version screen won because it stays readable at the smallest window size and makes the chosen version explicit before a game starts.

## Consequences

- DQN v2 keeps its own Live Training save, separate from DQN v3's existing one, in the same DQN Training Checkpoint format.
- The Bot Mode factory, Bot Experiments, and the headless commands keep the same Bot Mode names.
- A Q-table panel for Q Learning is still not part of this; Q Learning versions differ in behavior and Records, not in a picture.
