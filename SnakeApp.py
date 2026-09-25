import arcade
from arcade.types import Color

from AppShell import AppShell
from GameView import GameView
from MenuView import MenuView
from MotionRules import ViewFade
from PlayView import PlayView
from RecordsView import RecordsView
from ReplayPlaybackView import ReplayPlaybackView
from ReplayView import ReplayView
from SessionSettings import SessionSettings
from SettingsView import SettingsView
import Theme
from WindowLayout import minimum_window_size


# A known starting size; the user can resize the window during this run.
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
            resizable=True,
        )
        self.center_window()
        self.shell = None
        self.view_fade = ViewFade()

    def show_view(self, new_view):
        if self.current_view is None:
            super().show_view(new_view)
            return

        self.view_fade.start(new_view)

    def on_update(self, delta_time):
        next_view = self.view_fade.advance_by(delta_time)
        if next_view is not None:
            super().show_view(next_view)

    def on_draw(self):
        alpha = self.view_fade.alpha
        if alpha > 0:
            surface = Theme.SURFACE
            arcade.draw_lbwh_rectangle_filled(
                0, 0, self.width, self.height,
                Color(surface.r, surface.g, surface.b, alpha),
            )

    def update_board_minimum(self, game_config):
        """Make the resize drag stop before the board becomes unreadable."""
        width, height = minimum_window_size(
            game_config.width, game_config.height, game_config.tile_size
        )
        self.set_minimum_size(width, height)

    def on_close(self):
        self.view_fade.clear()
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
    window.update_board_minimum(settings.build_game_config())

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
