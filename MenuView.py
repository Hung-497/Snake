import arcade.gui

import Theme


# Button label -> the App View that button opens, and whether it is the main
# action. Play is the thing people come here to do, so it leads.
MENU_ACTIONS = (
    ("Play", "play", True),
    ("Settings", "settings", False),
    ("Replay", "replay", False),
    ("Records", "records", False),
)


class MenuView(arcade.gui.UIView):
    """
    The Menu App View: the screen the app opens on.

    It only draws the menu and asks the shell to switch App View. It holds no
    Snake rules and no game state.
    """

    def __init__(self, shell):
        super().__init__()
        self.shell = shell
        self.background_color = Theme.SURFACE

        menu_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_UNIT)
        menu_box.add(
            Theme.create_label("Snake Game", font_size=Theme.TYPE_DISPLAY, semibold=True)
        )
        menu_box.add(Theme.create_spacer(Theme.SPACE_TIGHT))
        menu_box.add(
            Theme.create_label(
                "Choose a bot, adjust settings, and compare results",
                font_size=Theme.TYPE_BODY,
                color=Theme.TEXT_MUTED,
            )
        )
        menu_box.add(Theme.create_spacer(Theme.SPACE_SECTION))

        for button_text, view_name, is_primary in MENU_ACTIONS:
            create_button = (
                Theme.create_primary_button if is_primary else Theme.create_secondary_button
            )
            menu_box.add(create_button(button_text, self.open_view(view_name)))
            menu_box.add(Theme.create_spacer(Theme.SPACE_TIGHT))

        Theme.center_focusable(self.ui, menu_box)

    def open_view(self, view_name):
        return lambda: self.shell.show_view(view_name)

    def on_update(self, delta_time):
        # Arcade does not forward frame updates to widgets by itself, and the
        # buttons need them to ease between their states.
        self.ui.on_update(delta_time)
