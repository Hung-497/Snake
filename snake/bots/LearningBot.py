"""Decision rules shared by tabular Q Learning and future DQN Bot Modes.

The nine features and three relative actions deliberately match the saved
Q-table's existing contract. A learning bot supplies action values; this class
handles the state, safety, reward, discount, and exploration rules.
"""

from collections import deque

from snake.bots.BotMode import BotMode
from snake.engine.GameTypes import Direction


# Each Feature Set is a versioned list of observations (see CONTEXT.md).
FEATURE_SETS = ("v2", "v3")
FEATURE_COUNTS = {"v2": 9, "v3": 12}


class LearningBot(BotMode):
    feature_set = "v2"

    def __init__(self, engine, random_source=None, feature_set="v2"):
        super().__init__(engine, random_source)
        if feature_set not in FEATURE_SETS:
            raise ValueError(f"Unknown Feature Set: {feature_set!r}")
        self.feature_set = feature_set
        self.actions = ["Straight", "Turn_Left", "Turn_Right"]
        self.discount_rate = 0.9
        self.epsilon = 1.0
        self.min_epsilon = 0.05
        self.epsilon_decay = 0.997

    def action_direction(self, state, action):
        direction = state.direction
        if action == "Straight":
            return direction
        if action not in ("Turn_Left", "Turn_Right"):
            return None
        if direction == Direction.UP:
            return Direction.LEFT if action == "Turn_Left" else Direction.RIGHT
        if direction == Direction.DOWN:
            return Direction.RIGHT if action == "Turn_Left" else Direction.LEFT
        if direction == Direction.LEFT:
            return Direction.DOWN if action == "Turn_Left" else Direction.UP
        if direction == Direction.RIGHT:
            return Direction.UP if action == "Turn_Left" else Direction.DOWN
        return None

    def _get_direction_from_action(self, state, action):
        return self.action_direction(state, action)

    def get_food_distance(self, state):
        food_position = self.food_position(state)
        if food_position is None:
            return 0
        food_x, food_y = food_position
        head_x, head_y = self.head_position(state)
        return abs(food_x - head_x) + abs(food_y - head_y)

    def _is_danger(self, state, direction):
        next_position = self.position_after(self.head_position(state), direction)
        if not self.is_inside_board(state, next_position):
            return 1

        body = self.body_positions(state)
        # The tail leaves on a normal move, but stays when food is eaten.
        body_to_check = (
            body if next_position == self.food_position(state) else body[:-1]
        )
        return int(next_position in body_to_check)

    def available_actions(self, state):
        safe_actions = []
        for action in self.actions:
            direction = self.action_direction(state, action)
            if self._is_danger(state, direction) == 0:
                safe_actions.append(action)
        return safe_actions

    def _get_safe_actions(self, state):
        return self.available_actions(state)

    def _space_level(self, state, open_space):
        snake_size = len(self.body_positions(state)) + 1
        if open_space < snake_size:
            return 0
        if open_space < snake_size * 2:
            return 1
        return 2

    def _count_reachable_space(self, state, start_position, blocked_positions):
        positions_to_check = [start_position]
        visited_positions = {start_position}
        while positions_to_check:
            current_position = positions_to_check.pop(0)
            for direction in self.DIRECTIONS:
                next_position = self.position_after(current_position, direction)
                if next_position in visited_positions:
                    continue
                if next_position in blocked_positions:
                    continue
                if not self.is_inside_board(state, next_position):
                    continue
                visited_positions.add(next_position)
                positions_to_check.append(next_position)
        return len(visited_positions)

    def _count_space_after_action(self, state, action):
        direction = self.action_direction(state, action)
        next_position = self.position_after(self.head_position(state), direction)
        if self._is_danger(state, direction):
            return 0
        blocked_positions = set(self.body_positions(state))
        return self._count_reachable_space(state, next_position, blocked_positions)

    def features(self, state):
        """Return the observations of this bot's Feature Set.

        v2: nine danger, food-progress, and open-space features.
        v3: the same nine with tail-aware open space, then three
        tail-reachable features.
        """
        if self.feature_set == "v3":
            return self._features_v3(state)
        return self._features_v2(state)

    def _features_v3(self, state):
        v2_features = self._features_v2(state)
        dangers_and_food = v2_features[:6]
        space_levels = []
        tail_reachable = []
        for action in self.actions:
            body_after_move = self._body_after_action(state, action)
            if body_after_move is None:
                space_levels.append(0)
                tail_reachable.append(0)
                continue

            new_head = self._head_after_action(state, action)
            open_space = self._count_space_as_body_moves(
                state, new_head, body_after_move,
            )
            space_levels.append(self._space_level(state, open_space))
            tail_reachable.append(
                self._can_reach_tail(state, new_head, body_after_move)
            )
        return tuple(dangers_and_food) + tuple(space_levels) + tuple(tail_reachable)

    def _head_after_action(self, state, action):
        direction = self.action_direction(state, action)
        return self.position_after(self.head_position(state), direction)

    def _body_after_action(self, state, action):
        """The body (neck first, tail last) after a safe move, or None if unsafe."""
        direction = self.action_direction(state, action)
        if self._is_danger(state, direction):
            return None

        new_head = self._head_after_action(state, action)
        body = [self.head_position(state)] + self.body_positions(state)
        if new_head != self.food_position(state):
            # Without food the tail moves away; eating keeps it in place.
            body = body[:-1]
        return body

    def _count_space_as_body_moves(self, state, new_head, body_after_move):
        """Count cells the head can reach, freeing body cells as the tail moves.

        The segment k cells from the tail end has moved away after k more
        moves, so the head may enter it once it needs at least k moves to
        get there.
        """
        moves_until_free = {
            position: len(body_after_move) - index
            for index, position in enumerate(body_after_move)
        }
        visited_positions = {new_head}
        positions_to_check = deque([(new_head, 0)])
        while positions_to_check:
            current_position, moves = positions_to_check.popleft()
            for direction in self.DIRECTIONS:
                next_position = self.position_after(current_position, direction)
                if next_position in visited_positions:
                    continue
                if not self.is_inside_board(state, next_position):
                    continue
                if moves + 1 < moves_until_free.get(next_position, 0):
                    # Still blocked now; a longer path may reach it later.
                    continue
                visited_positions.add(next_position)
                positions_to_check.append((next_position, moves + 1))
        return len(visited_positions)

    def _can_reach_tail(self, state, new_head, body_after_move):
        """1 if a path leads from the new head to the tail, else 0."""
        if not body_after_move:
            return 1
        tail = body_after_move[-1]
        blocked_positions = set(body_after_move[:-1])
        visited_positions = {new_head}
        positions_to_check = deque([new_head])
        while positions_to_check:
            current_position = positions_to_check.popleft()
            for direction in self.DIRECTIONS:
                next_position = self.position_after(current_position, direction)
                if next_position == tail:
                    return 1
                if next_position in visited_positions:
                    continue
                if next_position in blocked_positions:
                    continue
                if not self.is_inside_board(state, next_position):
                    continue
                visited_positions.add(next_position)
                positions_to_check.append(next_position)
        return 0

    def _features_v2(self, state):
        directions = [self.action_direction(state, action) for action in self.actions]
        dangers = [self._is_danger(state, direction) for direction in directions]
        head = self.head_position(state)
        next_positions = [
            self.position_after(head, direction) for direction in directions
        ]
        current_distance = self.get_food_distance(state)
        food_x, food_y = self.food_position(state)
        food_progress = [
            int(abs(food_x - x) + abs(food_y - y) < current_distance)
            for x, y in next_positions
        ]
        space_levels = [
            self._space_level(state, self._count_space_after_action(state, action))
            for action in self.actions
        ]
        return tuple(dangers + food_progress + space_levels)

    def _get_state(self, state):
        return self.features(state)

    def action_space_level(self, features, action):
        if action == "Straight":
            return features[6]
        if action == "Turn_Left":
            return features[7]
        if action == "Turn_Right":
            return features[8]
        return 0

    def _get_action_space_level(self, features, action):
        return self.action_space_level(features, action)

    def reward(
        self, game_over, ate_food, old_distance, new_distance, action_space_level,
    ):
        if game_over:
            return -100
        if ate_food:
            return 100

        reward = -1
        reward += 5 if new_distance < old_distance else -2
        if action_space_level == 2:
            reward += 2
        elif action_space_level == 0:
            reward -= 8
        return reward

    def _get_reward(
        self, game_over, ate_food, old_distance, new_distance, action_space_level,
    ):
        return self.reward(
            game_over, ate_food, old_distance, new_distance, action_space_level,
        )

    def select_action(self, state, action_values, evaluation_mode=False):
        """Explore safe moves in training; choose the best safe value in evaluation."""
        safe_actions = self.available_actions(state)
        if not safe_actions:
            return self.random_source.choice(self.actions)
        if not evaluation_mode and self.random_source.random() < self.epsilon:
            return self.random_source.choice(safe_actions)

        best_action = safe_actions[0]
        best_value = action_values.get(best_action, 0)
        for action in safe_actions:
            value = action_values.get(action, 0)
            if value > best_value:
                best_action = action
                best_value = value
        return best_action

    def decay_epsilon(self):
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay
        if self.epsilon < self.min_epsilon:
            self.epsilon = self.min_epsilon
