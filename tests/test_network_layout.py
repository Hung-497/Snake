"""Where the network graph and the board sit, as plain arithmetic with no display."""

import pytest

from snake.ui.NetworkLayout import (
    BOARD_MARGIN, GRAPH_WIDTH, LIVE_TRAINING_HUD_HEIGHT, MAX_ROW_GAP, MIN_ROW_GAP, Area,
    activation_strength, connection_style, live_training_minimum_size,
    live_training_preferred_size,
    input_labels, live_training_window, neuron_positions, screen_containing, side_by_side_areas,
    strongest_connections,
)
from snake.ui.WindowLayout import MIN_READABLE_TILE_SIZE


def test_the_graph_sits_left_of_the_board_without_overlapping():
    window_width, window_height = live_training_minimum_size(24, 25)

    graph, board = side_by_side_areas(
        window_width, window_height, LIVE_TRAINING_HUD_HEIGHT, 24, 25, tile_size=25
    )

    assert graph.left == 0
    assert graph.width == GRAPH_WIDTH
    assert graph.left + graph.width <= board.left
    assert board.left + board.width <= window_width
    for area in (graph, board):
        assert area.bottom >= 0
        assert area.bottom + area.height <= window_height - LIVE_TRAINING_HUD_HEIGHT


def test_the_minimum_size_fits_the_graph_and_a_readable_board():
    for board_width, board_height in [(16, 16), (24, 25), (30, 30)]:
        window_width, window_height = live_training_minimum_size(board_width, board_height)
        graph, board = side_by_side_areas(
            window_width, window_height, LIVE_TRAINING_HUD_HEIGHT,
            board_width, board_height, tile_size=25,
        )

        assert board.width >= board_width * MIN_READABLE_TILE_SIZE
        assert board.height >= board_height * MIN_READABLE_TILE_SIZE
        # Hidden layers of 64 neurons keep at least MIN_ROW_GAP between neurons.
        hidden = neuron_positions([12, 64, 64, 3], graph)[1]
        assert abs(hidden[0][1] - hidden[1][1]) >= MIN_ROW_GAP


def test_a_larger_board_needs_a_wider_window():
    assert live_training_minimum_size(30, 30)[0] > live_training_minimum_size(16, 16)[0]


SCREEN = Area(left=0, bottom=0, width=1710, height=1107)


def test_a_small_window_grows_to_the_minimum_and_stays_on_its_screen():
    size, minimum, location = live_training_window(
        size=(900, 960), location=(1200, 100), minimum=(1000, 800), screen=SCREEN,
    )

    assert size == (1000, 960)
    assert minimum == (1000, 800)
    # Growing to the right would leave the screen, so the window moves left.
    assert location == (710, 100)


def test_a_large_enough_window_is_left_alone():
    size, minimum, location = live_training_window(
        size=(1300, 1000), location=(50, 40), minimum=(1000, 800), screen=SCREEN,
    )

    assert (size, minimum, location) == ((1300, 1000), (1000, 800), (50, 40))


def test_the_minimum_never_exceeds_the_screen():
    small_screen = Area(left=0, bottom=0, width=900, height=700)

    size, minimum, location = live_training_window(
        size=(800, 600), location=(0, 0), minimum=(1000, 800), screen=small_screen,
    )

    assert minimum == (900, 700)
    assert size == (900, 700)
    assert location == (0, 0)


def test_a_window_on_a_screen_left_of_the_main_one_stays_there():
    built_in = Area(left=-1710, bottom=0, width=1710, height=1107)

    _, _, location = live_training_window(
        size=(900, 960), location=(-1305, 73), minimum=(1000, 800), screen=built_in,
    )

    assert built_in.left <= location[0] <= built_in.left + built_in.width - 1000


def test_neurons_fill_their_layers_from_left_to_right():
    area = Area(left=0, bottom=0, width=400, height=600)

    positions = neuron_positions([12, 64, 64, 3], area)

    assert [len(layer) for layer in positions] == [12, 64, 64, 3]
    layer_x = [layer[0][0] for layer in positions]
    assert layer_x == sorted(layer_x) and len(set(layer_x)) == 4
    for layer in positions:
        assert len({x for x, _ in layer}) == 1
        for x, y in layer:
            assert 0 <= x <= 400 and 0 <= y <= 600


