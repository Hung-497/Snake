import arcade
import arcade.gui

from snake.ui import Theme
from snake.ui.BoardRenderer import BoardRenderer
from snake.ui.WindowLayout import HUD_HEIGHT, view_label_positions
from snake.ui.PlayerLabels import player_label


# The same pause keys as Human Play, so both App Views feel alike.
PAUSE_KEYS = (arcade.key.P, arcade.key.SPACE)
RESTART_KEY = arcade.key.R
SPEED_KEY = arcade.key.S

# The playback controls get their own row under the score line, because at the
# minimum window width there is no room for them beside the score.
CONTROLS_ROW_TOP = HUD_HEIGHT + Theme.SPACE_TIGHT
CONTROLS_ROW_WIDTH = 3 * Theme.HUD_BUTTON_WIDTH + 2 * Theme.SPACE_TIGHT
# A thin progress row sits under the controls, as wide as the controls row.
PROGRESS_ROW_TOP = CONTROLS_ROW_TOP + Theme.HUD_BUTTON_HEIGHT + Theme.SPACE_TIGHT
PROGRESS_ROW_HEIGHT = 18
PROGRESS_BAR_HEIGHT = 6
REPLAY_HUD_HEIGHT = PROGRESS_ROW_TOP + PROGRESS_ROW_HEIGHT + Theme.SPACE_TIGHT


