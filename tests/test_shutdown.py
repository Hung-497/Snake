import pytest
from tkinter import TclError

from Game import Game
from ReplayPlayer import ReplayPlayer


class CancelWindow:
    def __init__(self, error):
        self.window = self
        self.error = error
        self.cancelled_ids = []
        self.quit_called = False
        self.destroy_called = False

    def after_cancel(self, callback_id):
        self.cancelled_ids.append(callback_id)
        if (self.error is not None):
            raise self.error

    def quit(self):
        self.quit_called = True

    def destroy(self):
        self.destroy_called = True


def make_game(window, callback_name):
    game = Game.__new__(Game)
    game.window = window
    game.game_closed = False
    game.update_after_id = None
    game.reset_after_id = None
    setattr(game, callback_name, "callback-id")
    return game


@pytest.mark.parametrize("callback_name", ["update_after_id", "reset_after_id"])
def test_game_shutdown_ignores_expected_tkinter_cancellation(callback_name):
    window = CancelWindow(TclError("invalid command name"))
    game = make_game(window, callback_name)

    game.close_game()

    assert window.cancelled_ids == ["callback-id"]
    assert window.quit_called
    assert window.destroy_called


@pytest.mark.parametrize("callback_name", ["update_after_id", "reset_after_id"])
def test_game_shutdown_does_not_hide_unexpected_cancellation_errors(callback_name):
    window = CancelWindow(RuntimeError("unexpected failure"))
    game = make_game(window, callback_name)

    with pytest.raises(RuntimeError, match="unexpected failure"):
        game.close_game()


def test_replay_shutdown_uses_the_same_specific_tkinter_error():
    window = CancelWindow(TclError("invalid command name"))
    replay = ReplayPlayer.__new__(ReplayPlayer)
    replay.window = window
    replay.replay_closed = False
    replay.return_to_menu = False
    replay.update_after_id = "callback-id"

    replay.close_replay()

    assert window.cancelled_ids == ["callback-id"]
    assert window.quit_called
    assert window.destroy_called


def test_replay_shutdown_does_not_hide_unexpected_cancellation_errors():
    window = CancelWindow(RuntimeError("unexpected failure"))
    replay = ReplayPlayer.__new__(ReplayPlayer)
    replay.window = window
    replay.replay_closed = False
    replay.return_to_menu = False
    replay.update_after_id = "callback-id"

    with pytest.raises(RuntimeError, match="unexpected failure"):
        replay.close_replay()
