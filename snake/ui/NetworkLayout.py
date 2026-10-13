"""
Where the Live Training network graph goes, and how strongly each part is drawn.

Like WindowLayout, this is plain arithmetic: no Arcade, no window, and no
PyTorch, so it is tested without a display.
"""

from dataclasses import dataclass
import math

from snake.ui.WindowLayout import MIN_READABLE_TILE_SIZE


# Feature Set v3 inputs, in the order the network receives them.
INPUT_LABELS = (
    "Danger straight", "Danger left", "Danger right",
    "Food straight", "Food left", "Food right",
    "Space straight", "Space left", "Space right",
    "Tail straight", "Tail left", "Tail right",
)
# The graph's width in the side-by-side layout; the board gets the rest.
GRAPH_WIDTH = 520
# Room at the top of Live Training for the title, stats and controls lines.
LIVE_TRAINING_HUD_HEIGHT = 100
# Space kept around the board inside its area.
BOARD_MARGIN = 16
# Each layer keeps this share of its connections, the largest by size.
KEEP_FRACTION = 0.12
AREA_MARGIN = 16
# Small layers spread out to fit their labels, but no further apart than this.
MAX_ROW_GAP = 40
# The largest layers need at least this gap to read as separate neurons.
MIN_ROW_GAP = 10
LARGEST_LAYER = 64


@dataclass(frozen=True)
class Area:
    left: float
    bottom: float
    width: float
    height: float


def side_by_side_areas(window_width, window_height, hud_height,
                       board_width, board_height, tile_size):
    """Split the space under the HUD: the graph on the left, the board on the right.

    The board never draws bigger than its Tile Size, so it takes only the
    width it needs at that size and the graph gets all the rest. In a narrow
    window the graph keeps GRAPH_WIDTH and the board shrinks instead.
    """
    usable_height = window_height - hud_height
    board_area_width = min(
        window_width - GRAPH_WIDTH, board_width * tile_size + 2 * BOARD_MARGIN
    )
    graph_width = window_width - board_area_width
    graph = Area(0, 0, graph_width, usable_height)
    board = Area(
        graph_width + BOARD_MARGIN, BOARD_MARGIN,
        max(1, board_area_width - 2 * BOARD_MARGIN),
        max(1, usable_height - 2 * BOARD_MARGIN),
    )
    return graph, board


def live_training_minimum_size(board_width, board_height):
    """The smallest window that fits the whole graph and a readable board."""
    return live_training_preferred_size(board_width, board_height, MIN_READABLE_TILE_SIZE)


def live_training_preferred_size(board_width, board_height, tile_size):
    """A window that fits the whole graph and the board at this Tile Size."""
    graph_height = (LARGEST_LAYER - 1) * MIN_ROW_GAP + 2 * AREA_MARGIN
    board_pixel_height = board_height * tile_size + 2 * BOARD_MARGIN
    return (
        GRAPH_WIDTH + board_width * tile_size + 2 * BOARD_MARGIN,
        LIVE_TRAINING_HUD_HEIGHT + max(graph_height, board_pixel_height),
    )


def screen_containing(location, size, screens):
    """The screen holding the window's centre, or the first screen if none does."""
    centre_x = location[0] + size[0] / 2
    centre_y = location[1] + size[1] / 2
    for screen in screens:
        if (screen.left <= centre_x < screen.left + screen.width
                and screen.bottom <= centre_y < screen.bottom + screen.height):
            return screen
    return screens[0]


def live_training_window(size, location, minimum, screen, preferred=None):
    """Grow the window to the preferred size (or at least the minimum) and keep
    it on its screen.

    Returns the new size, the minimum to enforce, and the new location. The
    minimum never exceeds the screen, so a small screen still fits the window.
    Locations are the window's top-left corner in screen coordinates.
    """
    minimum = (min(minimum[0], screen.width), min(minimum[1], screen.height))
    target = preferred if preferred is not None else minimum
    size = (
        min(max(size[0], minimum[0], target[0]), screen.width),
        min(max(size[1], minimum[1], target[1]), screen.height),
    )
    x = max(screen.left, min(location[0], screen.left + screen.width - size[0]))
    y = max(screen.bottom, min(location[1], screen.bottom + screen.height - size[1]))
    return size, minimum, (x, y)