class ReplayPlaybackView(arcade.gui.UIView):
    """
    The Replay App View while a saved game is playing.

    Arcade's update lifecycle drives the playback, and the ReplaySession knows
    where the snake and food are. Leaving, closing, or reaching the end of the
    replay all stop it. This view only turns buttons and keys into session
    calls, such as pausing.
    """

    def __init__(self, shell, session, player):
        super().__init__()
        self.shell = shell
        self.session = session
        self.background_color = Theme.SURFACE
        self.board_renderer = BoardRenderer(self.window, hud_height=REPLAY_HUD_HEIGHT)

        sizes = Theme.type_sizes(self.window.width)
        self.pause_button = Theme.create_secondary_button(
            "Pause",
            self.toggle_pause,
            button_width=Theme.HUD_BUTTON_WIDTH,
            button_height=Theme.HUD_BUTTON_HEIGHT,
            font_size=sizes.body,
        )
        self.restart_button = Theme.create_secondary_button(
            "Restart",
            self.restart,
            button_width=Theme.HUD_BUTTON_WIDTH,
            button_height=Theme.HUD_BUTTON_HEIGHT,
            font_size=sizes.body,
        )
        self.speed_button = Theme.create_secondary_button(
            self.speed_button_text(),
            self.cycle_speed,
            button_width=Theme.HUD_BUTTON_WIDTH,
            button_height=Theme.HUD_BUTTON_HEIGHT,
            font_size=sizes.body,
        )
        self.back_button = Theme.create_secondary_button(
            "Back to Menu",
            self.back_to_menu,
            button_width=Theme.HUD_BUTTON_WIDTH,
            button_height=Theme.HUD_BUTTON_HEIGHT,
            font_size=sizes.body,
        )
        hud_layout = arcade.gui.UIAnchorLayout()
        hud_layout.add(
            self.back_button,
            anchor_x="right",
            anchor_y="top",
            align_x=-Theme.SPACE_TIGHT,
            align_y=-Theme.SPACE_TIGHT,
        )
        controls_row = arcade.gui.UIBoxLayout(vertical=False,
                                              space_between=Theme.SPACE_TIGHT)
        controls_row.add(self.pause_button)
        controls_row.add(self.restart_button)
        controls_row.add(self.speed_button)
        hud_layout.add(
            controls_row,
            anchor_x="center",
            anchor_y="top",
            align_y=-CONTROLS_ROW_TOP,
        )
        self.ui.add(hud_layout)

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
            f"{player_label(player)} replay",
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
        self.paused_label = arcade.Text(
            "Paused \u00b7 P or Space to resume",
            x=positions["result"][0],
            y=positions["result"][1],
            color=Theme.TEXT,
            font_size=sizes.body,
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
        self.progress_label = arcade.Text(
            "",
            x=0,
            y=0,
            color=Theme.TEXT_MUTED,
            font_size=sizes.body,
            font_name=Theme.FONT_REGULAR,
            anchor_y="center",
        )
        self.fit_result_labels()
        self.layout_progress()

    def layout_progress(self):
        """Place the "Move X / N" label and work out where the bar goes."""
        row_left = (self.window.width - CONTROLS_ROW_WIDTH) / 2
        self.progress_center_y = (
            self.window.height - PROGRESS_ROW_TOP - PROGRESS_ROW_HEIGHT / 2
        )
        self.progress_label.x = row_left
        self.progress_label.y = self.progress_center_y

        # Measure the widest the label can get, so the bar never jumps sideways
        # when the move count gains a digit.
        total = self.session.total_moves
        self.progress_label.text = f"Move {total} / {total}"
        self.progress_bar_left = row_left + self.progress_label.content_width + Theme.SPACE_TIGHT
        self.progress_bar_right = row_left + CONTROLS_ROW_WIDTH
        self.progress_label.text = ""

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
        Theme.fit_text_to_width(self.paused_label, sizes.body, available_width)

    def back_to_menu(self):
        self.session.stop()
        self.shell.show_view("menu")

    def toggle_pause(self):
        self.session.toggle_pause()
        self.update_pause_button()

    def restart(self):
        self.session.restart()
        self.update_pause_button()

    def cycle_speed(self):
        self.session.cycle_speed()
        self.speed_button.text = self.speed_button_text()

    def speed_button_text(self):
        return f"Speed: {self.session.speed_name}"

    def update_pause_button(self):
        # The button names the action it will take next.
        self.pause_button.text = "Resume" if self.session.paused else "Pause"

    def on_key_press(self, symbol, modifiers):
        if (symbol in PAUSE_KEYS):
            self.toggle_pause()
        elif (symbol == RESTART_KEY):
            self.restart()
        elif (symbol == SPEED_KEY):
            self.cycle_speed()

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
        for button in (self.pause_button, self.restart_button, self.speed_button,
                       self.back_button):
            button.shared_style.font_size = sizes.body
            button.trigger_full_render()
        self.score_label.x, self.score_label.y = positions["score"]
        self.score_label.font_size = sizes.game_score
        self.bot_mode_label.x, self.bot_mode_label.y = positions["bot_mode"]
        self.bot_mode_label.font_size = sizes.bot_mode
        self.finished_label.x, self.finished_label.y = positions["result"]
        self.finished_label.font_size = sizes.replay_result
        self.finished_score_label.x, self.finished_score_label.y = positions["result_score"]
        self.finished_score_label.font_size = sizes.replay_result_score
        self.paused_label.x, self.paused_label.y = positions["result"]
        self.paused_label.font_size = sizes.body
        self.progress_label.font_size = sizes.body
        self.fit_result_labels()
        self.layout_progress()

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
        self.draw_progress()

        if (self.session.finished):
            score_text = f"Score: {self.session.score}"
            if self.finished_score_label.text != score_text:
                self.finished_score_label.text = score_text
                self.fit_result_labels()
            self.finished_label.draw()
            self.finished_score_label.draw()
        elif (self.session.paused):
            self.paused_label.draw()

    def draw_progress(self):
        played = self.session.moves_played
        total = self.session.total_moves

        progress_text = f"Move {played} / {total}"
        if self.progress_label.text != progress_text:
            self.progress_label.text = progress_text
        self.progress_label.draw()

        bar_bottom = self.progress_center_y - PROGRESS_BAR_HEIGHT / 2
        bar_top = bar_bottom + PROGRESS_BAR_HEIGHT
        arcade.draw_lrbt_rectangle_filled(self.progress_bar_left, self.progress_bar_right,
                                          bar_bottom, bar_top, Theme.BORDER)

        if (total > 0 and played > 0):
            filled_right = self.progress_bar_left + (
                (self.progress_bar_right - self.progress_bar_left) * played / total
            )
            arcade.draw_lrbt_rectangle_filled(self.progress_bar_left, filled_right,
                                              bar_bottom, bar_top, Theme.PRIMARY)
