import arcade
from arcade.types import Color


# The board keeps the colours the Tkinter canvas used.
BOARD_COLOR = Color.from_hex_string("#000000")
SNAKE_HEAD_COLOR = Color.from_hex_string("#FFFF00")
SNAKE_BODY_COLOR = Color.from_hex_string("#008000")
FOOD_COLOR = Color.from_hex_string("#FF0000")

# Room at the top of the window for the score line.
HUD_HEIGHT = 60


class BoardRenderer:
    """
    Draws a Snake board in the window.

    Both the Game App View and the Replay App View show the same picture, so
    both hand their board, snake and food to this one renderer. It is the only
    place in the app that turns grid cells into pixels.
    """

    def __init__(self, window, hud_height=HUD_HEIGHT):
        self.window = window
        self.hud_height = hud_height

    def board_area(self, board_width, board_height, tile_size):
        """Where the board sits in the window, in pixels."""
        board_pixel_width = board_width * tile_size
        board_pixel_height = board_height * tile_size
        left = (self.window.width - board_pixel_width) / 2
        bottom = (self.window.height - self.hud_height - board_pixel_height) / 2

        return left, bottom, board_pixel_width, board_pixel_height

    def cell_to_pixels(self, cell, board_width, board_height, tile_size):
        """
        Turn a grid cell into the pixel corner Arcade draws from.

        Grid rows count downwards from the top, while Arcade's y axis counts
        upwards from the bottom, so the row is flipped here.
        """
        column, row = cell
        left, bottom, _, board_pixel_height = self.board_area(
            board_width, board_height, tile_size
        )

        x = left + column * tile_size
        y = bottom + board_pixel_height - (row + 1) * tile_size

        return x, y

    def draw(self, board_width, board_height, tile_size, snake_position, snake_body, food_position):
        left, bottom, board_pixel_width, board_pixel_height = self.board_area(
            board_width, board_height, tile_size
        )
        arcade.draw_lbwh_rectangle_filled(
            left, bottom, board_pixel_width, board_pixel_height, BOARD_COLOR
        )

        for body_cell in snake_body:
            self.draw_cell(body_cell, board_width, board_height, tile_size, SNAKE_BODY_COLOR)

        self.draw_cell(
            snake_position, board_width, board_height, tile_size, SNAKE_HEAD_COLOR
        )

        if (food_position is not None):
            self.draw_food(food_position, board_width, board_height, tile_size)

    def draw_cell(self, cell, board_width, board_height, tile_size, color):
        x, y = self.cell_to_pixels(cell, board_width, board_height, tile_size)
        arcade.draw_lbwh_rectangle_filled(x, y, tile_size, tile_size, color)

    def draw_food(self, food_position, board_width, board_height, tile_size):
        x, y = self.cell_to_pixels(food_position, board_width, board_height, tile_size)
        radius = tile_size / 2
        arcade.draw_circle_filled(x + radius, y + radius, radius, FOOD_COLOR)
