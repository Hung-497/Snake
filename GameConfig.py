from dataclasses import dataclass


@dataclass(frozen=True)
class GameConfig:
    """Validated board settings that gameplay can use without a window."""

    width: int
    height: int
    tile_size: int = 25

    def __post_init__(self):
        for name, value in (
            ("width", self.width),
            ("height", self.height),
            ("tile_size", self.tile_size),
        ):
            if (type(value) is not int or value <= 0):
                raise ValueError(f"{name} must be a positive integer")

    @property
    def board_width(self):
        return self.width

    @property
    def board_height(self):
        return self.height
