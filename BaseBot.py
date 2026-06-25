class BaseBot:
    """
    Shared parent class for future bot refactors.

    This placeholder will later hold helper methods that every bot can reuse,
    such as direction checks and next-position calculations.
    """

    DIRECTIONS = ["Up", "Down", "Left", "Right"]

    def __init__(self, game):
        self.game = game
    
    def _get_current_position(self):
        return self.game.snake.x, self.game.snake.y
    
    def _get_position_after(self, x, y, direction):
        if (direction == "Up"):
            y -= self.game.window.tile_size
        elif (direction == "Down"):
            y += self.game.window.tile_size
        elif (direction == "Left"):
            x -= self.game.window.tile_size
        elif (direction == "Right"):
            x += self.game.window.tile_size
        
        return x, y
    
    def _get_next_position(self, direction):
        current_x, current_y = self._get_current_position()
        return self._get_position_after(current_x, current_y, direction)
    
    def _is_inside_board(self, x, y):
        if (x < 0 or x >= self.game.window.WINDOW_WIDTH):
            return False
        
        if (y < 0 or y >= self.game.window.WINDOW_HEIGHT):
            return False
        
        return True
    
    def _can_turn(self, direction):
        # prevent reversing direction
        if (direction == "Up" and self.game.movement.velocity_y == 1):
            return False
        elif (direction == "Down" and self.game.movement.velocity_y == -1):
            return False
        elif (direction == "Left" and self.game.movement.velocity_x == 1):
            return False
        elif (direction == "Right" and self.game.movement.velocity_x == -1):
            return False
        
        return True
    
    def _is_safe_direction(self, direction):
        if (not self._can_turn(direction)):
            return False
        
        next_x, next_y = self._get_next_position(direction)

        # check wall collision
        if (not self._is_inside_board(next_x, next_y)):
            return False
        
        # check self collision
        if ((next_x, next_y) in self.game.snake.body):
            return False
        
        return True

    def _is_safe_position(self, x, y):
        if (not self._is_inside_board(x, y)):
            return False
        
        if ((x,y) in self.game.snake.body):
            return False
        
        return True

