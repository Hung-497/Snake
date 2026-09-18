import arcade.gui

from BotFactory import supports_board
from ViewStyle import (
    BACKGROUND_COLOR,
    SECONDARY_BUTTON_COLOR,
    WARNING_TEXT_COLOR,
    center_in_view,
    create_button,
    create_muted_label,
    create_title_label,
)


# The name the Bot Mode factory uses -> the name shown to the user.
BOT_MODE_LABELS = {
    "rule": "Rule Based",
    "q_learning": "Q Learning",
    "hamiltonian": "Hamiltonian",
}

UNSUPPORTED_BOARD_MESSAGE = "Hamiltonian Bot needs at least one even board side."


class PlayView(arcade.gui.UIView):
    """
    The Play App View: pick the Bot Mode that will play the games.

    A Bot Mode that cannot play the board chosen in Settings never reaches the
    Game App View; this view explains why instead.
    """

    def __init__(self, shell, settings):
        super().__init__()
        self.shell = shell
        self.settings = settings
        self.background_color = BACKGROUND_COLOR

        play_box = arcade.gui.UIBoxLayout(space_between=9)
        play_box.add(create_title_label("Choose Bot Mode:", font_size=46))
        play_box.add(arcade.gui.UISpace(height=20, color=BACKGROUND_COLOR))

        for bot_mode, button_text in BOT_MODE_LABELS.items():
            play_box.add(create_button(button_text, self.start_game(bot_mode)))

        self.message_label = create_muted_label("", font_size=15)
        self.message_label.update_font(font_color=WARNING_TEXT_COLOR)
        play_box.add(arcade.gui.UISpace(height=10, color=BACKGROUND_COLOR))
        play_box.add(self.message_label)

        play_box.add(arcade.gui.UISpace(height=8, color=BACKGROUND_COLOR))
        play_box.add(
            create_button(
                "Back",
                lambda: self.shell.show_view("menu"),
                button_color=SECONDARY_BUTTON_COLOR,
                button_width=170,
            )
        )

        center_in_view(self.ui, play_box)

    def start_game(self, bot_mode):
        def start():
            game_config = self.settings.build_game_config()

            if (not supports_board(bot_mode, game_config.width, game_config.height)):
                self.message_label.text = UNSUPPORTED_BOARD_MESSAGE
                return

            self.message_label.text = ""
            self.shell.show_view("game", bot_mode=bot_mode)

        return start
