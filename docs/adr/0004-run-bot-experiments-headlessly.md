# Run Bot Experiments headlessly and keep their records separate

Bot Experiments run through the Game Engine and Bot Mode contract without an Arcade window. A headless runner can use fixed seeds and compare Bot Modes without the frame timing, replay saving, and watched-game records owned by `GameSession`. Each experiment saves its own JSON result instead of adding benchmark games to the existing game-record CSV.

## Considered Options

- Reuse `GameSession` and the watched-game CSV for experiments.
- Run experiments headlessly and store separate JSON results.

The second option keeps measurements reproducible and prevents benchmark games from appearing as games watched in the app.

## Consequences

- Q Learning training is explicit and resumes the existing saved Q-table. The Arcade Game App View keeps its current training behavior.
- Q Learning evaluation does not explore, update values, decay epsilon, or change the Q-table. Benchmark evaluation changes no learning data, watched-game records, or replays; its experiment JSON is the only saved result.
- An all-Bot Mode comparison rejects a board unsupported by Hamiltonian before any games begin.
