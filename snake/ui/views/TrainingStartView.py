import arcade.gui

from snake.sessions.EvaluationSession import GAME_COUNTS
from snake.sessions.TrainingSaves import SHOWCASE_BOTS, backup_summary
from snake.ui import Theme
from snake.ui.PlayerLabels import app_view_for_bot_mode, player_label
from snake.ui.WindowLayout import layout_step


class TrainingStartView(arcade.gui.UIView):
    """
    The Start training App View for a learning Bot Mode, in two parts.

    Your training: continue the saved training, start it over from game 0,
    or measure it with Evaluate. Showcase bot: evaluate the finished study
    bot shipped with the app (ADR 0017). Evaluate first asks how many of the
    study's games to play.

    Play always opens it for DQN and Q Learning, even with no training yet.
    Start new opens the Set up training App View, where the old save becomes
    a backup. A save that cannot be read can only be started over, so it is
    never overwritten. summary is None when there is no save.
    """

    def __init__(self, shell, bot_mode, summary, back):
        super().__init__()
        self.shell = shell
        self.bot_mode = bot_mode
        self.summary = summary
        self.backups = backup_summary(bot_mode)
        self.back = back
        self.background_color = Theme.SURFACE
        # While Evaluate asks how many games to play, this names what is
        # evaluated ("training" or "showcase"); None shows the usual buttons.
        self.evaluating = None
        self.current_layout_step = layout_step(self.window.width)
        self.build_ui()

    def build_ui(self):
        self.ui.clear()
        sizes = Theme.type_sizes(self.window.width)
        start_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_TIGHT)
        start_box.add(Theme.create_label(player_label(self.bot_mode),
                                         font_size=sizes.display, semibold=True))
        start_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))

        if self.evaluating is not None:
            self.add_game_count_choice(start_box, sizes)
        else:
            self.add_training_choices(start_box, sizes)
            self.add_showcase_choice(start_box, sizes)

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
        start_box.add(Theme.create_label(self.summary_text(),
                                         font_size=sizes.body, color=Theme.TEXT_MUTED))
        start_box.add(Theme.create_label(self.backup_text(),
                                         font_size=sizes.caption, color=Theme.TEXT_MUTED))
        if self.has_readable_save():
            start_box.add(Theme.create_primary_button("Continue training",
                                                      self.continue_training,
                                                      font_size=sizes.heading))
            start_box.add(Theme.create_primary_button("Evaluate",
                                                      self.choose_game_count("training"),
                                                      font_size=sizes.heading))
        start_box.add(Theme.create_primary_button("Start new training", self.start_new_training,
                                                  font_size=sizes.heading))
        if self.summary is not None:
            start_box.add(Theme.create_label("The old training is kept as a backup.",
                                             font_size=sizes.caption, color=Theme.TEXT_MUTED))

    def add_showcase_choice(self, start_box, sizes):
        showcase = SHOWCASE_BOTS.get(self.bot_mode)
        if showcase is None:
            return
        start_box.add(Theme.create_spacer(Theme.SPACE_SECTION))
        start_box.add(Theme.create_label(f"Showcase bot: {showcase.label}",
                                         font_size=sizes.body, color=Theme.TEXT_MUTED))
        start_box.add(Theme.create_primary_button("Evaluate showcase",
                                                  self.choose_game_count("showcase"),
                                                  font_size=sizes.heading))

    def add_game_count_choice(self, start_box, sizes):
        what = "the showcase bot" if self.evaluating == "showcase" else "your training"
        start_box.add(Theme.create_label(f"Evaluate {what} on how many of the study's games?",
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

    def has_readable_save(self):
        return self.summary is not None and self.summary.games is not None

    def choose_game_count(self, evaluating):
        def choose():
            self.evaluating = evaluating
            self.build_ui()

        return choose

    def cancel_game_count(self):
        self.evaluating = None
        self.build_ui()

    def evaluate(self, game_count):
        return lambda: self.shell.show_view(
            "evaluate", bot_mode=self.bot_mode, game_count=game_count,
            source=self.evaluating,
        )

    def summary_text(self):
        if self.summary is None:
            return "Your training: none yet"
        if self.summary.games is None:
            return "Your training: the save could not be read"
        text = f"Your training: {self.summary.games} games"
        if self.summary.best_score is not None:
            text += f", best {self.summary.best_score}"
        if self.summary.game_limit is not None:
            text += f", stops at {self.summary.game_limit}"
        return text

    def backup_text(self):
        if self.backups.unreadable_count:
            return f"Saved backups: {self.backups.count} readable · Some sizes unavailable"
        megabytes = self.backups.total_bytes / (1024 * 1024)
        return f"Saved backups: {self.backups.count} · {megabytes:.2f} MB"

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
