from dataclasses import replace
import random

import json
import os

from snake.engine.GameConfig import GameConfig
from snake.engine.GameTypes import Direction
from snake.bots.QLearningBot import QLearningBot
from snake.bots.RuleBasedBot import RuleBasedBot
from snake.bots.BotFactory import create_bot_mode
from snake.engine.SnakeEngine import SnakeEngine


def make_engine(width=4, height=4, start_position=(1, 1), body=(), direction=Direction.RIGHT, food_position=(3, 1)):
    return SnakeEngine(
        GameConfig(width=width, height=height, tile_size=20),
        start_position=start_position,
        body=body,
        direction=direction,
        food_position=food_position,
        random_source=random.Random(5),
    )


class CountingEngine(SnakeEngine):
    def __init__(self, *args, **kwargs):
        self.preview_calls = 0
        super().__init__(*args, **kwargs)

    def preview_from(self, state, direction=None):
        self.preview_calls += 1
        return super().preview_from(state, direction)


def make_counting_engine(food_position=(3, 3)):
    return CountingEngine(
        GameConfig(width=4, height=4, tile_size=20),
        start_position=(1, 1),
        direction=Direction.RIGHT,
        food_position=food_position,
        random_source=random.Random(5),
    )


def test_rule_based_chooses_a_direction_from_engine_state_alone():
    engine = make_engine()

    bot = RuleBasedBot(engine)

    assert bot.choose_action(engine.state) is Direction.RIGHT


def test_search_based_plans_through_a_departing_tail_to_reach_food():
    engine = make_engine(
        width=4,
        height=3,
        start_position=(1, 1),
        body=((2, 1),),
        direction=Direction.RIGHT,
        food_position=(3, 1),
    )
    bot = create_bot_mode("search_based", engine)

    assert bot.choose_action(engine.state) is Direction.RIGHT


def test_search_based_returns_the_same_action_for_the_same_state():
    engine = make_engine(
        width=4,
        height=4,
        start_position=(1, 1),
        direction=Direction.RIGHT,
        food_position=(3, 3),
    )
    bot = create_bot_mode("search_based", engine)

    actions = [bot.choose_action(engine.state) for _ in range(4)]

    assert actions == [actions[0]] * 4


def test_search_based_shares_one_budget_across_food_and_fallback_searches():
    engine = make_counting_engine()
    bot = create_bot_mode("search_based", engine)
    bot.MAX_EXPLORED_STATES = 1
    state = engine.state

    action = bot.choose_action(state)
    decision_preview_calls = engine.preview_calls

    assert action is not None
    assert engine.preview_from(state, action).moved is True
    assert decision_preview_calls <= 6


def test_search_based_fallback_does_not_multiply_the_budget_per_candidate():
    engine = make_counting_engine()
    bot = create_bot_mode("search_based", engine)
    bot.MAX_EXPLORED_STATES = 1
    state = replace(engine.state, food_position=None)

    action = bot.choose_action(state)
    decision_preview_calls = engine.preview_calls

    assert action is not None
    assert engine.preview_from(state, action).moved is True
    assert decision_preview_calls <= 6


def test_search_based_fallback_stays_deterministic_when_budget_is_exhausted():
    engine = make_counting_engine()
    bot = create_bot_mode("search_based", engine)
    bot.MAX_EXPLORED_STATES = 1
    state = replace(engine.state, food_position=None)

    first = bot.choose_action(state)
    second = bot.choose_action(state)

    assert first is second
    assert engine.preview_from(state, first).moved is True


def test_search_based_chooses_the_shortest_safe_food_route():
    engine = make_engine(
        width=4,
        height=4,
        start_position=(0, 1),
        body=((1, 1), (2, 1), (2, 2), (2, 3),
              (3, 3), (3, 2), (3, 1)),
        direction=Direction.LEFT,
        food_position=(0, 3),
    )
    bot = create_bot_mode("search_based", engine)

    # Up begins the shortest route that can still continue after eating.
    assert bot.choose_action(engine.state) is Direction.UP


def test_search_based_avoids_food_that_would_trap_its_head():
    engine = make_engine(
        width=4,
        height=3,
        start_position=(3, 1),
        body=((3, 2), (2, 2), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1)),
        direction=Direction.UP,
        food_position=(3, 0),
    )
    bot = create_bot_mode("search_based", engine)

    # Food is one step up, but eating keeps the tail in place and blocks
    # every move afterward. Moving left into the departing tail stays legal.
    assert bot.choose_action(engine.state) is Direction.LEFT


def test_search_based_fallback_does_not_retake_rejected_food():
    engine = make_engine(
        width=4,
        height=4,
        start_position=(2, 3),
        body=((2, 2), (3, 2), (3, 1), (2, 1), (1, 1),
              (0, 1), (0, 0), (1, 0), (2, 0), (3, 0)),
        direction=Direction.DOWN,
        food_position=(1, 3),
    )
    bot = create_bot_mode("search_based", engine)

    # The immediate food route fails the tail check; moving right stays safe.
    assert bot.choose_action(engine.state) is Direction.RIGHT


def test_search_based_fallback_uses_food_distance_when_space_is_equal():
    engine = make_engine(
        width=30,
        height=30,
        start_position=(15, 15),
        direction=Direction.RIGHT,
        food_position=(29, 15),
    )
    bot = create_bot_mode("search_based", engine)

    # The food lies beyond this move's search limit. Right and down offer
    # equal future room, so the bot should make progress toward the food.
    assert bot.choose_action(engine.state) is Direction.RIGHT


def test_search_based_takes_a_full_board_win():
    engine = make_engine(
        width=2,
        height=1,
        start_position=(0, 0),
        direction=Direction.RIGHT,
        food_position=(1, 0),
    )
    bot = create_bot_mode("search_based", engine)

    assert bot.choose_action(engine.state) is Direction.RIGHT
    engine.step()
    assert engine.game_won is True


def test_search_based_returns_no_action_when_every_move_is_unsafe():
    engine = make_engine(
        width=3,
        height=3,
        start_position=(0, 0),
        body=((1, 0), (1, 1), (0, 1), (0, 2)),
        direction=Direction.RIGHT,
        food_position=(2, 2),
    )
    bot = create_bot_mode("search_based", engine)

    assert bot.choose_action(engine.state) is None


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
