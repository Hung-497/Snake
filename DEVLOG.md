# Development Diary

## Aim of this project

Play snake game using AI
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
