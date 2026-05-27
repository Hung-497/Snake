import tkinter as tk
import random

class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.body = [] # multiple snake tiles
    def snake_body(self, canvas, tile_size):
        for tile in self.body:
            tile_x, tile_y = tile
            canvas.create_rectangle(tile_x, tile_y, tile_x + tile_size, tile_y + tile_size, fill = "lime green")

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Movement:
    def __init__(self):
        self.velocity_x = 0
        self.velocity_y = 0

    def change_direction(self, e): # e = event
        if (e.keysym == "Up" and self.velocity_y != 1):
            self.velocity_x = 0
            self.velocity_y = -1
        elif (e.keysym == "Down" and self.velocity_y != -1):
            self.velocity_x = 0
            self.velocity_y = 1
        elif (e.keysym == "Left" and self.velocity_x != 1):
            self.velocity_x = -1
            self.velocity_y = 0
        elif (e.keysym == "Right" and self.velocity_x != -1):
            self.velocity_x = 1
            self.velocity_y = 0

    def move(self, snake, tile_size, food, width, height, game_over):
        ate_food = False
        # check game over
        if (game_over):
            return ate_food, game_over
        
        if (snake.x < 0 or snake.x >= tile_size*width or snake.y < 0 or snake.y >= tile_size*height): # game over whether hitting the wall
            game_over = True
            return ate_food, game_over
        
        for tile in snake.body:
            tile_x, tile_y = tile
            if (snake.x == tile_x and snake.y == tile_y):    # game over whether touching your body
                game_over = True
                return ate_food, game_over

        # check whether snake eats food
        if (snake.x == food.x and snake.y == food.y):
            snake.body.append((food.x,food.y))
            food.x = random.randint(0, width-1) * tile_size
            food.y = random.randint(0, height-1) * tile_size
            ate_food = True

        # update snake body to make it follows the old positions
        for i in range(len(snake.body)-1, -1, -1):
            if (i == 0):
                snake.body[i] = (snake.x, snake.y)
            else:
                snake.body[i] = snake.body[i-1]


        #update snake head position
        snake.x += self.velocity_x * tile_size
        snake.y += self.velocity_y * tile_size
        return ate_food, game_over

class Window:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size

        self.WINDOW_WIDTH = self.tile_size * self.width
        self.WINDOW_HEIGHT = self.tile_size * self.height

        # game window
        self.window = tk.Tk()
        self.window.title('Snake Game')
        self.window.resizable(False,False)
    
    def create_canvas(self):
        self.canvas = tk.Canvas(self.window, bg = 'black', width= self.WINDOW_WIDTH, height = self.WINDOW_HEIGHT, borderwidth = 0, highlightthickness = 0)
        self.canvas.pack()
        self.window.update() # add canvas and update the window

    def center_window(self):
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        window_x = int((screen_width / 2) - (window_width / 2))
        window_y = int((screen_height / 2) - (window_height / 2))
        # format "(w)x(h)+(x)+(y)"
        self.window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}") # update the geometry of the window to center it on the screen

    def draw_snake(self, snake):
        self.canvas.create_rectangle(snake.x, snake.y, snake.x + self.tile_size, snake.y + self.tile_size, fill = "lime green")

    def draw_food(self, food):
        self.canvas.create_rectangle(food.x, food.y, food.x + self.tile_size, food.y + self.tile_size, fill = "red")
    
    def draw_score(self, score, game_over, width, height):
        if (game_over):
            self.canvas.create_text(width/2, height/2, font = 'Arial 20 ', text = f"GAME OVER: {score}", fill = 'white')
        else:
            self.canvas.create_text(30, 20, font = 'Arial 10', text = f"Score: {score}", fill = 'white')
    
    def clear(self):
        self.canvas.delete("all")
    
    def after(self, delay, function):
        self.window.after(delay, function)

    def start(self):
        self.window.mainloop()

class Game:
    def __init__(self):
        self.window = Window(25,25,25)
        self.movement = Movement()

        snake_x = random.randint(0, self.window.width - 1) * self.window.tile_size
        snake_y = random.randint(0, self.window.height - 1) * self.window.tile_size
        self.snake = Snake(snake_x, snake_y)

        food_x = random.randint(0, self.window.width - 1) * self.window.tile_size
        food_y = random.randint(0, self.window.height - 1) * self.window.tile_size
        self.food = Food(food_x, food_y)

        self.game_over = False 
        self.score = 0

    def draw(self):
        self.window.clear()
        self.window.draw_food(self.food)
        self.window.draw_snake(self.snake)
        self.snake.snake_body(self.window.canvas, self.window.tile_size)
        self.window.draw_score(self.score, self.game_over, self.window.WINDOW_WIDTH, self.window.WINDOW_HEIGHT)

    def handle_key_press(self, e):
        if (self.game_over and e.keysym == "space"): # press space to reset the game
            self.reset()
            return
        self.movement.change_direction(e)

    def update(self):
        ate_food, self.game_over = self.movement.move(self.snake, self.window.tile_size, self.food, self.window.width, self.window.height, self.game_over)

        if (ate_food):
            self.score += 1

        self.draw()

        if (self.game_over):
            return

        # Call update again after 100ms
        time_delay = 100 # 100ms = 1/10 second, 10 frames/second
        self.window.after(time_delay, self.update) 
    
    def reset(self):
        snake_x = random.randint(0, self.window.width - 1) * self.window.tile_size
        snake_y = random.randint(0, self.window.height - 1) * self.window.tile_size
        self.snake = Snake(snake_x, snake_y)

        food_x = random.randint(0, self.window.width - 1) * self.window.tile_size
        food_y = random.randint(0, self.window.height - 1) * self.window.tile_size
        self.food = Food(food_x, food_y)

        self.game_over = False
        self.score = 0

        self.movement.velocity_x = 0
        self.movement.velocity_y = 0

        self.draw()
        self.update()

    def run(self):
        self.window.create_canvas()
        self.window.center_window()
        self.window.window.bind("<KeyRelease>", self.handle_key_press) # when you press on any key and then game start
        self.draw()
        self.update()
        self.window.start()

game = Game()
game.run()