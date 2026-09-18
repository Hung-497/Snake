import json

import pytest

from GameConfig import GameConfig
from GameTypes import Direction
from ReplayManager import ReplayCompatibilityError, ReplayManager
from SnakeEngine import SnakeEngine


def make_engine():
    return SnakeEngine(
        GameConfig(width=4, height=3, tile_size=20),
        start_position=(1, 1),
        direction=Direction.RIGHT,
        food_position=(2, 1),
    )


def test_new_replays_declare_grid_schema_and_store_cell_positions(tmp_path):
    manager = ReplayManager(folder_name=str(tmp_path))

    manager.start_recording("rule", 4, 3, 20, 1, engine=make_engine())
    manager.record_move(Direction.RIGHT)

    assert manager.replay_data["schema_version"] == 2
    assert manager.replay_data["coordinate_system"] == "grid"
    assert manager.replay_data["start_snake"] == [1, 1]
    assert manager.replay_data["start_food"] == [2, 1]
    assert manager.replay_data["moves"] == [4]


def test_legacy_pixel_replay_is_migrated_to_grid_cells(tmp_path):
    manager = ReplayManager(folder_name=str(tmp_path))
    path = manager.get_replay_file_path("rule")
    path_data = {
        "bot_name": "rule",
        "board_width": 4,
        "board_height": 3,
        "tile_size": 20,
        "speed_delay": 1,
        "start_snake": [20, 20],
        "start_food": [40, 20],
        "moves": [4],
        "foods": [[40, 20], [60, 20]],
        "final_score": 1,
    }
    with open(path, "w") as file:
        json.dump(path_data, file)

    replay = manager.load_replay("rule")

    assert replay["schema_version"] == 2
    assert replay["coordinate_system"] == "grid"
    assert replay["start_snake"] == [1, 1]
    assert replay["start_food"] == [2, 1]
    assert replay["foods"] == [[2, 1], [3, 1]]


@pytest.mark.parametrize(
    "payload",
    [
        {"schema_version": 99, "coordinate_system": "grid"},
        {"schema_version": 2, "coordinate_system": "pixels"},
        {"schema_version": 2, "coordinate_system": "grid", "start_snake": [4, 0]},
    ],
)
def test_unsupported_or_malformed_replays_report_compatibility_failure(
    tmp_path, payload
):
    manager = ReplayManager(folder_name=str(tmp_path))
    path = manager.get_replay_file_path("rule")
    with open(path, "w") as file:
        json.dump(payload, file)

    with pytest.raises(ReplayCompatibilityError):
        manager.load_replay("rule")


def test_misaligned_legacy_pixel_replay_is_not_silently_read_as_grid(tmp_path):
    manager = ReplayManager(folder_name=str(tmp_path))
    path = manager.get_replay_file_path("rule")
    with open(path, "w") as file:
        json.dump(
            {
                "board_width": 4,
                "board_height": 3,
                "tile_size": 20,
                "speed_delay": 1,
                "start_snake": [1, 1],
                "start_food": [40, 20],
                "moves": [],
                "foods": [[40, 20]],
                "final_score": 0,
            },
            file,
        )

    with pytest.raises(ReplayCompatibilityError, match="pixel"):
        manager.load_replay("rule")
