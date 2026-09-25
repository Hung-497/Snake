import arcade
from arcade.types import Color

from WindowLayout import HUD_HEIGHT, layout_board


# The board keeps the colours the Tkinter canvas used.
BOARD_COLOR = Color.from_hex_string("#000000")
SNAKE_HEAD_COLOR = Color.from_hex_string("#FFFF00")
SNAKE_BODY_COLOR = Color.from_hex_string("#008000")
FOOD_COLOR = Color.from_hex_string("#FF0000")


class BoardRenderer:
    """
    Draws a Snake board in the window.

    Both the Game and the Replay App Views show the same picture, so both hand
    their board, snake and food to this one renderer. Where the board goes is
    worked out by WindowLayout; this only draws what it is told.
    """

    def __init__(self, window, hud_height=HUD_HEIGHT):
        self.window = window
        self.hud_height = hud_height

    def board_layout(self, board_width, board_height, tile_size):
        return layout_board(
            self.window.width,
            self.window.height,
            board_width,
            board_height,
            tile_size,
            self.hud_height,
        )

    def draw(self, board_width, board_height, tile_size, snake_position, snake_body, food_position):
        layout = self.board_layout(board_width, board_height, tile_size)

        arcade.draw_lbwh_rectangle_filled(
            layout.left, layout.bottom, layout.width, layout.height, BOARD_COLOR
        )

        for body_cell in snake_body:
            self.draw_cell(layout, body_cell, SNAKE_BODY_COLOR)

        self.draw_cell(layout, snake_position, SNAKE_HEAD_COLOR)

        if (food_position is not None):
            self.draw_food(layout, food_position)

    def draw_cell(self, layout, cell, color):
        x, y = layout.cell_to_pixels(cell)
        arcade.draw_lbwh_rectangle_filled(x, y, layout.tile_size, layout.tile_size, color)

    def draw_food(self, layout, food_position):
        x, y = layout.cell_to_pixels(food_position)
        radius = layout.tile_size / 2
        arcade.draw_circle_filled(x + radius, y + radius, radius, FOOD_COLOR)
