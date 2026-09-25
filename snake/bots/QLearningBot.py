import json
import math
import os

from snake.bots.BotMode import BotMode
from snake.engine.GameTypes import Direction

class QLearningBot(BotMode):
    """
    Bot that explores actions and learns from rewards with Q-learning.

    It stores action values in a Q-table. Rewards and penalties update that
    table so the bot can learn which action is usually better for a given game
    state.
    """

    def __init__(
        self, engine, random_source=None, require_saved_table=False,
        evaluation_mode=False, q_table_file=None,
    ):
        super().__init__(engine, random_source)

        self.evaluation_mode = evaluation_mode
        self.q_table = {} # the AI memory, store knowledge [state][action]
        self.q_table_file = (
            q_table_file if q_table_file is not None
            else os.path.join("learning_data", "q_table_space_state_v2.json")
        )
        self.learning_rate = 0.1 # how fast AI learns new information
        self.discount_rate = 0.9 # how much AI cares about future rewards
        self.epsilon = 1.0 # how often AI explores random actions
        self.min_epsilon = 0.05
        self.epsilon_decay = 0.997
        self.game_trained = 0
        self.actions = ["Straight", "Turn_Left", "Turn_Right"]
        self.current_state = None
        self.current_action = None
        self.distance_before_move = 0

        loaded = self.load_q_table()
        if (require_saved_table or evaluation_mode) and not loaded:
            raise ValueError(
                f"Saved Q-table is missing or malformed: {self.q_table_file}"
            )

    def choose_action(self, state):
        self.current_state = self._get_state(state)
        self.current_action = self._pick_action(state, self.current_state)
        self.distance_before_move = self.get_food_distance(state)

        return self._get_direction_from_action(state, self.current_action)

    def observe(self, transition):
        if self.evaluation_mode:
            return

        state_after_move = self.engine.state

        new_distance = self.get_food_distance(state_after_move)
        action_space_level = self._get_action_space_level(
            self.current_state,
            self.current_action,
        )
        reward = self._get_reward(
            transition.game_over,
            transition.ate_food,
            self.distance_before_move,
            new_distance,
            action_space_level,
        )
        # terminal moves have no future state
        next_state = None if transition.game_over else self._get_state(state_after_move)

        self._update_q_values(
            self.current_state,
            self.current_action,
            reward,
            next_state,
        ) # update q-table memory

    def on_game_end(self, result):
        if self.evaluation_mode:
            return

        self.game_trained += 1
        self.decay_epsilon()
        self.save_q_table()

    def _state_to_key(self, state):
        key_parts = [str(value) for value in state]

        return "_".join(key_parts)

    def _key_to_state(self, key):
        values = key.split("_")
        state = tuple(int(value) for value in values)

        return state

    def save_q_table(self):
        if self.evaluation_mode:
            return

        os.makedirs("learning_data", exist_ok=True)

        q_table_to_save = {}
        epsilon_to_save = self.epsilon

        for state, action_values in self.q_table.items():
            state_key = self._state_to_key(state)
            q_table_to_save[state_key] = action_values

        data_to_save = {
            "q_table": q_table_to_save,
            "epsilon": epsilon_to_save,
            "game_trained": self.game_trained
        }

        with open(self.q_table_file, "w") as file:
            json.dump(data_to_save, file, indent=4)

    def load_q_table(self):
        try:
            if (not os.path.exists(self.q_table_file)):
                return False

            if (os.path.getsize(self.q_table_file) == 0):
                return False

            with open(self.q_table_file, "r") as file:
                saved_data = json.load(file)
        except (OSError, ValueError, UnicodeError):
            return False

        if (not isinstance(saved_data, dict)):
            return False

        required_keys = {"q_table", "epsilon", "game_trained"}
        if (not required_keys.issubset(saved_data)):
            return False

        epsilon = saved_data["epsilon"]
        game_trained = saved_data["game_trained"]

        if (
            not self._is_valid_number(epsilon)
            or not 0 <= epsilon <= 1
            or type(game_trained) is not int
            or game_trained < 0
        ):
            return False

        loaded_q_table = self._parse_q_table(saved_data["q_table"])
        if (loaded_q_table is None):
            return False

        self.q_table = loaded_q_table
        self.epsilon = epsilon
        self.game_trained = game_trained
        return True

    def _is_valid_number(self, value):
        if (type(value) is int):
            return True

        return type(value) is float and math.isfinite(value)

    def _parse_q_table(self, saved_q_table):
        if (not isinstance(saved_q_table, dict)):
            return None

        loaded_q_table = {}

        for state_key, action_values in saved_q_table.items():
            if (not isinstance(state_key, str)):
                return None

            try:
                state = self._key_to_state(state_key)
            except (TypeError, ValueError):
                return None

            if (
                len(state) != 9
                or any(type(value) is not int or value not in (0, 1, 2) for value in state)
            ):
                return None

            if (not isinstance(action_values, dict)):
                return None

            if (set(action_values) != set(self.actions)):
                return None

            if (not all(self._is_valid_number(value) for value in action_values.values())):
                return None

            loaded_q_table[state] = dict(action_values)

        return loaded_q_table

    def _get_action_space_level(self, state, action):
        if (action == "Straight"):
            return state[6]

        if (action == "Turn_Left"):
            return state[7]

        if (action == "Turn_Right"):
            return state[8]

        return 0

    def _is_danger(self, state, direction):
        next_position = self.position_after(self.head_position(state), direction)

        if (not self.is_inside_board(state, next_position)):
            return 1

        body = self.body_positions(state)

        if (next_position == self.food_position(state)):
            body_to_check = body
        else:
            body_to_check = body[:-1]

        if (next_position in body_to_check):
            return 1

        return 0

    def _space_level(self, state, open_space):
        snake_size = len(self.body_positions(state)) + 1

        if (open_space < snake_size):
            return 0

        if (open_space < snake_size * 2):
            return 1

        return 2

    def _count_space_after_action(self, state, action):
        direction = self._get_direction_from_action(state, action)
        next_position = self.position_after(self.head_position(state), direction)

        if (self._is_danger(state, direction)):
            return 0

        blocked_positions = set(self.body_positions(state))

        return self._count_reachable_space(state, next_position, blocked_positions)

    def _count_reachable_space(self, state, start_position, blocked_positions):
        positions_to_check = [start_position]
        visited_positions = {start_position}

        while (len(positions_to_check) > 0):
            current_position = positions_to_check.pop(0)

            for direction in self.DIRECTIONS:
                next_position = self.position_after(current_position, direction)

                if (next_position in visited_positions):
                    continue

                if (next_position in blocked_positions):
                    continue

                if (not self.is_inside_board(state, next_position)):
                    continue

                visited_positions.add(next_position)
                positions_to_check.append(next_position)

        return len(visited_positions)

    def _get_state(self, state):
        straight_direction = self._get_direction_from_action(state, "Straight")
        left_direction = self._get_direction_from_action(state, "Turn_Left")
        right_direction = self._get_direction_from_action(state, "Turn_Right")

        danger_straight = self._is_danger(state, straight_direction)
        danger_left = self._is_danger(state, left_direction)
        danger_right = self._is_danger(state, right_direction)

        head = self.head_position(state)
        next_straight_x, next_straight_y = self.position_after(head, straight_direction)
        next_left_x, next_left_y = self.position_after(head, left_direction)
        next_right_x, next_right_y = self.position_after(head, right_direction)

        current_distance = self.get_food_distance(state)

        food_x, food_y = self.food_position(state)
        food_straight = int(abs(food_x - next_straight_x) + abs(food_y - next_straight_y) < current_distance)
        food_left = int(abs(food_x - next_left_x) + abs(food_y - next_left_y) < current_distance)
        food_right = int(abs(food_x - next_right_x) + abs(food_y - next_right_y) < current_distance)

        straight_space = self._count_space_after_action(state, "Straight")
        left_space = self._count_space_after_action(state, "Turn_Left")
        right_space = self._count_space_after_action(state, "Turn_Right")

        straight_space_level = self._space_level(state, straight_space)
        left_space_level = self._space_level(state, left_space)
        right_space_level = self._space_level(state, right_space)

        return (
            danger_straight,
            danger_left,
            danger_right,
            food_straight,
            food_left,
            food_right,
            straight_space_level,
            left_space_level,
            right_space_level
        )

    def _get_direction_from_action(self, state, action):
        current_direction = state.direction

        if (action == "Straight"):
            return current_direction

        if (current_direction == Direction.UP):
            if (action == "Turn_Left"):
                return Direction.LEFT
            elif (action == "Turn_Right"):
                return Direction.RIGHT
        elif (current_direction == Direction.DOWN):
            if (action == "Turn_Left"):
                return Direction.RIGHT
            elif (action == "Turn_Right"):
                return Direction.LEFT
        elif (current_direction == Direction.LEFT):
            if (action == "Turn_Left"):
                return Direction.DOWN
            elif (action == "Turn_Right"):
                return Direction.UP
        elif (current_direction == Direction.RIGHT):
            if (action == "Turn_Left"):
                return Direction.UP
            elif (action == "Turn_Right"):
                return Direction.DOWN

    def _make_state_if_needed(self, state):
        if (state not in self.q_table):
            self.q_table[state] = {
                "Straight": 0,
                "Turn_Left": 0,
                "Turn_Right": 0
            }

    def _update_q_values(self, state, action, reward, next_state):
        self._make_state_if_needed(state)

        old_value = self.q_table[state][action]
        if (next_state is None):
            best_next_value = 0
        else:
            self._make_state_if_needed(next_state)
            best_next_value = max(self.q_table[next_state].values())

        new_value = old_value + self.learning_rate * (
            reward + self.discount_rate * best_next_value - old_value
        )

        self.q_table[state][action] = new_value

    def get_food_distance(self, state):
        food_position = self.food_position(state)
        if food_position is None:
            return 0

        food_x, food_y = food_position
        snake_x, snake_y = self.head_position(state)
        distance_x = abs(food_x - snake_x)
        distance_y = abs(food_y - snake_y)

        return distance_x + distance_y

    def _get_reward(self, game_over, ate_food, old_distance, new_distance, action_space_level):
        if (game_over):
            return -100

        if (ate_food):
            return 100

        reward = -1

        if (new_distance < old_distance):
            reward += 5
        else:
            reward -= 2

        if (action_space_level == 2):
            reward += 2
        elif (action_space_level == 0):
            reward -= 8

        return reward

    def decay_epsilon(self):
        if (self.epsilon > self.min_epsilon):
            self.epsilon *= self.epsilon_decay

        if (self.epsilon < self.min_epsilon):
            self.epsilon = self.min_epsilon

    def _get_safe_actions(self, state):
        safe_actions = []

        for action in self.actions:
            direction = self._get_direction_from_action(state, action)

            if (self._is_danger(state, direction) == 0):
                safe_actions.append(action)

        return safe_actions

    def _pick_action(self, state, state_key):
        if not self.evaluation_mode:
            self._make_state_if_needed(state_key)

        safe_actions = self._get_safe_actions(state)

        if (len(safe_actions) == 0):
            return self.random_source.choice(self.actions)

        if (not self.evaluation_mode and self.random_source.random() < self.epsilon):
            return self.random_source.choice(safe_actions)

        best_action = safe_actions[0]
        # An unseen state has equal zero values during evaluation.
        action_values = self.q_table.get(state_key, {})
        best_value = action_values.get(best_action, 0)

        for action in safe_actions:
            value = action_values.get(action, 0)

            if (value > best_value):
                best_value = value
                best_action = action

        return best_action
