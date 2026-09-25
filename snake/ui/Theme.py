"""
The app's design tokens, and the widgets that use them.

Everything visual is named by role here — surface, primary, text — rather than
by appearance, so changing the look means changing a token instead of hunting
through every App View.
"""

import os
from dataclasses import dataclass

import arcade
import arcade.gui
from arcade.gui.experimental.focus import FocusMode, UIFocusGroup
from arcade.types import Color

from snake.ui.WindowLayout import layout_step


# --- Fonts -----------------------------------------------------------------
# Inter is bundled with the project so macOS, Windows and Linux all render the
# same text. Asking for a system font instead means each platform substitutes
# whatever it happens to have.
# Theme lives under snake/ui; bundled fonts stay at the repository root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONT_DIR = os.path.join(PROJECT_ROOT, "assets", "fonts")
FONT_REGULAR = "Inter"
# The bold face registers under its own family name, so it is chosen by name
# rather than by asking for bold.
FONT_SEMIBOLD = "Inter SemiBold"

_fonts_loaded = False


def load_fonts():
    """Register the bundled fonts. Safe to call more than once."""
    global _fonts_loaded

    if _fonts_loaded:
        return

    for file_name in ("Inter-Regular.ttf", "Inter-SemiBold.ttf"):
        arcade.load_font(os.path.join(FONT_DIR, file_name))

    _fonts_loaded = True


load_fonts()


# --- Colour tokens ---------------------------------------------------------
SURFACE = Color.from_hex_string("#0A1628")
SURFACE_RAISED = Color.from_hex_string("#12243D")
BORDER = Color.from_hex_string("#1E3A5F")

PRIMARY = Color.from_hex_string("#3B82F6")
PRIMARY_HOVER = Color.from_hex_string("#60A5FA")
PRIMARY_PRESS = Color.from_hex_string("#1D4ED8")

SECONDARY = Color.from_hex_string("#24374F")
SECONDARY_HOVER = Color.from_hex_string("#314966")
SECONDARY_PRESS = Color.from_hex_string("#1B2A3C")

DISABLED = Color.from_hex_string("#1A2537")

TEXT = Color.from_hex_string("#EAF2FF")
TEXT_MUTED = Color.from_hex_string("#8FA3BF")
TEXT_DISABLED = Color.from_hex_string("#54657E")
WARNING = Color.from_hex_string("#FF9B9B")

# The Board Area has its own roles so Game and Replay use the same palette.
BOARD_BACKGROUND = Color.from_hex_string("#0D2035")
BOARD_GRID = Color.from_hex_string("#1C344B")
BOARD_FRAME = Color.from_hex_string("#52718E")
BOARD_FLASH = Color.from_hex_string("#D6F29B")
SNAKE_BODY = Color.from_hex_string("#2EAA82")
SNAKE_HEAD = Color.from_hex_string("#D6F29B")
FOOD = Color.from_hex_string("#FF7575")
BOARD_GRID_WIDTH = 1
BOARD_FRAME_WIDTH = 2


# --- Type scale ------------------------------------------------------------
TYPE_DISPLAY = 44
TYPE_TITLE = 28
TYPE_HEADING = 20
TYPE_BODY = 15
TYPE_CAPTION = 12


@dataclass(frozen=True)
class TypeSizes:
    display: int
    title: int
    heading: int
    body: int
    caption: int
    game_score: int
    bot_mode: int
    game_result: int
    game_result_score: int
    replay_result: int
    replay_result_score: int


REGULAR_TYPE_SIZES = TypeSizes(44, 28, 20, 15, 12, 18, 14, 54, 40, 44, 36)
COMPACT_TYPE_SIZES = TypeSizes(34, 24, 18, 14, 11, 16, 12, 40, 30, 30, 28)


def type_sizes(window_width):
    """Return the shared type scale for the window's layout step."""
    return (COMPACT_TYPE_SIZES if layout_step(window_width) == "compact"
            else REGULAR_TYPE_SIZES)


def fit_text_to_width(label, preferred_font_size, available_width):
    """Keep a result overlay inside its Board Area, including small boards."""
    label.font_size = preferred_font_size
    while label.text and label.content_width > available_width and label.font_size > 1:
        label.font_size -= 1


# --- Spacing ---------------------------------------------------------------
# Everything is a multiple of one base unit, so the rhythm stays even.
SPACE_UNIT = 4
SPACE_TIGHT = SPACE_UNIT * 2
SPACE_CONTROL = SPACE_UNIT * 3
SPACE_INNER = SPACE_UNIT * 4
SPACE_SECTION = SPACE_UNIT * 6
SPACE_WIDE = SPACE_UNIT * 8


# --- Controls --------------------------------------------------------------
BUTTON_WIDTH = 260
BUTTON_HEIGHT = 52
BACK_BUTTON_WIDTH = 170
OPTION_WIDTH = 280
OPTION_HEIGHT = 42
FILTER_BUTTON_WIDTH = 150
FILTER_BUTTON_HEIGHT = 38
PAGE_BUTTON_WIDTH = 120
PAGE_BUTTON_HEIGHT = 34
HUD_BUTTON_WIDTH = 150
HUD_BUTTON_HEIGHT = 38
# How long a button takes to settle into its new colour. Short enough to feel
# immediate, long enough to read as a response rather than a jump.
STATE_EASE_SECONDS = 0.09


