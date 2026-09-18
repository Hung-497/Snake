from types import SimpleNamespace

from GameTypes import Direction
from ReplayPlayer import ReplayPlayer


class FakeCanvas:
    def __init__(self):
        self.rectangles = []
        self.ovals = []

    def create_rectangle(self, *args, **kwargs):
        self.rectangles.append(args)

    def create_oval(self, *args, **kwargs):
        self.ovals.append(args)


class FakeWindow:
    tile_size = 20

    def __init__(self):
        self.canvas = FakeCanvas()

    def clear_canvas(self):
        pass

    def update_score_label(self, *args):
        pass


def test_grid_replay_moves_in_cells_and_renders_in_pixels():
    player = ReplayPlayer(
        FakeWindow(),
        {
            "schema_version": 2,
            "coordinate_system": "grid",
            "start_snake": [1, 1],
            "start_food": [3, 1],
            "foods": [[3, 1]],
            "moves": [4],
            "final_score": 0,
        },
    )

    player.move_snake(Direction.RIGHT)
    player.draw()

    assert (player.snake_x, player.snake_y) == (2, 1)
    assert player.window.canvas.rectangles[0] == (40, 20, 60, 40)
    assert player.window.canvas.ovals[0] == (60, 20, 80, 40)
