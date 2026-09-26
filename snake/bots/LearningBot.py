"""Decision rules shared by tabular Q Learning and future DQN Bot Modes.

The nine features and three relative actions deliberately match the saved
Q-table's existing contract. A learning bot supplies action values; this class
handles the state, safety, reward, discount, and exploration rules.
"""

from snake.bots.BotMode import BotMode
from snake.engine.GameTypes import Direction


class LearningBot(BotMode):
    def __init__(self, engine, random_source=None):
        super().__init__(engine, random_source)
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
        """Return the existing nine danger, food, and open-space features."""
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
