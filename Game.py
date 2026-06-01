import random
from Snake import Snake
from Food import Food
from Window import Window
from Movement import Movement

class Game:
    def __init__(self, window, snake, food, movement):
        self.window = window
        self.snake = snake
        self.food = food
        self.movement = movement

        self.score = 0
        self.game_over = False
    
    def draw(self):
        self.window.clear_canvas()
        self.window.update_score_label(self.score)
        self.food.draw_food()
        self.snake.draw_snake()
        self.snake.draw_snake_body()
    
    def update(self):
        self.bot_change_direction()

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
    

    # ------ Adding bot ------
    def get_next_direction(self, direction):
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

    def safe_move(self, direction):
        next_x, next_y = self.get_next_direction(direction)

        # check wall collision
        if (next_x < 0 or next_x >= self.window.width * self.window.tile_size or next_y < 0 or next_y >= self.window.height * self.window.tile_size):
            return False
        
        # check self collision
        if ((next_x, next_y) in self.snake.body):
            return False
        
        return True
    
    def get_safe_directions(self):
        safe_directions = []

        for direction in ["Up", "Down", "Left", "Right"]:
            if (self.safe_move(direction)):
                safe_directions.append(direction)

        return safe_directions
    
    def get_position_after(self, x, y, direction):
        if (direction == "Up"):
            y -= self.window.tile_size
        elif (direction == "Down"):
            y += self.window.tile_size
        elif (direction == "Left"):
            x -= self.window.tile_size
        elif (direction == "Right"):
            x += self.window.tile_size
        
        return x, y
    
    def is_safe_position(self, x, y):
        if (x < 0 or x >= self.window.WINDOW_WIDTH):
            return False
        
        if (y < 0 or y >= self.window.WINDOW_HEIGHT):
            return False
        
        if ((x,y) in self.snake.body):
            return False
        
        return True

    def find_path_to_food(self):
        start = (self.snake.x, self.snake.y)
        target = (self.food.x, self.food.y)

        position_to_check = [((start), [])]
        visited_positions = {start}

        while (len(position_to_check) > 0):
            current_position, path = position_to_check.pop(0)
            current_x, current_y = current_position

            if (current_x == target[0] and current_y == target[1]):
                return path
            
            for direction in ["Up", "Down", "Left", "Right"]:
                next_x, next_y = self.get_position_after(current_x, current_y, direction)
                next_position = (next_x, next_y)

                if (next_position in visited_positions):
                    continue

                if (not self.is_safe_position(next_x, next_y)):
                    continue

                visited_positions.add(next_position)
                position_to_check.append((next_position, path + [direction]))
            
        return []
    
    def find_path_to_tail(self):
        if (len(self.snake.body) == 0):
            return []
        
        start = (self.snake.x, self.snake.y)
        tail = self.snake.body[-1]
        body_without_tail = self.snake.body[:-1]

        position_to_check = [((start), [])]
        visited_positions = {start}

        while (len(position_to_check) > 0):
            current_position, path = position_to_check.pop(0)
            current_x, current_y = current_position

            if (current_x == tail[0] and current_y == tail[1]):
                return path
            
            for direction in ["Up", "Down", "Left", "Right"]:
                next_x, next_y = self.get_position_after(current_x, current_y, direction)
                next_position = (next_x, next_y)

                if (next_position in visited_positions):
                    continue

                if (next_x < 0 or next_x >= self.window.WINDOW_WIDTH or next_y < 0 or next_y >= self.window.WINDOW_HEIGHT):
                    continue

                if (next_position in body_without_tail):
                    continue

                visited_positions.add(next_position)
                position_to_check.append((next_position, path + [direction]))
            
        return []
    
    def can_escape_after_path(self, path):
        if (len(path) == 0):
            return False
        
        fake_head_x = self.snake.x
        fake_head_y = self.snake.y
        fake_body = self.snake.body.copy()

        for direction in path:
            next_x, next_y = self.get_position_after(fake_head_x, fake_head_y, direction)
            
            ate_food = (next_x == self.food.x and next_y == self.food.y)

            if (ate_food):
                fake_body = [(fake_head_x, fake_head_y)] + fake_body
            else:
                fake_body = [(fake_head_x, fake_head_y)] + fake_body[:-1]

            fake_head_x = next_x
            fake_head_y = next_y
        
        if (len(fake_body) == 0):
            return True
        
        fake_tail = fake_body[-1]
        fake_body_without_tail = fake_body[:-1]

        position_to_check = [((fake_head_x, fake_head_y), [])]
        visited_positions = {(fake_head_x, fake_head_y)}

        while (len(position_to_check) > 0):
            current_position, path_to_tail = position_to_check.pop(0)
            current_x, current_y = current_position

            if (current_x == fake_tail[0] and current_y == fake_tail[1]):
                return True
            
            for direction in ["Up", "Down", "Left", "Right"]:
                next_x, next_y = self.get_position_after(current_x, current_y, direction)
                next_position = (next_x, next_y)

                if (next_position in visited_positions):
                    continue

                if (next_x < 0 or next_x >= self.window.WINDOW_WIDTH or next_y < 0 or next_y >= self.window.WINDOW_HEIGHT):
                    continue

                if (next_position in fake_body_without_tail):
                    continue

                visited_positions.add(next_position)
                position_to_check.append((next_position, path_to_tail + [direction]))
            
        return False

    def count_space_after_move(self, direction):
        next_x, next_y = self.get_next_direction(direction)

        if (not self.safe_move(direction)):
            return 0
        
        position_to_check = [(next_x, next_y)]
        visited_positions = {(next_x, next_y)}

        while (len(position_to_check) > 0):
            current_x, current_y = position_to_check.pop(0)
            
            for next_direction in ["Up", "Down", "Left", "Right"]:
                check_x, check_y = self.get_position_after(current_x, current_y, next_direction)
                check_position = (check_x, check_y)

                if (check_position in visited_positions):
                    continue

                if (not self.is_safe_position(check_x, check_y)):
                    continue

                visited_positions.add(check_position)
                position_to_check.append(check_position)
            
        return len(visited_positions)
    
    def choose_largest_space_move(self):
        safe_directions = self.get_safe_directions()

        if (len(safe_directions) == 0):
            return None
        
        best_direction = safe_directions[0]
        best_space = -1

        for direction in safe_directions:
            space = self.count_space_after_move(direction)

            if (space > best_space):
                best_space = space
                best_direction = direction
        
        return best_direction
    
    def bot_change_direction(self):
        safe_directions = self.get_safe_directions()

        if (len(safe_directions) == 0):
            return
        
        food_path = self.find_path_to_food()

        if (len(food_path) > 0 and self.can_escape_after_path(food_path)):
            self.movement.change_direction(food_path[0])
            return
        
        tail_path = self.find_path_to_tail()
        
        if (len(tail_path) > 0):
            self.movement.change_direction(tail_path[0])
            return
        
        largest_space_move = self.choose_largest_space_move()

        if (largest_space_move != None):
            self.movement.change_direction(largest_space_move)


        



