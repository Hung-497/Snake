# Arcade smoke checklist

Manual checks for the Arcade app, to run once on each supported system. The
automated tests cover the App View flow and the game and replay sessions, but
they never open a window, so everything below has to be seen by a person.

Run the app with:

```bash
python3 SnakeApp.py
```

## Checks

| # | Check | What to expect |
|---|---|---|
| 1 | Window creation | One window opens, titled "Snake Game", 900 x 960 pixels. |
| 2 | Centering | The window appears in the middle of the screen. |
| 3 | Not resizable | Dragging an edge or corner does not change the window size. |
| 4 | Menu controls | Play, Settings, Replay and Records all respond to a click and to hover. |
| 5 | Settings | Each dropdown opens, a choice sticks, and Back returns to the Menu. |
| 6 | Retained settings | Reopening Settings still shows the choices made a moment ago. |
| 7 | Game rendering | The board, the yellow head, the green body, the red food, and the score line all draw. |
| 8 | Repeated games | A finished game briefly shows its result, then the next game starts by itself. |
| 9 | Unsupported board | With an odd-by-odd board, Hamiltonian stays on Play and explains why. |
| 10 | Records | Summary statistics appear, each filter changes them, and Newer/Older page through the list. |
| 11 | Replay | A saved replay plays and ends on "Replay Finished". A bot with no saved replay shows a message instead. |
| 12 | Navigation | Back returns to the Menu from every screen, in the same window. |
| 13 | Clean shutdown | Closing the window ends the process with no error and no leftover window. |

## Results

| System | Checked on | Result |
|---|---|---|
| macOS 26 (Apple Silicon), Python 3.14, Arcade 3.3.3 | 2026-09-19 | Passed, with checks 3 and 13 confirmed programmatically rather than by hand. |
| Windows | not yet checked | |
| Linux | not yet checked | |
