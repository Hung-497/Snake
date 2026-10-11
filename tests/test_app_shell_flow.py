"""
Flow tests for the Arcade application shell.

These tests check which App View the app opens and that closing it stops the
app cleanly. They use a fake window instead of a real Arcade window, so they
need no graphical display and never depend on Arcade's own behaviour.
"""


from snake.ui.AppShell import AppShell


class FakeWindow:
    """Stands in for the Arcade window and records what the shell asked it to do."""

    def __init__(self):
        self.shown_views = []
        self.close_count = 0

    def show_view(self, view):
        self.shown_views.append(view)

    def close(self):
        self.close_count += 1


def make_shell(**view_builders):
    """Build a shell whose view builders just return their own name."""
    window = FakeWindow()
    builders = {name: (lambda built=built: built) for name, built in view_builders.items()}
    return AppShell(window, builders), window


def test_app_starts_on_the_menu_app_view():
    shell, window = make_shell(menu="menu-view")

    shell.start()

    assert shell.current_view_name == "menu"
    assert window.shown_views == ["menu-view"]
    assert shell.is_running


def test_closing_the_app_stops_it_cleanly():
    shell, window = make_shell(menu="menu-view")
    shell.start()

    shell.close()

    assert not shell.is_running
    assert window.close_count == 1


def test_closing_the_app_twice_only_closes_the_window_once():
    shell, window = make_shell(menu="menu-view")
    shell.start()

    shell.close()
    shell.close()

    assert window.close_count == 1


def test_a_view_that_is_not_registered_yet_is_ignored():
    shell, window = make_shell(menu="menu-view")
    shell.start()

    opened = shell.show_view("settings")

    assert opened is False
    assert shell.current_view_name == "menu"
    assert window.shown_views == ["menu-view"]


def test_a_view_can_be_registered_after_the_shell_is_built():
    shell, window = make_shell()

    shell.register_view("menu", lambda: "menu-view")
    shell.start()

    assert shell.current_view_name == "menu"
    assert window.shown_views == ["menu-view"]


def test_a_view_can_be_opened_with_a_choice_the_user_made():
    window = FakeWindow()
    shell = AppShell(window, {"game": lambda bot_mode: f"game-view:{bot_mode}"})

    opened = shell.show_view("game", bot_mode="rule")

    assert opened is True
    assert window.shown_views == ["game-view:rule"]


def test_the_app_moves_among_every_app_view_and_then_closes_cleanly():
    window = FakeWindow()
    shell = AppShell(
        window,
        {
            "menu": lambda: "menu-view",
            "settings": lambda: "settings-view",
            "play": lambda: "play-view",
            "game": lambda bot_mode: f"game-view:{bot_mode}",
            "records": lambda: "records-view",
            "replay": lambda: "replay-view",
            "replay_playback": lambda session, player: f"replay-playback-view:{player}",
        },
    )

    shell.start()
    shell.show_view("settings")
    shell.show_view("menu")
    shell.show_view("records")
    shell.show_view("menu")
    shell.show_view("replay")
    shell.show_view("replay_playback", session="saved-game", player="rule")
    shell.show_view("menu")
    shell.show_view("play")
    shell.show_view("game", bot_mode="hamiltonian")
    shell.show_view("menu")
    shell.close()

    assert window.shown_views == [
        "menu-view",
        "settings-view",
        "menu-view",
        "records-view",
        "menu-view",
        "replay-view",
        "replay-playback-view:rule",
        "menu-view",
        "play-view",
        "game-view:hamiltonian",
        "menu-view",
    ]
    assert shell.current_view_name == "menu"
    assert not shell.is_running
    assert window.close_count == 1
