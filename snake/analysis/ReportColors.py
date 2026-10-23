"""The colours Bot Reports use: the app's dark board palette and Player colours.

Each Bot Mode's colours come from the Bot Mode catalogue, which the app's
Records Analytics reads too, so a bot looks the same in the app and in a
report. The board palette is copied here rather than imported from the UI
Theme, so writing a report never loads Arcade; a test checks that it still
matches.
"""

from snake.bots.BotModeCatalogue import BOT_MODES, bot_mode_colors


SURFACE = "#0A1628"
SURFACE_RAISED = "#12243D"
BORDER = "#1E3A5F"
BOARD_GRID = "#1C344B"
TEXT = "#EAF2FF"
TEXT_MUTED = "#8FA3BF"
SNAKE_HEAD = "#D6F29B"
FOOD = "#FF7575"

# Each Bot Mode's colour comes from the catalogue, the same as in the app.
BOT_MODE_COLORS = bot_mode_colors()
# Muted text on a light page, for a bot the app does not know.
LIGHT_TEXT_MUTED = "#596171"

# Reports name bots by label; terminal runs save any DQN as "dqn", so the
# label (which includes the Feature Set) decides the colour, not the key.
KEYS_BY_LABEL = {mode.label: mode.key for mode in BOT_MODES}


def bot_color(label, light=False):
    """The colour of a bot by its report label; a bot the app does not know is muted."""
    colors = BOT_MODE_COLORS.get(KEYS_BY_LABEL.get(label))
    if colors is None:
        return LIGHT_TEXT_MUTED if light else TEXT_MUTED
    return colors.light if light else colors.dark
