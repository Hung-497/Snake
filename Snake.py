import random

class Snake:
    """
    Represents the snake head and body.

    The head is stored as pixel coordinates in x and y. The body is stored as a
    list of previous head positions, also in pixel coordinates.
    """

    def __init__(self, window):
        self.window = window
        self.x = random.randint(0, self.window.width - 1) * self.window.tile_size
        self.y = random.randint(0, self.window.height - 1) * self.window.tile_size
        self.body = []
    
    def draw_snake(self):
        self.window.canvas.create_rectangle(
            self.x, 
            self.y, 
            self.x + self.window.tile_size, 
            self.y + self.window.tile_size, 
            fill = 'yellow', 
            tag = 'snake'
            )
    
    def draw_snake_body(self):
        for x, y in self.body:
            self.window.canvas.create_rectangle(
                x, 
                y, 
                x + self.window.tile_size, 
                y + self.window.tile_size, 
                fill = 'green', 
                tag = 'snake'
                )
    
    def reset(self):
        self.x = random.randint(0, self.window.width - 1) * self.window.tile_size
        self.y = random.randint(0, self.window.height - 1) * self.window.tile_size
        self.body = []
