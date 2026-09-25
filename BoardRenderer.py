import arcade
from arcade.types import Color

import Theme
from WindowLayout import HUD_HEIGHT, layout_board


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

    def draw(
        self, board_width, board_height, tile_size, snake_position, snake_body,
        food_position, food_scale=1.0, flash_alpha=0,
    ):
        layout = self.board_layout(board_width, board_height, tile_size)

        arcade.draw_lbwh_rectangle_filled(
            layout.left, layout.bottom, layout.width, layout.height, Theme.BOARD_BACKGROUND
        )
        self.draw_grid(layout, board_width, board_height)

        for body_cell in snake_body:
            self.draw_cell(layout, body_cell, Theme.SNAKE_BODY)

        self.draw_cell(layout, snake_position, Theme.SNAKE_HEAD)

        if (food_position is not None):
            self.draw_food(layout, food_position, food_scale)

        # Draw the boundary last so it stays visible beside edge cells.
        inset = Theme.BOARD_FRAME_WIDTH / 2
        arcade.draw_lbwh_rectangle_outline(
            layout.left + inset,
            layout.bottom + inset,
            layout.width - 2 * inset,
            layout.height - 2 * inset,
            Theme.BOARD_FRAME,
            Theme.BOARD_FRAME_WIDTH,
        )

        if flash_alpha > 0:
            flash_color = Color(
                Theme.BOARD_FLASH.r,
                Theme.BOARD_FLASH.g,
                Theme.BOARD_FLASH.b,
                flash_alpha,
            )
            arcade.draw_lbwh_rectangle_filled(
                layout.left, layout.bottom, layout.width, layout.height, flash_color
            )

    def draw_grid(self, layout, board_width, board_height):
        """Draw quiet lines between cells without covering the snake or food."""
        for column in range(1, board_width):
            x, _ = layout.cell_to_pixels((column, 0))
            arcade.draw_line(
                x, layout.bottom, x, layout.bottom + layout.height,
                Theme.BOARD_GRID, Theme.BOARD_GRID_WIDTH,
            )

        for row in range(1, board_height):
            _, y = layout.cell_to_pixels((0, row - 1))
            arcade.draw_line(
                layout.left, y, layout.left + layout.width, y,
                Theme.BOARD_GRID, Theme.BOARD_GRID_WIDTH,
            )

    def draw_cell(self, layout, cell, color):
        x, y = layout.cell_to_pixels(cell)
        arcade.draw_lbwh_rectangle_filled(x, y, layout.tile_size, layout.tile_size, color)

    def draw_food(self, layout, food_position, food_scale):
        x, y = layout.cell_to_pixels(food_position)
        half_tile = layout.tile_size / 2
        radius = half_tile * food_scale
        arcade.draw_circle_filled(x + half_tile, y + half_tile, radius, Theme.FOOD)