def blend_color(from_color, to_color, amount):
    """Mix two colours. An amount of 0 is the first colour, 1 the second."""
    amount = max(0.0, min(1.0, amount))

    return Color(
        round(from_color.r + (to_color.r - from_color.r) * amount),
        round(from_color.g + (to_color.g - from_color.g) * amount),
        round(from_color.b + (to_color.b - from_color.b) * amount),
        255,
    )


class ThemedButton(arcade.gui.UIFlatButton):
    """
    A button whose background eases between states instead of snapping.

    Arcade swaps a whole style when a button is hovered or pressed, which reads
    as a jump. This keeps one style and moves its colour towards the state's
    colour a little each frame, so the control feels like it is responding.
    """

    def __init__(
        self,
        button_text,
        on_click,
        base_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        press_color=PRIMARY_PRESS,
        button_width=BUTTON_WIDTH,
        button_height=BUTTON_HEIGHT,
        font_size=TYPE_HEADING,
    ):
        self.base_color = base_color
        self.hover_color = hover_color
        self.press_color = press_color
        self.shown_color = base_color

        style = arcade.gui.UIFlatButton.UIStyle(
            font_size=font_size,
            font_name=FONT_SEMIBOLD,
            font_color=TEXT,
            bg=base_color,
            border=None,
            border_width=0,
        )
        # Every state shares one style object, because this widget decides the
        # colour itself rather than letting the state pick a different style.
        self.shared_style = style

        super().__init__(
            text=button_text,
            width=button_width,
            height=button_height,
            style={state: style for state in ("normal", "hover", "press", "disabled")},
        )

        self.focus_mode = FocusMode.ALL
        self.on_click = lambda event: on_click()

    def target_color(self):
        if (self.disabled):
            return DISABLED
        if (self.pressed):
            return self.press_color
        if (self.hovered):
            return self.hover_color

        return self.base_color

    def on_update(self, dt):
        target = self.target_color()

        if (self.shown_color == target):
            return

        self.shown_color = blend_color(self.shown_color, target, dt / STATE_EASE_SECONDS)

        # Stop once the difference stops being visible, so the button settles
        # instead of redrawing forever.
        if (max(abs(self.shown_color[i] - target[i]) for i in range(3)) <= 2):
            self.shown_color = target

        self.shared_style.bg = self.shown_color
        self.trigger_full_render()

    def do_render_focus(self, surface):
        """
        Draw the keyboard focus ring.

        The ring is near-white rather than an accent colour, because it has to
        be equally visible on a blue primary button and a navy secondary one.
        """
        self.prepare_render(surface)
        arcade.draw_lbwh_rectangle_outline(
            0, 0, self.content_width, self.content_height, TEXT, 2
        )


def create_primary_button(button_text, on_click, **kwargs):
    return ThemedButton(button_text, on_click, **kwargs)


def create_secondary_button(button_text, on_click, **kwargs):
    return ThemedButton(
        button_text,
        on_click,
        base_color=SECONDARY,
        hover_color=SECONDARY_HOVER,
        press_color=SECONDARY_PRESS,
        **kwargs,
    )


def create_dropdown_style(base_color=SECONDARY, hover_color=SECONDARY_HOVER,
                          press_color=SECONDARY_PRESS, font_size=TYPE_BODY):
    """Give dropdown buttons the same four clear states as Menu controls."""
    style = arcade.gui.UIFlatButton.UIStyle
    shared = dict(font_size=font_size, font_name=FONT_SEMIBOLD, border=None,
                  border_width=0)
    return {
        "normal": style(bg=base_color, font_color=TEXT, **shared),
        "hover": style(bg=hover_color, font_color=TEXT, **shared),
        "press": style(bg=press_color, font_color=TEXT, **shared),
        "disabled": style(bg=DISABLED, font_color=TEXT_DISABLED, **shared),
    }


def create_label(text, font_size=TYPE_BODY, color=TEXT, semibold=False):
    return arcade.gui.UILabel(
        text=text,
        font_name=FONT_SEMIBOLD if semibold else FONT_REGULAR,
        font_size=font_size,
        text_color=color,
    )


def create_spacer(height):
    return arcade.gui.UISpace(height=height, color=SURFACE)


class FocusGroup(UIFocusGroup):
    """
    A focus group that lets keyboard navigation actually start.

    Arcade's own group ignores Tab while nothing is focused yet, so a keyboard
    user can never reach the first control. This focuses it on the first Tab.
    """

    def on_event(self, event):
        starting_navigation = (
            self.focused_widget is None
            and isinstance(event, arcade.gui.UIKeyPressEvent)
            and event.symbol == arcade.key.TAB
            # No public way to ask whether anything is focusable, and this is
            # already the one place that touches the experimental focus API.
            and self._focusable_widgets
        )

        if (starting_navigation):
            self.set_focus()
            return True

        return super().on_event(event)


def center_focusable(ui_manager, widget):
    """
    Centre a widget and make everything inside it reachable by keyboard.

    UIFocusGroup comes from Arcade's experimental package and is documented as
    going away once focus moves into UILayout, so it is used only here: when it
    changes, this is the one place to fix.
    """
    focus_group = FocusGroup()
    focus_group.add(widget, anchor_x="center", anchor_y="center")
    ui_manager.add(focus_group)
    focus_group.detect_focusable_widgets()

    return focus_group
