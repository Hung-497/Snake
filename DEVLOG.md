# Development Diary

## Aim of this project

Build a Snake game and add AI bots to play it.
Development Order:

- Step 1: Create a snake game using Python
- Step 2: Add simple rule-based bot
- Step 3: Start learning and using AI for snake game

## 2026-05-27

### What I worked on

- Started planning a snake game using tkinter
- Learn what data the game needs: snake position, body, food, direction, score, game state
- Learn how to use tkinter

### Problems I found

- Actually I followed video from one guy in youtube hence I didn't meet any challenges yet.

### What I learned

- How to use tkinter, create snake game with logical game play.

## 2026-05-28 (1)

### What I worked on

- Separated code into each class: "Food", "Snake", "Movement", "Window", "Game".
- Added random positions for food and snake.
- Added keyboard direction logic.
- Added snake body logic after eat food.
- Added reset logic.
- Updated wall collision, body collision, and game over screen.
- Started improve code organization using OOP.

### Problems I found

- Snake location changed too often because random position was inside the repeated draw/update logic.
- Body update was difficult because each body tile needs to follow the previous tile.
- Food could spawn in bad places.

### What I learned

- The snake should store its body as a list of `(x, y)` positions.
- The game should calculate the next position before moving.
- Collision should be checked before updating the snake position.

## 2026-05-28 (2)

### What I worked on

- Added a simple rule-based bot.
- Made the bot choose directions based on food position.
- Added methods hence the bot can avoid walls and body.
- Added reward for bot when is near or eat the food.
- Added food path checking.
- Improve the bot to achieve the most score as possible.

### Problems I found

- The bot sometimes hit the wall when food was on the same line.
- The bot sometimes got stuck in the loop.
- The bot sometimes trapped itself inside its own body.
- Adding many small rules made the code harder to organize, improve, and understand.

### What I learned

- A simple bot can work by scoring possible moves
- Chasing food directly is not enough, otherwise, the bot needs to check safety, open space, and whether the food is reachable.
- BFS can search reachable positions on the board.

## 2026-05-29

### What I worked on

- Improved the rule-based bot.
- Added logic to check safe moves.
- Added path checking hence the bot can find a short path to food.
- Added tail-following logic hence the bot can avoid some traps.
- Added escape checking after a possible food path.
- Cleaned up some confusing return values.

### Problems I found

- The bot could still trap itself even when the next move looked safe.
- Some helper methods returned values that were not needed.
- I learned that a move can be safe immediately but dangerous later.

### What I learned

- A snake bot should not only chase food, it should check if it can have a chance to escape after eating.
- Simulating future movement helps the bot make better decisions.

## 2026-05-30

### What I worked on

- Start writing a development diary.
- Added and fixed comments.
- Start thinking about separating the code into multiple files.

### Problems I found

- Code was too long that it was quite hard to check and debug.
- Some functions were in the wrong class I suppose.
- Some comments did not match what the code actually did.

### What I learned

- Comments should describe the current code accurately.
- A devlog is useful for recording the learning process.

## 2026-06-01

### What I worked on

- Rewrote the project into separate files: Snake, Movement, Food, Window, Game, main
- Added a score label hence I can see the score clearer than the previous writing text in the left top corner method.
- Added reset logic using the Space key that I had forgotten to add after adding the bot.
- Optimized and debugged the rule methods for bot to try to beat the game.

### Problems I found

- Food spawning needed to avoid the snake head and body.
- Movement needed to check the next position before moving.
- BFS was difficult to understand at first.
- Some list syntax like `[-1]` and `[:-1]` needed review.

### What I learned

- Splitting files makes the code easier to organize.
- BFS can find a safe path through the board.
- Tail-following is a useful safety rule for Snake bots.

## 2026-06-02

### What I worked on

- Checked the full project again.
- Ran syntax checks on the separated files.
- Tested the bot logic with simulations.

### Problems I found

- The bot does not beat the full Snake game consistently.
- It can survive for a while, but it still eventually loses.
- A simple rule-based bot has limits.

### What I learned

- A rule-based bot can be good without being unbeatable.
- To beat Snake consistently, a stronger strategy would be needed later.

## 2026-06-03

### What I worked on

- Split the bot logic into a separate `Bot.py` file.
- Made the project files more readable and easier to debug.

### Problems I found

- No major bug

### What I learned

- Separating the bot into its own file makes the project easier to organize.

## 2026-06-04 to 2026-06-06

### What I worked on

- Added a simple tabular Q-learning bot.
- Created a Q-table to store state-action values.
- Used actions: Straight, Turn_Left, Turn_Right.
- Added epsilon so the bot can explore random moves while learning.
- Added epsilon decay after each game.
- Made the game reset automatically after game over.
- Added games played, best score, and average score tracking.
- Improved the state from absolute food direction to relative food direction.
- Added a safe-action filter so the bot only chooses safe moves when possible.

