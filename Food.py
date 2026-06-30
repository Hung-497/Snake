import random

class Food:
    """
    Represents the food tile.

    Food chooses a random empty tile and avoids spawning on the snake head or
    body.
    """

    def __init__(self, window, snake):
        self.window = window
        self.snake = snake
        self.x = 0
        self.y = 0
        self.spawn_food()
    
    def draw_food(self):
        self.window.canvas.create_oval(
            self.x, 
            self.y, 
            self.x + self.window.tile_size, 
            self.y + self.window.tile_size, 
            fill = 'red',
            outline='', 
            tag = 'food'
            )
    
    def spawn_food(self):
        while True:
            new_x = random.randint(0, self.window.width - 1) * self.window.tile_size
            new_y = random.randint(0, self.window.height - 1) * self.window.tile_size

            if (new_x == self.snake.x and new_y == self.snake.y):
                continue

            if ((new_x, new_y) in self.snake.body):
                continue

            self.x = new_x
            self.y = new_y
            
            return 
