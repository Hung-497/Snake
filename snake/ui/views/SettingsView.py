import arcade.gui

from snake.ui import Theme
from snake.ui.WindowLayout import layout_step


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
        self.background_color = Theme.SURFACE
        self.current_layout_step = layout_step(self.window.width)
        self.build_ui()

    def build_ui(self):
        self.ui.clear()
        sizes = Theme.type_sizes(self.window.width)
        settings = self.settings
        settings_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_UNIT)
        settings_box.add(Theme.create_label("Settings", font_size=sizes.display,
                                            semibold=True))
        settings_box.add(Theme.create_spacer(Theme.SPACE_SECTION))

        self.add_option_row(
            settings_box,
            "Game Speed",
            settings.speed_names(),
            settings.selected_speed_name,
            settings.select_speed,
            sizes,
        )
        self.add_option_row(
            settings_box,
            "Board Size",
            settings.board_size_names(),
            settings.selected_board_size_name,
            settings.select_board_size,
            sizes,
        )
        self.add_option_row(
            settings_box,
            "Tile Size",
            settings.tile_size_names(),
            settings.selected_tile_size_name,
            settings.select_tile_size,
            sizes,
        )
        settings_box.add(Theme.create_label(
            "Preferred size; the board scales down to fit the window.",
            font_size=sizes.caption,
            color=Theme.TEXT_MUTED,
        ))

        settings_box.add(Theme.create_spacer(Theme.SPACE_SECTION))
        settings_box.add(
            Theme.create_secondary_button(
                "Back",
                lambda: self.shell.show_view("menu"),
                button_width=Theme.BACK_BUTTON_WIDTH,
                font_size=sizes.heading,
            )
        )

        Theme.center_focusable(self.ui, settings_box)

    def add_option_row(self, settings_box, label_text, option_names, selected_name,
                       select_option, sizes):
        """One labelled dropdown for a session setting."""
        settings_box.add(Theme.create_label(label_text, font_size=sizes.body,
                                             color=Theme.TEXT_MUTED,
                                             semibold=True))

        dropdown = arcade.gui.UIDropdown(
            default=selected_name,
            options=list(option_names),
            width=Theme.OPTION_WIDTH,
            height=Theme.OPTION_HEIGHT,
            primary_style=Theme.create_dropdown_style(font_size=sizes.body),
            dropdown_style=Theme.create_dropdown_style(font_size=sizes.body),
            active_style=Theme.create_dropdown_style(
                Theme.PRIMARY, Theme.PRIMARY_HOVER, Theme.PRIMARY_PRESS,
                font_size=sizes.body,
            ),
        )
        # The dropdown reports the newly chosen option name; the settings object
        # is what decides whether that option is one the app offers.
        dropdown.on_change = lambda event: self.change_setting(
            select_option, event.new_value
        )
        settings_box.add(dropdown)

        settings_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))

        return dropdown

    def change_setting(self, select_option, value):
        select_option(value)
        self.shell.window.update_board_minimum(self.settings.build_game_config())

    def on_resize(self, width, height):
        if layout_step(width) != self.current_layout_step:
            self.current_layout_step = layout_step(width)
            self.build_ui()

    def on_update(self, delta_time):
        self.ui.on_update(delta_time)
