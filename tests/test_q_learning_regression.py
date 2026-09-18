from types import SimpleNamespace

import pytest

from QLearningBot import QLearningBot


def make_transition(game_over, ate_food=False):
    return SimpleNamespace(game_over=game_over, ate_food=ate_food)


def make_bot(current_state, next_state, next_values):
    bot = QLearningBot.__new__(QLearningBot)
    bot.q_table = {
        current_state: {
            "Straight": 0,
            "Turn_Left": 0,
            "Turn_Right": 0,
        },
        next_state: next_values,
    }
    bot.learning_rate = 0.1
    bot.discount_rate = 0.9
    bot.current_state = current_state
    bot.current_action = "Straight"
    bot.distance_before_move = 10
    bot.engine = SimpleNamespace(state=SimpleNamespace())
    bot.get_food_distance = lambda state: 9
    bot._get_state = lambda state: next_state
    return bot


def test_terminal_update_does_not_bootstrap_from_next_state():
    current_state = (0, 0, 0, 0, 0, 0, 2, 0, 0)
    next_state = (1, 1, 1, 1, 1, 1, 2, 2, 2)
    bot = make_bot(
        current_state,
        next_state,
        {"Straight": 100, "Turn_Left": 80, "Turn_Right": 60},
    )
    bot.q_table = {
        current_state: {"Straight": 0, "Turn_Left": 0, "Turn_Right": 0}
    }
    bot._get_state = lambda state: pytest.fail(
        "terminal updates should not calculate a next state"
    )

    bot.observe(make_transition(game_over=True))

    assert bot.q_table[current_state]["Straight"] == pytest.approx(-10)


def test_non_terminal_update_uses_best_next_state_value():
    current_state = (0, 0, 0, 0, 0, 0, 2, 0, 0)
    next_state = (1, 1, 1, 1, 1, 1, 2, 2, 2)
    bot = make_bot(
        current_state,
        next_state,
        {"Straight": 20, "Turn_Left": 10, "Turn_Right": 5},
    )

    bot.observe(make_transition(game_over=False))

    # Reward is 6: step penalty, food progress, and open-space bonus.
    assert bot.q_table[current_state]["Straight"] == pytest.approx(2.4)
