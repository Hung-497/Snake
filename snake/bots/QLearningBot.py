import json
import math
import os

from snake.bots.LearningBot import LearningBot


class QLearningBot(LearningBot):
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
        self.game_trained = 0
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

    def _make_state_if_needed(self, state):
        if (state not in self.q_table):
            self.q_table[state] = {action: 0 for action in self.actions}

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

    def _pick_action(self, state, state_key):
        if not self.evaluation_mode:
            self._make_state_if_needed(state_key)
        # An unseen state has equal zero values during evaluation.
        action_values = self.q_table.get(state_key, {})
        return self.select_action(state, action_values, self.evaluation_mode)
