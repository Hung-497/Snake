"""One real move updates the Q-table by the Q Learning rule."""

import json

import pytest

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.engine.SnakeEngine import SnakeEngine


class FirstChoiceRandom:
    """Always explore, and always take the first offered action."""

    def random(self):
        return 0.0

    def choice(self, options):
        return options[0]


def play_one_move(bot, engine):
    direction = bot.choose_action(engine.state)
    engine.change_direction(direction)
    transition = engine.preview()
    engine.step()
    bot.observe(transition)
    return transition


def test_terminal_update_does_not_bootstrap_from_a_next_state(tmp_path):
    # On a 2x1 board facing the wall every move is fatal, so "Straight" ends the game.
    engine = SnakeEngine(
        GameConfig(2, 1, 25), start_position=(1, 0), direction=Direction.RIGHT,
        food_position=(0, 0),
    )
    bot = QLearningBot(
        engine, random_source=FirstChoiceRandom(), q_table_file=str(tmp_path / "t.json"),
    )
    state_before = bot.features(engine.state)

    transition = play_one_move(bot, engine)

    assert transition.game_over is True
    # Only the -100 reward counts: 0 + 0.1 * (-100 - 0).
    assert bot.q_table[state_before]["Straight"] == pytest.approx(-10)


def test_non_terminal_update_uses_the_best_value_of_the_next_state(tmp_path):
    def make_engine():
        return SnakeEngine(
            GameConfig(5, 5, 25), start_position=(1, 2), direction=Direction.RIGHT,
            food_position=(2, 1),
        )

    # Find the state after one straight move, and give it known values.
    preview_engine = make_engine()
    preview_engine.step()
    reader = QLearningBot(preview_engine, q_table_file=str(tmp_path / "unused.json"))
    next_key = "_".join(str(value) for value in reader.features(preview_engine.state))
    table_path = tmp_path / "table.json"
    table_path.write_text(json.dumps({
        "q_table": {next_key: {"Straight": 20, "Turn_Left": 10, "Turn_Right": 5}},
        "epsilon": 1.0,
        "game_trained": 0,
    }))
    engine = make_engine()
    bot = QLearningBot(engine, random_source=FirstChoiceRandom(), q_table_file=str(table_path))
    state_before = bot.features(engine.state)
    # The move must change the state, or the old value would be the preloaded 20.
    assert "_".join(str(value) for value in state_before) != next_key

    transition = play_one_move(bot, engine)

    assert transition.game_over is False
    # Reward 6 (step -1, closer +5, open space +2), best next value 20:
    # 0 + 0.1 * (6 + 0.9 * 20 - 0) = 2.4.
    assert bot.q_table[state_before]["Straight"] == pytest.approx(2.4)
