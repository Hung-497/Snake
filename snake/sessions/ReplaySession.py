from snake.engine.GameTypes import Direction
from snake.storage.ReplayManager import (
    GRID_COORDINATE_SYSTEM,
    NUMBER_TO_DIRECTION,
    ReplayCompatibilityError,
)


# Replay Speed name -> milliseconds per move, in the order the speed button
# cycles through them. They ignore the speed the game was played at.
REPLAY_SPEEDS = {"Slow": 100, "Normal": 10, "Fast": 2}
DEFAULT_REPLAY_SPEED = "Normal"


def load_replay_session(replay_manager, player):
    """
    Try to open a saved replay for a Player.

    Returns (session, message). Exactly one of them is set: a session when the
    replay can be played, or a message explaining why it cannot. Replay data
    that cannot be trusted never turns into a session, so it is never drawn as
    if it were fine.
    """
    try:
        replay_data = replay_manager.load_replay(player)
    except ReplayCompatibilityError as error:
        return None, str(error)

    if (replay_data is None):
        return None, f"No replay saved for {player} yet."

    try:
        return ReplaySession(replay_data), None
    except ReplayCompatibilityError as error:
        return None, str(error)


class ReplaySession:
    """
    Replays a saved game by rebuilding the snake from the saved moves.

    This is the headless half of the Replay App View: it keeps time and knows
    where the snake and the food are, but draws nothing. ReplayManager has
    already turned the saved data into grid cells before it arrives here.
    """

    # One long frame must not freeze the window by trying to catch up forever.
    MOVES_PER_UPDATE_LIMIT = 50

    def __init__(self, replay_data):
        coordinate_system = replay_data.get("coordinate_system")

        if (coordinate_system != GRID_COORDINATE_SYSTEM):
            raise ReplayCompatibilityError(
                f"Unsupported replay coordinate system: {coordinate_system}"
            )

        self.board_width = replay_data["board_width"]
        self.board_height = replay_data["board_height"]
        self.tile_size = replay_data["tile_size"]

        self.start_snake = tuple(replay_data["start_snake"])
        self.foods = replay_data["foods"]
        self.moves = replay_data["moves"]
        self.final_score = replay_data["final_score"]

        self.stopped = False
        self.set_speed(DEFAULT_REPLAY_SPEED)
        self.reset_playback()

    def reset_playback(self):
        """Put the snake, food, score and timer back to the replay's first move."""
        self.snake_position = self.start_snake
        self.snake_body = []

        self.food_index = 0
        self.food_position = tuple(self.foods[0]) if self.foods else None

        self.move_index = 0
        self.score = 0
        self.time_since_last_move = 0.0

        self.finished = False
        self.paused = False

    @property
    def moves_played(self):
        """How many saved moves have been played so far, for the progress display."""
        return self.move_index

    @property
    def total_moves(self):
        return len(self.moves)

    def advance_by(self, elapsed_seconds):
        """Play the moves that fit in the time one Arcade frame took."""
        # Paused time is not counted, so resuming causes no burst of moves.
        if (self.stopped or self.finished or self.paused):
            return 0

        self.time_since_last_move += elapsed_seconds
        moves_played = 0

        while (self.time_since_last_move >= self.move_interval):
            if (moves_played >= self.MOVES_PER_UPDATE_LIMIT):
                break

            self.time_since_last_move -= self.move_interval
            self.advance()
            moves_played += 1

            if (self.finished):
                break

        return moves_played

    def advance(self):
        """Play one saved move."""
        if (self.stopped or self.finished):
            return

        if (self.move_index >= len(self.moves)):
            self.finished = True
            return

        direction = NUMBER_TO_DIRECTION.get(self.moves[self.move_index])

        if (direction is None):
            # An unreadable move ends the replay instead of guessing.
            self.finished = True
            return

        moved = self.move_snake(direction)
        self.move_index += 1

        # A fatal move ends the game, so nothing after it can be played.
        if (not moved or self.move_index >= len(self.moves)):
            self.finished = True

    def move_snake(self, direction):
        """
        Move the snake one cell, or return False for a fatal move.

        A saved game that ended in a collision also saved that last move, but
        the Game Engine never moved the snake for it. The same rules apply
        here, so the head never leaves the board or lands on the body.
        """
        column, row = self.snake_position
        next_column, next_row = column, row

        if (direction == Direction.UP):
            next_row -= 1
        elif (direction == Direction.DOWN):
            next_row += 1
        elif (direction == Direction.LEFT):
            next_column -= 1
        elif (direction == Direction.RIGHT):
            next_column += 1

        ate_food = (
            self.food_position is not None
            and (next_column, next_row) == self.food_position
        )

        inside_board = (0 <= next_column < self.board_width
                        and 0 <= next_row < self.board_height)
        # The tail moves away on this move unless the snake grows.
        body_in_the_way = self.snake_body if ate_food else self.snake_body[:-1]

        if (not inside_board or (next_column, next_row) in body_in_the_way):
            return False

        if (ate_food):
            # The snake grows, so the old head stays and no tail cell is dropped.
            self.snake_body = [self.snake_position] + self.snake_body
            self.score += 1
            self.move_to_next_food()
        elif (len(self.snake_body) > 0):
            self.snake_body = [self.snake_position] + self.snake_body[:-1]

        self.snake_position = (next_column, next_row)
        return True

    def move_to_next_food(self):
        if (self.food_index + 1 >= len(self.foods)):
            return

        self.food_index += 1
        self.food_position = tuple(self.foods[self.food_index])

    def toggle_pause(self):
        """Pause or resume playback. A finished or stopped replay stays as it is."""
        if (self.stopped or self.finished):
            return

        self.paused = not self.paused

    def set_speed(self, speed_name):
        self.speed_name = speed_name
        # Replay Speeds are in milliseconds; Arcade works in seconds.
        self.move_interval = REPLAY_SPEEDS[speed_name] / 1000
        # Time saved up at the old speed must not become a burst at the new one.
        self.time_since_last_move = 0.0

    def cycle_speed(self):
        """Switch to the next Replay Speed: Slow, then Normal, then Fast, then Slow."""
        if (self.stopped):
            return

        speed_names = list(REPLAY_SPEEDS)
        next_index = (speed_names.index(self.speed_name) + 1) % len(speed_names)
        self.set_speed(speed_names[next_index])

    def restart(self):
        """Play the replay again from its first move, even if paused or finished."""
        if (self.stopped):
            return

        self.reset_playback()

    def stop(self):
        """Prevent any further playback, for leaving or closing the App View."""
        self.stopped = True
