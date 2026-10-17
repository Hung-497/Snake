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


# The learning families Play and Replay show as one button each.
FAMILY_LABELS = {"q_learning": "Q Learning", "dqn": "DQN"}

# In the order Play and Replay list them.
BOT_MODES = (
    BotMode("rule", "Rule Based"),
    BotMode(
        "q_learning", "Q Learning v2", family="q_learning", version="v2",
        save_path=LEARNING_DATA / "q_table_app_v2.json",
        shared_q_table=LEARNING_DATA / "q_table_space_state_v2.json",
        showcase=ShowcaseBot(SHOWCASE_DIRECTORY / "q_table_v2_seed12000.json", 12000),
    ),
    BotMode("hamiltonian", "Hamiltonian"),
    BotMode("search_based", "Search-Based"),
    BotMode(
        "q_learning_v3", "Q Learning v3", family="q_learning", version="v3",
        save_path=LEARNING_DATA / "q_table_app_v3.json",
        shared_q_table=LEARNING_DATA / "q_table_space_state_v3.json",
        showcase=ShowcaseBot(SHOWCASE_DIRECTORY / "q_table_v3_seed15000.json", 15000),
    ),
    BotMode(
        "dqn", "DQN v3", family="dqn", version="v3", live_training=True,
        save_path=LEARNING_DATA / "dqn_live_training.pt",
        showcase=ShowcaseBot(SHOWCASE_DIRECTORY / "dqn_v3_seed9000.pt", 9000),
    ),
    # The DQN v2 study models were not kept, so it has no Showcase Bot yet.
    BotMode(
        "dqn_v2", "DQN v2", family="dqn", version="v2", live_training=True,
        save_path=LEARNING_DATA / "dqn_v2_live_training.pt",
    ),
)

_BOT_MODES_BY_KEY = {mode.key: mode for mode in BOT_MODES}


def bot_mode(key):
    """The catalogue entry for a Bot Mode's saved name."""
    return _BOT_MODES_BY_KEY[key]


def bot_modes_in_family(family):
    return [mode for mode in BOT_MODES if mode.family == family]
