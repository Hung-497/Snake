import arcade
import arcade.gui

from snake.ui import Theme
from snake.ui.BoardRenderer import BoardRenderer
from snake.ui.WindowLayout import view_label_positions
from snake.sessions.LiveTraining import missing_dependency_message, start_live_training


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

    def on_update(self, delta_time):
        self.ui.on_update(delta_time)
        if self.session is not None:
            # Live mode: one training move per frame.
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
        self.message_label.x, self.message_label.y = positions["result"]
        self.message_label.width = max(1, width - 2 * Theme.SPACE_WIDE)
        self.message_label.font_size = sizes.body

    def on_draw_before_ui(self):
        self.title_label.draw()
        if self.session is None:
            self.message_label.draw()
            return

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
