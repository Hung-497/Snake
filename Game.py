from types import SimpleNamespace

from BotFactory import create_bot_mode
from RecordManager import RecordManager
from ReplayManager import ReplayManager
from tkinter import TclError
import time
from GameTypes import Direction

class Game:
    """
    Coordinates the main Snake game loop.

    Game owns the current score, win/loss state, selected bot mode, and update
    loop. It asks the active bot for a direction, moves the snake, checks food
    and collisions, then redraws the screen.
    """

    def __init__(
        self,
        window,
        snake=None,
        food=None,
        movement=None,
        bot_mode=None,
        speed_delay=1,
        engine=None,
    ):
        self.window = window
        self.engine = engine

        if (self.engine is None):
            self.snake = snake
            self.food = food
            self.movement = movement
        else:
            self.snake = SimpleNamespace(x=0, y=0, body=[])
            self.food = SimpleNamespace(x=0, y=0)
            self.movement = SimpleNamespace(velocity_x=0, velocity_y=0)

        self.speed_delay = speed_delay

        self.record_manager = RecordManager()
        self.replay_manager = ReplayManager()

        self.bot_mode = bot_mode
        self.bot = create_bot_mode(bot_mode, self.engine)

        self.score = 0 if self.engine is None else self.engine.score
        self.game_over = False if self.engine is None else self.engine.game_over
        self.game_won = False if self.engine is None else self.engine.game_won

        if (self.engine is not None):
            self._sync_engine_views()

        self.recent_scores = []
        self.games_played = 0
        self.best_score = 0

        self.total_moves = 0
        self.total_moves_history = []

        self.session_start_time = time.perf_counter()
        self.game_start_time = time.perf_counter()

        self.game_closed = False
        self.update_after_id = None
        self.reset_after_id = None

        self.return_to_menu = False
    
    def start_replay_recording(self):
        if (getattr(self, "engine", None) is not None):
            self.replay_manager.start_recording(
                self.bot_mode,
                self.engine.board_width,
                self.engine.board_height,
                self.engine.tile_size,
                self.speed_delay,
                engine=self.engine,
            )
            return

        self.replay_manager.start_recording(
            self.bot_mode,
            self.window.width,
            self.window.height,
            self.window.tile_size,
            self.speed_delay,
            self.snake,
            self.food
        )
    
    def draw(self):
        if (getattr(self, "engine", None) is not None):
            self._draw_engine_state()
            return

        self.window.clear_canvas()
        self.window.update_score_label(self.score, self.games_played, self.best_score)
        self.food.draw_food()
        self.snake.draw_snake()
        self.snake.draw_snake_body()

    def _draw_engine_state(self):
        state = self.engine.state
        canvas = self.window.canvas

        self.window.clear_canvas()
        self.window.update_score_label(self.score, self.games_played, self.best_score)

        if (state.food_position is not None):
            food_x, food_y = self._position_to_pixels(state.food_position)
            canvas.create_oval(
                food_x,
                food_y,
                food_x + state.tile_size,
                food_y + state.tile_size,
                fill="red",
                outline="",
                tag="food",
            )

        snake_x, snake_y = self._position_to_pixels(state.snake_position)
        canvas.create_rectangle(
            snake_x,
            snake_y,
            snake_x + state.tile_size,
            snake_y + state.tile_size,
            fill="yellow",
            outline="black",
            tag="snake",
        )

        for body_x, body_y in state.snake_body:
            body_x *= state.tile_size
            body_y *= state.tile_size
            canvas.create_rectangle(
                body_x,
                body_y,
                body_x + state.tile_size,
                body_y + state.tile_size,
                fill="green",
                outline="black",
                tag="snake",
            )

    def _position_to_pixels(self, position):
        x, y = position
        return x * self.engine.tile_size, y * self.engine.tile_size

    def _sync_engine_views(self):
        state = self.engine.state
        self.snake.x, self.snake.y = state.snake_position
        self.snake.body = list(state.snake_body)

        if (state.food_position is not None):
            self.food.x, self.food.y = state.food_position

        velocity_by_direction = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0),
        }
        self.movement.velocity_x, self.movement.velocity_y = velocity_by_direction[
            state.direction
        ]

    def _update_engine(self):
        if (self.game_closed):
            return

        direction = None

        self._sync_engine_views()

        if (self.bot is not None):
            direction = self.bot.choose_action(self.engine.state)

        if (direction is not None):
            self.engine.change_direction(direction)
            self.replay_manager.record_move(direction)

        score_before = self.engine.score
        # preview and step agree, so this describes the move step commits
        transition = self.engine.preview()
        self.engine.step()
        self._sync_engine_views()

        self.score = self.engine.score
        self.game_over = self.engine.game_over
        self.game_won = self.engine.game_won
        self.total_moves += 1

        if (self.bot is not None):
            self.bot.observe(transition)

        if (self.engine.score > score_before and self.engine.food_position is not None):
            self.replay_manager.record_food(self.engine.food_position)

        self.draw()

        if (self.game_over):
            self._finish_engine_game()
            return

        self.update_after_id = self.window.window.after(self.speed_delay, self.update)

    def _bot_epsilon(self):
        # Only a learning Bot Mode has one; the summary line stays the same.
        return getattr(self.bot, "epsilon", 0.0)

    def _finish_engine_game(self):
        self.games_played += 1
        self.recent_scores.append(self.score)

        if (self.score > self.best_score):
            self.best_score = self.score

        if (len(self.recent_scores) > 100):
            self.recent_scores.pop(0)

        average_score = sum(self.recent_scores) / len(self.recent_scores)

        self.total_moves_history.append(self.total_moves)
        if (len(self.total_moves_history) > 10):
            self.total_moves_history.pop(0)

        average_total_moves = sum(self.total_moves_history) / len(self.total_moves_history)
        game_time = time.perf_counter() - self.game_start_time
        session_time = time.perf_counter() - self.session_start_time

        self.replay_manager.save_replay(self.bot_mode, self.score, self.game_won)
        self.record_manager.save_game_result(
            self.bot_mode,
            self.games_played,
            self.score,
            self.best_score,
            average_score,
            self.total_moves,
            game_time,
            session_time,
            self.engine.board_width,
            self.engine.board_height,
            self.engine.tile_size,
            self.speed_delay,
        )

        print(
            f"Game: {self.games_played}, "
            f"Score: {self.score}, "
            f"Best: {self.best_score}, "
            f"Avg: {average_score:.1f}, "
            f"Total Moves: {self.total_moves}, "
            f"Avg total move: {average_total_moves:.1f}, "
            f"Epsilon: {self._bot_epsilon():.3f}, "
            f"Game Time: {game_time:.1f}s, "
            f"Session Time: {session_time:.1f}s"
        )

        if (self.bot is not None):
            self.bot.on_game_end(self.engine.state)

        if (self.game_won):
            self.window.draw_game_won(self.score)
        else:
            self.window.draw_game_over(self.score)

        self.reset_after_id = self.window.window.after(10, self.start_next_game)
    
    def update(self):
        if (getattr(self, "engine", None) is not None):
            self._update_engine()
            return

        if (self.game_closed):
            return

        direction = None

        if (direction is not None):
            self.movement.change_direction(direction)
            self.replay_manager.record_move(direction)

        ate_food, self.game_over = self.movement.move_snake(
            self.snake, 
            self.window.tile_size, 
            self.food, 
            self.window.width, 
            self.window.height, 
            self.game_over
        )

        self.total_moves += 1

        if (ate_food):
            self.score += 1

            occupied_tiles = len(self.snake.body) + 1
            total_tiles = self.window.width * self.window.height

            if (occupied_tiles == total_tiles):
                self.game_over = True
                self.game_won = True
            else:
                self.food.spawn_food()
                self.replay_manager.record_food(self.food)

        self.draw()

        if (self.game_over):
            self.games_played += 1
            self.recent_scores.append(self.score)

            if (self.score > self.best_score):
                self.best_score = self.score

            if (len(self.recent_scores) > 100):
                self.recent_scores.pop(0)

            average_score = sum(self.recent_scores) / len(self.recent_scores)

            self.total_moves_history.append(self.total_moves)
            if (len(self.total_moves_history) > 10):
                self.total_moves_history.pop(0)

            average_total_moves = sum(self.total_moves_history) / len(self.total_moves_history)

            game_time = time.perf_counter() - self.game_start_time
            session_time = time.perf_counter() - self.session_start_time

            self.replay_manager.save_replay(
                self.bot_mode,
                self.score,
                self.game_won
            )

            self.record_manager.save_game_result(
                self.bot_mode,
                self.games_played,
                self.score,
                self.best_score,
                average_score,
                self.total_moves,
                game_time,
                session_time,
                self.window.width,
                self.window.height,
                self.window.tile_size,
                self.speed_delay
            )

            print(
                f"Game: {self.games_played}, "
                f"Score: {self.score}, "
                f"Best: {self.best_score}, "
                f"Avg: {average_score:.1f}, "
                f"Total Moves: {self.total_moves}, "
                f"Avg total move: {average_total_moves:.1f}, "
                f"Epsilon: {self._bot_epsilon():.3f}, "
                f"Game Time: {game_time:.1f}s, "
                f"Session Time: {session_time:.1f}s"
            )

            if (self.game_won):
                self.window.draw_game_won(self.score)
            elif (self.game_over):
                self.window.draw_game_over(self.score)

            # reset game
            self.reset_after_id = self.window.window.after(10, self.start_next_game)
            return
        
        self.update_after_id = self.window.window.after(self.speed_delay, self.update)
    
    def run(self):
        self.window.window.protocol("WM_DELETE_WINDOW", self.close_game)
        self.window.draw_score_label()
        self.window.create_canvas()
        self.window.draw_back_button(self.back_to_menu)
        self.window.center_window()
        self.start_replay_recording()

        self.draw()
        self.update()
        self.window.start()

    def close_game(self):
        self.game_closed = True

        if (self.update_after_id is not None):
            try:
                self.window.window.after_cancel(self.update_after_id)
            except TclError:
                pass

        if (self.reset_after_id is not None):
            try:
                self.window.window.after_cancel(self.reset_after_id)
            except TclError:
                pass

        self.window.window.quit()
        self.window.window.destroy()

    def reset_game_state(self):
        if (getattr(self, "engine", None) is not None):
            self.engine.reset()
            self._sync_engine_views()
            self.score = self.engine.score
            self.game_over = self.engine.game_over
            self.game_won = self.engine.game_won
            self.total_moves = 0
            self.game_start_time = time.perf_counter()
            self.start_replay_recording()
            return

        self.score = 0
        self.game_over = False
        self.game_won = False

        self.total_moves = 0
        self.game_start_time = time.perf_counter()


        self.snake.reset()
        self.food.spawn_food()
        self.movement.reset()
        self.start_replay_recording()

    def start_next_game(self):
        if (self.game_closed):
            return

        self.reset_game_state()
        self.draw()
        self.update()

    def back_to_menu(self):
        self.return_to_menu = True
        self.close_game()
