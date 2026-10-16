import arcade.gui

from snake.bots.BotFactory import supports_board
from snake.sessions.HumanPlayer import HUMAN_PLAY
from snake.sessions.LiveTraining import DQN_VERSIONS, missing_dependency_message
from snake.sessions.TrainingSaves import SAVE_PATHS, copy_shared_q_table_once, saved_training
from snake.ui import Theme
from snake.ui.PlayerLabels import LEARNING_FAMILIES, app_view_for_bot_mode, bot_mode_choices
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

        for choice in bot_mode_choices():
            action = (self.choose_version(choice.key) if choice.is_family
                      else self.start_game(choice.key))
            play_box.add(Theme.create_primary_button(choice.label, action,
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
            message = self.start_bot_mode(bot_mode)
            self.message_text = message or ""
            self.message_label.text = self.message_text

        return start

    def start_bot_mode(self, bot_mode):
        """Open the App View for a Bot Mode, or return why it cannot play here."""
        game_config = self.settings.build_game_config()

        if (not supports_board(bot_mode, game_config.width, game_config.height)):
            return UNSUPPORTED_BOARD_MESSAGE

        app_view = app_view_for_bot_mode(bot_mode)
        # Without PyTorch, Live Training opens straight away to explain how
        # to install it.
        no_dqn = bot_mode in DQN_VERSIONS and missing_dependency_message()
        if bot_mode not in SAVE_PATHS or no_dqn:
            self.shell.show_view(app_view, bot_mode=bot_mode)
            return None

        # A learning Bot Mode asks first: continue a save, or set up a new
        # training. Q Learning's app table starts as a copy of the shared one.
        copy_shared_q_table_once(bot_mode)
        back = self.choose_version(family_of(bot_mode))
        # It opens even with no save, so the Showcase Bot can still be reached.
        self.shell.show_view("training_start", bot_mode=bot_mode,
                             summary=saved_training(bot_mode), back=back)
        return None

    def choose_version(self, family):
        return lambda: self.shell.show_view(
            "choose_version", family=family, choose=self.start_bot_mode,
            back=lambda: self.shell.show_view("play"),
        )

    def on_resize(self, width, height):
        if layout_step(width) != self.current_layout_step:
            self.current_layout_step = layout_step(width)
            self.build_ui()

    def on_update(self, delta_time):
        self.ui.on_update(delta_time)


def family_of(bot_mode):
    """The learning family a versioned Bot Mode belongs to."""
    return next(
        family_key for family_key, family in LEARNING_FAMILIES.items()
        if bot_mode in family.versions.values()
    )
