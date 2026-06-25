from BaseBot import BaseBot

class HamiltonianBot(BaseBot):
    """
    Bot that follows a Hamiltonian cycle and takes safe shortcuts.

    A Hamiltonian cycle visits every tile on the board exactly once before
    returning to the starting tile. This bot follows that safe route, but can
    take shortcuts when tail reachability and flood fill checks say the move is
    still safe.
    """

    def __init__(self, game):
        super().__init__(game)

        self.cycle = self._create_cycle()
    
    def _create_cycle(self):
        path = []

        for column in range(self.game.window.width):
            path.append((column, 0))

        for column in range(self.game.window.width - 1, -1, -1):
            if ((self.game.window.width - 1 - column) % 2 == 0):
                for row in range(1, self.game.window.height):
                    path.append((column, row))
            else: 
                for row in range(self.game.window.height - 1, 0, -1):
                    path.append((column, row))

        return path
    
    def _pixel_to_grid(self, x, y):
        column = x // self.game.window.tile_size
        row = y // self.game.window.tile_size

        return column, row
    
    def _get_next_tile(self, current_tile):
        current_index = self.cycle.index(current_tile)
        next_index = current_index + 1

        if (next_index >= len(self.cycle)):
            next_index = 0

        return self.cycle[next_index]
    
    def _get_direction_from_tile(self, current_tile, next_tile):
        current_column, current_row = current_tile
        next_column, next_row = next_tile

        if (next_column > current_column):
            return "Right"
        elif (next_column < current_column):
            return "Left"
        elif (next_row > current_row):
            return "Down"
        elif (next_row < current_row):
            return "Up"
        
    def get_next_direction(self):
        current_tile = self._pixel_to_grid(self.game.snake.x, self.game.snake.y)
        next_tile = self._get_next_tile(current_tile)
        cycle_direction = self._get_direction_from_tile(current_tile, next_tile)

        shortcut_direction = self._get_best_shortcut_direction()

        if (shortcut_direction is not None):
            return shortcut_direction

        return cycle_direction
    
    def _are_neighbors(self, first_tile, second_tile):
        first_column, first_row = first_tile
        second_column, second_row = second_tile

        distance = abs(first_column - second_column) + abs(first_row - second_row)

        return distance == 1
    
    def _is_valid_cycle(self):
        expected_tile = self.game.window.height * self.game.window.width

        if (len(self.cycle) != expected_tile):
            return False
        
        if (len(set(self.cycle)) != expected_tile):
            return False

        for index in range(len(self.cycle) - 1):
            current_tile = self.cycle[index]
            next_tile = self.cycle[index + 1]

            if (not self._are_neighbors(current_tile, next_tile)):
                return False
            
        if (not self._are_neighbors(self.cycle[-1], self.cycle[0])):
            return False
        
        return True
    
    def _get_cycle_index(self, obj):
        return self.cycle.index(obj)
    
    def _get_head_tile(self):
        snake_tile = self._pixel_to_grid(self.game.snake.x, self.game.snake.y)

        return snake_tile

    def _get_food_tile(self):
        food_tile = self._pixel_to_grid(self.game.food.x, self.game.food.y)

        return food_tile
    
    def _get_tail_tile(self):
        if (len(self.game.snake.body) == 0):
            return self._get_head_tile()
        
        tail_x, tail_y = self.game.snake.body[-1]
        tail_tile = self._pixel_to_grid(tail_x, tail_y)

        return tail_tile
    
    def _get_distance_forward(self, start_index, target_index):
        if (target_index >= start_index):
            return target_index - start_index

        return len(self.cycle) - start_index + target_index
    
    def _is_ahead_before_tail(self, target_tile):
        if (len(self.game.snake.body) == 0):
            return True
        
        head_tile = self._get_head_tile()
        tail_tile = self._get_tail_tile()

        head_index = self._get_cycle_index(head_tile)
        tail_index = self._get_cycle_index(tail_tile)
        target_index = self._get_cycle_index(target_tile)

        distance_to_target = self._get_distance_forward(head_index, target_index)
        distance_to_tail = self._get_distance_forward(head_index, tail_index)

        return distance_to_target < distance_to_tail
    
    def _get_tile_after_direction(self, direction):
        head_tile = self._get_head_tile()
        column, row = head_tile

        if (direction == "Up"):
            row -= 1
        elif (direction == "Down"):
            row += 1
        elif (direction == "Left"):
            column -= 1
        elif (direction == "Right"):
            column += 1
        
        return column, row
    
    def _is_tile_inside_board(self, tile):
        column, row = tile

        x = column * self.game.window.tile_size
        y = row * self.game.window.tile_size
    
        return self._is_inside_board(x, y)
    
    def _get_best_shortcut_direction(self):
        best_direction = None
        best_progress = None

        cycle_distance_to_food = self._get_cycle_distance_to_food()

        for direction in self.DIRECTIONS:
            if (not self._is_immediate_safe_direction(direction)):
                continue

            tile = self._get_tile_after_direction(direction)

            if (not self._is_ahead_before_tail(tile)):
                continue

            cycle_distance_after_move = self._get_cycle_distance_after_direction(direction)

            if (cycle_distance_after_move > cycle_distance_to_food):
                continue

            if (not self._can_reach_tail_after_direction(direction)):
                continue

            if (not self._has_enough_space_after_direction(direction)):
                continue

            if (best_progress is None or cycle_distance_after_move > best_progress):
                best_direction = direction
                best_progress = cycle_distance_after_move

        return best_direction
    
    def _is_immediate_safe_direction(self, direction):
        if (not self._can_turn(direction)):
            return False
        
        tile = self._get_tile_after_direction(direction)

        if (not self._is_tile_inside_board(tile)):
            return False
        
        ate_food = (tile == self._get_food_tile())

        body_tiles = []

        for body_tile in self.game.snake.body:
            grid_tile = self._pixel_to_grid(body_tile[0], body_tile[1])
            body_tiles.append(grid_tile)
        
        if (ate_food):
            body_to_check = body_tiles
        else:
            body_to_check = body_tiles[:-1]

        if (tile in body_to_check):
            return False    
    
        return True
    
    def _get_cycle_distance_after_direction(self, direction):
        head_tile = self._get_head_tile()
        next_tile = self._get_tile_after_direction(direction)

        head_index = self._get_cycle_index(head_tile)
        next_index = self._get_cycle_index(next_tile)

        return self._get_distance_forward(head_index, next_index)
    
    def _get_cycle_distance_to_food(self):
        head_tile = self._get_head_tile()
        food_tile = self._get_food_tile()

        head_index = self._get_cycle_index(head_tile)
        food_index = self._get_cycle_index(food_tile)

        return self._get_distance_forward(head_index, food_index)
    
    def _can_reach_tail_after_direction(self, direction):
        if (len(self.game.snake.body) == 0):
            return True
        
        start_tile = self._get_tile_after_direction(direction)
        tail_tile = self._get_tail_tile()

        body_tiles = []

        for body_x, body_y in self.game.snake.body:
            body_tile = self._pixel_to_grid(body_x, body_y)
            body_tiles.append(body_tile)

        # If we do not eat food, the tail moves away, so ignore the old tail
        if (start_tile != self._get_food_tile()):
            body_tiles = body_tiles[:-1]

        blocked_tiles = set(body_tiles)
        position_to_check = [start_tile]
        visited_position = {start_tile}

        while (len(position_to_check) > 0):
            current_tile = position_to_check.pop(0)

            if (current_tile == tail_tile):
                return True

            column, row = current_tile

            next_tiles = [
                (column, row - 1),
                (column, row + 1),
                (column - 1, row),
                (column + 1, row)
            ]

            for next_tile in next_tiles:
                if (next_tile in visited_position):
                    continue

                if (not self._is_tile_inside_board(next_tile)):
                    continue

                if (next_tile in blocked_tiles):
                    continue

                visited_position.add(next_tile)
                position_to_check.append(next_tile)
            
        return False
        
    def _count_reachable_space(self, start_tile, blocked_tiles):
        position_to_check = [start_tile]
        visited_tiles = {start_tile}
        blocked_tiles = set(blocked_tiles)

        while (len(position_to_check) > 0):
            current_tile = position_to_check.pop(0)
            column, row = current_tile

            next_tiles = [
                (column, row + 1),
                (column, row - 1),
                (column + 1, row),
                (column - 1, row)
            ]

            for next_tile in next_tiles:
                if (next_tile in visited_tiles):
                    continue

                if (next_tile in blocked_tiles):
                    continue

                if (not self._is_tile_inside_board(next_tile)):
                    continue

                position_to_check.append(next_tile)
                visited_tiles.add(next_tile)
        
        return len(visited_tiles)

    def _get_body_tiles_after_direction(self, direction):
        next_tile = self._get_tile_after_direction(direction)
        head_tile = self._get_head_tile()

        body_tiles = []

        for body_x, body_y in self.game.snake.body:
            body_tile = self._pixel_to_grid(body_x, body_y)
            body_tiles.append(body_tile)

        if (next_tile == self._get_food_tile()):
            return [head_tile] + body_tiles
        
        return [head_tile] + body_tiles[:-1]
    
    def _has_enough_space_after_direction(self, direction):
        start_tile = self._get_tile_after_direction(direction)
        blocked_tiles = self._get_body_tiles_after_direction(direction)

        reachable_space = self._count_reachable_space(start_tile, blocked_tiles)

        snake_size_after_move = len(blocked_tiles) + 1

        return reachable_space >= snake_size_after_move
