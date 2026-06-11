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
- Updated wall collision, body  collision, and game over screen.
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