### Problems I found

- At first, the bot looked very silly because epsilon was high, so it made many random moves.
- The first Q-learning state was too weak or confusing.
- A smaller state with only danger straight/left/right became worse at first.
- Food direction needed to match the bot actions, so I changed it to relative food direction.
- The bot still trapped itself inside its body.
- The safe-action method had a bug because it looped through an empty list.
- Even after improving, tabular Q-learning still does not understand long-term body traps.

### Experiment results

- Early Q-learning result: low scores and unstable behavior.
- Old state reached around best score 49.
- Bad state experiment dropped to around best score 8.
- Relative food direction improved the bot again.
- Setting epsilon to 0 after training showed that random exploration was hurting good runs.
- After fixing the safe-action filter, average score improved clearly.
- Best score reached around 76.
- Average score reached around 36-37.

### What I learned

- Epsilon means the bot sometimes chooses random actions.
- Too much randomness can kill the snake even if the bot learned something useful.
- The state must match the action system.
- Safe immediate moves are not enough to beat Snake.
- Tabular Q-learning can learn short-term food seeking and danger avoidance.
- It still struggles with long-term planning.

## 2026-06-08

### What I worked on

- Started building a planning AI using a Hamiltonian cycle.
- Learned that a Hamiltonian cycle visits every tile exactly once and connects back to the start.
- Changed the board to `24 x 25` because a Hamiltonian cycle is easier when at least one side is even.
- Created `HamiltonianBot.py`.
- Added logic to convert pixel positions to grid positions.
- Created a Hamiltonian cycle path for the board.
- Added a method to find the next tile in the cycle.
- Added a method to convert the next tile into a movement direction.
- Added a cycle validator to check whether the cycle is valid.
- Connected the Hamiltonian bot to the main game.
- Added a game won scenario when the snake fills the whole board.

### Problems I found

- My first board was `25 x 25`, but that is not good for a clean Hamiltonian cycle because both sides are odd.
- I needed to understand the difference between pixel positions, grid positions, and tile numbers.
- The bot looked slow because it follows the full cycle instead of rushing directly to food.
- When the snake filled the board, the game froze because food spawning tried to find an empty tile forever.
- I needed to add a win condition before spawning new food.

### Experiment results

- The Hamiltonian cycle validator returned true.
- The snake followed the cycle without hitting the wall or its own body.
- The score kept increasing slowly but safely.
- The snake eventually filled the board. Yassss
- The final score reached `599` on a `24 x 25` board.
- Since the board has `600` tiles and the snake head counts as one tile, `599` is the maximum score.

### What I learned

- A Hamiltonian cycle is a safe route that can make Snake beatable.
- Planning AI can be more reliable than Q-learning for this problem.
- Q-learning learned short-term behavior, but Hamiltonian planning solves the long-term body-trap problem.
- A safe solution is not always the fastest solution.

## 2026-06-09 to 2026-06-11

### What I worked on

- Studied Hamiltonian cycle and how it can be used to beat Snake.
- Added a bot selection menu so I can choose rule-based, Q-learning, or Hamiltonian bot.
- Added shortcut logic to make the Hamiltonian bot faster.
- Added tail reachability checking.
- Added flood fill to count reachable space before taking shortcuts.
- Compared total moves between different matches.

### Problems I found

- Calling `get_best_shortcut_direction()` directly made the Hamiltonian bot act badly because it can return `None`.
- I fixed it by using `get_next_direction()`, which falls back to the normal Hamiltonian cycle.
- Some safety checks were placed after choosing `best_direction`, so bad moves could still be selected.
- The max shortcut distance rule made the bot slower.

### Experiment results

- The pure Hamiltonian bot took around `85,000` moves.
- After adding shortcut safety, tail reachability, and flood fill, the bot averaged around `47,000` moves.
- In one test, 6 winning games averaged around `47,458` moves.

### What I learned

- Shortcuts must be checked carefully before using them.
- Tail reachability helps check whether the snake still has an escape path.
- Flood fill can count reachable space and reject risky shortcuts.
- The order of safety checks matters.

## 2026-06-24

### Code Review Refactor and Bot Performance Logging

#### What I worked on

- Refactored the project after receiving code review feedback.
- Added documentation/docstrings to explain the purpose of each main class.
- Added a shared BaseBot parent class.
- Updated RuleBasedBot, QLearningBot, and HamiltonianBot to inherit from BaseBot.
- Moved shared helper logic into BaseBot.
- Renamed internal helper methods with `_` to show they are meant to be used inside the class.
- Improved the bot interface so Game can ask each bot for `get_next_direction()`.
- Kept Q-learning learning logic inside QLearningBot instead of making Game handle its internal state.
- Added game time and session time to the terminal output.
- Prepared the project to compare bot performance with score, moves, and time.

