import arcade.gui

from snake.sessions.LiveTraining import TRAINING_LIMITS, start_over
from snake.ui import Theme
from snake.ui.PlayerLabels import player_label
from snake.ui.WindowLayout import layout_step


class TrainingSetupView(arcade.gui.UIView):
    """
    The Set up training App View: choose a game limit, then start a new Live
    Training from game 0.

    The limit is saved with the training, so continuing it later stops at the
    same limit. Any old save is moved to a backup only when training starts,
    so going Back from here changes nothing.
    """

    def __init__(self, shell, bot_mode, back):
        super().__init__()
        self.shell = shell
        self.bot_mode = bot_mode
        self.back = back
        self.background_color = Theme.SURFACE
        self.selected_limit_name = next(iter(TRAINING_LIMITS))
        self.current_layout_step = layout_step(self.window.width)
        self.build_ui()

    def build_ui(self):
        self.ui.clear()
        sizes = Theme.type_sizes(self.window.width)
        setup_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_TIGHT)
        setup_box.add(Theme.create_label(player_label(self.bot_mode),
                                         font_size=sizes.display, semibold=True))
        setup_box.add(Theme.create_label("Start new training from game 0",
                                         font_size=sizes.body, color=Theme.TEXT_MUTED))
        setup_box.add(Theme.create_spacer(Theme.SPACE_SECTION))

        setup_box.add(Theme.create_label("Training Limit", font_size=sizes.body,
                                         color=Theme.TEXT_MUTED, semibold=True))
        limit_dropdown = arcade.gui.UIDropdown(
            default=self.selected_limit_name,
            options=list(TRAINING_LIMITS),
            width=Theme.OPTION_WIDTH,
            height=Theme.OPTION_HEIGHT,
            primary_style=Theme.create_dropdown_style(font_size=sizes.body),
            dropdown_style=Theme.create_dropdown_style(font_size=sizes.body),
            active_style=Theme.create_dropdown_style(
                Theme.PRIMARY, Theme.PRIMARY_HOVER, Theme.PRIMARY_PRESS,
                font_size=sizes.body,
            ),
        )
        limit_dropdown.on_change = self.change_limit
        setup_box.add(limit_dropdown)
        # Epsilon reaches its floor after about 1000 games, so that is when
        # exploring ends and the bot mostly uses what it learned.
        setup_box.add(Theme.create_label(
            "Training stops after this many games. Exploring ends near game 1000.",
            font_size=sizes.caption, color=Theme.TEXT_MUTED,
        ))
        setup_box.add(Theme.create_spacer(Theme.SPACE_SECTION))

        setup_box.add(Theme.create_primary_button("Start training", self.start_training,
                                                  font_size=sizes.heading))

        setup_box.add(Theme.create_spacer(Theme.SPACE_TIGHT))
        setup_box.add(
            Theme.create_secondary_button(
                "Back",
                self.back,
                button_width=Theme.BACK_BUTTON_WIDTH,
                font_size=sizes.heading,
            )
        )

        Theme.center_focusable(self.ui, setup_box)

    def change_limit(self, event):
        self.selected_limit_name = event.new_value

    def start_training(self):
        # With any old save moved to a backup, Live Training starts at game 0.
        start_over(self.bot_mode)
        self.shell.show_view(
            "live_training", bot_mode=self.bot_mode,
            game_limit=TRAINING_LIMITS[self.selected_limit_name],
        )

    def on_resize(self, width, height):
        if layout_step(width) != self.current_layout_step:
            self.current_layout_step = layout_step(width)
            self.build_ui()

    def on_update(self, delta_time):
        # Arcade does not forward frame updates to widgets by itself, and the
        # buttons need them to ease between their states.
        self.ui.on_update(delta_time)
