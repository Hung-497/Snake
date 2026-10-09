"""Faster feature searches must not change what the learning bots learn.

The expected fingerprints were recorded from the code before the searches
were optimized: a fixed-seed training run must still make the same moves and
learn exactly the same Q-table.
"""

import hashlib
import json
import random

import pytest

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine


def training_fingerprint(feature_set, games=40, seed=11, move_limit=400):
    engine = SnakeEngine(
        GameConfig(10, 10), start_position=None, random_source=random.Random(seed),
    )
    bot = QLearningBot(
        engine, random_source=random.Random(seed + 1),
        feature_set=feature_set, q_table_file="unused.json",
    )
    bot.save_q_table = lambda: None
    total_moves = 0
    for game in range(games):
        if game:
            engine.reset()
        moves = 0
        while not engine.game_over and moves < move_limit:
            direction = bot.choose_action(engine.state)
            if direction is not None:
                engine.change_direction(direction)
            transition = engine.preview()
            engine.step()
            bot.observe(transition)
            moves += 1
        bot.on_game_end(engine.state)
        total_moves += moves

    table = json.dumps(
        {bot._state_to_key(state): values for state, values in sorted(bot.q_table.items())},
        sort_keys=True,
    )
    return total_moves, len(bot.q_table), hashlib.sha256(table.encode()).hexdigest()


@pytest.mark.parametrize("feature_set, expected", [
    ("v2", (15222, 49, "86a7125a41bd69beb8c97c2b1227ac59ced878b7434c6ea05945d69e95d0fbb4")),
    ("v3", (15288, 47, "22541528c22173173fcec0d9674ec3e19e5192a708dd1ec5af4f663e5cb7981a")),
])
def test_fixed_seed_training_learns_the_same_q_table(feature_set, expected):
    assert training_fingerprint(feature_set) == expected


def test_features_of_the_same_board_are_computed_once(monkeypatch):
    engine = SnakeEngine(GameConfig(8, 8), start_position=(2, 2), food_position=(5, 5))
    bot = QLearningBot(engine, feature_set="v3", q_table_file="unused.json")
    searches = []
    original = bot._can_reach_tail
    monkeypatch.setattr(
        bot, "_can_reach_tail", lambda *args: searches.append(1) or original(*args),
    )

    first = bot.features(engine.state)
    again = bot.features(engine.state)

    assert first == again
    assert len(searches) == 3
