"""Bot Reports keep the app's colours without importing the Arcade UI."""

from snake.analysis import ReportColors
from snake.bots.BotModeCatalogue import BOT_MODES
from snake.ui import Theme


def hex_of(color):
    return f"#{color.r:02X}{color.g:02X}{color.b:02X}"


def test_every_bot_mode_has_its_records_analytics_colour():
    bot_modes = {key: color for key, color in Theme.PLAYER_COLORS.items() if key != "human"}

    assert ReportColors.PLAYER_COLORS == {key: hex_of(color) for key, color in bot_modes.items()}


def test_the_board_palette_matches_the_app():
    for name in ("SURFACE", "SURFACE_RAISED", "BORDER", "BOARD_GRID", "TEXT", "TEXT_MUTED",
                 "SNAKE_HEAD", "FOOD"):
        assert getattr(ReportColors, name) == hex_of(getattr(Theme, name)), name


def test_bots_are_coloured_by_label_so_dqn_versions_differ():
    assert ReportColors.bot_color("DQN v2") == ReportColors.PLAYER_COLORS["dqn_v2"]
    assert ReportColors.bot_color("DQN v3") == ReportColors.PLAYER_COLORS["dqn"]
    assert ReportColors.bot_color("Not a bot") == ReportColors.TEXT_MUTED


def test_every_bot_mode_has_a_colour_in_both_themes():
    # A new Bot Mode, such as a DQN v4, needs its colour added here too.
    for mode in BOT_MODES:
        assert mode.key in ReportColors.PLAYER_COLORS, mode.key
        assert mode.key in ReportColors.LIGHT_PLAYER_COLORS, mode.key
