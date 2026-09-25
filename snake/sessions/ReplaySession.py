from snake.engine.GameTypes import Direction
from snake.storage.ReplayManager import (
    GRID_COORDINATE_SYSTEM,
    NUMBER_TO_DIRECTION,
    ReplayCompatibilityError,
)


def load_replay_session(replay_manager, bot_name):
    """
    Try to open a saved replay for a Bot Mode.

    Returns (session, message). Exactly one of them is set: a session when the
    replay can be played, or a message explaining why it cannot. Replay data
    that cannot be trusted never turns into a session, so it is never drawn as
    if it were fine.
    """
    try:
        replay_data = replay_manager.load_replay(bot_name)
    except ReplayCompatibilityError as error:
        return None, str(error)

    if (replay_data is None):
        return None, f"No replay saved for {bot_name} yet."

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

    def __init__(self, replay_data, move_delay=10):
        coordinate_system = replay_data.get("coordinate_system")

        if (coordinate_system != GRID_COORDINATE_SYSTEM):
            raise ReplayCompatibilityError(
                f"Unsupported replay coordinate system: {coordinate_system}"
            )

        self.board_width = replay_data["board_width"]
        self.board_height = replay_data["board_height"]
        self.tile_size = replay_data["tile_size"]

        self.snake_position = tuple(replay_data["start_snake"])
        self.snake_body = []

        self.foods = replay_data["foods"]
        self.food_index = 0
        self.food_position = tuple(self.foods[0]) if self.foods else None

        self.moves = replay_data["moves"]
        self.move_index = 0
        self.score = 0
        self.final_score = replay_data["final_score"]

        # The saved replay delay is in milliseconds; Arcade works in seconds.
        self.move_interval = move_delay / 1000
        self.time_since_last_move = 0.0

        self.finished = False
        self.stopped = False

    def advance_by(self, elapsed_seconds):
        """Play the moves that fit in the time one Arcade frame took."""
        if (self.stopped or self.finished):
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

        self.move_snake(direction)
        self.move_index += 1

        if (self.move_index >= len(self.moves)):
            self.finished = True

    def move_snake(self, direction):
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

        if (ate_food):
            # The snake grows, so the old head stays and no tail cell is dropped.
            self.snake_body = [self.snake_position] + self.snake_body
            self.score += 1
            self.move_to_next_food()
        elif (len(self.snake_body) > 0):
            self.snake_body = [self.snake_position] + self.snake_body[:-1]

        self.snake_position = (next_column, next_row)

    def move_to_next_food(self):
        if (self.food_index + 1 >= len(self.foods)):
            return

        self.food_index += 1
        self.food_position = tuple(self.foods[self.food_index])

    def stop(self):
        """Prevent any further playback, for leaving or closing the App View."""
        self.stopped = True
