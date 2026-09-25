from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import OPPOSITE_DIRECTION


# The name saved in records and replays for games a person played.
HUMAN_PLAY = "human"


class HumanPlayer:
    """
    Human Play: the Player that turns key presses into snake directions.

    It is a Player but not a Bot Mode, so it does not subclass BotMode. It
    offers the same choose_action / observe / on_game_end methods, which lets
    the game session drive it exactly like a bot.
    """

    # Two quick turns (like Up then Left) often land inside one step, so both
    # are kept and used one per step. More than two would keep the snake
    # turning after the person stopped pressing keys.
    MAX_QUEUED_TURNS = 2

    def __init__(self, engine):
        self.engine = engine
        self.queued_directions = []

    def press(self, direction):
        """Queue a turn. Returns False when the press is ignored."""
        new_direction = Direction.from_value(direction)

        if (new_direction is None or len(self.queued_directions) >= self.MAX_QUEUED_TURNS):
            return False

        # Compare with the turn the snake will be facing when this one is used.
        if (self.queued_directions):
            last_direction = self.queued_directions[-1]
        else:
            last_direction = self.engine.state.direction

        # A repeat changes nothing, and a reversal would steer into the body.
        if (new_direction == last_direction or new_direction == OPPOSITE_DIRECTION[last_direction]):
            return False

        self.queued_directions.append(new_direction)
        return True

    def choose_action(self, state):
        if (self.queued_directions):
            return self.queued_directions.pop(0)

        # No turn waiting: the snake keeps going straight.
        return None

    def observe(self, transition):
        pass

    def on_game_end(self, result):
        self.queued_directions.clear()
