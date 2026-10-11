"""
Which boards each Player can play on.

The Hamiltonian Bot Mode follows a cycle that visits every cell, and such a
cycle only exists when at least one board side is even. Asking before starting
keeps an unsupported game out of the Game App View.
"""

import pytest

from snake.bots.BotFactory import supports_board


@pytest.mark.parametrize("bot_mode", ["rule", "q_learning", "search_based", "human"])
@pytest.mark.parametrize("board", [(25, 25), (24, 25), (16, 16)])
def test_the_other_players_play_on_any_board(bot_mode, board):
    board_width, board_height = board

    assert supports_board(bot_mode, board_width, board_height)


@pytest.mark.parametrize("board", [(24, 25), (25, 24), (24, 24), (16, 16), (30, 30)])
def test_hamiltonian_plays_on_a_board_with_at_least_one_even_side(board):
    board_width, board_height = board

    assert supports_board("hamiltonian", board_width, board_height)


def test_hamiltonian_cannot_play_on_an_odd_by_odd_board():
    assert not supports_board("hamiltonian", 25, 25)


def test_an_unknown_bot_mode_is_not_blocked_by_this_check():
    assert supports_board("replay", 25, 25)


@pytest.mark.parametrize("bot_mode", ["q_learning", "q_learning_v3", "dqn"])
def test_learning_bot_modes_need_a_free_cell_for_food(bot_mode):
    assert supports_board(bot_mode, 1, 1) is False
    assert supports_board(bot_mode, 2, 1) is True


@pytest.mark.parametrize("board", [(1, 4), (4, 1), (2, 1)])
def test_hamiltonian_cannot_play_on_a_board_one_cell_wide_or_high(board):
    assert supports_board("hamiltonian", *board) is False
