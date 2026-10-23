"""Bot Reports keep the app's colours without importing the Arcade UI."""

from snake.analysis import ReportColors
from snake.bots.BotModeCatalogue import BOT_MODES, bot_mode_colors
from snake.ui import Theme


def hex_of(color):
    return f"#{color.r:02X}{color.g:02X}{color.b:02X}"


# The colours each Bot Mode had before they moved into the catalogue.
EXPECTED_COLORS = {
    "rule": ("#F2B84B", "#9A6B00"),
    "q_learning": ("#60A5FA", "#2F5FD0"),
    "hamiltonian": ("#34D399", "#0B8A5E"),
    "search_based": ("#F472B6", "#BE2D69"),
    "q_learning_v3": ("#22D3EE", "#0B7F9C"),
    "dqn": ("#FB923C", "#C9580A"),
    "dqn_v2": ("#A3E635", "#5E8F1F"),
}


def test_the_app_and_the_report_give_every_bot_mode_its_catalogue_colour():
    colors = bot_mode_colors()
    for mode in BOT_MODES:
        app = hex_of(Theme.player_color(mode.key))

        assert app == ReportColors.bot_color(mode.label) == colors[mode.key].dark, mode.key
        assert ReportColors.bot_color(mode.label, light=True) == colors[mode.key].light, mode.key
        assert app not in (hex_of(Theme.TEXT_MUTED), hex_of(Theme.player_color("human"))), mode.key


def test_every_bot_mode_keeps_its_colours_in_both_themes():
    for mode in BOT_MODES:
        assert (
            ReportColors.bot_color(mode.label), ReportColors.bot_color(mode.label, light=True),
        ) == EXPECTED_COLORS[mode.key], mode.key


def test_the_board_palette_matches_the_app():
    for name in ("SURFACE", "SURFACE_RAISED", "BORDER", "BOARD_GRID", "TEXT", "TEXT_MUTED",
                 "SNAKE_HEAD", "FOOD"):
        assert getattr(ReportColors, name) == hex_of(getattr(Theme, name)), name


def test_bots_are_coloured_by_label_so_dqn_versions_differ():
    assert ReportColors.bot_color("DQN v2") == "#A3E635"
    assert ReportColors.bot_color("DQN v3") == "#FB923C"
    assert ReportColors.bot_color("Not a bot") == ReportColors.TEXT_MUTED
