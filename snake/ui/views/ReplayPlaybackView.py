import arcade
import arcade.gui

from snake.ui import Theme
from snake.ui.BoardRenderer import BoardRenderer
from snake.ui.WindowLayout import view_label_positions
from snake.ui.PlayerLabels import player_label


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
        self.background_color = Theme.SURFACE
        self.board_renderer = BoardRenderer(self.window)

        sizes = Theme.type_sizes(self.window.width)
        back_layout = arcade.gui.UIAnchorLayout()
        self.back_button = Theme.create_secondary_button(
            "Back to Menu",
            self.back_to_menu,
            button_width=Theme.HUD_BUTTON_WIDTH,
            button_height=Theme.HUD_BUTTON_HEIGHT,
            font_size=sizes.body,
        )
        back_layout.add(
            self.back_button,
            anchor_x="right",
            anchor_y="top",
            align_x=-Theme.SPACE_TIGHT,
            align_y=-Theme.SPACE_TIGHT,
        )
        self.ui.add(back_layout)

        positions = view_label_positions(self.window.width, self.window.height, 56)
        self.score_label = arcade.Text(
            "",
            x=positions["score"][0],
            y=positions["score"][1],
            color=Theme.TEXT,
            font_size=sizes.game_score,
            font_name=Theme.FONT_REGULAR,
            anchor_x="center",
        )
        self.bot_mode_label = arcade.Text(
            f"{player_label(bot_mode)} replay",
            x=positions["bot_mode"][0],
            y=positions["bot_mode"][1],
            color=Theme.TEXT_MUTED,
            font_size=sizes.bot_mode,
            font_name=Theme.FONT_REGULAR,
        )
        self.finished_label = arcade.Text(
            "Replay Finished",
            x=positions["result"][0],
            y=positions["result"][1],
            color=Theme.TEXT,
            font_size=sizes.replay_result,
            font_name=Theme.FONT_SEMIBOLD,
            anchor_x="center",
        )
        self.finished_score_label = arcade.Text(
            "",
            x=positions["result_score"][0],
            y=positions["result_score"][1],
            color=Theme.TEXT,
            font_size=sizes.replay_result_score,
            font_name=Theme.FONT_SEMIBOLD,
            anchor_x="center",
        )
        self.fit_result_labels()

    def fit_result_labels(self):
        board_width = self.board_renderer.board_layout(
            self.session.board_width, self.session.board_height, self.session.tile_size
        ).width
        sizes = Theme.type_sizes(self.window.width)
        available_width = board_width - Theme.SPACE_WIDE
        Theme.fit_text_to_width(self.finished_label, sizes.replay_result,
                                available_width)
        Theme.fit_text_to_width(self.finished_score_label, sizes.replay_result_score,
                                available_width)

    def back_to_menu(self):
        self.session.stop()
        self.shell.show_view("menu")

    def on_hide_view(self):
        # Leaving or closing must not leave a replay playing.
        self.session.stop()
        super().on_hide_view()

    def on_update(self, delta_time):
        self.ui.on_update(delta_time)
        self.session.advance_by(delta_time)

    def on_resize(self, width, height):
        positions = view_label_positions(width, height, 56)
        sizes = Theme.type_sizes(width)
        self.back_button.shared_style.font_size = sizes.body
        self.back_button.trigger_full_render()
        self.score_label.x, self.score_label.y = positions["score"]
        self.score_label.font_size = sizes.game_score
        self.bot_mode_label.x, self.bot_mode_label.y = positions["bot_mode"]
        self.bot_mode_label.font_size = sizes.bot_mode
        self.finished_label.x, self.finished_label.y = positions["result"]
        self.finished_label.font_size = sizes.replay_result
        self.finished_score_label.x, self.finished_score_label.y = positions["result_score"]
        self.finished_score_label.font_size = sizes.replay_result_score
        self.fit_result_labels()

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
            score_text = f"Score: {self.session.score}"
            if self.finished_score_label.text != score_text:
                self.finished_score_label.text = score_text
                self.fit_result_labels()
            self.finished_label.draw()
            self.finished_score_label.draw()
