from dataclasses import replace

import arcade.gui
from arcade.types import Color


# The App Views keep the colours the CustomTkinter menu already used, so the
# app still looks like itself after moving to Arcade.
BACKGROUND_COLOR = Color.from_hex_string("#071A2D")
BUTTON_COLOR = Color.from_hex_string("#2F80ED")
BUTTON_HOVER_COLOR = Color.from_hex_string("#56CCF2")
BUTTON_PRESS_COLOR = Color.from_hex_string("#1D4ED8")
SECONDARY_BUTTON_COLOR = Color.from_hex_string("#334155")
OPTION_COLOR = Color.from_hex_string("#0E2A47")
TEXT_COLOR = Color.from_hex_string("#F2F7FF")
MUTED_TEXT_COLOR = Color.from_hex_string("#A8B3C7")
WARNING_TEXT_COLOR = Color.from_hex_string("#FCA5A5")

FONT_NAME = ("Arial", "Helvetica")
BUTTON_WIDTH = 230
BUTTON_HEIGHT = 48


def create_button_style(button_color=BUTTON_COLOR, font_size=22):
    """One shared style so every button in the app looks the same."""
    normal_style = arcade.gui.UIFlatButton.UIStyle(
        font_size=font_size,
        font_name=FONT_NAME,
        font_color=TEXT_COLOR,
        bg=button_color,
        border=None,
        border_width=0,
    )

    return {
        "normal": normal_style,
        "hover": replace(normal_style, bg=BUTTON_HOVER_COLOR),
        "press": replace(normal_style, bg=BUTTON_PRESS_COLOR),
        "disabled": normal_style,
    }


def create_button(
    button_text,
    on_click,
    button_color=BUTTON_COLOR,
    button_width=BUTTON_WIDTH,
    button_height=BUTTON_HEIGHT,
    font_size=22,
):
    button = arcade.gui.UIFlatButton(
        text=button_text,
        width=button_width,
        height=button_height,
        style=create_button_style(button_color, font_size=font_size),
    )
    button.on_click = lambda event: on_click()

    return button


def create_title_label(text, font_size=52):
    return arcade.gui.UILabel(
        text=text,
        font_name=FONT_NAME,
        font_size=font_size,
        bold=True,
        text_color=TEXT_COLOR,
    )


def create_text_label(text, font_size=13, bold=False):
    return arcade.gui.UILabel(
        text=text,
        font_name=FONT_NAME,
        font_size=font_size,
        bold=bold,
        text_color=TEXT_COLOR,
    )


def create_muted_label(text, font_size=15, bold=False):
    return arcade.gui.UILabel(
        text=text,
        font_name=FONT_NAME,
        font_size=font_size,
        bold=bold,
        text_color=MUTED_TEXT_COLOR,
    )


def center_in_view(ui_manager, widget):
    """Keep a widget centred whatever the window size is."""
    centered_layout = arcade.gui.UIAnchorLayout()
    centered_layout.add(widget, anchor_x="center", anchor_y="center")
    ui_manager.add(centered_layout)
