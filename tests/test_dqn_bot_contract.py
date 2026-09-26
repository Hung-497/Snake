"""DQN consumes the shared learning-bot action contract."""

import random

import pytest


torch = pytest.importorskip("torch")

from snake.bots.DQNBot import DQNBot
from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import SnakeEngine


def test_dqn_greedy_choice_excludes_unsafe_action_and_evaluation_is_read_only():
    engine = SnakeEngine(
        GameConfig(4, 4),
        start_position=(0, 0),
        food_position=(2, 0),
        direction=Direction.RIGHT,
        random_source=random.Random(1),
    )
    bot = DQNBot(
        engine,
        random_source=random.Random(2),
        evaluation_mode=True,
    )
    with torch.no_grad():
        for parameter in bot.network.parameters():
            parameter.zero_()
        # Turn Left has the highest value, but it points through the top wall.
        bot.network[-1].bias.copy_(torch.tensor([2.0, 100.0, 1.0]))

    assert bot.available_actions(engine.state) == ["Straight", "Turn_Right"]
    assert bot.choose_action(engine.state) is Direction.RIGHT
    transition = engine.preview()
    engine.step()
    bot.observe(transition)
    bot.on_game_end(engine.state)

    assert list(bot.replay) == []
    assert bot.game_trained == 0
    assert bot.epsilon == 1.0
