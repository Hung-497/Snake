# Arcade smoke checklist

Manual checks for the Arcade app, to run once on each supported system. The
automated tests cover the App View flow and the game and replay sessions, but
they never open a window, so everything below has to be seen by a person.

Run the app with:

```bash
uv sync
uv run python SnakeApp.py
```

## Checks

| # | Check | What to expect |
|---|---|---|
| 1 | Window creation | After `uv sync`, `uv run python SnakeApp.py` starts without errors and one window opens, titled "Snake Game", 900 x 960 pixels. |
| 2 | Centering | The window appears in the middle of the screen. |
| 3 | Resizing | Dragging an edge or corner resizes the window, but not below its minimum size. The board scales to fit, and every screen stays usable. |
| 4 | Menu controls | Play, Settings, Replay and Records all respond to a click and to hover. |
| 5 | Settings | Each dropdown opens, a choice sticks, and Back returns to the Menu. |
| 6 | Retained settings | Reopening Settings still shows the choices made a moment ago. |
| 7 | Game rendering | The board, the yellow head, the green body, the red food, and the score line all draw. |
| 8 | Repeated games | With a Bot Mode, a finished game briefly shows its result, then the next game starts by itself. |
| 9 | Unsupported board | With an odd-by-odd board, Hamiltonian stays on Play and explains why. |
| 10 | Records | Summary statistics appear, each filter changes them, and Newer/Older page through the list. |
| 11 | Replay | A saved replay plays and ends on "Replay Finished". A Player with no saved replay shows a message instead. |
| 12 | Navigation | Back returns to the Menu from every screen, in the same window. |
| 13 | Clean shutdown | Closing the window ends the process with no error and no leftover window. |
| 14 | Play Yourself | Play shows "Play Yourself" above the Bot Modes. It opens a game on every board size, labelled "Human". |
| 15 | Human Play start and steering | The snake stays still with "Press an arrow key to start" until an arrow or WASD key is pressed. Arrow keys and WASD both steer, a quick double turn (like Up then Left) makes both turns, and a key that would reverse the snake is ignored. The speed is playable on Slow, Normal and Fast. |
| 16 | Human Play result and leaving | A finished game keeps its result and score on screen until Space or Enter starts a new game, which waits for an arrow key again. Esc returns to the Menu at any time, and leaving mid-game adds no record. |
| 17 | Human Play pause | P or Space pauses a game in play and shows "Paused"; pressing either again resumes with no jump. Arrow keys do nothing while paused. Switching to another app pauses the game, and it stays paused on return. |
| 18 | Human records and replay | Records has a "Human" filter that shows only Human Play games, and all Player filters fit at the smallest window width. Replay has a "Human" button that plays the best Human Play game at the same Replay Speeds as every other Player, or shows a message if none is saved. |
| 19 | Replay pause | On a Bot Mode replay and on the Human replay, P, Space, and the Pause button each pause playback and show "Paused"; the button then reads "Resume", and pressing any of them again resumes with no jump. The Pause button sits in its own row under the score line and covers neither the score nor the board at the smallest window size. Switching to another app does not pause a replay, and Pause does nothing once "Replay Finished" shows. |
| 20 | Replay restart | On a Bot Mode replay and on the Human replay, R and the Restart button each send the snake back to its start with the first food and a score of 0, and playback starts at once. This works mid-replay, while paused (the button goes back to "Pause"), and after "Replay Finished", which disappears until the replay ends again. Space only pauses and never restarts. |
| 21 | Replay Speed | On a Bot Mode replay and on the Human replay, the speed button reads "Speed: Normal" when a replay opens. S and the button each cycle it Slow, Normal, Fast, then Slow again: Slow is easy to follow move by move, Fast is clearly quicker than Normal, and no change causes a sudden jump. The speed can change while paused and takes effect on resume, a restart keeps the chosen speed, and opening a replay again starts back on Normal. |
| 22 | Replay progress and layout | On a Bot Mode replay and on the Human replay, "Move X / N" and a bar sit in a thin row under the playback buttons. Both count up during playback, stay still while paused, go back to "Move 0 / N" on restart, and read "Move N / N" with a full bar at "Replay Finished". The bar does not shift sideways as the move count grows. On the Large 30 x 30 board at the smallest window size and again after resizing larger, the score, Back to Menu, Pause, Restart, Speed and the progress row all stay readable, and none of them covers the board or the result labels. A replay of a game that ended against a wall or the snake's own body finishes with the snake where it died, never outside the board or on top of itself. Rows 19 to 21 still pass. |
| 23 | Records upgrade | With a records file saved before Game Outcomes, finishing any game creates `records/game_records.csv.bak` beside it. Records still lists the old games as "Outcome unknown", and the new game shows Won or Died. |
| 24 | Game Conditions filters | Records opens with Board and Speed set to the current Settings choices. Changing either dropdown updates the summary and the list; Human Play and bot games on the same speed name appear together, and a filter with no games shows "No games match these filters". Both dropdowns fit at the smallest window size. |
| 25 | Compare tab | Records opens on Compare. It lists one row per Player with games under the chosen Board and Speed, each with its colour swatch, and the columns line up. Win rate shows "-" when no outcome is known, and recent form shows an up arrow, a down arrow, or "=". The Games tab keeps the Player filters and the paged list, and the chosen tab and filters stay while moving between tabs. Both tabs fit at the smallest window size. |
| 26 | Compare bar chart | Under the Compare table, one bar per Player shows its average score in the Player's colour, with a white line at its best score and a label under each bar. It changes with the Board and Speed dropdowns, disappears with the table when no games match, and fits at the smallest window size. With many Players at the smallest size, the chart gives way to "Make the window taller to see the bar chart" and nothing runs off the window. |
| 27 | Trends tab | Trends shows one coloured line per Player over its last 100 games, each Player's latest game at the right edge, with a legend of Player colours. A Player with one game shows a single dot. The Board and Speed dropdowns apply, no games shows the empty message, and the chart fits at the smallest window size. With more than four Players, the legend wraps onto further rows (four per row), the chart gets shorter to make room, and nothing runs off the window's sides or bottom. |
| 28 | Search-Based Play and Replay | Play and Replay each offer Search-Based. A watched Search-Based game finishes and saves a record and best replay; Replay plays it to "Replay Finished" or shows the missing-replay message before one exists. Check both screens at the 700 x 700 minimum and after enlarging the window. |
| 29 | Search-Based Records | Games has a Search-Based filter that shows only its games and outcome. Compare includes its row and pink colour swatch; Trends includes its pink line and legend entry. The Board and Speed filters still apply. All six Games filters and the Compare and Trends views fit at 700 x 700 and after resizing larger. |
| 30 | Q Learning v3 | Play and Replay each offer "Q Learning v3" beside "Q Learning". A watched Q Learning v3 game starts without a saved v3 table, creates `learning_data/q_table_space_state_v3.json`, and leaves the v2 table unchanged. Its records and best replay are its own: Games has a "Q-Learning v3" filter, and Compare and Trends show it in cyan, separate from Q Learning. All seven Games filters and the Play and Replay buttons fit at 700 x 700 and after resizing larger. |
| 31 | Live Training | The Menu has a Live Training button. With `uv sync --group dqn`, it opens the board size chosen in Settings, the snake moves every frame, and the line above the board shows Game, Score, Best, Avg and Epsilon; the game number counts up and Epsilon falls as games finish. Esc and Back to Menu both return to the Menu, and opening it again starts fresh. Without PyTorch (plain `uv sync`), the app still starts, and Live Training shows how to install it with `uv sync --group dqn` instead of a board. Check at 700 x 700 and after resizing larger. |
| 32 | Live Training modes | Live Training opens in Live mode at 1x, with a line under the stats naming the mode, speed, and keys. S cycles the speed 1x, 5x, 25x, 100x, then 1x again, and the snake visibly moves faster. B switches to Background: the board disappears, the network graph fills the window and can be zoomed like the Network focus layout, the stats keep counting up quickly, and B switches back to the board. P or Space pauses in either mode (the line starts with "Paused" and the stats stop) and pressing either again resumes. Esc still returns to the Menu, and the controls line fits at 700 x 700 and after resizing larger. |
| 33 | Live Training network graph | In Live mode the network sits left of the board: 12 labelled inputs (Danger, Food, Space, Tail for straight, left, right), two hidden columns of 64, and outputs Straight, Left, Right with their Q-values. Active neurons glow green, connections are blue (positive) or red (negative), and the graph changes as the bot learns. The output the bot took has a yellow ring, and "random move" appears under the outputs on exploration moves, more often while Epsilon is high. Background mode hides only the board and keeps the graph. In a window wider than the board needs, the graph takes the extra width, with no empty gap before the board. Opening Live Training from a 900 x 960 window grows it to fit the graph and the board at the Settings Tile Size, on the same screen; dragging it smaller stops at the Live Training minimum, where no label is cut off and the graph does not cover the board or the top lines. Back on the Menu, the window can shrink to 700 x 700 again. |
| 34 | Live Training save | Train a few games, then leave with Back to Menu: `learning_data/dqn_live_training.pt` appears. Opening Live Training again continues from the same game count, Best, Avg and Epsilon, with a fresh game on the board. Train more and close the window instead of leaving: reopening the app and Live Training still continues. Choose another board size in Settings and open Live Training: it explains that the save is for the other board and how to continue or start over, nothing trains, and the save is unchanged. |
| 35 | Network focus layout | In Live mode the title line reads "N network focus". N switches to the Network focus layout: the board disappears, the graph fills the window, and the title line shows the zoom level ("zoom 1.0x") with wheel zoom, drag pan, R reset and N board. Every output label, including "random move", fits inside the window. The mouse wheel zooms towards the point under the cursor, up to 8x, and back out to the whole graph; dragging moves a zoomed graph until its edge meets the window edge, and does nothing at 1x. R shows the whole graph again and the zoom level reads 1.0x. The stats keep counting while zoomed, a zoomed graph never covers the top lines, N returns to the board, and resizing the window keeps the zoomed graph in view. |

## Results

| System | Checked on | Result |
|---|---|---|
| macOS 26 (Apple Silicon), Python 3.14, Arcade 3.3.3 | 2026-09-19 | Passed, with checks 3 and 13 confirmed programmatically rather than by hand. |
| Windows | not yet checked | |
| Linux | not yet checked | |
