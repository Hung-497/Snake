"""The colours Bot Reports use: the app's dark board palette and Player colours.

Each Bot Mode keeps the colour it has in Records Analytics, so a bot looks the
same in the app and in a report. The values are copied here rather than
imported from the UI Theme, so writing a report never loads Arcade; a test
checks that they still match.
"""

from snake.bots.BotModeCatalogue import BOT_MODES


SURFACE = "#0A1628"
SURFACE_RAISED = "#12243D"
BORDER = "#1E3A5F"
BOARD_GRID = "#1C344B"
TEXT = "#EAF2FF"
TEXT_MUTED = "#8FA3BF"
SNAKE_HEAD = "#D6F29B"
FOOD = "#FF7575"

PLAYER_COLORS = {
    "rule": "#F2B84B",
    "q_learning": "#60A5FA",
    "hamiltonian": "#34D399",
    "search_based": "#F472B6",
    "q_learning_v3": "#22D3EE",
    "dqn": "#FB923C",
    "dqn_v2": "#A3E635",
}

# Reports name bots by label; terminal runs save any DQN as "dqn", so the
# label (which includes the Feature Set) decides the colour, not the key.
KEYS_BY_LABEL = {mode.label: mode.key for mode in BOT_MODES}


def bot_color(label):
    """The colour of a bot by its report label; a bot the app does not know is muted."""
    return PLAYER_COLORS.get(KEYS_BY_LABEL.get(label), TEXT_MUTED)
