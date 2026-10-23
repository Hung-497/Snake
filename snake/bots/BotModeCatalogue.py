"""
The Bot Mode catalogue: every fact about each Bot Mode, written once.

Play's buttons, the version screen, where training is saved, the Showcase
Bots, and the terminal commands all read these entries, so adding or
renaming a Bot Mode is one change here. It imports nothing heavy, so the app
and the headless commands can both use it.
"""

from dataclasses import dataclass
from pathlib import Path


LEARNING_DATA = Path("learning_data")
# Finished study bots shipped read-only with the app (ADR 0017).
SHOWCASE_DIRECTORY = Path("starter_data") / "showcase"


@dataclass(frozen=True)
class ShowcaseBot:
    """A finished study bot shipped read-only with the app (ADR 0017)."""

    path: Path
    seed: int

    @property
    def label(self):
        return f"Best of 3 study runs (seed {self.seed})"


@dataclass(frozen=True)
class BotColors:
    """A Bot Mode's chart colour on the app's dark surfaces and on a light page."""

    dark: str
    light: str


@dataclass(frozen=True)
class BotMode:
    """One Bot Mode. The key is its saved name, which never changes (ADR 0013)."""

    key: str
    label: str
    # Learning Bot Modes come in Feature Set versions within a family.
    family: str | None = None
    version: str | None = None
    # Play opens Live Training instead of the Game App View.
    live_training: bool = False
    # Where the app saves this Bot Mode's training.
    save_path: Path | None = None
    # The headless commands' Q-table, copied once to start the app's (ADR 0016).
    shared_q_table: Path | None = None
    showcase: ShowcaseBot | None = None
    # None takes the next spare colour, so a new Bot Mode gets one automatically.
    colors: BotColors | None = None


# For Bot Modes without their own colours, in this order. Each was checked to
# stay easier to tell apart from the others than the closest existing pair.
# When they run out, a Bot Mode is muted until it gets colours of its own.
SPARE_COLORS = (
    BotColors("#7C3AED", "#A855F7"),
    BotColors("#DC2626", "#EF4444"),
    BotColors("#0D9488", "#115E59"),
)

# The learning families Play and Replay show as one button each.
FAMILY_LABELS = {"q_learning": "Q Learning", "dqn": "DQN"}

# In the order Play and Replay list them.
BOT_MODES = (
    BotMode("rule", "Rule Based", colors=BotColors("#F2B84B", "#9A6B00")),
    BotMode(
        "q_learning", "Q Learning v2", family="q_learning", version="v2",
        save_path=LEARNING_DATA / "q_table_app_v2.json",
        shared_q_table=LEARNING_DATA / "q_table_space_state_v2.json",
        showcase=ShowcaseBot(SHOWCASE_DIRECTORY / "q_table_v2_seed12000.json", 12000),
        colors=BotColors("#60A5FA", "#2F5FD0"),
    ),
    BotMode("hamiltonian", "Hamiltonian", colors=BotColors("#34D399", "#0B8A5E")),
    BotMode("search_based", "Search-Based", colors=BotColors("#F472B6", "#BE2D69")),
    BotMode(
        "q_learning_v3", "Q Learning v3", family="q_learning", version="v3",
        save_path=LEARNING_DATA / "q_table_app_v3.json",
        shared_q_table=LEARNING_DATA / "q_table_space_state_v3.json",
        showcase=ShowcaseBot(SHOWCASE_DIRECTORY / "q_table_v3_seed15000.json", 15000),
        colors=BotColors("#22D3EE", "#0B7F9C"),
    ),
    BotMode(
        "dqn", "DQN v3", family="dqn", version="v3", live_training=True,
        save_path=LEARNING_DATA / "dqn_live_training.pt",
        showcase=ShowcaseBot(SHOWCASE_DIRECTORY / "dqn_v3_seed9000.pt", 9000),
        colors=BotColors("#FB923C", "#C9580A"),
    ),
    # The DQN v2 study models were not kept, so it has no Showcase Bot yet.
    BotMode(
        "dqn_v2", "DQN v2", family="dqn", version="v2", live_training=True,
        save_path=LEARNING_DATA / "dqn_v2_live_training.pt",
        colors=BotColors("#A3E635", "#5E8F1F"),
    ),
)

_BOT_MODES_BY_KEY = {mode.key: mode for mode in BOT_MODES}


def bot_mode(key):
    """The catalogue entry for a Bot Mode's saved name."""
    return _BOT_MODES_BY_KEY[key]


def bot_modes_in_family(family):
    return [mode for mode in BOT_MODES if mode.family == family]


def bot_mode_colors(modes=BOT_MODES):
    """Each Bot Mode's colours by key; modes without their own take the spares in order."""
    colors = {}
    spares = iter(SPARE_COLORS)
    for mode in modes:
        color = mode.colors or next(spares, None)
        if color is not None:
            colors[mode.key] = color
    return colors
