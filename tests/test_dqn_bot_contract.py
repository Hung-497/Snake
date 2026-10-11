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


class FirstChoiceRandom:
    """Always explore, and always take the first offered action."""

    def random(self):
        return 0.0

    def choice(self, options):
        return options[0]


def make_learning_bot(engine):
    """A DQN bot whose network outputs are known exactly and that learns at once."""
    bot = DQNBot(
        engine, random_source=FirstChoiceRandom(), replay_random_source=random.Random(3),
        settings={
            "hidden_size": 8, "learning_rate": 0.001, "batch_size": 1,
            "replay_capacity": 10, "target_update_steps": 100,
        },
    )
    with torch.no_grad():
        # Zero weights make every output its bias, whatever the features.
        for network, biases in ((bot.network, [0.0, 0.0, 0.0]),
                                (bot.target_network, [10.0, 30.0, 20.0])):
            for parameter in network.parameters():
                parameter.zero_()
            network[-1].bias.copy_(torch.tensor(biases))
    return bot


def action_values(bot, features):
    with torch.no_grad():
        return bot.network(torch.tensor(features, dtype=torch.float32)).tolist()


@pytest.mark.parametrize(
    "board, start, food, game_over, expected_loss",
    [
        # Safe move closer with open space: reward 6, target 6 + 0.9 * 30 = 33.
        ((5, 5), (1, 2), (2, 1), False, 32.5),
        # Fatal move: reward -100, and no future value, so the target is -100.
        ((2, 1), (1, 0), (0, 0), True, 99.5),
    ],
)
def test_one_learning_step_moves_the_chosen_value_toward_the_q_learning_target(
    board, start, food, game_over, expected_loss,
):
    engine = SnakeEngine(
        GameConfig(*board), start_position=start, food_position=food,
        direction=Direction.RIGHT,
    )
    bot = make_learning_bot(engine)

    direction = bot.choose_action(engine.state)
    features_before = bot.current_features
    engine.change_direction(direction)
    transition = engine.preview()
    engine.step()
    bot.observe(transition)

    assert transition.game_over is game_over
    assert bot.current_action == "Straight"
    assert bot.optimizer_steps == 1
    # Smooth L1 loss of a chosen value of 0 against the target: |target| - 0.5.
    assert bot.game_losses[-1] == pytest.approx(expected_loss)
    straight, turn_left, turn_right = action_values(bot, features_before)
    assert (straight > 0) is (not game_over)   # moved toward +33 or toward -100
    assert straight != 0
    assert (turn_left, turn_right) == (0.0, 0.0)   # untouched actions keep their value
