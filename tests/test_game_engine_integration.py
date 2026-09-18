from types import SimpleNamespace

from Game import Game
from GameConfig import GameConfig
from GameTypes import Direction
from SnakeEngine import SnakeEngine


class FakeCanvas:
    def __init__(self):
        self.rectangles = []
        self.ovals = []

    def create_rectangle(self, *args, **kwargs):
        self.rectangles.append((args, kwargs))

    def create_oval(self, *args, **kwargs):
        self.ovals.append((args, kwargs))

    def delete(self, tag):
        pass


class FakeWindow:
    width = 3
    height = 1
    tile_size = 25

    def __init__(self):
        self.window = self
        self.canvas = FakeCanvas()
        self.scores = []
        self.scheduled_callbacks = []

    def clear_canvas(self):
        self.canvas.delete("all")

    def update_score_label(self, score, games_played, best_score):
        self.scores.append((score, games_played, best_score))

    def after(self, delay, callback):
        self.scheduled_callbacks.append((delay, callback))
        return len(self.scheduled_callbacks)


class FakeReplayManager:
    def start_recording(self, *args, **kwargs):
        pass

    def record_move(self, direction):
        pass

    def record_food(self, food):
        pass

    def save_replay(self, bot_mode, score, game_won):
        pass


class FakeRecordManager:
    def save_game_result(self, *args):
        pass


def test_game_can_advance_engine_without_legacy_domain_objects(monkeypatch):
    monkeypatch.setattr("Game.ReplayManager", FakeReplayManager)
    monkeypatch.setattr("Game.RecordManager", FakeRecordManager)

    window = FakeWindow()
    engine = SnakeEngine(
        GameConfig(width=3, height=1, tile_size=25),
        start_position=(0, 0),
        direction=Direction.RIGHT,
        food_position=(25, 0),
    )
    game = Game(
        window,
        bot_mode=None,
        speed_delay=1,
        engine=engine,
    )

    game.update()

    assert engine.snake_position == (25, 0)
    assert engine.snake_body == ((0, 0),)
    assert engine.score == 1
    assert game.score == 1
    assert window.scores[-1][0] == 1
    assert len(window.canvas.rectangles) == 2
    assert len(window.canvas.ovals) == 1
