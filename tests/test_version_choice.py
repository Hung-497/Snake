"""Learning Bot Modes are grouped by family, and each version says what it sees."""

from snake.sessions.HumanPlayer import HUMAN_PLAY
from snake.ui.PlayerLabels import (
    BOT_MODE_LABELS, LEARNING_FAMILIES, VERSION_DESCRIPTIONS, bot_mode_choices, player_label,
)
from snake.ui.RecordsBrowser import ALL_PLAYERS
from snake.ui.views.RecordsView import FILTER_CHOICES


def test_play_and_replay_show_each_learning_family_once():
    choices = [(choice.key, choice.label, choice.is_family) for choice in bot_mode_choices()]

    assert choices == [
        ("rule", "Rule Based", False),
        ("q_learning", "Q Learning", True),
        ("hamiltonian", "Hamiltonian", False),
        ("search_based", "Search-Based", False),
        ("dqn", "DQN", True),
    ]


def test_the_q_learning_family_maps_each_version_to_its_bot_mode():
    family = LEARNING_FAMILIES["q_learning"]

    assert family.label == "Q Learning"
    assert family.versions == {"v2": "q_learning", "v3": "q_learning_v3"}
    # Saved Player names do not change, so old Records and Q-tables still work.
    assert set(family.versions.values()) <= set(BOT_MODE_LABELS)


def test_the_dqn_family_maps_each_version_to_its_bot_mode():
    family = LEARNING_FAMILIES["dqn"]

    assert family.label == "DQN"
    # DQN v3 keeps its saved name, so its Records and Replays still work.
    assert family.versions == {"v2": "dqn_v2", "v3": "dqn"}
    assert set(family.versions.values()) <= set(BOT_MODE_LABELS)


def test_every_learning_label_shows_its_version():
    assert player_label("q_learning") == "Q Learning v2"
    assert player_label("q_learning_v3") == "Q Learning v3"
    assert player_label("dqn") == "DQN v3"
    assert player_label("dqn_v2") == "DQN v2"
    assert HUMAN_PLAY not in BOT_MODE_LABELS


def test_every_version_says_what_it_sees():
    assert VERSION_DESCRIPTIONS == {
        "v2": "Sees danger, food, and open space.",
        "v3": "Also checks it can still reach its tail, to avoid trapping itself.",
    }


def test_records_offer_one_filter_per_player_with_its_label():
    values = [value for _, value in FILTER_CHOICES]
    labels = [label for label, _ in FILTER_CHOICES]

    assert values == [ALL_PLAYERS, *BOT_MODE_LABELS, HUMAN_PLAY]
    assert labels == ["All Players", *(player_label(value) for value in values[1:])]
    assert "dqn" in values
    assert "dqn_v2" in values
