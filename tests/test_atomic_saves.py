import json

import pytest

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine
from snake.storage.ReplayManager import ReplayManager


class SaveInterrupted(Exception):
    """Stands in for Ctrl+C or a crash in the middle of a save."""


@pytest.fixture
def interrupt_saves(monkeypatch):
    """Make the next JSON save stop part-way, after writing only its start."""
    def write_part_then_stop(data, file, **options):
        file.write('{"half": ')
        raise SaveInterrupted

    def start():
        monkeypatch.setattr(json, "dump", write_part_then_stop)

    return start


def make_engine():
    return SnakeEngine(GameConfig(4, 4, 25), start_position=None)


def test_a_q_table_stopped_mid_save_keeps_its_last_complete_save(tmp_path, interrupt_saves):
    table_path = tmp_path / "q_table.json"
    bot = QLearningBot(make_engine(), q_table_file=str(table_path))
    bot.game_trained = 40
    bot.save_q_table()

    bot.game_trained = 41
    interrupt_saves()
    with pytest.raises(SaveInterrupted):
        bot.save_q_table()

    # The table still loads, exactly as the last finished save left it.
    reloaded = QLearningBot(make_engine(), q_table_file=str(table_path), require_saved_table=True)
    assert reloaded.game_trained == 40
    assert [path.name for path in tmp_path.iterdir()] == ["q_table.json"]


def test_a_replay_stopped_mid_save_keeps_the_previous_best(tmp_path, interrupt_saves):
    manager = ReplayManager(folder_name=str(tmp_path))
    manager.start_recording("rule", 4, 4, 25, 10, engine=make_engine())
    manager.save_replay("rule", score=3)

    manager.start_recording("rule", 4, 4, 25, 10, engine=make_engine())
    interrupt_saves()
    with pytest.raises(SaveInterrupted):
        manager.save_replay("rule", score=7)

    # The previous best replay is still complete and readable.
    assert manager.load_replay("rule")["final_score"] == 3
    assert [path.name for path in tmp_path.iterdir()] == ["rule_best.json"]
