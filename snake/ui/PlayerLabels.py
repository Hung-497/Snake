"""
The names shown to the user for each Player.

A Player is whoever controls a game: one of the Bot Modes or Human Play. The
two maps are kept apart on purpose. The Play and Replay App Views build one
button per Bot Mode, so a Player that is not a Bot Mode must never be added
to BOT_MODE_LABELS by accident.
"""

from dataclasses import dataclass

from snake.bots.BotModeCatalogue import BOT_MODES, FAMILY_LABELS, bot_modes_in_family
from snake.sessions.HumanPlayer import HUMAN_PLAY


# The name the Bot Mode factory uses -> the name shown to the user.
# Learning Bot Modes name their Feature Set version, so every screen says which
# version a game used. The saved names on the left never change (ADR 0013).
BOT_MODE_LABELS = {mode.key: mode.label for mode in BOT_MODES}


@dataclass(frozen=True)
class LearningFamily:
    """A learning Bot Mode that comes in Feature Set versions."""

    label: str
    # Feature Set version -> the Bot Mode name saved in Records and Replays.
    versions: dict


# Play and Replay show one button per family, then a Choose a version screen.
LEARNING_FAMILIES = {
    family: LearningFamily(label, {
        mode.version: mode.key
        for mode in sorted(bot_modes_in_family(family), key=lambda mode: mode.version)
    })
    for family, label in FAMILY_LABELS.items()
}

# What each Feature Set version sees, shown on the Choose a version screen.
VERSION_DESCRIPTIONS = {
    "v2": "Sees danger, food, and open space.",
    "v3": "Also checks it can still reach its tail, to avoid trapping itself.",
}


@dataclass(frozen=True)
class BotModeChoice:
    """One button in Play or Replay: a single Bot Mode or a learning family."""

    key: str
    label: str
    is_family: bool


def bot_mode_choices():
    """The Play and Replay buttons, in Bot Mode order, with each family once."""
    family_of = {
        bot_mode: family_key
        for family_key, family in LEARNING_FAMILIES.items()
        for bot_mode in family.versions.values()
    }
    choices = []
    for bot_mode, label in BOT_MODE_LABELS.items():
        family_key = family_of.get(bot_mode)
        if family_key is None:
            choices.append(BotModeChoice(bot_mode, label, False))
        elif all(choice.key != family_key for choice in choices):
            choices.append(
                BotModeChoice(family_key, LEARNING_FAMILIES[family_key].label, True)
            )
    return choices

# Bot Modes that Play opens in Live Training instead of the Game App View.
LIVE_TRAINING_BOT_MODES = tuple(mode.key for mode in BOT_MODES if mode.live_training)

# Every Player the app can show, keyed by the name saved in records and replays.
PLAYER_LABELS = dict(BOT_MODE_LABELS)
PLAYER_LABELS[HUMAN_PLAY] = "Human"


def app_view_for_bot_mode(bot_mode_key):
    """The App View Play opens for a Bot Mode: Live Training for DQN, else the game."""
    return "live_training" if bot_mode_key in LIVE_TRAINING_BOT_MODES else "game"


def player_label(player):
    """The name shown for a Player, or the saved name itself if it is unknown."""
    return PLAYER_LABELS.get(player, player)
