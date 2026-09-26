from dataclasses import dataclass
import random

from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction, Position


@dataclass(frozen=True)
class EngineState:
    """Immutable, presentation-neutral snapshot of the engine state."""

    board_width: int
    board_height: int
    tile_size: int
    snake_position: Position
    snake_body: tuple
    direction: Direction
    food_position: Position | None
    score: int
    game_over: bool
    game_won: bool


@dataclass(frozen=True)
class Transition:
    """What one move would do, reported identically by preview and step.

    The record never names the next food cell, because choosing one
    consumes randomness and may only happen on a committed step.
    """

    direction: Direction
    position: Position
    body: tuple
    moved: bool
    ate_food: bool
    score_change: int
    score: int
    collision: bool
    game_over: bool
    game_won: bool


OPPOSITE_DIRECTION = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


class SnakeEngine:
    """Headless Snake rules using zero-based board-cell coordinates."""

    def __init__(
        self,
        config,
        start_position=(0, 0),
        body=(),
        direction=Direction.RIGHT,
        random_source=None,
        food_position=None,
    ):
        if not isinstance(config, GameConfig):
            raise TypeError("config must be a GameConfig")

        self.config = config
        self.random_source = random_source if random_source is not None else random

        if start_position is None:
            start_position = self._random_position()
        else:
            start_position = self._coerce_position(start_position)

        initial_direction = Direction.from_value(direction)
        if initial_direction is None:
            raise ValueError("direction must be a Direction")

        initial_body = tuple(self._coerce_position(position) for position in body)
        if food_position is not None:
            food_position = self._coerce_position(food_position)
            if food_position == start_position or food_position in initial_body:
                raise ValueError("food must be placed on a free cell")

        self._initial_position = start_position
        self._initial_body = initial_body
        self._initial_direction = initial_direction
        self._initial_food_position = food_position
        self._food_position_is_fixed = food_position is not None
        self.reset()

    @property
    def state(self):
        return EngineState(
            board_width=self.config.width,
            board_height=self.config.height,
            tile_size=self.config.tile_size,
            snake_position=self.snake_position,
            snake_body=self.snake_body,
            direction=self.direction,
            food_position=self.food_position,
            score=self.score,
            game_over=self.game_over,
            game_won=self.game_won,
        )

    @property
    def board_width(self):
        return self.config.width

    @property
    def board_height(self):
        return self.config.height

    @property
    def tile_size(self):
        return self.config.tile_size

    @property
    def snake_position(self):
        return self._snake_position

    @property
    def snake_body(self):
        return tuple(self._snake_body)

    @property
    def direction(self):
        return self._direction

    @property
    def game_over(self):
        return self._game_over

    @property
    def food_position(self):
        return self._food_position

    @property
    def score(self):
        return self._score

    @property
    def game_won(self):
        return self._game_won

    def change_direction(self, direction):
        new_direction = Direction.from_value(direction)
        if new_direction is None:
            return False

        if OPPOSITE_DIRECTION[new_direction] == self._direction:
            return False

        self._direction = new_direction
        return True

    def choose_start_direction(self, direction):
        """
        Pick the direction a game starts in, before its first move.

        Unlike change_direction, this may turn the snake around when it has
        no body yet, because there is nothing behind the head to run into.
        """
        if self._snake_body:
            return self.change_direction(direction)

        new_direction = Direction.from_value(direction)
        if new_direction is None:
            return False

        self._direction = new_direction
        return True

    def preview(self, direction=None):
        """Report what a move would do without committing anything."""
        return self.preview_from(self.state, direction)

    def preview_from(self, state, direction=None):
        """Preview a move from a future state without changing the live game."""
        return self._calculate_transition(state, direction)

    def _resolve_direction(self, current_direction, direction):
        if direction is None:
            return current_direction

        requested = Direction.from_value(direction)
        if requested is None:
            raise ValueError("direction must be a Direction")

        # A reversal is refused, so the move still uses the current heading.
        if OPPOSITE_DIRECTION[requested] == current_direction:
            return current_direction

        return requested

    def _calculate_transition(self, state, direction=None):
        resolved_direction = self._resolve_direction(state.direction, direction)
        current_body = tuple(state.snake_body)

        def blocked(collision):
            return Transition(
                direction=resolved_direction,
                position=state.snake_position,
                body=current_body,
                moved=False,
                ate_food=False,
                score_change=0,
                score=state.score,
                collision=collision,
                game_over=state.game_over or collision,
                game_won=state.game_won,
            )

        if state.game_over:
            return blocked(False)

        next_position = self._position_after(state.snake_position, resolved_direction)

        if not self._is_inside_board(next_position):
            return blocked(True)

        ate_food = next_position == state.food_position
        body_to_check = current_body if ate_food else current_body[:-1]
        if next_position in body_to_check:
            return blocked(True)

        previous_head = state.snake_position
        if ate_food:
            next_body = (previous_head, *current_body)
        elif len(current_body) > 0:
            next_body = (previous_head, *current_body[:-1])
        else:
            next_body = ()

        occupied_tiles = len(next_body) + 1
        total_tiles = state.board_width * state.board_height
        game_won = ate_food and occupied_tiles == total_tiles

        return Transition(
            direction=resolved_direction,
            position=next_position,
            body=next_body,
            moved=True,
            ate_food=ate_food,
            score_change=1 if ate_food else 0,
            score=state.score + (1 if ate_food else 0),
            collision=False,
            game_over=game_won,
            game_won=game_won,
        )

    def step(self):
        transition = self.preview()

        if not transition.moved:
            self._game_over = transition.game_over
            return False

        self._snake_position = transition.position
        self._snake_body = list(transition.body)
        self._score = transition.score

        # Food placement is commit-only, so preview never consumes randomness.
        if transition.ate_food:
            if transition.game_won:
                self._food_position = None
                self._game_over = True
                self._game_won = True
            else:
                self._food_position = self._spawn_food()

        return True

    def reset(self):
        self._snake_position = self._initial_position
        self._snake_body = list(self._initial_body)
        self._direction = self._initial_direction
        self._score = 0
        self._game_over = False
        self._game_won = False

        if self._food_position_is_fixed:
            self._food_position = self._initial_food_position
        else:
            self._food_position = self._spawn_food()

    def _position_after(self, position, direction):
        x, y = position

        if direction == Direction.UP:
            y -= 1
        elif direction == Direction.DOWN:
            y += 1
        elif direction == Direction.LEFT:
            x -= 1
        elif direction == Direction.RIGHT:
            x += 1

        return Position(x, y)

    def _random_position(self):
        return Position(
            self.random_source.randint(0, self.board_width - 1),
            self.random_source.randint(0, self.board_height - 1),
        )

    def _spawn_food(self):
        occupied_positions = {self._snake_position, *self._snake_body}
        free_positions = []

        for row in range(self.board_height):
            for column in range(self.board_width):
                position = Position(column, row)
                if position not in occupied_positions:
                    free_positions.append(position)

        if len(free_positions) == 0:
            return None

        food_index = self.random_source.randint(0, len(free_positions) - 1)
        return free_positions[food_index]

    def _is_inside_board(self, position):
        x, y = position
        return 0 <= x < self.board_width and 0 <= y < self.board_height

    def _coerce_position(self, position):
        if isinstance(position, Position):
            candidate = (position.x, position.y)
        elif (
            isinstance(position, (tuple, list))
            and len(position) == 2
            and all(type(value) is int for value in position)
        ):
            candidate = tuple(position)
        else:
            raise ValueError("positions must contain two integer coordinates")

        x, y = candidate
        if self._is_inside_board(candidate):
            return Position(x, y)

        # Accept old pixel inputs at the migration boundary.  The engine's
        # authoritative state remains in cells after this conversion.
        if (
            x % self.tile_size == 0
            and y % self.tile_size == 0
            and 0 <= x < self.board_width * self.tile_size
            and 0 <= y < self.board_height * self.tile_size
        ):
            return Position(x // self.tile_size, y // self.tile_size)

        raise ValueError("positions must be inside the board")