def test_each_layer_is_centred_and_evenly_spaced():
    area = Area(left=10, bottom=20, width=300, height=500)

    small_layer = neuron_positions([3, 64], area)[0]

    ys = sorted(y for _, y in small_layer)
    assert ys[1] - ys[0] == pytest.approx(ys[2] - ys[1])
    assert ys[1] == pytest.approx(20 + 500 / 2)


def test_only_the_strongest_connections_are_kept_in_each_layer():
    weights = [
        [[0.1, -0.9], [0.2, 0.3]],  # layer 0: 2 neurons <- 2 neurons
        [[0.5, -0.05]],             # layer 1: 1 neuron <- 2 neurons
    ]

    kept = strongest_connections(weights, keep_fraction=0.25)

    # (layer, from neuron, to neuron, weight); at least one per layer.
    assert kept == [(0, 1, 0, -0.9), (1, 0, 0, 0.5)]


def test_connection_colour_follows_the_weight_sign_and_size():
    assert connection_style(0.5, largest=1.0) == ("positive", 0.5)
    assert connection_style(-1.0, largest=1.0) == ("negative", 1.0)
    assert connection_style(0.0, largest=0.0) == ("positive", 0.0)


def test_activation_strength_is_between_zero_and_one():
    assert activation_strength(2.0, largest=4.0) == 0.5
    assert activation_strength(9.0, largest=4.0) == 1.0
    assert activation_strength(-3.0, largest=4.0) == 0.0
    assert activation_strength(1.0, largest=0.0) == 0.0


def test_every_feature_set_v3_input_has_a_label():
    labels = input_labels("v3")

    assert len(labels) == 12
    assert labels[:3] == ("Danger straight", "Danger left", "Danger right")
    assert labels[9:] == ("Tail straight", "Tail left", "Tail right")


def test_feature_set_v2_has_nine_labelled_inputs_without_tail():
    assert input_labels("v2") == (
        "Danger straight", "Danger left", "Danger right",
        "Food straight", "Food left", "Food right",
        "Space straight", "Space left", "Space right",
    )


def test_small_layers_spread_out_more_than_large_ones():
    area = Area(left=0, bottom=0, width=400, height=800)

    inputs, hidden, _, outputs = neuron_positions([12, 64, 64, 3], area)

    def gap(layer):
        return abs(layer[0][1] - layer[1][1])

    # So labels beside the inputs and outputs have room and do not overlap.
    assert gap(inputs) > gap(hidden)
    assert gap(outputs) > gap(hidden)
    assert gap(inputs) <= MAX_ROW_GAP


def test_the_window_uses_the_screen_it_is_on_now():
    main = Area(left=0, bottom=0, width=1920, height=1080)
    built_in = Area(left=-1710, bottom=0, width=1710, height=1107)

    assert screen_containing((-1305, 100), (900, 960), [main, built_in]) == built_in
    assert screen_containing((400, 50), (900, 960), [main, built_in]) == main
    # A window off every screen falls back to the first (main) one.
    assert screen_containing((5000, 5000), (900, 960), [main, built_in]) == main


def test_the_preferred_size_fits_the_board_at_its_settings_tile_size():
    width, height = live_training_preferred_size(24, 25, tile_size=25)
    graph, board = side_by_side_areas(
        width, height, LIVE_TRAINING_HUD_HEIGHT, 24, 25, tile_size=25
    )

    assert board.width >= 24 * 25 and board.height >= 25 * 25
    assert (width, height) >= live_training_minimum_size(24, 25)


def test_a_window_grows_to_the_preferred_size_when_the_screen_allows():
    size, minimum, _ = live_training_window(
        size=(900, 700), location=(0, 0), minimum=(936, 762), screen=SCREEN,
        preferred=(1152, 790),
    )

    assert size == (1152, 790)
    assert minimum == (936, 762)


def test_the_preferred_size_is_cut_to_the_screen():
    size, _, _ = live_training_window(
        size=(900, 700), location=(0, 0), minimum=(936, 762), screen=SCREEN,
        preferred=(2400, 1500),
    )

    assert size == (1710, 1107)


def test_a_wider_window_gives_the_extra_width_to_the_graph():
    # The board never draws bigger than its Tile Size, so extra width would
    # otherwise be an empty gap between the graph and the board.
    graph, board = side_by_side_areas(1600, 1000, LIVE_TRAINING_HUD_HEIGHT, 24, 25, tile_size=25)

    assert board.width == 24 * 25
    assert board.left + board.width + BOARD_MARGIN == 1600
    assert graph.width == board.left - BOARD_MARGIN
    assert graph.width > GRAPH_WIDTH
