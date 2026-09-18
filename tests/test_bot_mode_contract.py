import random

import json
import os

from GameConfig import GameConfig
from GameTypes import Direction
from QLearningBot import QLearningBot
from RuleBasedBot import RuleBasedBot
from SnakeEngine import SnakeEngine


def make_engine(width=4, height=4, start_position=(1, 1), body=(), direction=Direction.RIGHT, food_position=(3, 1)):
    return SnakeEngine(
        GameConfig(width=width, height=height, tile_size=20),
        start_position=start_position,
        body=body,
        direction=direction,
        food_position=food_position,
        random_source=random.Random(5),
    )


def test_rule_based_chooses_a_direction_from_engine_state_alone():
    engine = make_engine()

    bot = RuleBasedBot(engine)

    assert bot.choose_action(engine.state) is Direction.RIGHT


def test_rule_based_follows_its_tail_when_the_food_path_has_no_escape():
    engine = make_engine(
        start_position=(0, 0),
        body=((1, 0), (2, 0), (2, 1), (1, 1)),
        direction=Direction.DOWN,
        food_position=(3, 0),
    )

    bot = RuleBasedBot(engine)

    # The food lies to the right, but that path cannot escape afterwards.
    assert bot.choose_action(engine.state) is Direction.DOWN


def test_rule_based_falls_back_to_the_largest_open_space():
    engine = make_engine(
        start_position=(1, 0),
        body=((2, 0), (2, 1), (3, 1), (3, 0)),
        direction=Direction.DOWN,
        food_position=(0, 0),
    )

    bot = RuleBasedBot(engine)

    # The food is one step left, but neither the food path nor the tail is
    # reachable safely, so the fallback picks the roomier direction.
    assert bot.choose_action(engine.state) is Direction.DOWN


def test_rule_based_returns_no_action_when_every_direction_is_unsafe():
    engine = SnakeEngine(
        GameConfig(width=3, height=3, tile_size=20),
        start_position=(0, 0),
        body=((1, 0), (1, 1), (0, 1), (0, 2)),
        direction=Direction.RIGHT,
        food_position=(2, 2),
        random_source=random.Random(5),
    )

    bot = RuleBasedBot(engine)

    assert bot.safe_directions(engine.state) == []
    assert bot.choose_action(engine.state) is None


def test_bot_safety_follows_engine_preview_into_the_departing_tail():
    engine = make_engine(
        start_position=(1, 1),
        body=((2, 1),),
        direction=Direction.RIGHT,
        food_position=(3, 3),
    )

    bot = RuleBasedBot(engine)

    # The tail cell empties as the snake advances, so the engine allows it.
    assert bot.is_safe_direction(engine.state, Direction.RIGHT) is True


def test_bot_random_source_is_injectable_and_separate_from_the_engine():
    bot_random = random.Random(99)
    engine = make_engine()

    bot = RuleBasedBot(engine, random_source=bot_random)

    assert bot.random_source is bot_random
    assert bot.random_source is not engine.random_source


def test_bot_defaults_to_its_own_random_source():
    engine = make_engine()

    bot = RuleBasedBot(engine)

    assert bot.random_source is not engine.random_source


def make_q_learning_bot(engine, tmp_path, random_source=None):
    bot = QLearningBot(engine, random_source=random_source)
    bot.q_table_file = os.path.join(str(tmp_path), "q_table.json")
    return bot


def test_q_learning_chooses_a_direction_from_engine_state_alone(tmp_path):
    engine = make_engine(food_position=(2, 1))
    bot = make_q_learning_bot(engine, tmp_path, random_source=random.Random(1))
    bot.q_table = {}
    bot.epsilon = 0

    assert bot.choose_action(engine.state) is Direction.RIGHT


def test_q_learning_game_end_owns_training_count_decay_and_persistence(tmp_path):
    engine = make_engine()
    bot = make_q_learning_bot(engine, tmp_path, random_source=random.Random(1))
    bot.game_trained = 4
    bot.epsilon = 1.0

    bot.on_game_end(engine.state)

    assert bot.game_trained == 5
    assert bot.epsilon < 1.0
    with open(bot.q_table_file) as saved_file:
        saved = json.load(saved_file)
    assert saved["game_trained"] == 5


def test_q_learning_exploration_does_not_consume_engine_randomness(tmp_path):
    class FailingRandom:
        def randint(self, start, end):
            raise AssertionError("bot exploration must not use engine randomness")

    engine = SnakeEngine(
        GameConfig(width=4, height=4, tile_size=20),
        start_position=(1, 1),
        direction=Direction.RIGHT,
        food_position=(3, 1),
        random_source=FailingRandom(),
    )
    bot = make_q_learning_bot(engine, tmp_path, random_source=random.Random(3))
    bot.epsilon = 1.0

    # Always exploring: every action comes from the bot's own source.
    for _ in range(20):
        assert bot.choose_action(engine.state) in tuple(Direction)

    assert bot.random_source is not engine.random_source
