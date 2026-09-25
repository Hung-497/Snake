import os
import json
from snake.engine.GameTypes import Direction


REPLAY_SCHEMA_VERSION = 2
GRID_COORDINATE_SYSTEM = "grid"
PIXEL_COORDINATE_SYSTEM = "pixel"


class ReplayCompatibilityError(ValueError):
    """Raised when replay data cannot be safely interpreted."""

DIRECTION_TO_NUMBER = {
    Direction.UP: 1,
    Direction.LEFT: 2,
    Direction.DOWN: 3,
    Direction.RIGHT: 4
}

NUMBER_TO_DIRECTION = {
    1: Direction.UP,
    2: Direction.LEFT,
    3: Direction.DOWN,
    4: Direction.RIGHT
}

class ReplayManager:
    """
    Handles replay data for finished games.

    Game records only save summary data.
    Replay data saves enough information to watch a game again later.
    """

    def __init__(self, folder_name="replays"):
        self.folder_name = folder_name
        self.replay_data = None

        os.makedirs(self.folder_name, exist_ok=True)

    def start_recording(
        self,
        player,
        board_width,
        board_height,
        tile_size,
        speed_delay,
        snake=None,
        food=None,
        engine=None,
    ):
        if (engine is not None):
            start_snake = tuple(engine.snake_position)
            start_food = (
                None
                if engine.food_position is None
                else tuple(engine.food_position)
            )
        else:
            start_snake = self._pixel_to_grid(
                (snake.x, snake.y), board_width, board_height, tile_size
            )
            start_food = self._pixel_to_grid(
                (food.x, food.y), board_width, board_height, tile_size
            )

        self.replay_data = {
            "player": player,
            "board_width": board_width,
            "board_height": board_height,
            "tile_size": tile_size,
            "speed_delay": speed_delay,
            "schema_version": REPLAY_SCHEMA_VERSION,
            "coordinate_system": GRID_COORDINATE_SYSTEM,
            "start_snake": list(start_snake),
            "start_food": None if start_food is None else list(start_food),
            "moves": [],
            "foods": [] if start_food is None else [list(start_food)],
            "final_score": 0
        }
    
    def record_move(self, direction):
        if (self.replay_data is None):
            return 
        
        direction = Direction.from_value(direction)
        move_number = DIRECTION_TO_NUMBER.get(direction)

        if (move_number is None):
            return
        self.replay_data["moves"].append(move_number)
    
    def record_food(self, food):
        if (self.replay_data is None):
            return 
        
        if (hasattr(food, "x") and hasattr(food, "y")):
            food_position = (food.x, food.y)
        else:
            food_position = tuple(food)

        if self.replay_data["coordinate_system"] == GRID_COORDINATE_SYSTEM:
            if not self._is_grid_position(
                food_position,
                self.replay_data["board_width"],
                self.replay_data["board_height"],
            ):
                food_position = self._pixel_to_grid(
                    food_position,
                    self.replay_data["board_width"],
                    self.replay_data["board_height"],
                    self.replay_data["tile_size"],
                )

        self.replay_data["foods"].append(list(food_position))

    def record_final_score(self, score):
        if (self.replay_data is None):
            return
        
        self.replay_data["final_score"] = score

    def save_replay(self, player, score, game_won=False):
        if (self.replay_data is None):
            return

        self.record_final_score(score)

        file_path = self.get_replay_file_path(player)

        if (player == "hamiltonian" and not game_won):
            return
        
        if (player != "hamiltonian" and not self.should_replace_replay(file_path, score)):
            return
        
        with open(file_path, "w") as file:
            json.dump(self.replay_data, file, indent=4)
    
    def get_replay_file_path(self, player):
        if (player == "rule"):
            file_name = "rule_best.json"
        elif (player == "q_learning"):
            file_name = "q_learning_best.json"
        elif (player == "hamiltonian"):
            file_name = "hamiltonian_best.json"
        else:
            file_name = f"{player}_best.json"

        return os.path.join(self.folder_name, file_name)
    
    def should_replace_replay(self, file_path, score):
        if (not os.path.exists(file_path)):
            return True
        
        with open(file_path, "r") as file:
            old_replay_data = json.load(file)

        old_score = old_replay_data.get("final_score", 0)

        return score > old_score

    def load_replay(self, player):
        file_path = self.get_replay_file_path(player)

        if (not os.path.exists(file_path)):
            return None
        
        try:
            with open(file_path, "r") as file:
                replay_data = json.load(file)
        except (OSError, json.JSONDecodeError, UnicodeError) as error:
            raise ReplayCompatibilityError(
                f"Replay data is malformed: {error}"
            ) from error

        return self._normalise_replay(replay_data)

    def _normalise_replay(self, replay_data):
        if not isinstance(replay_data, dict):
            raise ReplayCompatibilityError("Replay data must be a JSON object")

        schema_version = replay_data.get("schema_version")
        coordinate_system = replay_data.get("coordinate_system")

        if schema_version is None and coordinate_system is None:
            return self._normalise_pixel_replay(replay_data)

        if schema_version != REPLAY_SCHEMA_VERSION:
            raise ReplayCompatibilityError(
                f"Unsupported replay schema version: {schema_version}"
            )

        if coordinate_system == GRID_COORDINATE_SYSTEM:
            return self._normalise_grid_replay(replay_data)
        if coordinate_system == PIXEL_COORDINATE_SYSTEM:
            return self._normalise_pixel_replay(replay_data)

        raise ReplayCompatibilityError(
            f"Unsupported replay coordinate system: {coordinate_system}"
        )

    def _normalise_grid_replay(self, replay_data):
        self._validate_replay_metadata(replay_data)
        board_width = replay_data["board_width"]
        board_height = replay_data["board_height"]

        start_snake = self._require_grid_position(
            replay_data.get("start_snake"), board_width, board_height
        )
        start_food = replay_data.get("start_food")
        if start_food is not None:
            start_food = self._require_grid_position(
                start_food, board_width, board_height
            )

        foods = replay_data.get("foods")
        if not isinstance(foods, list):
            raise ReplayCompatibilityError("Replay foods must be a list")
        normalised_foods = [
            self._require_grid_position(food, board_width, board_height)
            for food in foods
        ]
        self._validate_moves(replay_data.get("moves"))

        normalised = dict(replay_data)
        normalised["schema_version"] = REPLAY_SCHEMA_VERSION
        normalised["coordinate_system"] = GRID_COORDINATE_SYSTEM
        normalised["start_snake"] = list(start_snake)
        normalised["start_food"] = (
            None if start_food is None else list(start_food)
        )
        normalised["foods"] = [list(food) for food in normalised_foods]
        return normalised

    def _normalise_pixel_replay(self, replay_data):
        self._validate_replay_metadata(replay_data)
        board_width = replay_data["board_width"]
        board_height = replay_data["board_height"]
        tile_size = replay_data["tile_size"]

        try:
            start_snake = self._pixel_to_grid(
                replay_data.get("start_snake"),
                board_width,
                board_height,
                tile_size,
            )
            start_food_data = replay_data.get("start_food")
            start_food = (
                None
                if start_food_data is None
                else self._pixel_to_grid(
                    start_food_data,
                    board_width,
                    board_height,
                    tile_size,
                )
            )
            foods = replay_data.get("foods")
            if not isinstance(foods, list):
                raise ReplayCompatibilityError("Replay foods must be a list")
            normalised_foods = [
                self._pixel_to_grid(food, board_width, board_height, tile_size)
                for food in foods
            ]
        except ReplayCompatibilityError:
            raise

        self._validate_moves(replay_data.get("moves"))
        normalised = dict(replay_data)
        normalised["schema_version"] = REPLAY_SCHEMA_VERSION
        normalised["coordinate_system"] = GRID_COORDINATE_SYSTEM
        normalised["start_snake"] = list(start_snake)
        normalised["start_food"] = (
            None if start_food is None else list(start_food)
        )
        normalised["foods"] = [list(food) for food in normalised_foods]
        return normalised

    def _validate_replay_metadata(self, replay_data):
        for field in ("board_width", "board_height", "tile_size"):
            value = replay_data.get(field)
            if type(value) is not int or value <= 0:
                raise ReplayCompatibilityError(
                    f"Replay {field} must be a positive integer"
                )

        if type(replay_data.get("speed_delay")) is not int or replay_data["speed_delay"] < 0:
            raise ReplayCompatibilityError(
                "Replay speed_delay must be a non-negative integer"
            )
        if not isinstance(replay_data.get("moves"), list):
            raise ReplayCompatibilityError("Replay moves must be a list")
        if (
            type(replay_data.get("final_score")) is not int
            or replay_data["final_score"] < 0
        ):
            raise ReplayCompatibilityError("Replay final_score must be an integer")

    def _validate_moves(self, moves):
        if not isinstance(moves, list) or any(
            type(move) is not int or move not in NUMBER_TO_DIRECTION
            for move in moves
        ):
            raise ReplayCompatibilityError("Replay contains an invalid direction")

    def _require_grid_position(self, position, board_width, board_height):
        if not self._is_grid_position(position, board_width, board_height):
            raise ReplayCompatibilityError("Replay contains an invalid grid position")
        return tuple(position)

    def _is_grid_position(self, position, board_width, board_height):
        return (
            isinstance(position, (list, tuple))
            and len(position) == 2
            and all(type(value) is int for value in position)
            and 0 <= position[0] < board_width
            and 0 <= position[1] < board_height
        )

    def _pixel_to_grid(self, position, board_width, board_height, tile_size):
        if (
            not isinstance(position, (list, tuple))
            or len(position) != 2
            or any(type(value) is not int for value in position)
        ):
            raise ReplayCompatibilityError("Replay pixel position is malformed")

        x, y = position
        if (
            x % tile_size != 0
            or y % tile_size != 0
            or x < 0
            or y < 0
            or x >= board_width * tile_size
            or y >= board_height * tile_size
        ):
            raise ReplayCompatibilityError(
                "Replay pixel coordinates cannot be migrated safely"
            )
        return x // tile_size, y // tile_size
