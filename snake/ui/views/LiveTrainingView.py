import arcade
import arcade.gui

from snake.ui import Theme
from snake.ui.BoardRenderer import BoardRenderer
from snake.ui.WindowLayout import view_label_positions
from snake.sessions.LiveTraining import missing_dependency_message, start_live_training


# Live mode speeds, in training moves per frame; S cycles through them.
LIVE_SPEEDS = (1, 5, 25, 100)
# Background mode trains for this long each frame. Arcade updates at most 60
# times a second, so a budget of one 60th would leave much of each second idle;
# 50 ms trains close to headless speed and still answers keys about 20 times
# a second.
BACKGROUND_BUDGET_SECONDS = 0.05
PAUSE_KEYS = (arcade.key.P, arcade.key.SPACE)
# How far below the stats line the controls line sits.
CONTROLS_GAP = 28


class LiveTrainingView(arcade.gui.UIView):
    """
    The Live Training App View: watch a DQN Bot Mode learn on the board.

    This view only draws, keeps time and passes key presses on. Training
    belongs to the Live Training session, which is only loaded when PyTorch
    is installed, so the app still starts without it.
    """

    def __init__(self, shell, settings):
        super().__init__()
        self.shell = shell
        self.background_color = Theme.SURFACE
        self.board_renderer = BoardRenderer(self.window)
        self.message = missing_dependency_message()
        self.session = None if self.message else start_live_training(settings)
        self.background_mode = False
        self.paused = False
        self.speed_index = 0

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

        # Text objects are reused because drawing new text every frame is slow.
        positions = view_label_positions(self.window.width, self.window.height, 60)
        self.stats_label = arcade.Text(
            "",
            x=positions["score"][0],
            y=positions["score"][1],
            color=Theme.TEXT,
            font_size=sizes.body,
            font_name=Theme.FONT_REGULAR,
            anchor_x="center",
        )
        self.title_label = arcade.Text(
            "Live Training · DQN",
            x=positions["bot_mode"][0],
            y=positions["bot_mode"][1],
            color=Theme.TEXT_MUTED,
            font_size=sizes.bot_mode,
            font_name=Theme.FONT_REGULAR,
        )
        self.controls_label = arcade.Text(
            "",
            x=positions["score"][0],
            y=positions["score"][1] - CONTROLS_GAP,
            color=Theme.TEXT_MUTED,
            font_size=sizes.body,
            font_name=Theme.FONT_REGULAR,
            anchor_x="center",
        )
        self.message_label = arcade.Text(
            self.message or "",
            x=positions["result"][0],
            y=positions["result"][1],
            color=Theme.TEXT,
            font_size=sizes.body,
            font_name=Theme.FONT_REGULAR,
            anchor_x="center",
            anchor_y="center",
            multiline=True,
            width=max(1, self.window.width - 2 * Theme.SPACE_WIDE),
            align="center",
        )

    def back_to_menu(self):
        self.shell.show_view("menu")

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.back_to_menu()
        elif self.session is None:
            return
        elif symbol == arcade.key.B:
            self.background_mode = not self.background_mode
        elif symbol in PAUSE_KEYS:
            self.paused = not self.paused
        elif symbol == arcade.key.S:
            self.speed_index = (self.speed_index + 1) % len(LIVE_SPEEDS)

    def on_update(self, delta_time):
        self.ui.on_update(delta_time)
        if self.session is None or self.paused:
            return
        if self.background_mode:
            self.session.make_moves_for(BACKGROUND_BUDGET_SECONDS)
        else:
            for _ in range(LIVE_SPEEDS[self.speed_index]):
                self.session.make_move()

    def on_resize(self, width, height):
        positions = view_label_positions(width, height, 60)
        sizes = Theme.type_sizes(width)
        self.back_button.shared_style.font_size = sizes.body
        self.back_button.trigger_full_render()
        self.stats_label.x, self.stats_label.y = positions["score"]
        self.stats_label.font_size = sizes.body
        self.title_label.x, self.title_label.y = positions["bot_mode"]
        self.title_label.font_size = sizes.bot_mode
        self.controls_label.x = positions["score"][0]
        self.controls_label.y = positions["score"][1] - CONTROLS_GAP
        self.controls_label.font_size = sizes.body
        self.message_label.x, self.message_label.y = positions["result"]
        self.message_label.width = max(1, width - 2 * Theme.SPACE_WIDE)
        self.message_label.font_size = sizes.body

    def on_draw_before_ui(self):
        self.title_label.draw()
        if self.session is None:
            self.message_label.draw()
            return

        if not self.background_mode:
            state = self.session.engine.state
            self.board_renderer.draw(
                state.board_width,
                state.board_height,
                state.tile_size,
                state.snake_position,
                state.snake_body,
                state.food_position,
            )
        stats = self.session.stats()
        self.stats_label.text = (
            f"Game {stats.games_played + 1}  Score: {stats.score}  "
            f"Best: {stats.best_score}  Avg: {stats.average_score:.1f}  "
            f"Epsilon: {stats.epsilon:.3f}"
        )
        self.stats_label.draw()
        self.controls_label.text = self.controls_text()
        self.controls_label.draw()

    def controls_text(self):
        if self.background_mode:
            mode = "Background training \u00b7 B for Live"
        else:
            mode = f"Live \u00b7 {LIVE_SPEEDS[self.speed_index]}x \u00b7 S speed \u00b7 B for Background"
        if self.paused:
            return f"Paused \u00b7 P or Space to resume \u00b7 {mode}"
        return f"{mode} \u00b7 P pause"
