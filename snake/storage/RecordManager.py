import csv
import os
import shutil
from datetime import datetime


# The columns of a records file, in order. A column is only ever added at the
# end, so older files keep their positions.
RECORD_COLUMNS = [
    "date_time",
    "player",
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
    "speed_delay",
    "outcome",
]


class RecordManager:
    """
    Saves game results so we can compare how each Player performs.

    Each game stores its Game Outcome: "won" or "died". Files saved before
    outcomes were kept have no outcome column; the first save to such a file
    backs it up and upgrades it (ADR 0006), and their old games read back
    with an empty outcome, which means unknown.
    """

    def __init__(self, file_name="records/game_records.csv"):
        self.file_name = file_name
        self.folder_name = os.path.dirname(self.file_name)

        if (self.folder_name != "" and not os.path.exists(self.folder_name)):
            os.makedirs(self.folder_name, exist_ok=True)
    
    def save_game_result(self, player, games_played, score, best_score, average_score, total_moves, game_time, session_time, board_width, board_height, tile_size, speed_delay, outcome=""):
        header = self.read_header()

        if (header is not None and "outcome" not in header):
            self.upgrade_old_file()
            header = RECORD_COLUMNS

        with open(self.file_name, mode='a', newline='') as file:
            writer = csv.writer(file)

            if (header is None):
                writer.writerow(RECORD_COLUMNS)
            
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                player,
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
                speed_delay,
                outcome,
            ])

    def read_game_records(self):
        if (not os.path.isfile(self.file_name)):
            return []
        
        records = []

        with open(self.file_name, mode='r', newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Files saved before Human Play named this column bot_name.
                if ("bot_name" in row and "player" not in row):
                    row["player"] = row.pop("bot_name")

                # Files saved before Game Outcomes were kept: the outcome is unknown.
                if (row.get("outcome") is None):
                    row["outcome"] = ""

                records.append(row)

        return records

    def read_header(self):
        """The file's column names, or None when there is no file or it is empty."""
        if (not os.path.isfile(self.file_name)):
            return None

        with open(self.file_name, mode='r', newline='') as file:
            return next(csv.reader(file), None)

    def upgrade_old_file(self):
        """
        Give an old records file the current columns, keeping every game.

        A copy is saved next to it first, and an existing copy is never
        overwritten, so the first backup always survives. The upgraded file
        is written beside the old one and only then swapped in, so a failure
        part-way leaves the old file exactly as it was.
        """
        backup_name = self.file_name + ".bak"
        upgraded_name = self.file_name + ".upgrading"

        if (not os.path.exists(backup_name)):
            shutil.copyfile(self.file_name, backup_name)

        with open(self.file_name, mode='r', newline='') as file:
            old_rows = list(csv.reader(file))[1:]

        try:
            with open(upgraded_name, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(RECORD_COLUMNS)

                for row in old_rows:
                    if (not row):
                        continue

                    # Old games have no outcome, so it is left empty: unknown.
                    writer.writerow(row + [""])

            # Replacing a file is all-or-nothing, so the records are never half-written.
            os.replace(upgraded_name, self.file_name)
        finally:
            if (os.path.exists(upgraded_name)):
                os.remove(upgraded_name)
