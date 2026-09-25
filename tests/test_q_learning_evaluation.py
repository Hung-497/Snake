"""Evaluation Mode keeps the learned Q-table read-only during play."""

import json

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import SnakeEngine


class FirstChoiceRandom:
    def random(self):
        return 0.0

    def choice(self, options):
        return options[0]


def test_evaluation_uses_best_saved_action_without_learning(tmp_path):
    table_path = tmp_path / "selected_table.json"
    original = json.dumps({
        "q_table": {
            "0_0_0_1_0_0_2_2_2": {
                "Straight": 0,
                "Turn_Left": 10,
                "Turn_Right": 0,
            }
        },
        "epsilon": 1.0,
        "game_trained": 12,
    })
    table_path.write_text(original)
    engine = SnakeEngine(
        GameConfig(4, 4), start_position=(1, 1), food_position=(3, 1),
    )
    bot = QLearningBot(
        engine, random_source=FirstChoiceRandom(), evaluation_mode=True,
        q_table_file=table_path,
    )
    original_values = {state: values.copy() for state, values in bot.q_table.items()}

    direction = bot.choose_action(engine.state)
    assert direction == Direction.UP
    engine.change_direction(direction)
    transition = engine.preview()
    engine.step()
    bot.observe(transition)
    bot.on_game_end(engine.state)

    assert bot.q_table == original_values
    assert bot.epsilon == 1.0
    assert bot.game_trained == 12
    assert table_path.read_text() == original
