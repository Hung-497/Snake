"""Shared learning rules stay usable by both tabular and future DQN bots."""

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


def test_learning_bot_uses_the_same_reward_and_exploration_rules():
    rules, state = make_rules()
    values = {"Straight": 0, "Turn_Left": 10, "Turn_Right": 0}

    assert rules.reward(False, False, 3, 2, 2) == 6
    assert rules.reward(True, False, 3, 2, 2) == -100
    assert rules.reward(False, True, 3, 2, 2) == 100
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
