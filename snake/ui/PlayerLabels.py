"""
The names shown to the user for each Player.

A Player is whoever controls a game: one of the Bot Modes or Human Play. The
two maps are kept apart on purpose. The Play and Replay App Views build one
button per Bot Mode, so a Player that is not a Bot Mode must never be added
to BOT_MODE_LABELS by accident.
"""

from snake.sessions.HumanPlayer import HUMAN_PLAY


# The name the Bot Mode factory uses -> the name shown to the user.
BOT_MODE_LABELS = {
    "rule": "Rule Based",
    "q_learning": "Q Learning",
    "hamiltonian": "Hamiltonian",
    "search_based": "Search-Based",
    "q_learning_v3": "Q Learning v3",
    "dqn": "DQN",
}

# Bot Modes that Play opens in Live Training instead of the Game App View.
LIVE_TRAINING_BOT_MODES = ("dqn",)

# Every Player the app can show, keyed by the name saved in records and replays.
PLAYER_LABELS = dict(BOT_MODE_LABELS)
PLAYER_LABELS[HUMAN_PLAY] = "Human"


def app_view_for_bot_mode(bot_mode):
    """The App View Play opens for a Bot Mode: Live Training for DQN, else the game."""
    return "live_training" if bot_mode in LIVE_TRAINING_BOT_MODES else "game"


def player_label(player):
    """The name shown for a Player, or the saved name itself if it is unknown."""
    return PLAYER_LABELS.get(player, player)
