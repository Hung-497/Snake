import arcade.gui

from snake.sessions.HumanPlayer import HUMAN_PLAY
from snake.ui.PlayerLabels import BOT_MODE_LABELS, player_label
from snake.storage.ReplayManager import ReplayManager
from snake.sessions.ReplaySession import load_replay_session
from snake.ui import Theme
from snake.ui.WindowLayout import layout_step


class ReplayView(arcade.gui.UIView):
    """
    The Replay App View: choose which Player's saved replay to watch.

    A replay that is missing or cannot be trusted keeps the user here with an
    explanation, so nothing unreadable is ever drawn as if it were a game.
    """

    def __init__(self, shell, replay_manager=None):
        super().__init__()
        self.shell = shell
        self.replay_manager = ReplayManager() if replay_manager is None else replay_manager
        self.background_color = Theme.SURFACE
        self.message_text = ""
        self.current_layout_step = layout_step(self.window.width)
        self.build_ui()

    def build_ui(self):
        self.ui.clear()
        sizes = Theme.type_sizes(self.window.width)
        replay_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_TIGHT)
        replay_box.add(Theme.create_label("Watch a Replay",
                                           font_size=sizes.display, semibold=True))
        replay_box.add(Theme.create_label("The best saved game for each Player",
                                           font_size=sizes.body, color=Theme.TEXT_MUTED))
        replay_box.add(Theme.create_spacer(Theme.SPACE_SECTION))

        for bot_mode, button_text in BOT_MODE_LABELS.items():
            replay_box.add(Theme.create_primary_button(button_text, self.watch_replay(bot_mode),
                                                       font_size=sizes.heading))

        # Human Play is a Player but not a Bot Mode, so it has its own button.
        replay_box.add(Theme.create_primary_button(player_label(HUMAN_PLAY),
                                                   self.watch_replay(HUMAN_PLAY),
                                                   font_size=sizes.heading))

        self.message_label = Theme.create_label(self.message_text,
                                                font_size=sizes.body, color=Theme.WARNING)
        replay_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))
        replay_box.add(self.message_label)

        replay_box.add(Theme.create_spacer(Theme.SPACE_TIGHT))
        replay_box.add(
            Theme.create_secondary_button(
                "Back",
                lambda: self.shell.show_view("menu"),
                button_width=Theme.BACK_BUTTON_WIDTH,
                font_size=sizes.heading,
            )
        )

        Theme.center_focusable(self.ui, replay_box)

    def watch_replay(self, bot_mode):
        def watch():
            session, message = load_replay_session(self.replay_manager, bot_mode)

            if (session is None):
                self.message_text = message
                self.message_label.text = message
                return

            self.message_text = ""
            self.message_label.text = ""
            self.shell.show_view("replay_playback", session=session, bot_mode=bot_mode)

        return watch

    def on_resize(self, width, height):
        if layout_step(width) != self.current_layout_step:
            self.current_layout_step = layout_step(width)
            self.build_ui()

    def on_update(self, delta_time):
        self.ui.on_update(delta_time)
