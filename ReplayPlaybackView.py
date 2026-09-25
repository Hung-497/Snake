import arcade
import arcade.gui
from arcade.types import Color

from BoardRenderer import BoardRenderer
from WindowLayout import HUD_HEIGHT
from PlayView import BOT_MODE_LABELS
from ViewStyle import (
    BACKGROUND_COLOR,
    FONT_NAME,
    MUTED_TEXT_COLOR,
    SECONDARY_BUTTON_COLOR,
    TEXT_COLOR,
    create_button,
)


FINISHED_COLOR = Color.from_hex_string("#FFFFFF")


class ReplayPlaybackView(arcade.gui.UIView):
    """
    The Replay App View while a saved game is playing.

    Arcade's update lifecycle drives the playback, and the ReplaySession knows
    where the snake and food are. Leaving, closing, or reaching the end of the
    replay all stop it.
    """

    def __init__(self, shell, session, bot_mode):
        super().__init__()
        self.shell = shell
        self.session = session
        self.background_color = BACKGROUND_COLOR
        self.board_renderer = BoardRenderer(self.window)

        back_layout = arcade.gui.UIAnchorLayout()
        back_layout.add(
            create_button(
                "Back to Menu",
                self.back_to_menu,
                button_color=SECONDARY_BUTTON_COLOR,
                button_width=200,
            ),
            anchor_x="right",
            anchor_y="bottom",
            align_x=-16,
            align_y=16,
        )
        self.ui.add(back_layout)

        self.score_label = arcade.Text(
            "",
            x=self.window.width / 2,
            y=self.window.height - HUD_HEIGHT + 14,
            color=TEXT_COLOR,
            font_size=22,
            font_name=FONT_NAME,
            anchor_x="center",
        )
        self.bot_mode_label = arcade.Text(
            f"{BOT_MODE_LABELS.get(bot_mode, bot_mode)} replay",
            x=16,
            y=self.window.height - HUD_HEIGHT + 20,
            color=MUTED_TEXT_COLOR,
            font_size=14,
            font_name=FONT_NAME,
        )
        self.finished_label = arcade.Text(
            "Replay Finished",
            x=self.window.width / 2,
            y=self.window.height / 2,
            color=FINISHED_COLOR,
            font_size=44,
            font_name=FONT_NAME,
            anchor_x="center",
            bold=True,
        )
        self.finished_score_label = arcade.Text(
            "",
            x=self.window.width / 2,
            y=self.window.height / 2 - 56,
            color=FINISHED_COLOR,
            font_size=36,
            font_name=FONT_NAME,
            anchor_x="center",
            bold=True,
        )

    def back_to_menu(self):
        self.session.stop()
        self.shell.show_view("menu")

    def on_hide_view(self):
        # Leaving or closing must not leave a replay playing.
        self.session.stop()
        super().on_hide_view()

    def on_update(self, delta_time):
        self.session.advance_by(delta_time)

    def on_draw_before_ui(self):
        self.board_renderer.draw(
            self.session.board_width,
            self.session.board_height,
            self.session.tile_size,
            self.session.snake_position,
            self.session.snake_body,
            self.session.food_position,
        )

        self.score_label.text = (
            f"Score: {self.session.score}   Final: {self.session.final_score}"
        )
        self.score_label.draw()
        self.bot_mode_label.draw()

        if (self.session.finished):
            self.finished_score_label.text = f"Score: {self.session.score}"
            self.finished_label.draw()
            self.finished_score_label.draw()
