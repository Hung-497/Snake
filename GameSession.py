import time

from BotFactory import create_bot_mode
from RecordManager import RecordManager
from ReplayManager import ReplayManager


class GameSession:
    """
    Runs repeated Snake games for one Bot Mode, without drawing anything.

    The session owns the bookkeeping the old Tkinter loop kept: the score, the
    match count, the best score, the rolling averages, saving records and
    replays, and starting the next game. All Snake rules stay in the Game
    Engine, and all drawing stays in the Game App View, which just asks the
    session to advance and then reads these values.
    """

    # The result of a finished game shows for a moment before the next one
    # starts, which is what the Tkinter loop did with after(10, ...).
    RESULT_PAUSE_SECONDS = 0.01
    # One long frame must not freeze the window by trying to catch up forever.
    MOVES_PER_UPDATE_LIMIT = 50

    def __init__(
        self,
        engine,
        bot_mode,
        speed_delay,
        record_manager=None,
        replay_manager=None,
        bot=None,
        now=time.perf_counter,
    ):
        self.engine = engine
        self.bot_mode = bot_mode
        self.speed_delay = speed_delay
        # The speed setting is a delay in milliseconds; Arcade works in seconds.
        self.move_interval = speed_delay / 1000
        self.now = now

        self.record_manager = RecordManager() if record_manager is None else record_manager
        self.replay_manager = ReplayManager() if replay_manager is None else replay_manager
        self.bot = create_bot_mode(bot_mode, engine) if bot is None else bot

        self.score = engine.score
        self.game_over = engine.game_over
        self.game_won = engine.game_won

        self.games_played = 0
        self.best_score = 0
        self.recent_scores = []
        self.total_moves = 0
        self.total_moves_history = []

        self.stopped = False
        self.time_since_last_move = 0.0
        self.result_pause_remaining = 0.0
        self.result_text = None

        self.session_start_time = self.now()
        self.game_start_time = self.now()

    def start(self):
        """Begin the first game of the session."""
        self.start_replay_recording()

    def start_replay_recording(self):
        self.replay_manager.start_recording(
            self.bot_mode,
            self.engine.board_width,
            self.engine.board_height,
            self.engine.tile_size,
            self.speed_delay,
            engine=self.engine,
        )

    def advance_by(self, elapsed_seconds):
        """
        Move the session forward by the time one Arcade frame took.

        Returns how many moves were made, so the caller can tell whether
        anything changed.
        """
        if (self.stopped):
            return 0

        # While a result is showing, the session only counts down that pause.
        if (self.result_pause_remaining > 0):
            self.result_pause_remaining -= elapsed_seconds

            if (self.result_pause_remaining <= 0):
                self.result_pause_remaining = 0
                self.start_next_game()

            return 0

        self.time_since_last_move += elapsed_seconds
        moves_made = 0

        while (self.time_since_last_move >= self.move_interval):
            if (moves_made >= self.MOVES_PER_UPDATE_LIMIT):
                break

            self.time_since_last_move -= self.move_interval
            self.advance()
            moves_made += 1

            if (self.result_pause_remaining > 0):
                # The game just ended, so stop moving and let the result show.
                break

        return moves_made

    def advance(self):
        """Play one move: ask the bot, step the engine, then report back."""
        if (self.stopped or self.game_over):
            return

        direction = None

        if (self.bot is not None):
            direction = self.bot.choose_action(self.engine.state)

        if (direction is not None):
            self.engine.change_direction(direction)
            self.replay_manager.record_move(direction)

        score_before = self.engine.score
        # preview and step agree, so this describes the move step commits
        transition = self.engine.preview()
        self.engine.step()

        self.score = self.engine.score
        self.game_over = self.engine.game_over
        self.game_won = self.engine.game_won
        self.total_moves += 1

        if (self.bot is not None):
            self.bot.observe(transition)

        if (self.engine.score > score_before and self.engine.food_position is not None):
            self.replay_manager.record_food(self.engine.food_position)

        if (self.game_over):
            self.finish_game()

    def finish_game(self):
        """Record a finished game and show its result before the next one."""
        self.games_played += 1
        self.recent_scores.append(self.score)

        if (self.score > self.best_score):
            self.best_score = self.score

        if (len(self.recent_scores) > 100):
            self.recent_scores.pop(0)

        average_score = sum(self.recent_scores) / len(self.recent_scores)

        self.total_moves_history.append(self.total_moves)
        if (len(self.total_moves_history) > 10):
            self.total_moves_history.pop(0)

        average_total_moves = sum(self.total_moves_history) / len(self.total_moves_history)
        game_time = self.now() - self.game_start_time
        session_time = self.now() - self.session_start_time

        self.replay_manager.save_replay(self.bot_mode, self.score, self.game_won)
        self.record_manager.save_game_result(
            self.bot_mode,
            self.games_played,
            self.score,
            self.best_score,
            average_score,
            self.total_moves,
            game_time,
            session_time,
            self.engine.board_width,
            self.engine.board_height,
            self.engine.tile_size,
            self.speed_delay,
        )

        print(
            f"Game: {self.games_played}, "
            f"Score: {self.score}, "
            f"Best: {self.best_score}, "
            f"Avg: {average_score:.1f}, "
            f"Total Moves: {self.total_moves}, "
            f"Avg total move: {average_total_moves:.1f}, "
            f"Epsilon: {self.bot_epsilon():.3f}, "
            f"Game Time: {game_time:.1f}s, "
            f"Session Time: {session_time:.1f}s"
        )

        if (self.bot is not None):
            self.bot.on_game_end(self.engine.state)

        self.result_text = "You won!" if self.game_won else "Game Over!"
        self.result_pause_remaining = self.RESULT_PAUSE_SECONDS

    def bot_epsilon(self):
        # Only a learning Bot Mode has one; the summary line stays the same.
        return getattr(self.bot, "epsilon", 0.0)

    def start_next_game(self):
        if (self.stopped):
            return

        self.engine.reset()

        self.score = self.engine.score
        self.game_over = self.engine.game_over
        self.game_won = self.engine.game_won
        self.total_moves = 0
        self.result_text = None
        self.time_since_last_move = 0.0
        self.game_start_time = self.now()

        self.start_replay_recording()

    def stop(self):
        """Prevent any further updates, for leaving or closing the App View."""
        self.stopped = True

    @property
    def state(self):
        """The Game Engine snapshot the Game App View draws."""
        return self.engine.state
