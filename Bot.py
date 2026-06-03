class Bot:
    def __init__(self, game):
        self.game = game
    
    def get_next_direction(self, direction):
        next_x = self.game.snake.x
        next_y = self.game.snake.y

        if (direction == "Up"):
            next_y -= self.game.window.tile_size
        elif (direction == "Down"):
            next_y += self.game.window.tile_size
        elif (direction == "Left"):
            next_x -= self.game.window.tile_size
        elif (direction == "Right"):
            next_x += self.game.window.tile_size

        return next_x, next_y

    def safe_move(self, direction):
        next_x, next_y = self.get_next_direction(direction)

        # check wall collision
        if (next_x < 0 or next_x >= self.game.window.width * self.game.window.tile_size or next_y < 0 or next_y >= self.game.window.height * self.game.window.tile_size):
            return False
        
        # check self collision
        if ((next_x, next_y) in self.game.snake.body):
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
            y -= self.game.window.tile_size
        elif (direction == "Down"):
            y += self.game.window.tile_size
        elif (direction == "Left"):
            x -= self.game.window.tile_size
        elif (direction == "Right"):
            x += self.game.window.tile_size
        
        return x, y
    
    def is_safe_position(self, x, y):
        if (x < 0 or x >= self.game.window.WINDOW_WIDTH):
            return False
        
        if (y < 0 or y >= self.game.window.WINDOW_HEIGHT):
            return False
        
        if ((x,y) in self.game.snake.body):
            return False
        
        return True

    def find_path_to_food(self):
        start = (self.game.snake.x, self.game.snake.y)
        target = (self.game.food.x, self.game.food.y)

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
        if (len(self.game.snake.body) == 0):
            return []
        
        start = (self.game.snake.x, self.game.snake.y)
        tail = self.game.snake.body[-1]
        body_without_tail = self.game.snake.body[:-1]

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

                if (next_x < 0 or next_x >= self.game.window.WINDOW_WIDTH or next_y < 0 or next_y >= self.game.window.WINDOW_HEIGHT):
                    continue

                if (next_position in body_without_tail):
                    continue

                visited_positions.add(next_position)
                position_to_check.append((next_position, path + [direction]))
            
        return []
    
    def can_escape_after_path(self, path):
        if (len(path) == 0):
            return False
        
        fake_head_x = self.game.snake.x
        fake_head_y = self.game.snake.y
        fake_body = self.game.snake.body.copy()

        for direction in path:
            next_x, next_y = self.get_position_after(fake_head_x, fake_head_y, direction)
            
            ate_food = (next_x == self.game.food.x and next_y == self.game.food.y)

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

                if (next_x < 0 or next_x >= self.game.window.WINDOW_WIDTH or next_y < 0 or next_y >= self.game.window.WINDOW_HEIGHT):
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
            self.game.movement.change_direction(food_path[0])
            return
        
        tail_path = self.find_path_to_tail()
        
        if (len(tail_path) > 0):
            self.game.movement.change_direction(tail_path[0])
            return
        
        largest_space_move = self.choose_largest_space_move()

        if (largest_space_move != None):
            self.game.movement.change_direction(largest_space_move)