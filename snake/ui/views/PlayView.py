import arcade.gui

from snake.bots.BotFactory import supports_board
from snake.sessions.HumanPlayer import HUMAN_PLAY
from snake.ui import Theme
from snake.ui.PlayerLabels import BOT_MODE_LABELS
from snake.ui.WindowLayout import layout_step

UNSUPPORTED_BOARD_MESSAGE = "Hamiltonian Bot needs at least one even board side."


class PlayView(arcade.gui.UIView):
    """
    The Play App View: play yourself, or pick the Bot Mode that will play.

    A Bot Mode that cannot play the board chosen in Settings never reaches the
    Game App View; this view explains why instead.
    """

    def __init__(self, shell, settings):
        super().__init__()
        self.shell = shell
        self.settings = settings
        self.background_color = Theme.SURFACE
        self.message_text = ""
        self.current_layout_step = layout_step(self.window.width)
        self.build_ui()

    def build_ui(self):
        self.ui.clear()
        sizes = Theme.type_sizes(self.window.width)
        play_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_TIGHT)
        play_box.add(Theme.create_label("Choose a Player:",
                                         font_size=sizes.display, semibold=True))
        play_box.add(Theme.create_spacer(Theme.SPACE_SECTION))

        # Human Play is a Player but not a Bot Mode, so it has its own button.
        play_box.add(Theme.create_primary_button("Play Yourself", self.start_game(HUMAN_PLAY),
                                                 font_size=sizes.heading))
        play_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))

        for bot_mode, button_text in BOT_MODE_LABELS.items():
            play_box.add(Theme.create_primary_button(button_text, self.start_game(bot_mode),
                                                     font_size=sizes.heading))

        self.message_label = Theme.create_label(self.message_text,
                                                font_size=sizes.body, color=Theme.WARNING)
        play_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))
        play_box.add(self.message_label)

        play_box.add(Theme.create_spacer(Theme.SPACE_TIGHT))
        play_box.add(
            Theme.create_secondary_button(
                "Back",
                lambda: self.shell.show_view("menu"),
                button_width=Theme.BACK_BUTTON_WIDTH,
                font_size=sizes.heading,
            )
        )

        Theme.center_focusable(self.ui, play_box)

    def start_game(self, bot_mode):
        def start():
            game_config = self.settings.build_game_config()

            if (not supports_board(bot_mode, game_config.width, game_config.height)):
                self.message_text = UNSUPPORTED_BOARD_MESSAGE
                self.message_label.text = self.message_text
                return

            self.message_text = ""
            self.message_label.text = ""
            self.shell.show_view("game", bot_mode=bot_mode)

        return start

    def on_resize(self, width, height):
        if layout_step(width) != self.current_layout_step:
            self.current_layout_step = layout_step(width)
            self.build_ui()

    def on_update(self, delta_time):
        self.ui.on_update(delta_time)
