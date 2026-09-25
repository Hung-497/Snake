# Keep motion in the presentation layer, and do not animate snake movement

The app adds motion to the interface: hover and press feedback, a short cross-fade between App Views, and time-based board effects such as a pulsing food and an end-of-game flash. Every effect is driven by elapsed wall-clock time inside an App View. The snake itself is not animated between cells.

Cell-to-cell animation was ruled out by the speed settings rather than by taste. A game step is 1 millisecond on Fast, 5 on Normal and 10 on Slow, while a frame is about 17 milliseconds, so the snake advances roughly sixteen, three and two cells per frame respectively. No frame ever shows a single step in progress, so there is nothing to interpolate without adding a speed far slower than any the app offers.

## Consequences

- The Game Engine, the game session and the replay session stay free of animation state, so they keep running and keep being tested without a display.
- Board effects suppress themselves at the fastest speed, where a flash on every finished game would strobe several times a second.
- The cross-fade is drawn as an overlay rather than by rendering two App Views at once, so the shell that owns App View flow is unchanged and its tests still need no display.
