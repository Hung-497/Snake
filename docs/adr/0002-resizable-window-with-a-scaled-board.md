# Make the window resizable and scale the board to fit it

ADR 0001 chose a fixed-size window for the first Arcade version. The app now lets the user resize the window, and the board is drawn at the largest whole tile size that fits the space available, never larger than the tile size chosen in Settings. The window has a hard minimum, so no App View ever has to render into a space too small for it.

## Considered Options

- Keep the tile size from Settings absolute, and refuse to shrink the window below the board it needs
- Scale the board to fit the window, treating the tile size as a preference

Scaling was chosen because a hard board-derived minimum barely resizes at all on large boards: a 30 x 30 board at 30 pixels needs the whole of the previous fixed window, so only small boards would have felt resizable. Scaling gives one rule for every board instead of a minimum that silently changes whenever Settings changes.

## Consequences

- Tile Size becomes the preferred size rather than a guarantee, and Settings says so.
- The minimum window size is a rule, not a constant: the larger of an absolute floor and what the current board needs at a minimum readable tile size. Today the floor always wins, so the rule is invisible until board options grow.
- The minimum is enforced by the window itself, so the resize drag stops rather than allowing a window that cannot be drawn into.
- Layout responds in discrete steps rather than scaling text proportionally, because proportional text becomes unreadable at the floor.
- The window size is not remembered between runs. Persisting it would be the app's first user preferences file, which is a separate decision.
