"""Read and save the app's local board, Tile Size, and speed preferences."""

import json
from pathlib import Path

from snake.sessions.SessionSettings import SessionSettings
from snake.storage.JsonFile import save_json_atomically


SETTINGS_SCHEMA_VERSION = 1
# Defaults belong to Snake even when the terminal starts in another folder.
DEFAULT_SETTINGS_PATH = Path(__file__).resolve().parents[2] / "settings.json"


class SettingsFile:
    def __init__(self, path=DEFAULT_SETTINGS_PATH):
        self.path = Path(path)

    def load(self):
        """Restore supported choices; missing or damaged fields keep defaults."""
        settings = SessionSettings()
        try:
            with self.path.open(encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, ValueError, UnicodeError):
            return settings

        if not isinstance(data, dict):
            return settings
        if type(data.get("schema_version")) is not int or data["schema_version"] != SETTINGS_SCHEMA_VERSION:
            return settings

        # Restore each field independently, so one old option cannot hide
        # another choice that the current app still supports.
        board_size = data.get("board_size")
        if isinstance(board_size, list) and len(board_size) == 2 and all(type(side) is int for side in board_size):
            for name, dimensions in settings.board_size_options.items():
                if list(dimensions) == board_size:
                    settings.select_board_size(name)
                    break

        tile_size = data.get("tile_size")
        if type(tile_size) is int:
            for name, pixels in settings.tile_size_options.items():
                if pixels == tile_size:
                    settings.select_tile_size(name)
                    break

        speed = data.get("speed")
        if isinstance(speed, str) and speed in settings.speed_options:
            settings.select_speed(speed)

        return settings

    def save(self, settings):
        """Save values atomically; the caller decides how to report write errors."""
        config = settings.build_game_config()
        data = {
            "schema_version": SETTINGS_SCHEMA_VERSION,
            "board_size": [config.width, config.height],
            "tile_size": config.tile_size,
            "speed": settings.selected_speed_name,
        }
        save_json_atomically(self.path, data)
