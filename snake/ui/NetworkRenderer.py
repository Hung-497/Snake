import arcade
from arcade.types import Color

from snake.ui import Theme
from snake.ui.NetworkLayout import (
    INPUT_LABELS, Area, activation_strength, connection_style, neuron_positions,
    strongest_connections,
)


ACTION_LABELS = {"Straight": "Straight", "Turn_Left": "Left", "Turn_Right": "Right"}
# Room beside the neuron columns for the input and output labels.
INPUT_LABEL_WIDTH = 118
OUTPUT_LABEL_WIDTH = 92
# Connections are drawn in this many strength steps per colour, so all lines of
# one step go to the GPU together instead of one draw call per line.
STRENGTH_STEPS = 5
NEURON_SEGMENTS = 12
CONNECTION_COLORS = {"positive": Theme.PRIMARY, "negative": Theme.FOOD}
NEURON_OFF = Theme.SURFACE_RAISED
NEURON_ON = Theme.SNAKE_BODY
CHOSEN_RING = Theme.SNAKE_HEAD


def with_alpha(color, alpha):
    return Color(color.r, color.g, color.b, int(alpha))


def blend(start, end, amount):
    return Color(*(round(a + (b - a) * amount) for a, b in zip(start[:3], end[:3])))


class NetworkRenderer:
    """
    Draws the Live Training network from a snapshot: neurons glow by activation,
    and the strongest connections are blue (positive) or red (negative).

    Where everything goes comes from NetworkLayout; this only draws.
    """

    def __init__(self, font_size):
        self.input_labels = [self.make_label(text, font_size, "right")
                             for text in INPUT_LABELS]
        self.output_labels = [self.make_label("", font_size, "left") for _ in range(3)]
        self.random_label = self.make_label("random move", font_size, "left")
        self.random_label.color = Theme.WARNING

    @staticmethod
    def make_label(text, font_size, anchor_x):
        return arcade.Text(
            text, x=0, y=0, color=Theme.TEXT_MUTED, font_size=font_size,
            font_name=Theme.FONT_REGULAR, anchor_x=anchor_x, anchor_y="center",
        )

    def set_font_size(self, font_size):
        for label in self.input_labels + self.output_labels + [self.random_label]:
            label.font_size = font_size

    def draw(self, snapshot, area):
        neuron_area = Area(
            area.left + INPUT_LABEL_WIDTH, area.bottom,
            max(1, area.width - INPUT_LABEL_WIDTH - OUTPUT_LABEL_WIDTH), area.height,
        )
        layer_sizes = [len(layer) for layer in snapshot.activations]
        positions = neuron_positions(layer_sizes, neuron_area)
        radius = self.neuron_radius(positions)

        self.draw_connections(snapshot, positions)
        self.draw_neurons(snapshot, positions, radius)
        self.draw_labels(snapshot, positions, radius)

    @staticmethod
    def neuron_radius(positions):
        tallest = max(positions, key=len)
        if len(tallest) < 2:
            return 6
        gap = abs(tallest[0][1] - tallest[1][1])
        return max(2, min(8, gap * 0.4))

    def draw_connections(self, snapshot, positions):
        connections = strongest_connections(snapshot.weights)
        largest = max((abs(weight) for *_, weight in connections), default=0)
        # (sign, strength step) -> the line end points drawn in that style.
        batches = {}
        for layer, from_neuron, to_neuron, weight in connections:
            sign, strength = connection_style(weight, largest)
            step = min(STRENGTH_STEPS - 1, int(strength * STRENGTH_STEPS))
            points = batches.setdefault((sign, step), [])
            points.append(positions[layer][from_neuron])
            points.append(positions[layer + 1][to_neuron])
        for (sign, step), points in sorted(batches.items(), key=lambda item: item[0][1]):
            strength = (step + 1) / STRENGTH_STEPS
            arcade.draw_lines(
                points, with_alpha(CONNECTION_COLORS[sign], 30 + 200 * strength),
                1 + strength,
            )

    def draw_neurons(self, snapshot, positions, radius):
        chosen = snapshot.actions.index(snapshot.chosen_action)
        for layer_index, layer in enumerate(snapshot.activations):
            largest = max((abs(value) for value in layer), default=0)
            is_output = layer_index == len(snapshot.activations) - 1
            for neuron, (x, y) in enumerate(positions[layer_index]):
                if is_output:
                    # Q-values can be negative, so the chosen one glows instead.
                    glow = 1.0 if neuron == chosen else 0.0
                else:
                    glow = activation_strength(layer[neuron], largest)
                arcade.draw_circle_filled(
                    x, y, radius, blend(NEURON_OFF, NEURON_ON, glow),
                    num_segments=NEURON_SEGMENTS,
                )
        x, y = positions[-1][chosen]
        arcade.draw_circle_outline(x, y, radius + 3, CHOSEN_RING, 2)

    def draw_labels(self, snapshot, positions, radius):
        for label, (x, y) in zip(self.input_labels, positions[0]):
            label.x, label.y = x - radius - 6, y
            label.draw()

        chosen = snapshot.actions.index(snapshot.chosen_action)
        q_values = snapshot.activations[-1]
        for index, (label, (x, y)) in enumerate(zip(self.output_labels, positions[-1])):
            label.text = f"{ACTION_LABELS[snapshot.actions[index]]} {q_values[index]:+.1f}"
            label.color = Theme.TEXT if index == chosen else Theme.TEXT_MUTED
            label.x, label.y = x + radius + 6, y
            label.draw()

        if snapshot.explored:
            # Under the outputs, so a random move is not read as the network's choice.
            x, y = positions[-1][-1]
            self.random_label.x = x + radius + 6
            self.random_label.y = y - 2 * self.random_label.font_size - radius
            self.random_label.draw()
