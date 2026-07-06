import os
import json

DIRECTION_TO_NUMBER = {
    "Up": 1,
    "Left": 2,
    "Down": 3,
    "Right": 4
}

NUMBER_TO_DIRECTION = {
    1: "Up",
    2: "Left",
    3: "Down",
    4: "Right"
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

    def start_recording(self, bot_name, board_width, board_height, tile_size, speed_delay, snake, food):
        self.replay_data = {
            "bot_name": bot_name,
            "board_width": board_width,
            "board_height": board_height,
            "tile_size": tile_size,
            "speed_delay": speed_delay,
            "start_snake": [snake.x, snake.y],
            "start_food": [food.x, food.y],
            "moves": [],
            "foods": [[food.x, food.y]],
            "final_score": 0
        }
    
    def record_move(self, direction):
        if (self.replay_data is None):
            return 
        
        move_number = DIRECTION_TO_NUMBER.get(direction)

        if (move_number is None):
            return
        self.replay_data["moves"].append(move_number)
    
    def record_food(self, food):
        if (self.replay_data is None):
            return 
        
        self.replay_data["foods"].append([food.x, food.y])

    def record_final_score(self, score):
        if (self.replay_data is None):
            return
        
        self.replay_data["final_score"] = score

    def save_replay(self, bot_name, score, game_won=False):
        if (self.replay_data is None):
            return

        self.record_final_score(score)

        file_path = self.get_replay_file_path(bot_name)

        if (bot_name == "hamiltonian" and not game_won):
            return
        
        if (bot_name != "hamiltonian" and not self.should_replace_replay(file_path, score)):
            return
        
        with open(file_path, "w") as file:
            json.dump(self.replay_data, file, indent=4)
    
    def get_replay_file_path(self, bot_name):
        if (bot_name == "rule"):
            file_name = "rule_best.json"
        elif (bot_name == "q_learning"):
            file_name = "q_learning_best.json"
        elif (bot_name == "hamiltonian"):
            file_name = "hamiltonian_best.json"
        else:
            file_name = f"{bot_name}_best.json"

        return os.path.join(self.folder_name, file_name)
    
    def should_replace_replay(self, file_path, score):
        if (not os.path.exists(file_path)):
            return True
        
        with open(file_path, "r") as file:
            old_replay_data = json.load(file)

        old_score = old_replay_data.get("final_score", 0)

        return score > old_score

    def load_replay(self, bot_name):
        file_path = self.get_replay_file_path(bot_name)

        if (not os.path.exists(file_path)):
            return None
        
        with open(file_path, "r") as file:
            replay_data = json.load(file)
        
        return replay_data
