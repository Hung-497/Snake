import arcade.gui

from snake.ui import Theme
from snake.ui.PlayerLabels import player_label
from snake.ui.WindowLayout import layout_step


class TrainingStartView(arcade.gui.UIView):
    """
    The Start Live Training App View: continue a DQN's saved Live Training,
    or start it over from game 0.

    Play opens it only when the chosen DQN already has a save. Start new opens
    the Set up training App View, where the old save becomes a backup.
    """

    def __init__(self, shell, bot_mode, summary, back):
        super().__init__()
        self.shell = shell
        self.bot_mode = bot_mode
        self.summary = summary
        self.back = back
        self.background_color = Theme.SURFACE
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

        start_box.add(Theme.create_primary_button("Continue training", self.continue_training,
                                                  font_size=sizes.heading))
        start_box.add(Theme.create_primary_button("Start new training", self.start_new_training,
                                                  font_size=sizes.heading))
        start_box.add(Theme.create_label("The old training is kept as a backup.",
                                         font_size=sizes.body, color=Theme.TEXT_MUTED))

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

    def summary_text(self):
        if self.summary.games is None:
            return "Saved training (could not be read)"
        text = f"Saved training: {self.summary.games} games"
        if self.summary.best_score is not None:
            text += f", best {self.summary.best_score}"
        if self.summary.game_limit is not None:
            text += f", stops at {self.summary.game_limit}"
        return text

    def continue_training(self):
        self.shell.show_view("live_training", bot_mode=self.bot_mode)

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
