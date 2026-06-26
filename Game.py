from RuleBasedBot import RuleBasedBot
from QLearningBot import QLearningBot
from HamiltonianBot import HamiltonianBot
import time

class Game:
    """
    Coordinates the main Snake game loop.

    Game owns the current score, win/loss state, selected bot mode, and update
    loop. It asks the active bot for a direction, moves the snake, checks food
    and collisions, then redraws the screen.
    """

    def __init__(self, window, snake, food, movement, bot_mode):
        self.window = window
        self.snake = snake
        self.food = food
        self.movement = movement

        self.bot = RuleBasedBot(self)
        self.q_bot = QLearningBot(self)
        self.hamiltonian_bot = HamiltonianBot(self)

        self.bot_mode = bot_mode

        self.score = 0
        self.game_over = False
        self.game_won = False

        self.recent_scores = []
        self.games_played = 0
        self.best_score = 0

        self.total_moves = 0
        self.total_moves_history = []

        self.session_start_time = time.perf_counter()
        self.game_start_time = time.perf_counter()
    
    def draw(self):
        self.window.clear_canvas()
        self.window.update_score_label(self.score, self.games_played, self.best_score)
        self.food.draw_food()
        self.snake.draw_snake()
        self.snake.draw_snake_body()
    
    def update(self):
        q_old_distance = None
        direction = None

        if (self.bot_mode == "rule"):
            direction = self.bot.get_next_direction()
        elif (self.bot_mode == "q_learning"):
            q_old_distance = self.q_bot.get_food_distance()
            direction = self.q_bot.get_next_direction()
        elif (self.bot_mode == "hamiltonian"):
            direction = self.hamiltonian_bot.get_next_direction()

        if (direction is not None):
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
            self.q_bot.learn_from_move(
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

            game_time = time.perf_counter() - self.game_start_time
            session_time = time.perf_counter() - self.session_start_time

            print(
                f"Game: {self.games_played}, "
                f"Score: {self.score}, "
                f"Best: {self.best_score}, "
                f"Avg: {average_score:.1f}, "
                f"Total Moves: {self.total_moves}, "
                f"Avg total move: {avg_score:.1f}, "
                f"Epsilon: {self.q_bot.epsilon:.3f}, "
                f"Game Time: {game_time:.1f}s, "
                f"Session Time: {session_time:.1f}s"
            )

            if (self.bot_mode == "q_learning"):
                self.q_bot.decay_epsilon()

            if (self.game_won):
                self.window.draw_game_won(self.score)
            elif (self.game_over):
                self.window.draw_game_over(self.score)

            # reset game
            self.window.window.after(10, self.start_next_game)
            return
        
        # Call update again
        if self.bot_mode == "hamiltonian":
            time_delay = 1 # milliseconds
        else:
            time_delay = 0
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
        self.game_start_time = time.perf_counter()


        self.snake.reset()
        self.food.spawn_food()
        self.movement.reset()

    def start_next_game(self):
        self.reset_game_state()
        self.draw()
        self.update()
