"""Train a Q Learning Bot Mode in Play, on its own app Q-table (ADR 0016).

A new app training plays the same games and learns the same table as
`TrainQLearning --new-table` with the default seed and move limit, so
watching in the app and training in the terminal agree.
"""

from pathlib import Path
import random

from snake.bots.BotFactory import BOT_MODE_CLASSES
from snake.engine.SnakeEngine import SnakeEngine
from snake.sessions.GameSession import GameSession
from snake.sessions.TrainingSaves import SAVE_PATHS, saved_training


# The same defaults as TrainQLearning's --seed and --max-moves.
SEED = 0
MAX_MOVES = 5000


def start_q_learning_training(settings, bot_mode, game_limit=None, table_path=None):
    """Continue this Q Learning's app training, or start it fresh on the Settings board.

    A fresh start stops at game_limit; a continued one keeps the limit it
    started with. Raises ValueError when the saved table cannot be read, so
    it is never overwritten by an empty one.
    """
    table_path = Path(SAVE_PATHS[bot_mode] if table_path is None else table_path)
    summary = saved_training(bot_mode, save_path=table_path)
    games_so_far = 0
    if summary is not None:
        games_so_far = summary.games or 0
        game_limit = summary.game_limit

    # Each session continues from where the table stopped, so a continued
    # training does not replay the food of its first games. A new one starts
    # at the command's seeds: SEED for the food and SEED + 1 for the bot.
    engine = SnakeEngine(
        settings.build_game_config(), start_position=None,
        random_source=random.Random(SEED + games_so_far),
    )
    session_description = {
        "source": "app", "seed": SEED, "max_moves": MAX_MOVES, "game_limit": game_limit,
    }
    bot = BOT_MODE_CLASSES[bot_mode](
        engine,
        random_source=random.Random(SEED + 1 + games_so_far),
        require_saved_table=summary is not None,
        q_table_file=str(table_path),
        session=session_description,
    )
    return GameSession(
        engine, bot_mode, settings.speed_delay_for(bot_mode), bot=bot,
        max_moves=MAX_MOVES, game_limit=game_limit,
    )
