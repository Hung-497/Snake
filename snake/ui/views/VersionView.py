import arcade.gui

from snake.ui import Theme
from snake.ui.PlayerLabels import LEARNING_FAMILIES, VERSION_DESCRIPTIONS
from snake.ui.WindowLayout import layout_step


class VersionView(arcade.gui.UIView):
    """
    The Choose a version App View: pick the Feature Set version of a learning
    Bot Mode family, each with one line saying what that version sees.

    Play and Replay both open it. The screen that opened it decides what a
    version does through `choose`, which returns a message to show here when
    it cannot go ahead (for example, a replay that is not saved yet), and how
    to go back through `back`.
    """

    def __init__(self, shell, family, choose, back):
        super().__init__()
        self.shell = shell
        self.family = LEARNING_FAMILIES[family]
        self.choose = choose
        self.back = back
        self.background_color = Theme.SURFACE
        self.message_text = ""
        self.current_layout_step = layout_step(self.window.width)
        self.build_ui()

    def build_ui(self):
        self.ui.clear()
        sizes = Theme.type_sizes(self.window.width)
        version_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_TIGHT)
        version_box.add(Theme.create_label(self.family.label,
                                           font_size=sizes.display, semibold=True))
        version_box.add(Theme.create_label("Choose a version",
                                           font_size=sizes.body, color=Theme.TEXT_MUTED))
        version_box.add(Theme.create_spacer(Theme.SPACE_SECTION))

        for version, bot_mode in self.family.versions.items():
            version_box.add(Theme.create_primary_button(
                f"{self.family.label} {version}", self.choose_version(bot_mode),
                font_size=sizes.heading,
            ))
            version_box.add(Theme.create_label(VERSION_DESCRIPTIONS[version],
                                               font_size=sizes.body, color=Theme.TEXT_MUTED))
            version_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))

        self.message_label = Theme.create_label(self.message_text,
                                                font_size=sizes.body, color=Theme.WARNING)
        version_box.add(self.message_label)

        version_box.add(Theme.create_spacer(Theme.SPACE_TIGHT))
        version_box.add(
            Theme.create_secondary_button(
                "Back",
                self.back,
                button_width=Theme.BACK_BUTTON_WIDTH,
                font_size=sizes.heading,
            )
        )

        Theme.center_focusable(self.ui, version_box)

    def choose_version(self, bot_mode):
        def choose():
            message = self.choose(bot_mode)
            if message:
                self.message_text = message
                self.message_label.text = message

        return choose

    def on_resize(self, width, height):
        if layout_step(width) != self.current_layout_step:
            self.current_layout_step = layout_step(width)
            self.build_ui()

    def on_update(self, delta_time):
        # Arcade does not forward frame updates to widgets by itself, and the
        # buttons need them to ease between their states.
        self.ui.on_update(delta_time)
