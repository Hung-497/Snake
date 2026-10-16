import arcade
import arcade.gui

from snake.ui import Theme
from snake.ui.BoardRenderer import BoardRenderer
from snake.ui.NetworkLayout import (
    LIVE_TRAINING_HUD_HEIGHT, Area, ZoomPan, focus_area, input_labels,
    live_training_minimum_size,
    pan_by, zoom_at,
    live_training_preferred_size, live_training_window,
    screen_containing, side_by_side_areas, tile_size_to_fill,
)
from snake.ui.NetworkRenderer import NetworkRenderer
from snake.ui.PlayerLabels import player_label
from snake.ui.WindowLayout import view_label_positions
from snake.sessions.LiveTraining import (
    DQN_VERSIONS, LiveTrainingCheckpointError, missing_dependency_message,
    start_live_training,
)


# Live mode speeds, in training moves per frame; S cycles through them.
LIVE_SPEEDS = (1, 5, 25, 100)
# Background mode trains for this long each frame. Arcade updates at most 60
# times a second, so a budget of one 60th would leave much of each second idle;
# 50 ms trains close to headless speed and still answers keys about 20 times
# a second.
BACKGROUND_BUDGET_SECONDS = 0.05
PAUSE_KEYS = (arcade.key.P, arcade.key.SPACE)
# Each mouse wheel step zooms the Network focus layout in or out by this factor.
ZOOM_STEP = 1.2
# The layout hint sits on the title line, this far right of the title.
LAYOUT_HINT_GAP = 24
# How far below the stats line the controls line sits.
CONTROLS_GAP = 28


