import arcade.gui

from ViewStyle import (
    BACKGROUND_COLOR,
    center_in_view,
    create_button,
    create_muted_label,
    create_title_label,
)


# Button label -> the App View that button opens. App Views that are not
# registered with the shell yet simply do nothing when their button is pressed.
MENU_ACTIONS = (
    ("Play", "play"),
    ("Settings", "settings"),
    ("Replay", "replay"),
    ("Records", "records"),
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
        self.background_color = BACKGROUND_COLOR

        menu_box = arcade.gui.UIBoxLayout(space_between=9)
        menu_box.add(create_title_label("Snake Game"))
        menu_box.add(create_muted_label("Choose a bot, adjust settings, and compare results"))

        for button_text, view_name in MENU_ACTIONS:
            menu_box.add(create_button(button_text, self.open_view(view_name)))

        center_in_view(self.ui, menu_box)

    def open_view(self, view_name):
        return lambda: self.shell.show_view(view_name)
