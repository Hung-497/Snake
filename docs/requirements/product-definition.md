# Snake AI: Product Definition

- Version: 1 (draft)
- Date: 2026-10-26
- Describes: the app as built at commit `07c9afe`
- Written from: `README.md`, `docs/adr/` (ADR 0001–0021), `docs/training.md`,
  `docs/bot-experiments.md`, `docs/results.md`, `DEVLOG.md`, closed GitHub
  issues, and the code

## 1. Problem

Claims like "this Snake bot plays better" are easy to make and hard to check.
Scores from single games vary a lot, bots are often tested on different games,
and training results are hard to repeat. A person who wants to learn how
different AI approaches play Snake needs one place where they can watch the
bots, train the learning ones, and compare all of them fairly.

## 2. Vision

For people learning about game AI who want to see how different approaches
really compare, Snake AI is a desktop Snake game and bot workbench that lets
them play, watch, train, and evaluate bots on the same fixed games. Unlike a
single Snake bot demo, it measures every bot under the same conditions and
shows how sure each comparison is.

## 3. Purpose

Snake AI is a desktop Snake game in which a person can play Snake and watch
AI bots play it. It is also a small research workbench: the learning bots can
be trained, and every bot can be measured on the same fixed games, so that
different ways of playing Snake can be compared fairly and the comparison can
be repeated.

## 4. Goals

1. **Play**: a person can play a classic Snake game with the keyboard.
2. **Watch**: a person can watch any bot play and see how it decides.
3. **Learn**: the learning bots can be trained, in the app and in the
   terminal, and training can be paused, resumed, or started over without
   losing earlier work.
4. **Compare fairly**: every bot can be evaluated on the same fixed games,
   and the results show which bot plays better and how sure that answer is.
5. **Keep results**: games, best replays, training progress, and evaluation
   reports are kept between runs and are never silently lost or corrupted.

## 5. Users

| User | What they want |
| --- | --- |
| Player | Play Snake themselves, or watch a bot play. |
| Bot developer | Train learning bots, run evaluations and Bot Experiments, and read Bot Reports. Today this is the project owner. |
| Visitor | Someone who clones the repository (for example from a CV or portfolio) and wants to run the app and understand the results. |

## 6. Main features

### 6.1 The game
- A grid board, a snake, and food. The snake grows when it eats; the game
  ends when the snake hits a wall or itself, or wins when it fills the board.
- The snake can never turn straight back into itself.

### 6.2 Players
- **Human Play**: steer with the arrow keys or WASD; pause, resume, play
  again, and return to the menu.
- **Bot Modes**: Rule Based, Search-Based, Hamiltonian, Q Learning (v2, v3),
  and DQN (v2, v3, optional). A bot plays one game after another until the
  person leaves.

### 6.3 Training in the app
- Learning bots (Q Learning and DQN, each in two versions) can continue their
  saved training, start new training with an optional game limit, or be
  evaluated.
- Starting over keeps the old training as a dated backup.
- DQN Live Training shows the board and the neural network side by side while
  it learns.

### 6.4 Evaluate
- Measures a bot (your own training or a bundled, read-only Showcase Bot)
  without learning, on fixed games: 20 or 200 games on a 24 × 25 board with a
  5000-move limit.
- A finished evaluation saves a report and opens its own report page;
  leaving early saves nothing.

### 6.5 Records and replays
- Records compare watched games by board and speed, show trends, list games,
  and list finished evaluations.
- Each Player's best game is saved as a replay that can be watched with
  pause, restart, and three speeds.

### 6.6 Settings
- Game speed, board size, and tile size, kept between app launches.
- The window can be resized; the board scales to fit.

### 6.7 Terminal commands
- Train Q Learning and DQN, evaluate DQN, and run Bot Experiments that
  compare chosen bots on the same seeds, without opening the app.

### 6.8 Bot Reports
- Every finished evaluation updates a local Bot Report: tables, score charts,
  and a game-by-game comparison of any two bots that played the same games.
- Each saved evaluation also gets its own run page.
- A Showcase Report of the study results is published in the repository.

## 7. Quality goals

- **Fair and repeatable**: the same bot, seeds, and settings give the same
  games and the same results.
- **Safe data**: an interrupted save never leaves a broken file; old training
  is backed up, never overwritten.
- **Responsive**: Human Play reacts to the keyboard without missed turns; the
  window stays usable while bots play or train.
- **Cross-platform**: runs on macOS, Windows, and Linux.
- **Easy to start**: a visitor can run the app with a few documented commands.
- **Maintainable**: the game rules and sessions can be tested without a
  window.

## 8. Constraints

- Python 3.13, managed with uv; the window uses Arcade 3 (OpenGL).
- DQN needs the optional PyTorch dependencies and runs on the CPU only.
- Everything runs locally: no network, accounts, or servers.
- Runtime Data (records, replays, training, experiments, reports, settings)
  stays local and is not stored in Git.

## 9. Success measures

- A visitor can start the app on macOS, Windows, or Linux with the Quick
  Start commands in the README.
- Evaluating the same bot file on the same seeds and move limit twice gives
  the same scores.
- Every finished evaluation, in the app or in the terminal, produces its
  report page without any extra command.
- Every comparison of two bots in a Bot Report shows how sure it is (a 95%
  range), not only the averages.
- The automated tests pass on all three systems for every change to `main`.

## 10. Assumptions and risks

- **Assumption**: the computer has a desktop and a graphics driver that
  supports OpenGL.
- **Assumption**: one copy of the app or one command uses the Snake folder at
  a time; two copies writing the same files at once are not expected.
- **Risk**: the app window has only been checked by hand on macOS; Windows and
  Linux are covered by automated tests only.
- **Risk**: learning results depend a lot on the training seed, so one
  training run can make a bot look better or worse than it usually is.
- **Risk**: Runtime Data is not in Git, so deleting the Snake folder loses
  records, replays, and training, apart from the bundled bots.

## 11. Out of scope

- Online play, multiplayer, accounts, or leaderboards.
- GPU training.
- An installer or published package.
- Mobile or web versions.
