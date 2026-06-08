class HamiltonianBot:
    def __init__(self, game):
        self.game = game
        self.cycle = self.create_cycle()
    
    def create_cycle(self):
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
    
    def pixel_to_grid(self, x, y):
        column = x // self.game.window.tile_size
        row = y // self.game.window.tile_size

        return column, row
    
    def get_next_tile(self, current_tile):
        current_index = self.cycle.index(current_tile)
        next_index = current_index + 1

        if (next_index >= len(self.cycle)):
            next_index = 0

        return self.cycle[next_index]
    
    def get_direction_from_tile(self, current_tile, next_tile):
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
        current_tile = self.pixel_to_grid(self.game.snake.x, self.game.snake.y)
        next_tile = self.get_next_tile(current_tile)
        direction = self.get_direction_from_tile(current_tile, next_tile)

        return direction
    
    def are_neighbors(self, first_tile, second_tile):
        first_column, first_row = first_tile
        second_column, second_row = second_tile

        distance = abs(first_column - second_column) + abs(first_row - second_row)

        return distance == 1
    
    def is_valid_cycle(self):
        expected_tile = self.game.window.height * self.game.window.width

        if (len(self.cycle) != expected_tile):
            return False
        
        if (len(set(self.cycle)) != expected_tile):
            return False

        for index in range(len(self.cycle) - 1):
            current_tile = self.cycle[index]
            next_tile = self.cycle[index + 1]

            if (not self.are_neighbors(current_tile, next_tile)):
                return False
            
        if (not self.are_neighbors(self.cycle[-1], self.cycle[0])):
            return False
        
        return True