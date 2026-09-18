from types import SimpleNamespace

import pytest

from Game import Game


class FakeWindow:
    width = 4
    height = 4
    tile_size = 25

    def __init__(self):
        self.window = self
        self.scheduled_callbacks = []

    def clear_canvas(self):
        pass

    def update_score_label(self, score, games_played, best_score):
        pass

    def draw_game_over(self, score):
        pass

    def draw_game_won(self, score):
        pass

    def after(self, delay, callback):
        self.scheduled_callbacks.append((delay, callback))
        return len(self.scheduled_callbacks)


class FakeSnake:
    body = []

    def draw_snake(self):
        pass

    def draw_snake_body(self):
        pass


class FakeFood:
    def draw_food(self):
        pass


class FakeMovement:
    def move_snake(self, snake, tile_size, food, width, height, game_over):
        return False, True


class FakeReplayManager:
    def save_replay(self, bot_mode, score, game_won):
        pass


class FakeRecordManager:
    def __init__(self):
        self.saved_result = None

    def save_game_result(self, *args):
        self.saved_result = args


def make_finished_game(score, total_moves, recent_scores, move_history):
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
    game.score = score
    game.game_over = False
    game.game_won = False
    game.recent_scores = recent_scores
    game.games_played = 0
    game.best_score = 0
    game.total_moves = total_moves
    game.total_moves_history = move_history
    game.game_closed = False
    game.update_after_id = None
    game.reset_after_id = None
    game.session_start_time = 0
    game.game_start_time = 0
    return game


def test_score_average_prunes_before_calculation():
    game = make_finished_game(
        score=2,
        total_moves=1,
        recent_scores=[1] * 100,
        move_history=[],
    )

    game.update()

    assert game.record_manager.saved_result[4] == pytest.approx(1.01)


def test_move_average_prunes_before_calculation(capsys):
    game = make_finished_game(
        score=1,
        total_moves=20,
        recent_scores=[],
        move_history=[10] * 10,
    )

    game.update()

    assert "Avg total move: 11.1" in capsys.readouterr().out
