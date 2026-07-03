import csv
import os
from datetime import datetime

class RecordManager:
    """
    Saves game results so we can compare the performance of different bots and strategies.
    """

    def __init__(self, file_name="records/game_records.csv"):
        self.file_name = file_name
        self.folder_name = os.path.dirname(self.file_name)

        if (self.folder_name != "" and not os.path.exists(self.folder_name)):
            os.makedirs(self.folder_name, exist_ok=True)
    
    def save_game_result(self, bot_name, games_played, score, best_score, average_score, total_moves, game_time, session_time, board_width, board_height, tile_size, speed_delay):
        file_exists = os.path.isfile(self.file_name)

        with open(self.file_name, mode='a', newline='') as file:
            writer = csv.writer(file)

            if (not file_exists):
                writer.writerow([
                    "date_time",
                    "bot_name",
                    "games_played",
                    "score",
                    "best_score",
                    "average_score",
                    "total_moves",
                    "game_time",
                    "session_time",
                    "board_width",
                    "board_height",
                    "tile_size",
                    "speed_delay"
                ])
            
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                bot_name,
                games_played,
                score,
                best_score,
                round(average_score, 2),
                total_moves,
                round(game_time, 2),
                round(session_time, 2),
                board_width,
                board_height,
                tile_size,
                speed_delay
            ])

    def read_game_records(self):
        if (not os.path.isfile(self.file_name)):
            return []
        
        records = []

        with open(self.file_name, mode='r', newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                records.append(row)

        return records
