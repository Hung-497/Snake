from snake.bots.HamiltonianBot import HamiltonianBot
from snake.bots.QLearningBot import QLearningBot, QLearningV3Bot
from snake.bots.RuleBasedBot import RuleBasedBot
from snake.bots.SearchBasedBot import SearchBasedBot


BOT_MODE_CLASSES = {
    "rule": RuleBasedBot,
    "q_learning": QLearningBot,
    "hamiltonian": HamiltonianBot,
    "search_based": SearchBasedBot,
    "q_learning_v3": QLearningV3Bot,
}

# Bot Modes that a Bot Experiment includes only when selected with --bots.
OPT_IN_EXPERIMENT_MODES = ("q_learning_v3",)


def normal_experiment_modes():
    """Normal Bot Modes need no optional library and join default experiments."""
    return tuple(
        bot_mode for bot_mode in BOT_MODE_CLASSES
        if bot_mode not in OPT_IN_EXPERIMENT_MODES
    )


def create_bot_mode(bot_mode, engine, random_source=None):
    """Build only the selected Bot Mode, so the others cause no side effects."""
    bot_class = BOT_MODE_CLASSES.get(bot_mode)

    if (bot_class is None):
        return None

    return bot_class(engine, random_source=random_source)


def supports_board(bot_mode, board_width, board_height):
    """
    Can this Bot Mode play on this board?

    The Hamiltonian Bot Mode follows a cycle through every cell, and such a
    cycle only exists when at least one side is even. Learning bots need a
    free cell for food when a game starts.
    """
    if bot_mode in ("q_learning", "q_learning_v3", "dqn") and board_width * board_height < 2:
        return False

    if (bot_mode == "hamiltonian"):
        return (
            board_width >= 2
            and board_height >= 2
            and (board_width % 2 == 0 or board_height % 2 == 0)
        )

    return True