#### Problems I found

- QLearningBot needed to store its own current state and current action.
- Game was still reaching into QLearningBot internals at first.
- Some methods still passed game as a parameter even though the bot already had self.game.
- HamiltonianBot uses grid tiles, so not every BaseBot pixel-based helper fits it.

#### What I learned

- Inheritance is useful when classes share real behavior.
- Public methods are the interface other classes should call.
- Game should not know too much about how each bot works internally.
- Not every parent method should be used by every child class.
- HamiltonianBot works with grid tiles, while other helpers often work with pixel positions.
- A cleaner interface makes code easier to read and maintain.
- Time, score, and move count together make bot comparison more meaningful.

## 2026-06-26

### What I worked on

- Created a menu screen using `customtkinter`.
- Added main menu options: Play, Settings, and Logs.
- Added a Play screen where I can choose between 3 bots.
- Connected `menu_test.py` with `Game.py` so the game starts after choosing a bot.
- Added simple screen switching by clearing the current frame before drawing the next screen.
- Added close-window handling so closing the menu does not start a game accidentally.

### Problems I found

- `customtkinter` printed callback warnings when the window was closed, but it did not affect gameplay.
- I needed to understand that button commands should use `lambda` when passing a bot mode.
- The old menu widgets stayed behind at first, so I added `clear_screen()` to remove the current frame.

### What I learned

- Learned how to build a basic UI with `customtkinter`.
- Learned how to connect a menu choice to the main game.
- Learned that `quit()`, `withdraw()`, and `destroy()` have different jobs when closing a Tkinter window.
- Learned how to switch screens by destroying the current frame and drawing a new one.

## 2026-06-29

### What I worked on

- Added a Back button to the Play screen.
- Checked the `Created by Nhism` label placement.
- Moved the credit label so it is positioned relative to the whole menu window instead of the menu frame.
- Found that the game screen white space came from the score label being wider than the canvas.
- Planned to shorten or resize the score label so it does not stretch the game window.

### Problems I found

- `place(relx=..., rely=...)` depends on the parent widget, so placing a label inside `current_frame` positions it relative to that frame.
- The score label font was too large, which made the game window wider than the canvas.
- `customtkinter` can still print shutdown warnings when its internal callbacks run after the window is closed.

### What I learned

- A label can change the size of the whole Tkinter window if its text is too wide.
- Some UI warnings are from library cleanup behavior, not from the Snake game logic.

## 2026-06-30

### What I worked on

- Improved the CustomTkinter menu UI.
- Added styled Settings controls for game speed, board size, and tile size.
- Connected selected board size and tile size to the game window.
- Connected selected game speed to the game loop.
- Added validation so Hamiltonian bot cannot start on a board where both sides are odd.
- Added a Tkinter `bgerror` handler to hide harmless CustomTkinter shutdown warnings.
- Improved game window closing by canceling pending `after()` callbacks and stopping the main loop.
- Renamed `MenuTestApp` class to `MenuApp`.
- Updated `README.md` so it points to `Menu.py` instead of the older terminal entry point.
- Removed the visible border around the snake head, snake body, and food.
- Updated the canvas drawing code by setting the shape outline to empty.

### Problems I found

- The speed option existed in the menu but was not used by `Game.py` yet.
- Closing the game window could leave scheduled callbacks running.
- The menu and game used separate Tk windows, so cleanup needed to be handled carefully.
- `moves_for_current_food` was leftover state and was no longer used.
- The README still described the old terminal-based startup flow.
- Tkinter canvas shapes can show a default outline even when the fill color is set.
- The border color was not from the CustomTkinter menu theme.

### What I learned

- A settings UI should pass real values into the game, not only display choices.
- `after()` callbacks should be canceled when closing a running Tkinter game.
- `quit()` stops the event loop, while `destroy()` removes the window.
- Keeping README instructions updated is part of keeping a project usable.
- Small cleanup matters because unused variables and outdated docs can confuse future readers.

## 2026-07-01

### What I worked on

- Added a text-style `Back to Menu` control on the game screen.
- Made the game return to the CustomTkinter menu without restarting the program.
- Updated the menu loop so a new menu opens again after returning from a game.
- Created `RecordManager.py` to save finished game results.
- Connected `Game.py` to `RecordManager` so each completed game writes a CSV row.
- Saved bot mode, games played, score, best score, average score, total moves, game time, and session time.
- Moved generated record data into a `records/` folder.

### Problems I found

- A normal Tkinter button looked too large and distracting on the game screen.
- `pack()` is not good for bottom-right placement because it stacks widgets instead of using relative coordinates.

