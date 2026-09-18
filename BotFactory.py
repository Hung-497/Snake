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
