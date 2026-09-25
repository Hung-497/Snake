from snake.bots.BotFactory import create_bot_mode
from snake.sessions.HumanPlayer import HUMAN_PLAY, HumanPlayer


def create_player(player, engine):
    """
    Build whatever controls a game: Human Play, or one of the Bot Modes.

    Bot Experiments and Q Learning training call the Bot Mode factory
    directly, so Human Play never takes part in them.
    """
    if (player == HUMAN_PLAY):
        return HumanPlayer(engine)

    return create_bot_mode(player, engine)
