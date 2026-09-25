import arcade
import arcade.gui
from arcade.types import Color

from BoardRenderer import BoardRenderer
from WindowLayout import HUD_HEIGHT
from GameSession import GameSession
from PlayView import BOT_MODE_LABELS
from SnakeEngine import SnakeEngine
from ViewStyle import (
    BACKGROUND_COLOR,
    FONT_NAME,
    MUTED_TEXT_COLOR,
    SECONDARY_BUTTON_COLOR,
    TEXT_COLOR,
    create_button,
)


GAME_OVER_COLOR = Color.from_hex_string("#FF5555")
GAME_WON_COLOR = Color.from_hex_string("#FFFF00")


class GameView(arcade.gui.UIView):
    """
    The Game App View: watch a Bot Mode play repeated games.

    This view only draws and keeps time. Every Snake rule stays in the Game
    Engine, and the score, match count, records and replays belong to the
    GameSession it drives.
    """

    def __init__(self, shell, settings, bot_mode):
        super().__init__()
        self.shell = shell
        self.background_color = BACKGROUND_COLOR
        self.board_renderer = BoardRenderer(self.window)

        game_config = settings.build_game_config()
        engine = SnakeEngine(game_config, start_position=None)
        self.session = GameSession(engine, bot_mode, settings.speed_delay)
        self.session.start()

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

        # Arcade warns that drawing text every frame is slow, so the lines that
        # change are kept as Text objects and only their contents are updated.
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
            BOT_MODE_LABELS.get(bot_mode, bot_mode),
            x=16,
            y=self.window.height - HUD_HEIGHT + 20,
            color=MUTED_TEXT_COLOR,
            font_size=14,
            font_name=FONT_NAME,
        )
        self.result_label = arcade.Text(
            "",
            x=self.window.width / 2,
            y=self.window.height / 2,
            color=GAME_OVER_COLOR,
            font_size=54,
            font_name=FONT_NAME,
            anchor_x="center",
        )
        self.result_score_label = arcade.Text(
            "",
            x=self.window.width / 2,
            y=self.window.height / 2 - 60,
            color=GAME_OVER_COLOR,
            font_size=40,
            font_name=FONT_NAME,
            anchor_x="center",
        )

    def back_to_menu(self):
        self.session.stop()
        self.shell.show_view("menu")

    def on_hide_view(self):
        # Leaving or closing the Game App View must not leave games running.
        self.session.stop()
        super().on_hide_view()

    def on_update(self, delta_time):
        self.session.advance_by(delta_time)

    def on_draw_before_ui(self):
        state = self.session.state

        self.board_renderer.draw(
            state.board_width,
            state.board_height,
            state.tile_size,
            state.snake_position,
            state.snake_body,
            state.food_position,
        )
        self.draw_score_line()

        if (self.session.result_text is not None):
            self.draw_result()

    def draw_score_line(self):
        self.score_label.text = (
            f"Score: {self.session.score}   "
            f"Match: {self.session.games_played}   "
            f"Best: {self.session.best_score}"
        )
        self.score_label.draw()
        self.bot_mode_label.draw()

    def draw_result(self):
        result_color = GAME_WON_COLOR if self.session.game_won else GAME_OVER_COLOR

        self.result_label.text = self.session.result_text
        self.result_label.color = result_color
        self.result_score_label.text = f"Your score: {self.session.score}"
        self.result_score_label.color = result_color

        self.result_label.draw()
        self.result_score_label.draw()