def neuron_positions(layer_sizes, area):
    """One column per layer, each centred vertically with even gaps between neurons.

    Each layer uses the full height, so small layers spread out more, up to
    MAX_ROW_GAP.
    """
    inner_left = area.left + AREA_MARGIN
    inner_width = max(0, area.width - 2 * AREA_MARGIN)
    inner_height = max(0, area.height - 2 * AREA_MARGIN)
    column_gap = inner_width / max(1, len(layer_sizes) - 1)
    middle_y = area.bottom + area.height / 2

    positions = []
    for layer_index, size in enumerate(layer_sizes):
        x = inner_left + layer_index * column_gap
        row_gap = min(MAX_ROW_GAP, inner_height / max(1, size - 1))
        first_y = middle_y + (size - 1) * row_gap / 2
        positions.append([(x, first_y - row * row_gap) for row in range(size)])
    return positions


def strongest_connections(weights, keep_fraction=KEEP_FRACTION):
    """The largest weights of each layer as (layer, from, to, weight), at least one each."""
    kept = []
    for layer_index, matrix in enumerate(weights):
        connections = [
            (layer_index, from_neuron, to_neuron, weight)
            for to_neuron, row in enumerate(matrix)
            for from_neuron, weight in enumerate(row)
        ]
        keep = max(1, math.ceil(len(connections) * keep_fraction))
        connections.sort(key=lambda connection: abs(connection[3]), reverse=True)
        kept.extend(connections[:keep])
    return kept


def connection_style(weight, largest):
    """Blue for positive and red for negative weights, stronger when larger."""
    sign = "negative" if weight < 0 else "positive"
    strength = min(1.0, abs(weight) / largest) if largest > 0 else 0.0
    return sign, strength


def activation_strength(value, largest):
    """How brightly a neuron glows, from 0 (off) to 1 (the most active)."""
    if largest <= 0:
        return 0.0
    return min(1.0, max(0.0, value / largest))


# --- Network focus layout: zoom and pan ------------------------------------

MIN_ZOOM = 1.0
MAX_ZOOM = 8.0


@dataclass(frozen=True)
class ZoomPan:
    """How far the focus layout is zoomed in, and how far it has been dragged."""

    zoom: float = 1.0
    offset_x: float = 0
    offset_y: float = 0


def focus_area(window_width, window_height, hud_height):
    """In the focus layout the graph gets the whole window under the HUD."""
    return Area(0, 0, window_width, window_height - hud_height)


def to_screen(view, point, area):
    """Where a graph point is drawn: scaled from the area's centre, then moved."""
    centre_x = area.left + area.width / 2
    centre_y = area.bottom + area.height / 2
    return (
        centre_x + (point[0] - centre_x) * view.zoom + view.offset_x,
        centre_y + (point[1] - centre_y) * view.zoom + view.offset_y,
    )


def zoom_at(view, factor, point, area):
    """Zoom by a factor while the graph point under the mouse stays put."""
    centre_x = area.left + area.width / 2
    centre_y = area.bottom + area.height / 2
    # The graph point currently drawn at the mouse position.
    graph_x = (point[0] - centre_x - view.offset_x) / view.zoom + centre_x
    graph_y = (point[1] - centre_y - view.offset_y) / view.zoom + centre_y
    zoom = min(MAX_ZOOM, max(MIN_ZOOM, view.zoom * factor))
    zoomed = ZoomPan(
        zoom,
        point[0] - centre_x - (graph_x - centre_x) * zoom,
        point[1] - centre_y - (graph_y - centre_y) * zoom,
    )
    return pan_by(zoomed, 0, 0, area)


def pan_by(view, dx, dy, area):
    """Drag the graph, stopping when its edge reaches the area's edge."""
    # A graph zoom times as big can move this far from the centre each way.
    limit_x = (view.zoom - 1) * area.width / 2
    limit_y = (view.zoom - 1) * area.height / 2
    return ZoomPan(
        view.zoom,
        min(limit_x, max(-limit_x, view.offset_x + dx)),
        min(limit_y, max(-limit_y, view.offset_y + dy)),
    )
