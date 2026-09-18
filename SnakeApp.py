import arcade

from AppShell import AppShell
from GameView import GameView
from MenuView import MenuView
from PlayView import PlayView
from RecordsView import RecordsView
from ReplayPlaybackView import ReplayPlaybackView
from ReplayView import ReplayView
from SessionSettings import SessionSettings
from SettingsView import SettingsView


# The window is fixed size, so it has to fit every board the settings allow.
# The largest board is 30 x 30 tiles at 30 pixels each, which is 900 x 900
# pixels, and the extra height leaves room for the Game App View's score row.
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 960
WINDOW_TITLE = "Snake Game"


class SnakeWindow(arcade.Window):
    """
    The single application window.

    Arcade owns the window and the frame loop; the shell owns which App View is
    showing. This class is only the small bridge between the two, so that
    closing the window also tells the shell the app has stopped.
    """

    def __init__(self):
        super().__init__(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            title=WINDOW_TITLE,
            resizable=False,
        )
        self.center_window()
        self.shell = None

    def on_close(self):
        if self.shell is None:
            super().on_close()
            return

        # The shell closes this window itself, so there is nothing else to do.
        self.shell.close()


def create_app():
    """Build the window, the shell, and the App Views the shell can open."""
    window = SnakeWindow()
    shell = AppShell(window, {})

    # One settings object for the whole session, so choices are kept when the
    # user leaves Settings and opens it again.
    settings = SessionSettings()

    shell.register_view("menu", lambda: MenuView(shell))
    shell.register_view("settings", lambda: SettingsView(shell, settings))
    shell.register_view("play", lambda: PlayView(shell, settings))
    shell.register_view("game", lambda bot_mode: GameView(shell, settings, bot_mode))
    shell.register_view("records", lambda: RecordsView(shell))
    shell.register_view("replay", lambda: ReplayView(shell))
    shell.register_view(
        "replay_playback",
        lambda session, bot_mode: ReplayPlaybackView(shell, session, bot_mode),
    )
    window.shell = shell

    return shell


def main():
    shell = create_app()
    shell.start()
    arcade.run()


if __name__ == "__main__":
    main()
