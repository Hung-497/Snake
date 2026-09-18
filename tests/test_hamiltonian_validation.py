import pytest

from GameConfig import GameConfig
from GameTypes import Direction
from HamiltonianBot import HamiltonianBot
from SnakeEngine import SnakeEngine


def make_engine(width, height):
    return SnakeEngine(
        GameConfig(width=width, height=height, tile_size=25),
        start_position=(0, 0),
        direction=Direction.RIGHT,
    )


def are_adjacent(first_tile, second_tile):
    first_column, first_row = first_tile
    second_column, second_row = second_tile
    return abs(first_column - second_column) + abs(first_row - second_row) == 1


@pytest.mark.parametrize("width, height", [(4, 3), (3, 4), (2, 2)])
def test_supported_board_generates_a_closed_cycle(width, height):
    bot = HamiltonianBot(make_engine(width, height))

    assert len(bot.cycle) == width * height
    assert len(set(bot.cycle)) == width * height
    assert all(
        are_adjacent(bot.cycle[index], bot.cycle[index + 1])
        for index in range(len(bot.cycle) - 1)
    )
    assert are_adjacent(bot.cycle[-1], bot.cycle[0])


def test_odd_by_odd_board_is_rejected_before_direction_is_requested():
    engine = make_engine(3, 3)
    bot = HamiltonianBot(engine)

    with pytest.raises(ValueError, match="valid Hamiltonian cycle"):
        bot.choose_action(engine.state)


def test_invalid_generated_cycle_is_rejected_before_direction_is_requested():
    class InvalidCycleBot(HamiltonianBot):
        def _create_cycle(self):
            return [(0, 0), (0, 0)]

    engine = make_engine(2, 2)
    bot = InvalidCycleBot(engine)

    with pytest.raises(ValueError, match="valid Hamiltonian cycle"):
        bot.choose_action(engine.state)
