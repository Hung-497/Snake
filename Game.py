import random
from Snake import Snake
from Food import Food
from Window import Window
from Movement import Movement
from Bot import Bot

class Game:
    def __init__(self, window, snake, food, movement):
        self.window = window
        self.snake = snake
        self.food = food
        self.movement = movement

        self.bot = Bot(self)

        self.score = 0
        self.game_over = False
    
    def draw(self):
        self.window.clear_canvas()
        self.window.update_score_label(self.score)
        self.food.draw_food()
        self.snake.draw_snake()
        self.snake.draw_snake_body()
    
    def update(self):
        self.bot.bot_change_direction()

        ate_food, self.game_over = self.movement.move_snake(
            self.snake, 
            self.window.tile_size, 
            self.food, 
            self.window.width, 
            self.window.height, 
            self.game_over
        )

        if (ate_food):
            self.score += 1
            self.food.spawn_food()
        
        self.draw()

        if (self.game_over):
            self.window.draw_game_over(self.score, self.game_over)
            return
        
        # Call update again
        time_delay = 50 # milliseconds
        self.window.window.after(time_delay, self.update)
    
    def run(self):
        self.window.draw_score_label()
        self.window.create_canvas()
        self.window.center_window()

        self.window.window.bind("<Key>", self.handle_key_press)

        self.draw()
        self.update()
        self.window.start()

    def reset(self):
        self.score = 0
        self.game_over = False

        self.snake.reset()
        self.food.spawn_food()
        self.movement.reset()

        self.draw()
        self.update()

    def handle_key_press(self, e):
        if (self.game_over and e.keysym == "space"): # press space to reset the game
            self.reset()
            return