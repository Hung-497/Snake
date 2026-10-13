"""Train a DQN Bot Mode one move at a time, for the Live Training App View.

Each move goes through the same play_move as headless training, and games,
seeds, and torch settings follow TrainDQN, so watching never changes what
is learned.
"""

from dataclasses import dataclass
import random
import time

import torch

from snake.bots.DQNBot import DEFAULT_DQN_SETTINGS, DQNBot
from snake.engine.SnakeEngine import SnakeEngine
from snake.sessions.TrainQLearning import play_move


FEATURE_SET = "v3"
# The average score covers this many of the most recent games.
RECENT_GAMES = 50


@dataclass(frozen=True)
class LiveTrainingStats:
    games_played: int
    score: int
    best_score: int
    average_score: float
    epsilon: float


class LiveTrainingSession:
    def __init__(self, config, seed=0, max_moves=5000):
        self.config = config
        self.seed = seed
        self.max_moves = max_moves
        self.moves_this_game = 0
        self.scores = []

        # The same CPU settings and seed offsets as TrainDQN keep runs repeatable.
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        torch.manual_seed(seed + 3)
        self.engine = self._make_engine(game_number=0)
        self.bot = DQNBot(
            self.engine,
            random_source=random.Random(seed + 1),
            replay_random_source=random.Random(seed + 2),
            settings=dict(DEFAULT_DQN_SETTINGS),
            feature_set=FEATURE_SET,
        )

    def make_move(self):
        """Make one training move, and start the next game if this one ended."""
        game_ended = play_move(self.engine, self.bot)
        self.moves_this_game += 1
        if game_ended or self.moves_this_game >= self.max_moves:
            self._finish_game()

    def make_moves_for(self, budget_seconds, clock=time.perf_counter):
        """Make training moves until the time budget runs out; return how many.

        At least one move is always made, so a slow frame still makes progress.
        Only the number of moves depends on time, never what is learned.
        """
        started_at = clock()
        moves = 0
        while True:
            self.make_move()
            moves += 1
            if clock() - started_at >= budget_seconds:
                return moves

    def stats(self):
        recent_scores = self.scores[-RECENT_GAMES:]
        average_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        return LiveTrainingStats(
            games_played=len(self.scores),
            score=self.engine.score,
            best_score=max(self.scores, default=0),
            average_score=average_score,
            epsilon=self.bot.epsilon,
        )

    def _finish_game(self):
        self.bot.on_game_end(self.engine.state)
        self.bot.take_game_loss()
        self.scores.append(self.engine.score)
        self.engine = self._make_engine(game_number=len(self.scores))
        self.bot.engine = self.engine
        self.moves_this_game = 0

    def _make_engine(self, game_number):
        return SnakeEngine(
            self.config, start_position=None,
            random_source=random.Random(self.seed + game_number),
        )