### What I learned

- `place(relx=..., rely=..., anchor=...)` is useful for small fixed-position UI labels.
- Game result records are like a scoreboard, while replay files are like a recording and Q-tables are like the bot brain.
- A small manager class is useful when one file should handle saving data.

## 2026-07-02

### What I worked on

- Added CSV reading to `RecordManager.py` using `csv.DictReader`.
- Connected the Logs screen in `Menu.py` to read saved game records.
- Added a scrollable records frame so the Logs screen can show many saved games.
- Limited the visible records to the latest 50 to keep the UI responsive.
- Added log filter buttons for All, Rule, Q-learning, and Hamiltonian records.
- Added summary stat cards for games played, best score, average score, and best moves.
- Rebalanced the Logs screen layout so the title, records, Back button, and credit text fit better.
- Added default stat values for empty filters so the Logs screen does not crash when one bot has no records yet.

### Problems I found

- Showing more than 1000 records as individual UI labels made the Logs screen slow.
- Mouse wheel scrolling in `CTkScrollableFrame` did not work reliably, so I kept the scrollbar as the stable option.
- The Logs screen became too tall after adding stats and started hiding the credit text.
- The Hamiltonian filter crashed when there were no Hamiltonian records because the stat variables were never created.

### What I learned

- `csv.DictReader` reads each CSV row as a dictionary, which makes record fields easier to access.
- UI performance can slow down when the program creates too many widgets at once.
- Filtering records before calculating stats keeps the summary matched to the selected bot.
- Empty lists need special handling before using `max()`, `min()`, or average calculations.
- Layout balance depends on both `place()` positioning and the internal `pack()` spacing.

## 2026-07-03

### What I worked on

- Added board width, board height, tile size, and speed delay to saved game records.
- Updated `Game.py` so each saved result includes the settings used for that session.
- Recreated the CSV record format so new sessions store the extra settings data.
- Improved the Logs screen so each record is shown as a two-line card instead of one long line.
- Organized `open_logs()` by moving filtering, stats, record section, and record card logic into smaller helper functions.
- Kept the Logs screen limited to the latest 50 records so it stays responsive.

### Problems I found

- A single long record label became too wide, so the right side of the text was hidden.
- A horizontal scrollbar would work, but it would make records harder to scan.
- `open_logs()` was doing too many jobs in one function, which made it harder to read and update.
- Old CSV rows can be missing newer columns, so record display needs fallback values.

### What I learned

- Logs are easier to read when the most important result is on the first line and settings details are on the second line.
- Saving board and speed settings makes bot comparisons more honest because results depend on game configuration.
- Helper functions make UI code easier to understand because each function has one clear job.

## 2026-07-04 to 2026-07-06

### What I worked on

- Improved Q-learning persistence so the bot can continue learning from a saved Q-table across sessions.
- Saved Q-learning data into a `learning_data/` folder.
- Compared Q-learning training results using game records, best score, average score, and consistency.
- Decided to keep tabular Q-learning as a learning prototype instead of trying to force it to beat Snake perfectly.
- Designed the replay system separately from game records and Q-learning data.
- Created `ReplayManager.py` to save and load replay JSON files.
- Saved compact replay data using starting positions, food positions, move numbers, settings, and final score.
- Added replay files for the best rule-based, Q-learning, and Hamiltonian runs.
- Added a Replay button to the CustomTkinter menu.
- Created `ReplayPlayer.py` to play saved replay moves back visually.
- Connected the replay screen so I can choose Rule-based, Q-learning, or Hamiltonian replay from the menu.
- Updated `README.md` to describe the current menu, settings, logs, replay system, and project structure.
- Cleaned small unused replay test code before preparing the project for GitHub.

### Problems I found

- Q-learning can save learned values, but tabular Q-learning still has limits because it does not fully understand long-term body traps.
- Replay data should not save every full snake body frame because that would create very large files.
- I needed to keep three types of data separate: records for summaries, replay files for playback, and Q-tables for learning.
- Replay needed to convert move numbers back into directions before drawing the snake.
- The README became outdated because the project no longer uses the old terminal entry point.

### Experiment results

- Rule-based replay was saved successfully with score, moves, food positions, and settings.
- Q-learning replay was saved successfully after a best run.
- Hamiltonian replay was saved successfully and shows a completed winning game.
- Replay files are much smaller than saving every frame because they store only moves and food positions.

### What I learned

- JSON is useful for replay data because it can store lists, settings, and metadata clearly.
- Saving directions as numbers keeps replay files smaller and easier to process.
- Separating `ReplayManager` and `ReplayPlayer` keeps saving logic away from playback logic.
- A complete project needs not only gameplay, but also records, replay, documentation, and cleanup.
