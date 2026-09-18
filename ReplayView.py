import arcade.gui

from PlayView import BOT_MODE_LABELS
from ReplayManager import ReplayManager
from ReplaySession import load_replay_session
from ViewStyle import (
    BACKGROUND_COLOR,
    SECONDARY_BUTTON_COLOR,
    WARNING_TEXT_COLOR,
    center_in_view,
    create_button,
    create_muted_label,
    create_title_label,
)


class ReplayView(arcade.gui.UIView):
    """
    The Replay App View: choose which Bot Mode's saved replay to watch.

    A replay that is missing or cannot be trusted keeps the user here with an
    explanation, so nothing unreadable is ever drawn as if it were a game.
    """

    def __init__(self, shell, replay_manager=None):
        super().__init__()
        self.shell = shell
        self.replay_manager = ReplayManager() if replay_manager is None else replay_manager
        self.background_color = BACKGROUND_COLOR

        replay_box = arcade.gui.UIBoxLayout(space_between=9)
        replay_box.add(create_title_label("Watch a Replay", font_size=46))
        replay_box.add(create_muted_label("The best saved game for each Bot Mode"))
        replay_box.add(arcade.gui.UISpace(height=20, color=BACKGROUND_COLOR))

        for bot_mode, button_text in BOT_MODE_LABELS.items():
            replay_box.add(create_button(button_text, self.watch_replay(bot_mode)))

        self.message_label = create_muted_label("", font_size=15)
        self.message_label.update_font(font_color=WARNING_TEXT_COLOR)
        replay_box.add(arcade.gui.UISpace(height=10, color=BACKGROUND_COLOR))
        replay_box.add(self.message_label)

        replay_box.add(arcade.gui.UISpace(height=8, color=BACKGROUND_COLOR))
        replay_box.add(
            create_button(
                "Back",
                lambda: self.shell.show_view("menu"),
                button_color=SECONDARY_BUTTON_COLOR,
                button_width=170,
            )
        )

        center_in_view(self.ui, replay_box)

    def watch_replay(self, bot_mode):
        def watch():
            session, message = load_replay_session(self.replay_manager, bot_mode)

            if (session is None):
                self.message_label.text = message
                return

            self.message_label.text = ""
            self.shell.show_view("replay_playback", session=session, bot_mode=bot_mode)

        return watch
