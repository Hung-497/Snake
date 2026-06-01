class Movement:
    def __init__(self):
        self.velocity_x = 0
        self.velocity_y = 0
    
    def change_direction(self, direction):
        if (direction == "Up" and self.velocity_y != 1):
            self.velocity_x = 0
            self.velocity_y = -1
        elif (direction == "Down" and self.velocity_y != -1):
            self.velocity_x = 0
            self.velocity_y = 1
        elif (direction == "Left" and self.velocity_x != 1):
            self.velocity_x = -1
            self.velocity_y = 0
        elif (direction == "Right" and self.velocity_x != -1):
            self.velocity_x = 1
            self.velocity_y = 0

    def move_snake(self, snake, tile_size, food, width, height, game_over):
        ate_food = False
        
        # check game over
        if (game_over):
            return ate_food, game_over
        
        # game over whether the snake hits the wall
        next_x = snake.x + self.velocity_x * tile_size
        next_y = snake.y + self.velocity_y * tile_size
        if (next_x < 0 or next_x >= width * tile_size or next_y < 0 or next_y >= height * tile_size):
            game_over = True
            return ate_food, game_over
        
        ate_food = (next_x == food.x and next_y == food.y)

        if (ate_food):
            body_to_check = snake.body
        else:
            body_to_check = snake.body[:-1]
        
        # game over whether the snake hits itself
        for tile in body_to_check:
            tile_x, tile_y = tile
            if (next_x == tile_x and next_y == tile_y):
                game_over = True
                return ate_food, game_over

        if (ate_food):
            snake.body = [(snake.x,snake.y)] + snake.body
        elif (len(snake.body) > 0):
            snake.body = [(snake.x,snake.y)] + snake.body[:-1]

        snake.x = next_x
        snake.y = next_y
        
        return ate_food, game_over

    def reset(self):
        self.velocity_x = 0
        self.velocity_y = 0