from ReplayManager import (
    GRID_COORDINATE_SYSTEM,
    NUMBER_TO_DIRECTION,
    PIXEL_COORDINATE_SYSTEM,
    ReplayCompatibilityError,
)
from GameTypes import Direction
from tkinter import TclError


class ReplayPlayer:
    """
    Plays a saved replay by rebuilding the snake from saved moves and food data.
    """

    def __init__(self, window, replay_data):
        self.window = window
        self.coordinate_system = replay_data.get("coordinate_system", "pixel")
        if self.coordinate_system not in {
            GRID_COORDINATE_SYSTEM,
            PIXEL_COORDINATE_SYSTEM,
        }:
            raise ReplayCompatibilityError(
                f"Unsupported replay coordinate system: {self.coordinate_system}"
            )
        self._uses_grid_coordinates = self.coordinate_system == "grid"

        self.snake_x = replay_data["start_snake"][0]
        self.snake_y = replay_data["start_snake"][1]
        self.snake_body = []

        self.foods = replay_data["foods"]
        self.food_index = 0
        if self.foods:
            self.food_x = self.foods[self.food_index][0]
            self.food_y = self.foods[self.food_index][1]
        else:
            self.food_x = None
            self.food_y = None

        self.moves = replay_data["moves"]
        self.move_index = 0
        self.score = 0
        self.final_score = replay_data["final_score"]
        self.replay_delay = 10

        self.replay_closed = False
        self.return_to_menu = False
        self.update_after_id = None

    def draw(self):
        self.window.clear_canvas()
        self.window.update_score_label(self.score, 0, self.final_score)
        self.draw_food()
        self.draw_snake()
        self.draw_snake_body()

    def draw_food(self):
        if self.food_x is None:
            return

        food_x, food_y = self._position_to_pixels(self.food_x, self.food_y)
        self.window.canvas.create_oval(
            food_x,
            food_y,
            food_x + self.window.tile_size,
            food_y + self.window.tile_size,
            fill="red",
            outline="",
            tag="food"
        )

    def draw_snake(self):
        snake_x, snake_y = self._position_to_pixels(self.snake_x, self.snake_y)
        self.window.canvas.create_rectangle(
            snake_x,
            snake_y,
            snake_x + self.window.tile_size,
            snake_y + self.window.tile_size,
            fill="yellow",
            outline="",
            tag="snake"
        )

    def draw_snake_body(self):
        for x, y in self.snake_body:
            x, y = self._position_to_pixels(x, y)
            self.window.canvas.create_rectangle(
                x,
                y,
                x + self.window.tile_size,
                y + self.window.tile_size,
                fill="green",
                outline="",
                tag="snake"
            )

    def update(self):
        if (self.replay_closed):
            return

        if (self.move_index >= len(self.moves)):
            self.draw_replay_finished()
            return

        move_number = self.moves[self.move_index]
        direction = NUMBER_TO_DIRECTION.get(move_number)

        if (direction is None):
            self.draw_replay_finished()
            return

        self.move_snake(direction)
        self.move_index += 1
        self.draw()

        self.update_after_id = self.window.window.after(
            self.replay_delay,
            self.update
        )

    def move_snake(self, direction):
        next_x = self.snake_x
        next_y = self.snake_y
        step_size = 1 if self._uses_grid_coordinates else self.window.tile_size

        if (direction == Direction.UP):
            next_y -= step_size
        elif (direction == Direction.DOWN):
            next_y += step_size
        elif (direction == Direction.LEFT):
            next_x -= step_size
        elif (direction == Direction.RIGHT):
            next_x += step_size

        ate_food = (
            self.food_x is not None
            and next_x == self.food_x
            and next_y == self.food_y
        )

        if (ate_food):
            self.snake_body = [(self.snake_x, self.snake_y)] + self.snake_body
            self.score += 1
            self.move_to_next_food()
        elif (len(self.snake_body) > 0):
            self.snake_body = [(self.snake_x, self.snake_y)] + self.snake_body[:-1]

        self.snake_x = next_x
        self.snake_y = next_y

    def _position_to_pixels(self, x, y):
        if self._uses_grid_coordinates:
            return x * self.window.tile_size, y * self.window.tile_size
        return x, y

    def move_to_next_food(self):
        if (self.food_index + 1 >= len(self.foods)):
            return

        self.food_index += 1
        self.food_x = self.foods[self.food_index][0]
        self.food_y = self.foods[self.food_index][1]

    def draw_replay_finished(self):
        self.window.canvas.create_text(
            self.window.WINDOW_WIDTH // 2,
            self.window.WINDOW_HEIGHT // 2,
            text=f"Replay Finished\nScore: {self.score}",
            fill="white",
            font=("Arial", 36, "bold"),
            tag="replay_finished"
        )

    def run(self):
        self.window.window.protocol("WM_DELETE_WINDOW", self.close_replay)
        self.window.draw_score_label()
        self.window.create_canvas()
        self.window.draw_back_button(self.back_to_menu)
        self.window.center_window()

        self.draw()
        self.update()
        self.window.start()

    def close_replay(self):
        self.replay_closed = True

        if (self.update_after_id is not None):
            try:
                self.window.window.after_cancel(self.update_after_id)
            except TclError:
                pass

        self.window.window.quit()
        self.window.window.destroy()

    def back_to_menu(self):
        self.return_to_menu = True
        self.close_replay()
