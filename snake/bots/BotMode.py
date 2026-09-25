import random

from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import OPPOSITE_DIRECTION


class BotMode:
    """Common responsibilities shared by every Bot Mode.

    A Bot Mode decides from presentation-neutral Game Engine state and
    previewed transitions. It never reads the window, canvas, or the mutable
    snake, food, and movement objects.
    """

    DIRECTIONS = (
        Direction.UP,
        Direction.DOWN,
        Direction.LEFT,
        Direction.RIGHT,
    )

    def __init__(self, engine, random_source=None):
        self.engine = engine
        # A bot-owned source keeps bot randomness from shifting engine food placement.
        self.random_source = (
            random_source if random_source is not None else random.Random()
        )

    def choose_action(self, state):
        raise NotImplementedError("a Bot Mode must choose an action")

    def observe(self, transition):
        pass

    def on_game_end(self, result):
        pass

    @staticmethod
    def head_position(state):
        return tuple(state.snake_position)

    @staticmethod
    def body_positions(state):
        return [tuple(position) for position in state.snake_body]

    @staticmethod
    def food_position(state):
        if state.food_position is None:
            return None

        return tuple(state.food_position)

    @staticmethod
    def position_after(position, direction):
        x, y = position

        if direction == Direction.UP:
            y -= 1
        elif direction == Direction.DOWN:
            y += 1
        elif direction == Direction.LEFT:
            x -= 1
        elif direction == Direction.RIGHT:
            x += 1

        return (x, y)

    @staticmethod
    def is_inside_board(state, position):
        x, y = position

        return 0 <= x < state.board_width and 0 <= y < state.board_height

    @staticmethod
    def can_turn(state, direction):
        return OPPOSITE_DIRECTION[direction] != state.direction

    def is_safe_direction(self, state, direction):
        # A reversal is refused by the engine, so preview would answer for the
        # current heading instead of this direction.
        if not self.can_turn(state, direction):
            return False

        return self.engine.preview(direction).moved

    def safe_directions(self, state):
        return [
            direction
            for direction in self.DIRECTIONS
            if self.is_safe_direction(state, direction)
        ]

    def is_safe_position(self, state, position):
        if not self.is_inside_board(state, position):
            return False

        return position not in self.body_positions(state)
