from Bot import Bot
from QLearningBot import QLearningBot
from HamiltonianBot import HamiltonianBot

class Game:
    def __init__(self, window, snake, food, movement, bot_mode):
        self.window = window
        self.snake = snake
        self.food = food
        self.movement = movement

        self.bot = Bot(self)
        self.q_bot = QLearningBot()
        self.hamiltonian_bot = HamiltonianBot(self)

        self.bot_mode = bot_mode

        self.score = 0
        self.game_over = False
        self.game_won = False

        self.recent_scores = []
        self.games_played = 0
        self.best_score = 0

        self.training_games = 1000
        self.is_training = True

        self.total_moves = 0
        self.total_moves_history = []
    
    def draw(self):
        self.window.clear_canvas()
        self.window.update_score_label(self.score, self.games_played, self.best_score)
        self.food.draw_food()
        self.snake.draw_snake()
        self.snake.draw_snake_body()
    
    def update(self):
        q_state = None
        q_action = None
        q_old_distance = None

        if (self.bot_mode == "rule"):
            self.bot.bot_change_direction()
        elif (self.bot_mode == "q_learning"):
            q_old_distance = self.q_bot.get_food_distance(self)
            q_state, q_action, direction = self.q_bot.get_action_and_direction (self)
            self.movement.change_direction(direction)
        elif (self.bot_mode == "hamiltonian"):
            direction = self.hamiltonian_bot.get_next_direction()
            self.movement.change_direction(direction)

        ate_food, self.game_over = self.movement.move_snake(
            self.snake, 
            self.window.tile_size, 
            self.food, 
            self.window.width, 
            self.window.height, 
            self.game_over
        )

        self.total_moves += 1

        if (ate_food):
            self.score += 1

            occupied_tiles = len(self.snake.body) + 1
            total_tiles = self.window.width * self.window.height

            if (occupied_tiles == total_tiles):
                self.game_over = True
                self.game_won = True
            else:
                self.food.spawn_food()

        if (self.bot_mode == "q_learning"):
            if (self.is_training):
                self.q_bot.learn_from_move(
                    self, 
                    q_state, 
                    q_action, 
                    q_old_distance, 
                    ate_food, 
                    self.game_over
                )
        
        self.draw()

        if (self.game_over):
            self.games_played += 1
            self.recent_scores.append(self.score)
            
            if (self.score > self.best_score):
                self.best_score = self.score
            
            if (len(self.recent_scores) > 100):
                self.recent_scores.pop(0)

            average_score = sum(self.recent_scores) / len(self.recent_scores)

            self.total_moves_history.append(self.total_moves)
            avg_score = sum(self.total_moves_history) / len(self.total_moves_history)

            if (len(self.total_moves_history) > 10):
                self.total_moves_history.pop(0)

            print(
                f"Game: {self.games_played}, "
                f"Score: {self.score}, "
                f"Best: {self.best_score}, "
                f"Avg: {average_score:.1f}, "
                f"Total Moves: {self.total_moves}, "
                f"Avg total move: {avg_score:.1f}"
            )

            if (self.bot_mode == "q_learning"):
                if (self.games_played >= self.training_games):
                    self.is_training = False
                    self.q_bot.epsilon = 0
                else:
                    self.q_bot.decay_epsilon()

            if (self.game_won):
                self.window.draw_game_won(self.score)
            elif (self.game_over):
                self.window.draw_game_over(self.score)

            # reset game
            self.window.window.after(10, self.start_next_game)
            return
        
        # Call update again
        time_delay = 1 # milliseconds
        self.window.window.after(time_delay, self.update)
    
    def run(self):
        self.window.draw_score_label()
        self.window.create_canvas()
        self.window.center_window()

        self.draw()
        self.update()
        self.window.start()

    def reset_game_state(self):
        self.score = 0
        self.game_over = False
        self.game_won = False

        self.total_moves = 0
        self.moves_for_current_food = 0

        self.snake.reset()
        self.food.spawn_food()
        self.movement.reset()

    def start_next_game(self):
        self.reset_game_state()
        self.draw()
        self.update()
