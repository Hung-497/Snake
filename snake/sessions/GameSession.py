import time

from snake.sessions.HumanPlayer import HUMAN_PLAY
from snake.sessions.PlayerFactory import create_player
from snake.storage.RecordManager import RecordManager
from snake.storage.ReplayManager import ReplayManager


class GameSession:
    """
    Runs repeated Snake games for one Player, without drawing anything.

    The session owns the bookkeeping the old Tkinter loop kept: the score, the
    match count, the best score, the rolling averages, saving records and
    replays, and starting the next game. All Snake rules stay in the Game
    Engine, and all drawing stays in the Game App View, which just asks the
    session to advance and then reads these values.

    Bot Modes play on by themselves. Human Play waits for the person instead:
    each game starts on their first direction, and a finished game waits for
    them to restart it.
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
        self.bot = create_player(bot_mode, engine) if bot is None else bot
        self.is_human_play = (bot_mode == HUMAN_PLAY)
        self.waiting_to_start = self.is_human_play
        self.paused = False
        self.pause_started_at = None
        # Paused time is left out of the game and session times that get saved.
        self.paused_seconds_this_game = 0.0
        self.paused_seconds_total = 0.0

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
        # Time spent paused is not counted, so resuming causes no burst of moves.
        if (self.stopped or self.waiting_to_start or self.paused):
            return 0

        # A finished Human Play game stays on screen until restart() is called.
        if (self.is_human_play and self.game_over):
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

        # A bot can catch up after a slow frame, but a person cannot react to
        # a burst of moves, so Human Play makes at most one move per update.
        moves_limit = 1 if self.is_human_play else self.MOVES_PER_UPDATE_LIMIT

        while (self.time_since_last_move >= self.move_interval):
            if (moves_made >= moves_limit):
                break

            self.time_since_last_move -= self.move_interval
            self.advance()
            moves_made += 1

            if (self.game_over):
                # The game just ended, so stop moving and let the result show.
                break

        # Drop the time a slow frame left over, so later updates do not catch up.
        if (self.is_human_play and self.time_since_last_move >= self.move_interval):
            self.time_since_last_move = 0.0

        return moves_made

    def press_direction(self, direction):
        """A person pressed a direction key during Human Play."""
        if (not self.is_human_play or self.stopped or self.game_over or self.paused):
            return

        if (not self.waiting_to_start):
            self.bot.press(direction)
            return

        # The first key picks the direction the game starts in, even the
        # opposite of the one the snake faces, because it has not moved yet.
        if (self.engine.choose_start_direction(direction)):
            self.waiting_to_start = False
            self.time_since_last_move = 0.0
            # The game only really starts now, not when it was shown.
            self.game_start_time = self.now()

    def toggle_pause(self):
        """Pause or resume a Human Play game that is being played."""
        if (self.paused):
            self.resume()
        elif (self.can_pause()):
            self.pause()

    def focus_lost(self):
        """The window lost focus: pause, but never resume on its own."""
        if (self.can_pause()):
            self.pause()

    def pause(self):
        self.paused = True
        self.pause_started_at = self.now()

    def resume(self):
        paused_seconds = self.now() - self.pause_started_at
        self.paused_seconds_this_game += paused_seconds
        self.paused_seconds_total += paused_seconds
        self.paused = False
        self.pause_started_at = None

    def can_pause(self):
        # Only a game in play can pause; waiting and the result have nothing to stop.
        return (
            self.is_human_play
            and not self.stopped
            and not self.waiting_to_start
            and not self.game_over
        )

    @property
    def status(self):
        """Which prompt the Game App View should show."""
        if (self.waiting_to_start):
            return "waiting_to_start"

        if (self.paused):
            return "paused"

        if (self.result_text is not None):
            return "showing_result"

        return "playing"

    def advance(self):
        """Play one move: ask the bot, step the engine, then report back."""
        if (self.stopped or self.game_over):
            return

        direction = None

        if (self.bot is not None):
            direction = self.bot.choose_action(self.engine.state)

        if (direction is not None):
            self.engine.change_direction(direction)

        # A replay plays back one direction per move, so record the direction
        # the snake really moves in: Human Play often chooses no turn at all,
        # and the Game Engine refuses a turn that would reverse the snake.
        self.replay_manager.record_move(self.engine.state.direction)

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
        game_time = self.now() - self.game_start_time - self.paused_seconds_this_game
        session_time = self.now() - self.session_start_time - self.paused_seconds_total

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
            outcome="won" if self.game_won else "died",
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

        # Bot Modes start the next game by themselves after a short pause.
        if (not self.is_human_play):
            self.result_pause_remaining = self.RESULT_PAUSE_SECONDS

    def bot_epsilon(self):
        # Only a learning Bot Mode has one; the summary line stays the same.
        return getattr(self.bot, "epsilon", 0.0)

    def restart(self):
        """A person asked for a new game after a Human Play game ended."""
        if (self.is_human_play and self.game_over):
            self.start_next_game()

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
        self.paused_seconds_this_game = 0.0
        self.waiting_to_start = self.is_human_play

        self.start_replay_recording()

    def stop(self):
        """Prevent any further updates, for leaving or closing the App View."""
        self.stopped = True

    @property
    def state(self):
        """The Game Engine snapshot the Game App View draws."""
        return self.engine.state
