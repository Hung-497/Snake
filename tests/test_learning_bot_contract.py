"""Shared learning rules stay usable by both tabular and future DQN bots."""

import pytest

from snake.bots.LearningBot import LearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import SnakeEngine


class FirstChoiceRandom:
    def random(self):
        return 0.0

    def choice(self, options):
        return options[0]


def make_rules(start_position=(1, 1), food_position=(3, 1)):
    engine = SnakeEngine(
        GameConfig(4, 4),
        start_position=start_position,
        food_position=food_position,
        direction=Direction.RIGHT,
    )
    return LearningBot(engine, random_source=FirstChoiceRandom()), engine.state


def test_learning_bot_exposes_the_nine_feature_contract():
    rules, state = make_rules()

    assert rules.features(state) == (0, 0, 0, 1, 0, 0, 2, 2, 2)


def test_learning_bot_excludes_unsafe_relative_actions():
    rules, state = make_rules(start_position=(0, 0), food_position=(2, 0))

    assert rules.available_actions(state) == ["Straight", "Turn_Right"]


@pytest.mark.parametrize(
    "game_over, ate_food, old_distance, new_distance, space_level, expected",
    [
        (True, False, 3, 2, 2, -100),   # game over
        (True, True, 3, 2, 2, -100),    # game over wins over eating
        (False, True, 3, 2, 0, 100),    # food, whatever the space
        (False, False, 3, 2, 2, 6),     # -1 move, +5 closer, +2 plenty of space
        (False, False, 3, 2, 1, 4),     # -1, +5, no space bonus
        (False, False, 3, 2, 0, -4),    # -1, +5, -8 almost no space
        (False, False, 2, 3, 2, -1),    # -1, -2 farther, +2
        (False, False, 2, 3, 1, -3),    # -1, -2
        (False, False, 2, 3, 0, -11),   # -1, -2, -8
    ],
)
def test_every_reward_rule_gives_its_exact_value(
    game_over, ate_food, old_distance, new_distance, space_level, expected,
):
    rules, _ = make_rules()

    assert rules.reward(
        game_over, ate_food, old_distance, new_distance, space_level,
    ) == expected


def test_learning_bot_explores_in_training_and_takes_the_best_value_in_evaluation():
    rules, state = make_rules()
    values = {"Straight": 0, "Turn_Left": 10, "Turn_Right": 0}

    assert rules.select_action(state, values, evaluation_mode=False) == "Straight"
    assert rules.select_action(state, values, evaluation_mode=True) == "Turn_Left"


def test_learning_bot_shares_discount_and_epsilon_decay():
    rules, _ = make_rules()

    assert rules.discount_rate == 0.9
    rules.decay_epsilon()
    assert rules.epsilon == 0.997
    rules.epsilon = 0.01
    rules.decay_epsilon()
    assert rules.epsilon == 0.05
