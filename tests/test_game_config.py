from dataclasses import FrozenInstanceError

import pytest

from GameConfig import GameConfig


def test_game_config_can_be_created_without_a_window():
    config = GameConfig(width=24, height=25, tile_size=25)

    assert config.width == 24
    assert config.height == 25
    assert config.tile_size == 25
    assert config.board_width == 24
    assert config.board_height == 25


@pytest.mark.parametrize(
    ("field", "value"),
    [("width", 0), ("height", -1), ("tile_size", 0), ("width", True)],
)
def test_game_config_rejects_invalid_dimensions_and_tile_size(field, value):
    values = {"width": 4, "height": 4, "tile_size": 25}
    values[field] = value

    with pytest.raises(ValueError, match=field):
        GameConfig(**values)


def test_game_config_is_immutable():
    config = GameConfig(width=4, height=4)

    with pytest.raises(FrozenInstanceError):
        config.width = 5