class LiveTrainingView(arcade.gui.UIView):
    """
    The Live Training App View: watch a DQN Bot Mode learn on the board.

    Each DQN version (DQN v2 or DQN v3) trains its own network with its own save.

    This view only draws, keeps time and passes key presses on. Training
    belongs to the Live Training session, which is only loaded when PyTorch
    is installed, so the app still starts without it.
    """

    def __init__(self, shell, settings, bot_mode="dqn"):
        super().__init__()
        self.shell = shell
        self.settings = settings
        self.bot_mode = bot_mode
        self.background_color = Theme.SURFACE
        self.board_renderer = BoardRenderer(self.window)
        self.message = missing_dependency_message()
        self.session = None
        if self.message is None:
            try:
                self.session = start_live_training(settings, bot_mode)
            except LiveTrainingCheckpointError as error:
                self.message = str(error)
        self.background_mode = False
        self.paused = False
        self.speed_index = 0
        self.focus_layout = False
        self.zoom_pan = ZoomPan()
        self.network_renderer = NetworkRenderer(
            Theme.type_sizes(self.window.width).caption,
            input_labels(DQN_VERSIONS[bot_mode].feature_set),
        )

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
            x=positions["bot_mode"][0],
            y=positions["score"][1],
            color=Theme.TEXT,
            font_size=sizes.body,
            font_name=Theme.FONT_REGULAR,
        )
        self.title_label = arcade.Text(
            f"Live Training · {player_label(bot_mode)}",
            x=positions["bot_mode"][0],
            y=positions["bot_mode"][1],
            color=Theme.TEXT_MUTED,
            font_size=sizes.bot_mode,
            font_name=Theme.FONT_REGULAR,
        )
        self.layout_label = arcade.Text(
            "",
            x=positions["bot_mode"][0],
            y=positions["bot_mode"][1],
            color=Theme.TEXT_MUTED,
            font_size=sizes.bot_mode,
            font_name=Theme.FONT_REGULAR,
        )
        self.controls_label = arcade.Text(
            "",
            x=positions["bot_mode"][0],
            y=positions["score"][1] - CONTROLS_GAP,
            color=Theme.TEXT_MUTED,
            font_size=sizes.body,
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

    def on_show_view(self):
        super().on_show_view()
        if self.session is None:
            return
        # Live Training needs room for the graph beside a readable board, so it
        # grows the window and raises the minimum only while it is open.
        config = self.session.config
        current_size = (self.window.width, self.window.height)
        current_location = self.window.get_location()
        # window.screen is the screen the window opened on, not the one it is on now.
        screens = [
            Area(screen.x, screen.y, screen.width, screen.height)
            for screen in self.window.display.get_screens()
        ]
        size, minimum, location = live_training_window(
            size=current_size,
            location=current_location,
            minimum=live_training_minimum_size(config.width, config.height),
            screen=screen_containing(current_location, current_size, screens),
            preferred=live_training_preferred_size(
                config.width, config.height, config.tile_size
            ),
        )
        self.window.set_minimum_size(*minimum)
        if size != (self.window.width, self.window.height):
            self.window.set_size(*size)
            self.window.set_location(*location)

    def on_hide_view(self):
        self.save_progress()
        # Other App Views keep the normal minimum from Settings.
        self.window.update_board_minimum(self.settings.build_game_config())
        super().on_hide_view()

    def save_progress(self):
        """Keep what the bot has learned, so Live Training continues next time."""
        if self.session is not None:
            self.session.save()

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
        elif symbol == arcade.key.N:
            self.focus_layout = not self.focus_layout
        elif symbol == arcade.key.R:
            self.zoom_pan = ZoomPan()

    def graph_focus_area(self):
        return focus_area(self.window.width, self.window.height, LIVE_TRAINING_HUD_HEIGHT)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.session is None or not self.graph_fills_window() or scroll_y == 0:
            return
        factor = ZOOM_STEP if scroll_y > 0 else 1 / ZOOM_STEP
        self.zoom_pan = zoom_at(self.zoom_pan, factor, (x, y), self.graph_focus_area())

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.session is None or not self.graph_fills_window():
            return
        self.zoom_pan = pan_by(self.zoom_pan, dx, dy, self.graph_focus_area())

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
        self.network_renderer.set_font_size(Theme.type_sizes(width).caption)
        positions = view_label_positions(width, height, 60)
        sizes = Theme.type_sizes(width)
        self.back_button.shared_style.font_size = sizes.body
        self.back_button.trigger_full_render()
        self.stats_label.x = positions["bot_mode"][0]
        self.stats_label.y = positions["score"][1]
        self.stats_label.font_size = sizes.body
        self.title_label.x, self.title_label.y = positions["bot_mode"]
        self.title_label.font_size = sizes.bot_mode
        self.layout_label.y = positions["bot_mode"][1]
        self.layout_label.font_size = sizes.bot_mode
        # The graph area changes size, so keep the zoomed graph inside it.
        self.zoom_pan = pan_by(self.zoom_pan, 0, 0, self.graph_focus_area())
        self.controls_label.x = positions["bot_mode"][0]
        self.controls_label.y = positions["score"][1] - CONTROLS_GAP
        self.controls_label.font_size = sizes.body
        self.message_label.x, self.message_label.y = positions["result"]
        self.message_label.width = max(1, width - 2 * Theme.SPACE_WIDE)
        self.message_label.font_size = sizes.body

    def on_draw_before_ui(self):
        if self.session is None:
            self.title_label.draw()
            self.message_label.draw()
            return

        if self.graph_fills_window():
            snapshot = self.session.network_snapshot()
            if snapshot is not None:
                self.network_renderer.draw(snapshot, self.graph_focus_area(), self.zoom_pan)
            # A zoomed graph can reach under the top lines, so cover it there.
            arcade.draw_lbwh_rectangle_filled(
                0, self.window.height - LIVE_TRAINING_HUD_HEIGHT,
                self.window.width, LIVE_TRAINING_HUD_HEIGHT, Theme.SURFACE,
            )
        else:
            state = self.session.engine.state
            graph_area, board_area = side_by_side_areas(
                self.window.width, self.window.height, LIVE_TRAINING_HUD_HEIGHT,
            )
            self.board_renderer.draw(
                state.board_width,
                state.board_height,
                tile_size_to_fill(board_area, state.board_width, state.board_height),
                state.snake_position,
                state.snake_body,
                state.food_position,
                area=board_area,
            )
            snapshot = self.session.network_snapshot()
            if snapshot is not None:
                self.network_renderer.draw(snapshot, graph_area)
        self.title_label.draw()
        self.layout_label.x = self.title_label.x + self.title_label.content_width + LAYOUT_HINT_GAP
        self.layout_label.text = self.layout_text()
        self.layout_label.draw()
        stats = self.session.stats()
        self.stats_label.text = (
            f"Game {stats.games_played + 1}  Score: {stats.score}  "
            f"Best: {stats.best_score}  Avg: {stats.average_score:.1f}  "
            f"Epsilon: {stats.epsilon:.3f}"
        )
        self.stats_label.draw()
        self.controls_label.text = self.controls_text()
        self.controls_label.draw()

    def graph_fills_window(self):
        """Background mode and the Network focus layout both hide the board."""
        return self.background_mode or self.focus_layout

    def layout_text(self):
        if not self.graph_fills_window():
            return "N network focus"
        zoom = f"zoom {self.zoom_pan.zoom:.1f}x \u00b7 wheel zoom \u00b7 drag pan \u00b7 R reset"
        if self.background_mode:
            return zoom
        return f"Network focus \u00b7 {zoom} \u00b7 N board"

    def controls_text(self):
        if self.background_mode:
            mode = "Background training \u00b7 B for Live"
        else:
            mode = f"Live \u00b7 {LIVE_SPEEDS[self.speed_index]}x \u00b7 S speed \u00b7 B for Background"
        if self.paused:
            return f"Paused \u00b7 P or Space to resume \u00b7 {mode}"
        return f"{mode} \u00b7 P pause"
