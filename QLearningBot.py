import random

class QLearningBot:
    def __init__(self):
        self.q_table = {} # the AI memory, store knowledge [state][action]
        self.learning_rate = 0.1 # how fast AI learns new information
        self.discount_rate = 0.9 # how much AI cares about future rewards
        self.epsilon = 1.0 # how often AI explores random actions
        self.min_epsilon = 0.05
        self.epsilon_decay = 0.995
        self.actions = ["Straight", "Turn_Left", "Turn_Right"]
    
    def get_next_position(self, game, direction):
        next_x = game.snake.x
        next_y = game.snake.y

        if (direction == "Up"):
            next_y -= game.window.tile_size
        elif (direction == "Down"):
            next_y += game.window.tile_size
        elif (direction == "Left"):
            next_x -= game.window.tile_size
        elif (direction == "Right"):
            next_x += game.window.tile_size

        return next_x, next_y
    
    def is_danger(self, game, direction):
        next_x, next_y = self.get_next_position(game, direction)

        if (next_x < 0 or next_x >= game.window.WINDOW_WIDTH):
            return 1
        
        if (next_y < 0 or next_y >= game.window.WINDOW_HEIGHT):
            return 1

        ate_food = (next_x == game.food.x and next_y == game.food.y)

        if (ate_food):
            body_to_check = game.snake.body
        else:
            body_to_check = game.snake.body[:-1]

        if ((next_x, next_y) in body_to_check):
            return 1
        
        return 0    
    
    def get_state(self, game):
        straight_direction = self.get_direction_from_action(game, "Straight")
        left_direction = self.get_direction_from_action(game, "Turn_Left")
        right_direction = self.get_direction_from_action(game, "Turn_Right")

        danger_straight = self.is_danger(game, straight_direction)
        danger_left = self.is_danger(game, left_direction)
        danger_right = self.is_danger(game, right_direction)

        next_straight_x, next_straight_y = self.get_next_position(game, straight_direction)
        next_left_x, next_left_y = self.get_next_position(game, left_direction)
        next_right_x, next_right_y = self.get_next_position(game, right_direction)

        current_distance = self.get_food_distance(game)

        food_straight = int(abs(game.food.x - next_straight_x) + abs(game.food.y - next_straight_y) < current_distance)
        food_left = int(abs(game.food.x - next_left_x) + abs(game.food.y - next_left_y) < current_distance)
        food_right = int(abs(game.food.x - next_right_x) + abs(game.food.y - next_right_y) < current_distance)

        return (
            danger_straight,
            danger_left,
            danger_right,
            food_straight,
            food_left,
            food_right
        )

    def get_current_direction(self, game):
        if (game.movement.velocity_y == -1):
            return "Up"
        elif (game.movement.velocity_y == 1):
            return "Down"
        elif (game.movement.velocity_x == -1):
            return "Left"
        elif (game.movement.velocity_x == 1):
            return "Right"
        
        return "Right"
    
    def get_direction_from_action(self, game, action):
        current_direction = self.get_current_direction(game)

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
            
    def make_state_if_needed(self, state):
        if (state not in self.q_table):
            self.q_table[state] = {
                "Straight": 0,
                "Turn_Left": 0,
                "Turn_Right": 0
            }
    
    def update_q_values(self, state, action, reward, next_state):
        self.make_state_if_needed(state)
        self.make_state_if_needed(next_state)

        old_value = self.q_table[state][action]
        best_next_value = max(self.q_table[next_state].values())

        new_value = old_value + self.learning_rate * (
            reward + self.discount_rate * best_next_value - old_value
        )

        self.q_table[state][action] = new_value

    def get_food_distance(self, game):
        distance_x = abs(game.food.x - game.snake.x)
        distance_y = abs(game.food.y - game.snake.y)

        return distance_x + distance_y
    
    def get_reward(self, game_over, ate_food, old_distance, new_distance):
        if (game_over):
            return -100
        
        if (ate_food):
            return 100
        
        if (new_distance < old_distance):
            return 5
        
        return -1 
    
    def get_action_and_direction(self, game):
        state = self.get_state(game)
        action = self.choose_action(game, state)
        direction = self.get_direction_from_action(game, action)

        return state, action, direction
    
    def learn_from_move(self, game, state, action, old_distance, ate_food, game_over):
        new_distance = self.get_food_distance(game) # check new distance
        reward = self.get_reward(game_over, ate_food, old_distance, new_distance) # calculate reward
        next_state = self.get_state(game) # get the new state

        self.update_q_values(state, action, reward, next_state) # update q-table memory
    
    def decay_epsilon(self):
        if (self.epsilon > self.min_epsilon):
            self.epsilon *= self.epsilon_decay
        
        if (self.epsilon < self.min_epsilon):
            self.epsilon = self.min_epsilon

    def get_safe_actions(self, game):
        safe_actions = []

        for action in self.actions:
            direction = self.get_direction_from_action(game, action)

            if (self.is_danger(game, direction) == 0):
                safe_actions.append(action)

        return safe_actions
    
    def choose_action(self, game, state):
        self.make_state_if_needed(state)

        safe_actions = self.get_safe_actions(game)

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