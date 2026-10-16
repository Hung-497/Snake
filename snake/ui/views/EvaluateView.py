import arcade
import arcade.gui

from snake.sessions.EvaluationSession import (
    STUDY_GAMES, start_dqn_evaluation, start_q_learning_evaluation,
)
from snake.sessions.LiveTraining import DQN_VERSIONS, missing_dependency_message
from snake.sessions.TrainingSaves import SHOWCASE_BOTS
from snake.ui import Theme
from snake.ui.BoardRenderer import BoardRenderer
from snake.ui.PlayerLabels import player_label
from snake.ui.WindowLayout import view_label_positions


# Room at the top for the title, progress, and controls lines.
EVALUATE_HUD_HEIGHT = 100
# Fast mode plays for this long each frame, like Live Training's Background.
FAST_BUDGET_SECONDS = 0.05
WATCH_KEY = arcade.key.W
# How far below the progress line the controls line sits.
CONTROLS_GAP = 28


class EvaluateView(arcade.gui.UIView):
    """
    The Evaluate App View: measure a learning Bot Mode on the study's games.

    The bot plays in Evaluation Mode, so nothing it plays changes its save.
    It runs fast by default; W shows the game being played, and both give
    the same result. A finished run is saved as a Bot Experiment report, and
    leaving early saves nothing. This view only draws, keeps time, and passes
    key presses on; the games and the report belong to the EvaluationSession.
    """

    def __init__(self, shell, bot_mode, game_count, source="training"):
        super().__init__()
        self.shell = shell
        self.bot_mode = bot_mode
        self.background_color = Theme.SURFACE
        self.board_renderer = BoardRenderer(self.window, hud_height=EVALUATE_HUD_HEIGHT)
        self.watching = False
        self.message = None
        self.session = None
        is_dqn = bot_mode in DQN_VERSIONS
        # Evaluating a DQN needs PyTorch, like Live Training (ADR 0007).
        if is_dqn:
            self.message = missing_dependency_message()
        if self.message is None:
            try:
                self.session = self.start_session(bot_mode, game_count, source, is_dqn)
            except ValueError as error:
                self.message = f"{error}\nTrain it first, or start new training."

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
        board = STUDY_GAMES.config
        self.title_label = arcade.Text(
            f"Evaluate · {player_label(bot_mode)} ({self.source_text(bot_mode, source)}) · "
            f"{board.width} × {board.height} board, like the study",
            x=0, y=0, color=Theme.TEXT_MUTED,
            font_size=sizes.bot_mode, font_name=Theme.FONT_REGULAR,
        )
        self.progress_label = arcade.Text(
            "", x=0, y=0, color=Theme.TEXT,
            font_size=sizes.body, font_name=Theme.FONT_REGULAR,
        )
        self.controls_label = arcade.Text(
            "", x=0, y=0, color=Theme.TEXT_MUTED,
            font_size=sizes.body, font_name=Theme.FONT_REGULAR,
        )
        self.centre_label = arcade.Text(
            self.message or "", x=0, y=0, color=Theme.TEXT,
            font_size=sizes.body, font_name=Theme.FONT_REGULAR,
            anchor_x="center", anchor_y="center", multiline=True,
            width=max(1, self.window.width - 2 * Theme.SPACE_WIDE), align="center",
        )
        self.on_resize(self.window.width, self.window.height)

    @staticmethod
    def start_session(bot_mode, game_count, source, is_dqn):
        if is_dqn and source == "showcase":
            return start_dqn_evaluation(
                bot_mode, game_count, model_path=SHOWCASE_BOTS[bot_mode].path,
                evaluated="showcase",
            )
        if is_dqn:
            return start_dqn_evaluation(bot_mode, game_count)
        if source == "showcase":
            return start_q_learning_evaluation(
                bot_mode, game_count, table_path=SHOWCASE_BOTS[bot_mode].path,
                evaluated="showcase",
            )
        return start_q_learning_evaluation(bot_mode, game_count)

    @staticmethod
    def source_text(bot_mode, source):
        if source == "showcase":
            return f"showcase, seed {SHOWCASE_BOTS[bot_mode].seed}"
        return "your training"

    def back_to_menu(self):
        # Nothing is saved for an unfinished run, so leaving simply stops it.
        self.shell.show_view("menu")

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.back_to_menu()
        elif symbol == WATCH_KEY and self.session is not None:
            self.watching = not self.watching

    def on_update(self, delta_time):
        self.ui.on_update(delta_time)
        if self.session is None or self.session.finished:
            return
        if self.watching:
            self.session.make_move()
        else:
            self.session.make_moves_for(FAST_BUDGET_SECONDS)

    def on_resize(self, width, height):
        positions = view_label_positions(width, height, 60)
        sizes = Theme.type_sizes(width)
        self.back_button.shared_style.font_size = sizes.body
        self.back_button.trigger_full_render()
        left = positions["bot_mode"][0]
        top = height - EVALUATE_HUD_HEIGHT
        self.title_label.x, self.title_label.y = left, top + 70
        # The title shrinks to stay clear of Back to Menu in a narrow window.
        Theme.fit_text_to_width(
            self.title_label, sizes.bot_mode,
            width - left - Theme.HUD_BUTTON_WIDTH - 3 * Theme.SPACE_TIGHT,
        )
        self.progress_label.x, self.progress_label.y = left, top + 40
        self.progress_label.font_size = sizes.body
        self.controls_label.x, self.controls_label.y = left, top + 40 - CONTROLS_GAP
        self.controls_label.font_size = sizes.body
        self.centre_label.x, self.centre_label.y = positions["result"]
        self.centre_label.width = max(1, width - 2 * Theme.SPACE_WIDE)
        self.centre_label.font_size = sizes.body

    def on_draw_before_ui(self):
        self.title_label.draw()
        if self.session is None:
            self.centre_label.draw()
            return

        if self.watching:
            engine = self.session.engine
            state = engine.state
            self.board_renderer.draw(
                state.board_width, state.board_height, state.tile_size,
                state.snake_position, state.snake_body, state.food_position,
            )
        else:
            self.centre_label.text = self.centre_text()
            self.centre_label.draw()

        progress = self.session.progress()
        self.progress_label.text = (
            f"Game {min(progress.games_done + 1, progress.game_count)} / {progress.game_count}"
            f"   Avg {progress.average_score:.1f}   Best {progress.best_score}"
            f"   Move limit: {progress.move_limits}"
        )
        self.progress_label.draw()
        self.controls_label.text = self.controls_text()
        self.controls_label.draw()

    def centre_text(self):
        progress = self.session.progress()
        if self.session.finished:
            return (
                f"Finished: {progress.game_count} games\n"
                f"Average {progress.average_score:.1f} · Best {progress.best_score} · "
                f"{progress.move_limits} stopped at the move limit\n"
                f"Saved {self.session.report_path}"
            )
        return f"Evaluating fast: {progress.games_done} of {progress.game_count} games done"

    def controls_text(self):
        if self.session.finished:
            return "Finished · W to see the last game"
        if self.watching:
            return "Watching · W for fast"
        return "Fast · W to watch"
