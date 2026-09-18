import arcade.gui

from ViewStyle import (
    BACKGROUND_COLOR,
    OPTION_COLOR,
    SECONDARY_BUTTON_COLOR,
    center_in_view,
    create_button,
    create_button_style,
    create_muted_label,
    create_title_label,
)


OPTION_WIDTH = 280
OPTION_HEIGHT = 42


class SettingsView(arcade.gui.UIView):
    """
    The Settings App View: choose board size, tile size and game speed.

    The choices themselves live in SessionSettings, which outlives this view, so
    leaving and reopening Settings shows the values that were picked earlier.
    This view only displays the options and reports the user's choice.
    """

    def __init__(self, shell, settings):
        super().__init__()
        self.shell = shell
        self.settings = settings
        self.background_color = BACKGROUND_COLOR

        settings_box = arcade.gui.UIBoxLayout(space_between=4)
        settings_box.add(create_title_label("Settings", font_size=46))
        settings_box.add(arcade.gui.UISpace(height=20, color=BACKGROUND_COLOR))

        self.add_option_row(
            settings_box,
            "Game Speed",
            settings.speed_names(),
            settings.selected_speed_name,
            settings.select_speed,
        )
        self.add_option_row(
            settings_box,
            "Board Size",
            settings.board_size_names(),
            settings.selected_board_size_name,
            settings.select_board_size,
        )
        self.add_option_row(
            settings_box,
            "Tile Size",
            settings.tile_size_names(),
            settings.selected_tile_size_name,
            settings.select_tile_size,
        )

        settings_box.add(arcade.gui.UISpace(height=18, color=BACKGROUND_COLOR))
        settings_box.add(
            create_button(
                "Back",
                lambda: self.shell.show_view("menu"),
                button_color=SECONDARY_BUTTON_COLOR,
                button_width=170,
            )
        )

        center_in_view(self.ui, settings_box)

    def add_option_row(self, settings_box, label_text, option_names, selected_name, select_option):
        """One labelled dropdown, matching the option boxes the old menu used."""
        settings_box.add(create_muted_label(label_text, font_size=16, bold=True))

        dropdown = arcade.gui.UIDropdown(
            default=selected_name,
            options=list(option_names),
            width=OPTION_WIDTH,
            height=OPTION_HEIGHT,
            primary_style=create_button_style(OPTION_COLOR, font_size=16),
            dropdown_style=create_button_style(OPTION_COLOR, font_size=15),
            active_style=create_button_style(font_size=15),
        )
        # The dropdown reports the newly chosen option name; the settings object
        # is what decides whether that option is one the app offers.
        dropdown.on_change = lambda event: select_option(event.new_value)
        settings_box.add(dropdown)

        settings_box.add(arcade.gui.UISpace(height=10, color=BACKGROUND_COLOR))

        return dropdown
