import arcade
import arcade.gui

from snake.ui import Theme
from snake.ui.BoardRenderer import BoardRenderer
from snake.ui.WindowLayout import view_label_positions
from snake.sessions.GameSession import GameSession
from snake.ui.MotionRules import board_effects_enabled, end_flash_alpha, food_pulse_scale
from snake.ui.views.PlayView import BOT_MODE_LABELS
from snake.engine.SnakeEngine import SnakeEngine


GAME_OVER_COLOR = Theme.WARNING
GAME_WON_COLOR = Theme.SNAKE_HEAD


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
        self.background_color = Theme.SURFACE
        self.board_renderer = BoardRenderer(self.window)

        game_config = settings.build_game_config()
        engine = SnakeEngine(game_config, start_position=None)
        self.session = GameSession(engine, bot_mode, settings.speed_delay)
        self.session.start()
        self.effects_enabled = board_effects_enabled(settings.speed_delay)
        self.motion_seconds = 0.0
        self.flash_started_at = None

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

        # Arcade warns that drawing text every frame is slow, so the lines that
        # change are kept as Text objects and only their contents are updated.
        positions = view_label_positions(self.window.width, self.window.height, 60)
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
            BOT_MODE_LABELS.get(bot_mode, bot_mode),
            x=positions["bot_mode"][0],
            y=positions["bot_mode"][1],
            color=Theme.TEXT_MUTED,
            font_size=sizes.bot_mode,
            font_name=Theme.FONT_REGULAR,
        )
        self.result_label = arcade.Text(
            "",
            x=positions["result"][0],
            y=positions["result"][1],
            color=GAME_OVER_COLOR,
            font_size=sizes.game_result,
            font_name=Theme.FONT_SEMIBOLD,
            anchor_x="center",
        )
        self.result_score_label = arcade.Text(
            "",
            x=positions["result_score"][0],
            y=positions["result_score"][1],
            color=GAME_OVER_COLOR,
            font_size=sizes.game_result_score,
            font_name=Theme.FONT_SEMIBOLD,
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
        self.ui.on_update(delta_time)
        self.motion_seconds += delta_time
        games_before_update = self.session.games_played
        self.session.advance_by(delta_time)

        if self.effects_enabled and self.session.games_played > games_before_update:
            self.flash_started_at = self.motion_seconds

    def on_resize(self, width, height):
        positions = view_label_positions(width, height, 60)
        sizes = Theme.type_sizes(width)
        self.back_button.shared_style.font_size = sizes.body
        self.back_button.trigger_full_render()
        self.score_label.x, self.score_label.y = positions["score"]
        self.score_label.font_size = sizes.game_score
        self.bot_mode_label.x, self.bot_mode_label.y = positions["bot_mode"]
        self.bot_mode_label.font_size = sizes.bot_mode
        self.result_label.x, self.result_label.y = positions["result"]
        self.result_label.font_size = sizes.game_result
        self.result_score_label.x, self.result_score_label.y = positions["result_score"]
        self.result_score_label.font_size = sizes.game_result_score
        self.fit_result_labels()

    def fit_result_labels(self):
        state = self.session.state
        board_width = self.board_renderer.board_layout(
            state.board_width, state.board_height, state.tile_size
        ).width
        sizes = Theme.type_sizes(self.window.width)
        available_width = board_width - Theme.SPACE_WIDE
        Theme.fit_text_to_width(self.result_label, sizes.game_result, available_width)
        Theme.fit_text_to_width(self.result_score_label, sizes.game_result_score,
                                available_width)

    def on_draw_before_ui(self):
        state = self.session.state
        food_scale = 1.0
        flash_alpha = 0

        if self.effects_enabled:
            if not self.session.game_over:
                food_scale = food_pulse_scale(self.motion_seconds)
            if self.flash_started_at is not None:
                flash_alpha = end_flash_alpha(self.motion_seconds - self.flash_started_at)

        self.board_renderer.draw(
            state.board_width,
            state.board_height,
            state.tile_size,
            state.snake_position,
            state.snake_body,
            state.food_position,
            food_scale=food_scale,
            flash_alpha=flash_alpha,
        )
        self.draw_score_line()

        if (self.session.result_text is not None):
            self.draw_result()

    def draw_score_line(self):
        self.score_label.text = (
            f"Score: {self.session.score}  "
            f"Match: {self.session.games_played}  "
            f"Best: {self.session.best_score}"
        )
        self.score_label.draw()
        self.bot_mode_label.draw()

    def draw_result(self):
        result_color = GAME_WON_COLOR if self.session.game_won else GAME_OVER_COLOR

        result_text = self.session.result_text
        score_text = f"Your score: {self.session.score}"
        if self.result_label.text != result_text or self.result_score_label.text != score_text:
            self.result_label.text = result_text
            self.result_score_label.text = score_text
            self.fit_result_labels()
        self.result_label.color = result_color
        self.result_score_label.color = result_color

        self.result_label.draw()
        self.result_score_label.draw()
