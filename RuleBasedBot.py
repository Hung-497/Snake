from BaseBot import BaseBot

class RuleBasedBot(BaseBot):
    """
    Bot that uses hand-written rules to choose its next move.

    It first tries to find a safe path to the food. If that is not possible,
    it follows its tail. If neither path is available, it moves toward the
    largest reachable open space.
    """
    
    def _get_safe_directions(self):
        safe_directions = []

        for direction in self.DIRECTIONS:
            if (self._is_safe_direction(direction)):
                safe_directions.append(direction)

        return safe_directions

    def _find_path_to_food(self):
        start = (self.game.snake.x, self.game.snake.y)
        target = (self.game.food.x, self.game.food.y)

        position_to_check = [((start), [])]
        visited_positions = {start}

        while (len(position_to_check) > 0):
            current_position, path = position_to_check.pop(0)
            current_x, current_y = current_position

            if (current_x == target[0] and current_y == target[1]):
                return path
            
            for direction in self.DIRECTIONS:
                next_x, next_y = self._get_position_after(current_x, current_y, direction)
                next_position = (next_x, next_y)

                if (next_position in visited_positions):
                    continue

                if (not self._is_inside_board(next_x, next_y)):
                    continue

                visited_positions.add(next_position)
                position_to_check.append((next_position, path + [direction]))
            
        return []
    
    def _find_path_to_tail(self):
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
            
            for direction in self.DIRECTIONS:
                next_x, next_y = self._get_position_after(current_x, current_y, direction)
                next_position = (next_x, next_y)

                if (next_position in visited_positions):
                    continue

                if (not self._is_inside_board(next_x, next_y)):
                    continue

                if (next_position in body_without_tail):
                    continue

                visited_positions.add(next_position)
                position_to_check.append((next_position, path + [direction]))
            
        return []
    
    def _can_escape_after_path(self, path):
        if (len(path) == 0):
            return False
        
        fake_head_x = self.game.snake.x
        fake_head_y = self.game.snake.y
        fake_body = self.game.snake.body.copy()

        for direction in path:
            next_x, next_y = self._get_position_after(fake_head_x, fake_head_y, direction)
            
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
            
            for direction in self.DIRECTIONS:
                next_x, next_y = self._get_position_after(current_x, current_y, direction)
                next_position = (next_x, next_y)

                if (next_position in visited_positions):
                    continue

                if (not self._is_inside_board(next_x, next_y)):
                    continue

                if (next_position in fake_body_without_tail):
                    continue

                visited_positions.add(next_position)
                position_to_check.append((next_position, path_to_tail + [direction]))
            
        return False

    def _count_space_after_move(self, direction):
        next_x, next_y = self._get_next_position(direction)

        if (not self._is_safe_direction(direction)):
            return 0
        
        position_to_check = [(next_x, next_y)]
        visited_positions = {(next_x, next_y)}

        while (len(position_to_check) > 0):
            current_x, current_y = position_to_check.pop(0)
            
            for next_direction in self.DIRECTIONS:
                check_x, check_y = self._get_position_after(current_x, current_y, next_direction)
                check_position = (check_x, check_y)

                if (check_position in visited_positions):
                    continue

                if (not self._is_safe_position(check_x, check_y)):
                    continue

                visited_positions.add(check_position)
                position_to_check.append(check_position)
            
        return len(visited_positions)
    
    def _choose_largest_space_move(self):
        safe_directions = self._get_safe_directions()

        if (len(safe_directions) == 0):
            return None
        
        best_direction = safe_directions[0]
        best_space = -1

        for direction in safe_directions:
            space = self._count_space_after_move(direction)

            if (space > best_space):
                best_space = space
                best_direction = direction
        
        return best_direction
    
    def get_next_direction(self):
        safe_directions = self._get_safe_directions()

        if (len(safe_directions) == 0):
            return None
        
        food_path = self._find_path_to_food()

        if (len(food_path) > 0 and self._can_escape_after_path(food_path)):
            return food_path[0]
        
        tail_path = self._find_path_to_tail()
        
        if (len(tail_path) > 0):
            return tail_path[0]
        
        largest_space_move = self._choose_largest_space_move()

        return largest_space_move
