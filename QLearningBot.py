import random
from BaseBot import BaseBot

class QLearningBot(BaseBot):
    """
    Bot that explores actions and learns from rewards with Q-learning.

    It stores action values in a Q-table. Rewards and penalties update that
    table so the bot can learn which action is usually better for a given game
    state.
    """

    def __init__(self, game):
        super().__init__(game)

        self.q_table = {} # the AI memory, store knowledge [state][action]
        self.learning_rate = 0.1 # how fast AI learns new information
        self.discount_rate = 0.9 # how much AI cares about future rewards
        self.epsilon = 1.0 # how often AI explores random actions
        self.min_epsilon = 0.00
        self.epsilon_decay = 0.997
        self.actions = ["Straight", "Turn_Left", "Turn_Right"]
        self.current_state = None
        self.current_action = None
    
    def _is_danger(self, direction):
        next_x, next_y = self._get_next_position(direction)

        if (not self._is_inside_board(next_x, next_y)):
            return 1

        ate_food = (next_x == self.game.food.x and next_y == self.game.food.y)

        if (ate_food):
            body_to_check = self.game.snake.body
        else:
            body_to_check = self.game.snake.body[:-1]

        if ((next_x, next_y) in body_to_check):
            return 1
        
        return 0    
    
    def _get_state(self):
        straight_direction = self._get_direction_from_action("Straight")
        left_direction = self._get_direction_from_action("Turn_Left")
        right_direction = self._get_direction_from_action("Turn_Right")

        danger_straight = self._is_danger(straight_direction)
        danger_left = self._is_danger(left_direction)
        danger_right = self._is_danger(right_direction)

        next_straight_x, next_straight_y = self._get_next_position(straight_direction)
        next_left_x, next_left_y = self._get_next_position(left_direction)
        next_right_x, next_right_y = self._get_next_position(right_direction)

        current_distance = self.get_food_distance()

        food_straight = int(abs(self.game.food.x - next_straight_x) + abs(self.game.food.y - next_straight_y) < current_distance)
        food_left = int(abs(self.game.food.x - next_left_x) + abs(self.game.food.y - next_left_y) < current_distance)
        food_right = int(abs(self.game.food.x - next_right_x) + abs(self.game.food.y - next_right_y) < current_distance)

        return (
            danger_straight,
            danger_left,
            danger_right,
            food_straight,
            food_left,
            food_right
        )

    def _get_current_direction(self):
        if (self.game.movement.velocity_y == -1):
            return "Up"
        elif (self.game.movement.velocity_y == 1):
            return "Down"
        elif (self.game.movement.velocity_x == -1):
            return "Left"
        elif (self.game.movement.velocity_x == 1):
            return "Right"
        
        return "Right"
    
    def _get_direction_from_action(self, action):
        current_direction = self._get_current_direction()

        if (action == "Straight"):
            return current_direction
        
        if (current_direction == "Up"):
            if (action == "Turn_Left"):
                return "Left"
            elif (action == "Turn_Right"):
                return "Right"
        elif (current_direction == "Down"):
            if (action == "Turn_Left"):
                return "Right"
            elif (action == "Turn_Right"):
                return "Left"
        elif (current_direction == "Left"):
            if (action == "Turn_Left"):
                return "Down"
            elif (action == "Turn_Right"):
                return "Up"
        elif (current_direction == "Right"):
            if (action == "Turn_Left"):
                return "Up"
            elif (action == "Turn_Right"):
                return "Down"
            
    def _make_state_if_needed(self, state):
        if (state not in self.q_table):
            self.q_table[state] = {
                "Straight": 0,
                "Turn_Left": 0,
                "Turn_Right": 0
            }
    
    def _update_q_values(self, state, action, reward, next_state):
        self._make_state_if_needed(state)
        self._make_state_if_needed(next_state)

        old_value = self.q_table[state][action]
        best_next_value = max(self.q_table[next_state].values())

        new_value = old_value + self.learning_rate * (
            reward + self.discount_rate * best_next_value - old_value
        )

        self.q_table[state][action] = new_value

    def get_food_distance(self):
        distance_x = abs(self.game.food.x - self.game.snake.x)
        distance_y = abs(self.game.food.y - self.game.snake.y)

        return distance_x + distance_y
    
    def _get_reward(self, game_over, ate_food, old_distance, new_distance):
        if (game_over):
            return -100
        
        if (ate_food):
            return 100
        
        if (new_distance < old_distance):
            return 5
        
        return -1 
    
    def learn_from_move(self, old_distance, ate_food, game_over):
        new_distance = self.get_food_distance() # check new distance
        reward = self._get_reward(game_over, ate_food, old_distance, new_distance) # calculate reward
        next_state = self._get_state() # get the new state

        self._update_q_values(
            self.current_state,
            self.current_action,
            reward,
            next_state
        ) # update q-table memory
    
    def decay_epsilon(self):
        if (self.epsilon > self.min_epsilon):
            self.epsilon *= self.epsilon_decay
        
        if (self.epsilon < self.min_epsilon):
            self.epsilon = self.min_epsilon

    def _get_safe_actions(self):
        safe_actions = []

        for action in self.actions:
            direction = self._get_direction_from_action(action)

            if (self._is_danger(direction) == 0):
                safe_actions.append(action)

        return safe_actions
    
    def _choose_action(self, state):
        self._make_state_if_needed(state)

        safe_actions = self._get_safe_actions()

        if (len(safe_actions) == 0):
            return random.choice(self.actions)
        
        if (random.random() < self.epsilon):
            return random.choice(safe_actions)
        
        best_action = safe_actions[0]
        best_value = self.q_table[state][best_action]

        for action in safe_actions:
            value = self.q_table[state][action]

            if (value > best_value):
                best_value = value
                best_action = action

        return best_action

    def get_next_direction(self):
        self.current_state = self._get_state()
        self.current_action = self._choose_action(self.current_state)
        return self._get_direction_from_action(self.current_action)
