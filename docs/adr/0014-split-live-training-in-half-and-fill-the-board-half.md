# Split Live Training in half and let the board fill its half

- Status: Accepted
- Category: Game & UI
- Recorded: 2026-10-16
- Amends: [ADR 0002](0002-resizable-window-with-a-scaled-board.md), which never draws the board larger than the Settings Tile Size
- Amends: [ADR 0011](0011-train-dqn-in-the-live-training-app-view.md), whose window fits the board at the Settings Tile Size

Live Training drew the board at no more than its Settings Tile Size and gave the network graph whatever width was left. The split between graph and board changed with the window: a wide window gave the graph a large share beside a small board, and a narrow one squeezed the graph to its minimum width. Live Training now splits the space under its HUD in half, the graph on the left and the board on the right, and draws the board at the largest whole tile size that fits its half, even when that is larger than the Settings Tile Size.

## Considered Options

- Keep the old split: the board at its Tile Size, the graph gets the rest
- Split in half and keep the board at its Tile Size, centred in its half
- Split in half and scale the board up to fill its half

Scaling up was chosen because both halves then look balanced at every window size. Keeping the Tile Size would leave a wide empty border around the board in large windows, which is the imbalance this change removes.

## Consequences

- Only Live Training draws the board larger than the Settings Tile Size. Every other App View keeps ADR 0002's rule, so BoardRenderer is unchanged and Live Training passes it the tile size that fills the board's half.
- In Live Training the Tile Size only sets the preferred window size: each half fits the board at that Tile Size, and the window is twice the wider of the graph and the board.
- The minimum window is twice the wider of the graph's minimum width and the board at a readable tile size, so neither half can be too small for its contents. Boards up to 30 columns fit beside the graph, so for them the graph sets the minimum width.
