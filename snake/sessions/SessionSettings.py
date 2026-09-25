from snake.engine.GameConfig import GameConfig
from snake.sessions.HumanPlayer import HUMAN_PLAY


class SessionSettings:
    """
    The board size, tile size and speed the user picked for this app session.

    These are the same options the CustomTkinter menu offered. Keeping them in
    one plain object means the Settings App View only has to show them, and the
    choices survive leaving and reopening Settings because the object outlives
    the view. Nothing here knows about Arcade, and no game or bot rule lives
    here: it only builds the GameConfig that gameplay already expects.
    """

    def __init__(self):
        self.board_size_options = {
            "Small 16 x 16": (16, 16),
            "Medium 24 x 25": (24, 25),
            "Large 30 x 30": (30, 30),
            "Square 25 x 25": (25, 25),
        }
        self.tile_size_options = {
            "Small tiles 20 px": 20,
            "Medium tiles 25 px": 25,
            "Large tiles 30 px": 30,
        }
        # The speed is a delay, so a smaller number means a faster game.
        self.speed_options = {
            "Slow": 10,
            "Normal": 5,
            "Fast": 1,
        }
        # A person cannot react to a move every few milliseconds, so Human
        # Play uses its own, slower delay for each of the same speed names.
        self.human_speed_options = {
            "Slow": 150,
            "Normal": 100,
            "Fast": 70,
        }

        self.selected_board_size_name = "Medium 24 x 25"
        self.selected_tile_size_name = "Medium tiles 25 px"
        self.selected_speed_name = "Fast"

    def board_size_names(self):
        return list(self.board_size_options)

    def tile_size_names(self):
        return list(self.tile_size_options)

    def speed_names(self):
        return list(self.speed_options)

    def select_board_size(self, option_name):
        self.check_option(self.board_size_options, option_name, "board size")
        self.selected_board_size_name = option_name

    def select_tile_size(self, option_name):
        self.check_option(self.tile_size_options, option_name, "tile size")
        self.selected_tile_size_name = option_name

    def select_speed(self, option_name):
        self.check_option(self.speed_options, option_name, "speed")
        self.selected_speed_name = option_name

    def check_option(self, options, option_name, setting_label):
        """Refuse an option the app does not offer, instead of failing later."""
        if option_name not in options:
            raise ValueError(f"Unknown {setting_label}: {option_name}")

    def build_game_config(self):
        board_width, board_height = self.board_size_options[self.selected_board_size_name]
        tile_size = self.tile_size_options[self.selected_tile_size_name]

        return GameConfig(board_width, board_height, tile_size)

    @property
    def speed_delay(self):
        return self.speed_options[self.selected_speed_name]

    def speed_delay_for(self, player):
        """The delay between moves for this Player at the chosen speed."""
        if (player == HUMAN_PLAY):
            return self.human_speed_options[self.selected_speed_name]

        return self.speed_delay
