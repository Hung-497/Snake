import arcade.gui

from snake.sessions.EvaluationSession import GAME_COUNTS
from snake.sessions.TrainingSaves import APP_Q_TABLES
from snake.ui import Theme
from snake.ui.PlayerLabels import app_view_for_bot_mode, player_label
from snake.ui.WindowLayout import layout_step


class TrainingStartView(arcade.gui.UIView):
    """
    The Start training App View: continue a learning Bot Mode's saved
    training, or start it over from game 0.

    Q Learning training can also be measured with Evaluate, after choosing
    how many of the study's games to play (ADR 0017).

    Play opens it only when the chosen DQN or Q Learning already has a save.
    Start new opens the Set up training App View, where the old save becomes
    a backup. A save that cannot be read can only be started over, so it is
    never overwritten.
    """

    def __init__(self, shell, bot_mode, summary, back):
        super().__init__()
        self.shell = shell
        self.bot_mode = bot_mode
        self.summary = summary
        self.back = back
        self.background_color = Theme.SURFACE
        # Evaluate first asks how many games to play, in place of the buttons.
        self.choosing_game_count = False
        self.current_layout_step = layout_step(self.window.width)
        self.build_ui()

    def build_ui(self):
        self.ui.clear()
        sizes = Theme.type_sizes(self.window.width)
        start_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_TIGHT)
        start_box.add(Theme.create_label(player_label(self.bot_mode),
                                         font_size=sizes.display, semibold=True))
        start_box.add(Theme.create_label(self.summary_text(),
                                         font_size=sizes.body, color=Theme.TEXT_MUTED))
        start_box.add(Theme.create_spacer(Theme.SPACE_SECTION))

        if self.choosing_game_count:
            self.add_game_count_choice(start_box, sizes)
        else:
            self.add_training_choices(start_box, sizes)

        start_box.add(Theme.create_spacer(Theme.SPACE_TIGHT))
        start_box.add(
            Theme.create_secondary_button(
                "Back",
                self.back,
                button_width=Theme.BACK_BUTTON_WIDTH,
                font_size=sizes.heading,
            )
        )

        Theme.center_focusable(self.ui, start_box)

    def add_training_choices(self, start_box, sizes):
        if self.summary.games is not None:
            start_box.add(Theme.create_primary_button("Continue training",
                                                      self.continue_training,
                                                      font_size=sizes.heading))
        start_box.add(Theme.create_primary_button("Start new training", self.start_new_training,
                                                  font_size=sizes.heading))
        start_box.add(Theme.create_label("The old training is kept as a backup.",
                                         font_size=sizes.body, color=Theme.TEXT_MUTED))
        if self.can_evaluate():
            start_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))
            start_box.add(Theme.create_primary_button("Evaluate", self.choose_game_count,
                                                      font_size=sizes.heading))
            start_box.add(Theme.create_label(
                "Measure it on the study's games, without learning.",
                font_size=sizes.body, color=Theme.TEXT_MUTED,
            ))

    def add_game_count_choice(self, start_box, sizes):
        start_box.add(Theme.create_label("How many of the study's games?",
                                         font_size=sizes.body, color=Theme.TEXT_MUTED))
        quick, full = GAME_COUNTS
        start_box.add(Theme.create_primary_button(f"{quick} games (quick)",
                                                  self.evaluate(quick),
                                                  font_size=sizes.heading))
        start_box.add(Theme.create_primary_button(f"{full} games (like the study)",
                                                  self.evaluate(full),
                                                  font_size=sizes.heading))
        start_box.add(Theme.create_secondary_button(
            "Cancel", self.cancel_game_count,
            button_width=Theme.BACK_BUTTON_WIDTH, font_size=sizes.heading,
        ))

    def can_evaluate(self):
        # DQN Evaluate comes later; only a readable save can be measured.
        return self.bot_mode in APP_Q_TABLES and self.summary.games is not None

    def choose_game_count(self):
        self.choosing_game_count = True
        self.build_ui()

    def cancel_game_count(self):
        self.choosing_game_count = False
        self.build_ui()

    def evaluate(self, game_count):
        return lambda: self.shell.show_view(
            "evaluate", bot_mode=self.bot_mode, game_count=game_count,
        )

    def summary_text(self):
        if self.summary.games is None:
            return "Saved training could not be read"
        text = f"Saved training: {self.summary.games} games"
        if self.summary.best_score is not None:
            text += f", best {self.summary.best_score}"
        if self.summary.game_limit is not None:
            text += f", stops at {self.summary.game_limit}"
        return text

    def continue_training(self):
        self.shell.show_view(app_view_for_bot_mode(self.bot_mode), bot_mode=self.bot_mode)

    def start_new_training(self):
        self.shell.show_view(
            "training_setup", bot_mode=self.bot_mode,
            back=lambda: self.shell.show_view(
                "training_start", bot_mode=self.bot_mode, summary=self.summary,
                back=self.back,
            ),
        )

    def on_resize(self, width, height):
        if layout_step(width) != self.current_layout_step:
            self.current_layout_step = layout_step(width)
            self.build_ui()

    def on_update(self, delta_time):
        # Arcade does not forward frame updates to widgets by itself, and the
        # buttons need them to ease between their states.
        self.ui.on_update(delta_time)
