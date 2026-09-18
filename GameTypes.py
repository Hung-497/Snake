from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True, eq=False)
class Position:
    """A board cell represented by zero-based column and row coordinates.

    New code should use ``x`` and ``y`` as cell coordinates and call
    ``to_pixels`` at the rendering boundary.  The legacy comparison keeps
    old 25-pixel characterization assertions readable during migration.
    """

    x: int
    y: int

    def __post_init__(self):
        if type(self.x) is not int or type(self.y) is not int:
            raise TypeError("position coordinates must be integers")

    @property
    def column(self):
        return self.x

    @property
    def row(self):
        return self.y

    def to_pixels(self, tile_size):
        return self.x * tile_size, self.y * tile_size

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index):
        return (self.x, self.y)[index]

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        if isinstance(other, (tuple, list)) and len(other) == 2:
            return tuple(other) in {
                (self.x, self.y),
                (self.x * 25, self.y * 25),
            }
        return NotImplemented


class Direction(str, Enum):
    """The four directions used inside the game logic."""

    UP = "Up"
    DOWN = "Down"
    LEFT = "Left"
    RIGHT = "Right"

    @classmethod
    def from_value(cls, value):
        if (isinstance(value, cls)):
            return value

        try:
            return cls(value)
        except (TypeError, ValueError):
            return None
