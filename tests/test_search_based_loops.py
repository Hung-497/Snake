import random

import pytest

from snake.bots.BotFactory import create_bot_mode
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine


MOVE_LIMIT = 2000


# On these seeds the bot used to fold into a hairpin next to the food and
# circle its own tail forever: the check "can I still reach my tail after
# eating?" ran out of search budget, and running out counted as "unsafe".
@pytest.mark.parametrize("seed", [2, 8, 10, 12, 22, 24, 34])
def test_search_based_never_repeats_a_situation_without_eating(seed):
    engine = SnakeEngine(
        GameConfig(width=8, height=8, tile_size=20),
        start_position=None,
        random_source=random.Random(seed),
    )
    bot = create_bot_mode("search_based", engine, random_source=random.Random(seed + 1))

    # The bot uses no randomness and food only moves when it is eaten, so a
    # repeated situation means the snake would repeat the same moves forever.
    situations_since_food = set()
    moves = 0
    while (not engine.game_over and moves < MOVE_LIMIT):
        state = engine.state
        situation = (
            state.snake_position, state.snake_body, state.direction, state.food_position
        )
        assert situation not in situations_since_food, (
            f"loop at move {moves} with score {state.score}"
        )
        situations_since_food.add(situation)

        direction = bot.choose_action(state)
        if (direction is not None):
            engine.change_direction(direction)
        transition = engine.preview()
        engine.step()
        bot.observe(transition)
        moves += 1

        if (transition.ate_food):
            situations_since_food.clear()
