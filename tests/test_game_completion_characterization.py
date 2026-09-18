from types import SimpleNamespace

from Game import Game


class FakeWindow:
    width = 2
    height = 2
    tile_size = 25

    def __init__(self):
        self.window = self
        self.drawn_won_score = None
        self.scheduled_callbacks = []

    def clear_canvas(self):
        pass

    def update_score_label(self, score, games_played, best_score):
        pass

    def draw_game_won(self, score):
        self.drawn_won_score = score

    def draw_game_over(self, score):
        pass

    def after(self, delay, callback):
        self.scheduled_callbacks.append((delay, callback))
        return len(self.scheduled_callbacks)


class FakeSnake:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.body = [(25, 0), (0, 25), (25, 25)]

    def draw_snake(self):
        pass

    def draw_snake_body(self):
        pass


class FakeFood:
    x = 25
    y = 25

    def draw_food(self):
        pass


class FakeMovement:
    def change_direction(self, direction):
        pass

    def move_snake(self, snake, tile_size, food, width, height, game_over):
        return True, game_over


class FakeReplayManager:
    def save_replay(self, bot_mode, score, game_won):
        pass


class FakeRecordManager:
    def save_game_result(self, *args):
        pass


def test_eating_the_final_free_cell_is_a_win():
    game = Game.__new__(Game)
    game.window = FakeWindow()
    game.snake = FakeSnake()
    game.food = FakeFood()
    game.movement = FakeMovement()
    game.bot_mode = None
    game.speed_delay = 1
    game.replay_manager = FakeReplayManager()
    game.record_manager = FakeRecordManager()
    game.bot = SimpleNamespace(epsilon=1.0)
    game.score = 0
    game.game_over = False
    game.game_won = False
    game.recent_scores = []
    game.games_played = 0
    game.best_score = 0
    game.total_moves = 0
    game.total_moves_history = []
    game.game_closed = False
    game.update_after_id = None
    game.reset_after_id = None
    game.session_start_time = 0
    game.game_start_time = 0

    game.update()

    assert game.score == 1
    assert game.game_over is True
    assert game.game_won is True
    assert game.window.drawn_won_score == 1
    assert game.food.x == 25
    assert game.food.y == 25
