from BotMode import BotMode
from GameTypes import Direction

class HamiltonianBot(BotMode):
    """
    Bot that follows a Hamiltonian cycle and takes safe shortcuts.

    A Hamiltonian cycle visits every tile on the board exactly once before
    returning to the starting tile. This bot follows that safe route, but can
    take shortcuts when tail reachability and flood fill checks say the move is
    still safe.
    """

    def __init__(self, engine, random_source=None):
        super().__init__(engine, random_source)

        self.board_width = engine.board_width
        self.board_height = engine.board_height
        self.cycle = self._create_cycle()

    def choose_action(self, state):
        if (not self._is_valid_cycle()):
            raise ValueError("Hamiltonian Bot requires a valid Hamiltonian cycle")

        current_tile = self.head_position(state)
        next_tile = self._get_next_tile(current_tile)
        cycle_direction = self._get_direction_from_tile(current_tile, next_tile)

        shortcut_direction = self._get_best_shortcut_direction(state)

        if (shortcut_direction is not None):
            return shortcut_direction

        if (self.is_safe_direction(state, cycle_direction)):
            return cycle_direction

        # A shortcut can land the head just behind its own cycle position, so
        # the next cycle tile is the cell it just came from. Rejoin the cycle
        # at the earliest reachable tile instead of stepping into the body.
        return self._rejoin_cycle_direction(state)

    def _rejoin_cycle_direction(self, state):
        head_index = self._get_cycle_index(self.head_position(state))

        best_direction = None
        best_distance = None

        for direction in self.DIRECTIONS:
            if (not self.is_safe_direction(state, direction)):
                continue

            tile = self._get_tile_after_direction(state, direction)
            distance = self._get_distance_forward(
                head_index,
                self._get_cycle_index(tile),
            )

            if (best_distance is None or distance < best_distance):
                best_distance = distance
                best_direction = direction

        return best_direction

    def _create_cycle(self):
        path = []

        width = self.board_width
        height = self.board_height

        if (width <= 0 or height <= 0):
            return path

        if (width % 2 == 0):
            for column in range(width):
                path.append((column, 0))

            for column in range(width - 1, -1, -1):
                if ((width - 1 - column) % 2 == 0):
                    for row in range(1, height):
                        path.append((column, row))
                else:
                    for row in range(height - 1, 0, -1):
                        path.append((column, row))
        elif (height % 2 == 0):
            for row in range(height):
                path.append((0, row))

            for row in range(height - 1, -1, -1):
                if ((height - 1 - row) % 2 == 0):
                    for column in range(1, width):
                        path.append((column, row))
                else:
                    for column in range(width - 1, 0, -1):
                        path.append((column, row))

        return path

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
            return Direction.RIGHT
        elif (next_column < current_column):
            return Direction.LEFT
        elif (next_row > current_row):
            return Direction.DOWN
        elif (next_row < current_row):
            return Direction.UP

    def _are_neighbors(self, first_tile, second_tile):
        first_column, first_row = first_tile
        second_column, second_row = second_tile

        distance = abs(first_column - second_column) + abs(first_row - second_row)

        return distance == 1

    def _is_valid_cycle(self):
        width = self.board_width
        height = self.board_height
        expected_tile = height * width

        if (width <= 0 or height <= 0):
            return False

        if (not isinstance(self.cycle, (list, tuple))):
            return False

        if (len(self.cycle) != expected_tile):
            return False

        for tile in self.cycle:
            if (
                not isinstance(tile, tuple)
                or len(tile) != 2
                or any(type(value) is not int for value in tile)
            ):
                return False

        if (len(set(self.cycle)) != expected_tile):
            return False

        expected_cells = {
            (column, row)
            for column in range(width)
            for row in range(height)
        }

        if (set(self.cycle) != expected_cells):
            return False

        for index in range(len(self.cycle) - 1):
            current_tile = self.cycle[index]
            next_tile = self.cycle[index + 1]

            if (not self._are_neighbors(current_tile, next_tile)):
                return False

        if (not self._are_neighbors(self.cycle[-1], self.cycle[0])):
            return False

        return True

    def _get_cycle_index(self, tile):
        return self.cycle.index(tile)

    def _get_tail_tile(self, state):
        body = self.body_positions(state)
        if (len(body) == 0):
            return self.head_position(state)

        return body[-1]

    def _get_distance_forward(self, start_index, target_index):
        if (target_index >= start_index):
            return target_index - start_index

        return len(self.cycle) - start_index + target_index

    def _is_ahead_before_tail(self, state, target_tile):
        if (len(self.body_positions(state)) == 0):
            return True

        head_index = self._get_cycle_index(self.head_position(state))
        tail_index = self._get_cycle_index(self._get_tail_tile(state))
        target_index = self._get_cycle_index(target_tile)

        distance_to_target = self._get_distance_forward(head_index, target_index)
        distance_to_tail = self._get_distance_forward(head_index, tail_index)

        return distance_to_target < distance_to_tail

    def _get_tile_after_direction(self, state, direction):
        return self.position_after(self.head_position(state), direction)

    def _get_best_shortcut_direction(self, state):
        best_direction = None
        best_progress = None

        cycle_distance_to_food = self._get_cycle_distance_to_food(state)

        for direction in self.DIRECTIONS:
            if (not self.is_safe_direction(state, direction)):
                continue

            tile = self._get_tile_after_direction(state, direction)

            if (not self._is_ahead_before_tail(state, tile)):
                continue

            cycle_distance_after_move = self._get_cycle_distance_after_direction(
                state,
                direction,
            )

            if (cycle_distance_after_move > cycle_distance_to_food):
                continue

            if (not self._can_reach_tail_after_direction(state, direction)):
                continue

            if (not self._has_enough_space_after_direction(state, direction)):
                continue

            if (best_progress is None or cycle_distance_after_move > best_progress):
                best_direction = direction
                best_progress = cycle_distance_after_move

        return best_direction

    def _get_cycle_distance_after_direction(self, state, direction):
        head_index = self._get_cycle_index(self.head_position(state))
        next_index = self._get_cycle_index(
            self._get_tile_after_direction(state, direction)
        )

        return self._get_distance_forward(head_index, next_index)

    def _get_cycle_distance_to_food(self, state):
        head_index = self._get_cycle_index(self.head_position(state))
        food_index = self._get_cycle_index(self.food_position(state))

        return self._get_distance_forward(head_index, food_index)

    def _body_after_direction(self, direction):
        # The engine's own preview owns the eat-and-tail rule, so the bot does
        # not repeat it.
        return [tuple(position) for position in self.engine.preview(direction).body]

    def _can_reach_tail_after_direction(self, state, direction):
        body_after_move = self._body_after_direction(direction)
        if (len(body_after_move) == 0):
            return True

        start_tile = self._get_tile_after_direction(state, direction)
        tail_tile = body_after_move[-1]
        blocked_tiles = set(body_after_move[:-1])

        position_to_check = [start_tile]
        visited_position = {start_tile}

        while (len(position_to_check) > 0):
            current_tile = position_to_check.pop(0)

            if (current_tile == tail_tile):
                return True

            for next_direction in self.DIRECTIONS:
                next_tile = self.position_after(current_tile, next_direction)

                if (next_tile in visited_position):
                    continue

                if (not self.is_inside_board(state, next_tile)):
                    continue

                if (next_tile in blocked_tiles):
                    continue

                visited_position.add(next_tile)
                position_to_check.append(next_tile)

        return False

    def _count_reachable_space(self, state, start_tile, blocked_tiles):
        position_to_check = [start_tile]
        visited_tiles = {start_tile}
        blocked_tiles = set(blocked_tiles)

        while (len(position_to_check) > 0):
            current_tile = position_to_check.pop(0)

            for direction in self.DIRECTIONS:
                next_tile = self.position_after(current_tile, direction)

                if (next_tile in visited_tiles):
                    continue

                if (next_tile in blocked_tiles):
                    continue

                if (not self.is_inside_board(state, next_tile)):
                    continue

                position_to_check.append(next_tile)
                visited_tiles.add(next_tile)

        return len(visited_tiles)

    def _has_enough_space_after_direction(self, state, direction):
        start_tile = self._get_tile_after_direction(state, direction)
        blocked_tiles = self._body_after_direction(direction)

        reachable_space = self._count_reachable_space(state, start_tile, blocked_tiles)

        snake_size_after_move = len(blocked_tiles) + 1

        return reachable_space >= snake_size_after_move
