from snake.bots.BotMode import BotMode


class RuleBasedBot(BotMode):
    """
    Bot that uses hand-written rules to choose its next move.

    It first tries to find a safe path to the food. If that is not possible,
    it follows its tail. If neither path is available, it moves toward the
    largest reachable open space.
    """

    def choose_action(self, state):
        safe_directions = self.safe_directions(state)

        if (len(safe_directions) == 0):
            return None

        food_path = self._find_path_to_food(state)

        if (len(food_path) > 0 and self._can_escape_after_path(state, food_path)):
            return food_path[0]

        tail_path = self._find_path_to_tail(state)

        if (len(tail_path) > 0):
            return tail_path[0]

        return self._choose_largest_space_move(state)

    def _find_path_to_food(self, state):
        start = self.head_position(state)
        target = self.food_position(state)

        position_to_check = [(start, [])]
        visited_positions = {start}

        while (len(position_to_check) > 0):
            current_position, path = position_to_check.pop(0)

            if (current_position == target):
                return path

            for direction in self.DIRECTIONS:
                next_position = self.position_after(current_position, direction)

                if (next_position in visited_positions):
                    continue

                if (not self.is_inside_board(state, next_position)):
                    continue

                visited_positions.add(next_position)
                position_to_check.append((next_position, path + [direction]))

        return []

    def _find_path_to_tail(self, state):
        body = self.body_positions(state)
        if (len(body) == 0):
            return []

        start = self.head_position(state)
        tail = body[-1]
        body_without_tail = body[:-1]

        position_to_check = [(start, [])]
        visited_positions = {start}

        while (len(position_to_check) > 0):
            current_position, path = position_to_check.pop(0)

            if (current_position == tail):
                return path

            for direction in self.DIRECTIONS:
                next_position = self.position_after(current_position, direction)

                if (next_position in visited_positions):
                    continue

                if (not self.is_inside_board(state, next_position)):
                    continue

                if (next_position in body_without_tail):
                    continue

                visited_positions.add(next_position)
                position_to_check.append((next_position, path + [direction]))

        return []

    def _can_escape_after_path(self, state, path):
        if (len(path) == 0):
            return False

        fake_head = self.head_position(state)
        fake_body = self.body_positions(state)
        food = self.food_position(state)

        for direction in path:
            next_position = self.position_after(fake_head, direction)

            if (next_position == food):
                fake_body = [fake_head] + fake_body
            else:
                fake_body = [fake_head] + fake_body[:-1]

            fake_head = next_position

        if (len(fake_body) == 0):
            return True

        fake_tail = fake_body[-1]
        fake_body_without_tail = fake_body[:-1]

        position_to_check = [fake_head]
        visited_positions = {fake_head}

        while (len(position_to_check) > 0):
            current_position = position_to_check.pop(0)

            if (current_position == fake_tail):
                return True

            for direction in self.DIRECTIONS:
                next_position = self.position_after(current_position, direction)

                if (next_position in visited_positions):
                    continue

                if (not self.is_inside_board(state, next_position)):
                    continue

                if (next_position in fake_body_without_tail):
                    continue

                visited_positions.add(next_position)
                position_to_check.append(next_position)

        return False

    def _count_space_after_move(self, state, direction):
        if (not self.is_safe_direction(state, direction)):
            return 0

        start_position = self.position_after(self.head_position(state), direction)

        position_to_check = [start_position]
        visited_positions = {start_position}

        while (len(position_to_check) > 0):
            current_position = position_to_check.pop(0)

            for next_direction in self.DIRECTIONS:
                check_position = self.position_after(current_position, next_direction)

                if (check_position in visited_positions):
                    continue

                if (not self.is_safe_position(state, check_position)):
                    continue

                visited_positions.add(check_position)
                position_to_check.append(check_position)

        return len(visited_positions)

    def _choose_largest_space_move(self, state):
        safe_directions = self.safe_directions(state)

        if (len(safe_directions) == 0):
            return None

        best_direction = safe_directions[0]
        best_space = -1

        for direction in safe_directions:
            space = self._count_space_after_move(state, direction)

            if (space > best_space):
                best_space = space
                best_direction = direction

        return best_direction
