from HamiltonianBot import HamiltonianBot
from QLearningBot import QLearningBot
from RuleBasedBot import RuleBasedBot


BOT_MODE_CLASSES = {
    "rule": RuleBasedBot,
    "q_learning": QLearningBot,
    "hamiltonian": HamiltonianBot,
}


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
    cycle only exists when at least one side is even. Every other Bot Mode
    plays on any board.
    """
    if (bot_mode == "hamiltonian"):
        return board_width % 2 == 0 or board_height % 2 == 0

    return True
