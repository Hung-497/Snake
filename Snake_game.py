import tkinter as tk
import random

class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.body = [] # multiple snake tiles
    
class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Movement:
    def __init__(self):
        self.velocity_x = 0
        self.velocity_y = 0

    def change_direction_from_text(self, direction): # direction is a string, "Up", "Down", "Left", "Right"
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

    def move(self, snake, tile_size, food, width, height, game_over):
        ate_food = False
        # check game over
        if (game_over):
            return ate_food, game_over
        
        next_x = snake.x + self.velocity_x * tile_size
        next_y = snake.y + self.velocity_y * tile_size

        if (next_x < 0 or next_x >= tile_size * width or next_y < 0 or next_y >= tile_size * height):
            game_over = True
            return ate_food, game_over

        ate_food = (next_x == food.x and next_y == food.y)

        if (ate_food):
            body_to_check = snake.body
        else:
            body_to_check = snake.body[:-1]

        for tile in body_to_check:
            tile_x, tile_y = tile
            if (next_x == tile_x and next_y == tile_y):
                game_over = True
                return ate_food, game_over

        if (ate_food):
            snake.body = [(snake.x, snake.y)] + snake.body
        elif (len(snake.body) > 0):
            snake.body = [(snake.x, snake.y)] + snake.body[:-1]

        snake.x = next_x
        snake.y = next_y

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
        # draw the snake head
        self.canvas.create_rectangle(snake.x, snake.y, snake.x + self.tile_size, snake.y + self.tile_size, fill = "yellow")
    
    def snake_body(self, snake):
        # draw the snake body
        for tile in snake.body:
            tile_x, tile_y = tile
            self.canvas.create_rectangle(tile_x, tile_y, tile_x + self.tile_size, tile_y + self.tile_size, fill = "lime green")

    def draw_food(self, food):
        # draw the food
        self.canvas.create_rectangle(food.x, food.y, food.x + self.tile_size, food.y + self.tile_size, fill = "red")
    
    def draw_score(self, score, game_over, width, height):
        # draw the score at the top left corner, and if game over, draw the game over message at the center of the window
        if (game_over):
            self.canvas.create_text(width/2, height/2, font = 'Arial 20 ', text = f"GAME OVER: {score}", fill = 'white')
        else:
            self.canvas.create_text(30, 20, font = 'Arial 10', text = f"Score: {score}", fill = 'white')
    
    def clear(self): # clear the canvas for the next frame
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
        self.snake = Snake(snake_x, snake_y) # initialize the snake at a random position

        self.food = self.spawn_food() # initialize the food at a random position

        self.game_over = False 
        self.score = 0

    def draw(self):
        self.window.clear()
        self.window.draw_food(self.food)
        self.window.draw_snake(self.snake)
        self.window.snake_body(self.snake)
        self.window.draw_score(self.score, self.game_over, self.window.WINDOW_WIDTH, self.window.WINDOW_HEIGHT)

    def change_direction(self, e):
        self.movement.change_direction_from_text(e.keysym)

    def get_next_position(self, direction): # get next position from the snake head
        next_x = self.snake.x
        next_y = self.snake.y

        if (direction == "Up"):
            next_y -= self.window.tile_size
        elif (direction == "Down"):
            next_y += self.window.tile_size
        elif (direction == "Left"):
            next_x -= self.window.tile_size
        elif (direction == "Right"):
            next_x += self.window.tile_size

        return next_x, next_y
    
    def get_position_after(self, x, y, direction): # get next position from any x, y
        if (direction == "Up"):
            y -= self.window.tile_size
        elif (direction == "Down"):
            y += self.window.tile_size
        elif (direction == "Left"):
            x -= self.window.tile_size
        elif (direction == "Right"):
            x += self.window.tile_size

        return x, y
    
    def is_safe_position(self, x, y): # check whether the position is safe for the snake to move to
        # check whether the next move will hit the wall
        if (x < 0 or x >= self.window.WINDOW_WIDTH):
            return False
        if (y < 0 or y >= self.window.WINDOW_HEIGHT):
            return False
        
        # check whether the next move will hit the snake body
        if ((x, y) in self.snake.body):
            return False
        
        return True

    def is_safe_position_with_body(self, x, y, body): # check a position using a simulated body
        if (x < 0 or x >= self.window.WINDOW_WIDTH):
            return False
        if (y < 0 or y >= self.window.WINDOW_HEIGHT):
            return False
        if ((x, y) in body):
            return False
        return True

    def get_body_after_move(self, direction): # simulate one move without changing the real snake
        next_x, next_y = self.get_next_position(direction)
        ate_food = (next_x == self.food.x and next_y == self.food.y)

        if (ate_food):
            new_body = [(self.snake.x, self.snake.y)] + self.snake.body
        else:
            new_body = [(self.snake.x, self.snake.y)] + self.snake.body[:-1]

        return next_x, next_y, new_body
    
    def is_opposite_direction(self, first_direction, second_direction): # check whether two directions are opposite
        if (first_direction == "Up" and second_direction == "Down"):
            return True
        elif (first_direction == "Down" and second_direction == "Up"):
            return True
        elif (first_direction == "Left" and second_direction == "Right"):
            return True
        elif (first_direction == "Right" and second_direction == "Left"):
            return True
        return False
    
    def count_safe_moves(self, first_direction): # count the number of safe moves after the first move in the given direction, which can be used to evaluate how good the first move is
        count = 0
        
        first_x, first_y = self.get_next_position(first_direction)

        for direction in ["Up", "Down", "Left", "Right"]:
            if (self.is_opposite_direction(first_direction, direction)):
                continue

            next_x = first_x
            next_y = first_y

            if (direction == "Up"):
                next_y -= self.window.tile_size
            elif (direction == "Down"):
                next_y += self.window.tile_size
            elif (direction == "Left"):
                next_x -= self.window.tile_size
            elif (direction == "Right"):
                next_x += self.window.tile_size
            
            if (next_x < 0 or next_x >= self.window.WINDOW_WIDTH):
                continue
            if (next_y < 0 or next_y >= self.window.WINDOW_HEIGHT):
                continue
            
            if ((next_x, next_y) in self.snake.body):
                continue

            count += 1

        return count

    def count_reachable_space_after(self, first_direction): # count how much space is reachable after one move
        start_x, start_y, new_body = self.get_body_after_move(first_direction)

        if (not self.is_safe_position_with_body(start_x, start_y, new_body)):
            return 0
        
        positions_to_check = [(start_x, start_y)]
        visited_positions = {(start_x, start_y)}

        while (len(positions_to_check) > 0):
            current_x, current_y = positions_to_check.pop(0)

            for direction in ["Up", "Down", "Left", "Right"]:
                next_x, next_y = self.get_position_after(current_x, current_y, direction)

                if ((next_x, next_y) in visited_positions):
                    continue

                if (not self.is_safe_position_with_body(next_x, next_y, new_body)):
                    continue

                visited_positions.add((next_x, next_y))
                positions_to_check.append((next_x, next_y))

        return len(visited_positions)

    def can_reach_food(self, first_direction):
        start_x, start_y, new_body = self.get_body_after_move(first_direction)

        if (not self.is_safe_position_with_body(start_x, start_y, new_body)):
            return False
        
        positions_to_check = [(start_x, start_y)]
        visited_positions = {(start_x, start_y)}

        while (len(positions_to_check) > 0):
            current_x, current_y = positions_to_check.pop(0)

            if (current_x == self.food.x and current_y == self.food.y):
                return True
            
            for direction in ["Up", "Down", "Left", "Right"]:
                next_x, next_y = self.get_position_after(current_x, current_y, direction)

                if ((next_x, next_y) in visited_positions):
                    continue

                if (not self.is_safe_position_with_body(next_x, next_y, new_body)):
                    continue

                visited_positions.add((next_x, next_y))
                positions_to_check.append((next_x, next_y))
        return False

    def can_escape_after(self, first_direction): # check whether the snake can still reach its tail after one move
        start_x, start_y, new_body = self.get_body_after_move(first_direction)

        if (not self.is_safe_position_with_body(start_x, start_y, new_body)):
            return False

        if (len(new_body) == 0):
            return True

        tail_x, tail_y = new_body[-1]
        body_without_tail = new_body[:-1]

        positions_to_check = [(start_x, start_y)]
        visited_positions = {(start_x, start_y)}

        while (len(positions_to_check) > 0):
            current_x, current_y = positions_to_check.pop(0)

            if (current_x == tail_x and current_y == tail_y):
                return True

            for direction in ["Up", "Down", "Left", "Right"]:
                next_x, next_y = self.get_position_after(current_x, current_y, direction)

                if ((next_x, next_y) in visited_positions):
                    continue

                if (not self.is_safe_position_with_body(next_x, next_y, body_without_tail)):
                    continue

                visited_positions.add((next_x, next_y))
                positions_to_check.append((next_x, next_y))

        return False
    
    def distance_to_food_after(self, direction): # measure distance to food after a possible move
        next_x, next_y = self.get_next_position(direction)

        distance_x = abs(self.food.x - next_x)
        distance_y = abs(self.food.y - next_y)

        return (distance_x + distance_y) // self.window.tile_size
    
    def distance_to_food_now(self):
        distance_x = abs(self.food.x - self.snake.x)
        distance_y = abs(self.food.y - self.snake.y)

        return (distance_x + distance_y) // self.window.tile_size
    
    def safe_move(self, direction): # check safety
        # check whether the next move is safe 
        if (not self.can_turn(direction)):
            return False
        
        next_x, next_y = self.get_next_position(direction)

        if (next_x < 0 or next_x >= self.window.WINDOW_WIDTH):
            return False
        if (next_y < 0 or next_y >= self.window.WINDOW_HEIGHT):
            return False

        ate_food = (next_x == self.food.x and next_y == self.food.y)

        if (ate_food):
            body_to_check = self.snake.body
        else:
            body_to_check = self.snake.body[:-1]

        if ((next_x, next_y) in body_to_check):
            return False

        return True
    
    def can_turn(self, direction): # make sure it cannot turn back to the opposite direction
        if (direction == "Up" and self.movement.velocity_y == 1): # if the snake is currently moving down, it cannot turn up
            return False
        elif (direction == "Down" and self.movement.velocity_y == -1): # if the snake is currently moving up, it cannot turn down
            return False
        elif (direction == "Left" and self.movement.velocity_x == 1): # if the snake is currently moving right, it cannot turn left
            return False
        elif (direction == "Right" and self.movement.velocity_x == -1): # if the snake is currently moving left, it cannot turn right
            return False
        return True 

    def spawn_food(self):
        while True:
            food_x = random.randint(0, self.window.width - 1) * self.window.tile_size
            food_y = random.randint(0, self.window.height - 1) * self.window.tile_size

            if (food_x == self.snake.x and food_y == self.snake.y):
                continue

            if ((food_x, food_y) in self.snake.body):
                continue

            return Food(food_x, food_y)

    def bot_change_direction(self):
        directions = []

        if (self.food.x > self.snake.x):
            directions.append("Right")
        elif (self.food.x < self.snake.x):
            directions.append("Left")

        if (self.food.y > self.snake.y):
            directions.append("Down")
        elif (self.food.y < self.snake.y):
            directions.append("Up")

        directions.append("Up")
        directions.append("Down")
        directions.append("Left")
        directions.append("Right")

        unique_directions = []
        for direction in directions:
            if direction not in unique_directions:
                unique_directions.append(direction)
                
        directions = unique_directions

        best_direction = None
        best_score = -999999 # comparing score
        current_distance = self.distance_to_food_now()

        for direction in directions: # score each safe direction and choose the best one
            if (self.safe_move(direction)):
                safe_count = self.count_safe_moves(direction)
                food_distance = self.distance_to_food_after(direction)
                can_reach_food = self.can_reach_food(direction)
                can_escape = self.can_escape_after(direction)
                reachable_space = self.count_reachable_space_after(direction)

                score = reachable_space
                score += safe_count * 10
                score -= food_distance

                if (food_distance == 0):
                    score += 60

                if (food_distance < current_distance):  # more rewards if closer the food, avoid food which spam near the wall
                    score += 20 

                if (can_reach_food): # more rewards if can reach the food, avoid food which is blocked by the snake body
                    score += 15
                else:
                    score -= 50

                if (can_escape): # more rewards if the snake can still escape after this move
                    score += 80
                else:
                    score -= 200

                if (score > best_score):
                    best_score = score
                    best_direction = direction
            
        if (best_direction != None):
            self.movement.change_direction_from_text(best_direction)


    def update(self):
        self.bot_change_direction()

        ate_food, self.game_over = self.movement.move(self.snake, self.window.tile_size, self.food, self.window.width, self.window.height, self.game_over)

        if (ate_food):
            self.score += 1
            self.food = self.spawn_food()

        self.draw()

        if (self.game_over):
            return

        # Call update again after 100ms
        time_delay = 50 # 50ms = 1/20 second, 20 frames/second
        self.window.after(time_delay, self.update) 
    
    def reset(self):
        snake_x = random.randint(0, self.window.width - 1) * self.window.tile_size
        snake_y = random.randint(0, self.window.height - 1) * self.window.tile_size
        self.snake = Snake(snake_x, snake_y)

        self.food = self.spawn_food()

        self.game_over = False
        self.score = 0

        self.movement.velocity_x = 0
        self.movement.velocity_y = 0

        self.draw()
        self.update()

    def run(self):
        self.window.create_canvas()
        self.window.center_window()
        self.draw()
        self.update()
        self.window.start()

game = Game()
game.run()
