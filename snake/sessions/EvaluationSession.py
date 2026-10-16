"""Evaluate a learning Bot Mode one move at a time, for the Evaluate App View.

Each game is played and recorded exactly as RunExperiment does, and a
finished run is saved as the same Bot Experiment report, so the app's
Evaluate and the terminal always agree (ADR 0017).
"""

from dataclasses import dataclass
from pathlib import Path
import random
import time

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.sessions.ExperimentReport import (
    BOT_SEED_OFFSET, build_report, game_record, make_engine, q_learning_identity,
    save_report, summarize_games,
)
from snake.sessions.TrainQLearning import FEATURE_SET_BY_BOT_MODE, play_move
from snake.sessions.TrainingSaves import SAVE_PATHS


@dataclass(frozen=True)
class EvaluationGames:
    """The board, first seed, and move limit every evaluated game is played with."""

    config: GameConfig
    base_seed: int
    max_moves: int


# The games docs/results.md was measured on, so app scores compare with it.
STUDY_GAMES = EvaluationGames(GameConfig(24, 25, 25), base_seed=200000, max_moves=5000)
# Quick, or the study's full set.
GAME_COUNTS = (20, 200)


@dataclass(frozen=True)
class EvaluationProgress:
    games_done: int
    game_count: int
    average_score: float
    best_score: int
    move_limits: int


class EvaluationSession:
    """Plays game_count evaluated games and saves one report when all are done.

    make_bot builds the bot in Evaluation Mode for one game's engine and
    random source; identity describes the evaluated model in the report.
    Stopping before the last game ends saves nothing.
    """

    def __init__(
        self, bot_mode, game_count, make_bot, identity, evaluated,
        games=STUDY_GAMES, report_directory=None, clock=time.perf_counter,
    ):
        self.bot_mode = bot_mode
        self.game_count = game_count
        self.make_bot = make_bot
        self.identity = identity
        self.evaluated = evaluated
        self.games = games
        self.report_directory = Path("experiments") if report_directory is None else report_directory
        self.clock = clock
        self.records = []
        self.elapsed_seconds = 0.0
        self.report_path = None
        self._start_game()

    @property
    def finished(self):
        return len(self.records) == self.game_count

    def make_move(self):
        """Make one move of the current game; after the last game, do nothing."""
        if self.finished:
            return
        if self.engine_ended:
            self._start_game()
        started_at = self.clock()
        play_move(self.engine, self.bot)
        self.moves += 1
        self.elapsed_seconds += self.clock() - started_at
        if self.engine.game_over or self.moves >= self.games.max_moves:
            self._finish_game()

    def make_moves_for(self, budget_seconds, clock=time.perf_counter):
        """Make moves until the time budget runs out or the run finishes; return how many."""
        started_at = clock()
        moves = 0
        while not self.finished:
            self.make_move()
            moves += 1
            if clock() - started_at >= budget_seconds:
                break
        return moves

    def progress(self):
        scores = [record["score"] for record in self.records]
        return EvaluationProgress(
            games_done=len(self.records),
            game_count=self.game_count,
            average_score=sum(scores) / len(scores) if scores else 0.0,
            best_score=max(scores, default=0),
            move_limits=sum(record["outcome"] == "move_limit" for record in self.records),
        )

    def _start_game(self):
        seed = self.games.base_seed + len(self.records)
        self.seed = seed
        self.engine = make_engine(self.games.config, seed)
        self.bot = self.make_bot(self.engine, random.Random(seed + BOT_SEED_OFFSET))
        self.moves = 0
        # The finished game stays on the board until the next move starts a new one.
        self.engine_ended = False

    def _finish_game(self):
        # Like play_game, so a Bot Mode sees the same calls as in RunExperiment.
        self.bot.on_game_end(self.engine.state)
        self.records.append(game_record(self.seed, self.engine, self.moves))
        self.engine_ended = True
        if self.finished:
            self._save_report()

    def _save_report(self):
        results = {self.bot_mode: {
            "games": self.records,
            "summary": summarize_games(self.records, self.elapsed_seconds),
        }}
        report = build_report(
            self.games.config, self.games.base_seed, self.game_count,
            self.games.max_moves, (self.bot_mode,), results,
        )
        report[self.bot_mode] = self.identity
        report["evaluated"] = self.evaluated
        self.report_path = save_report(report, self.report_directory)


def start_q_learning_evaluation(
    bot_mode, game_count, table_path=None, games=STUDY_GAMES, report_directory=None,
):
    """Evaluate a Q Learning app training. Raises ValueError when its table cannot be read."""
    table_path = str(SAVE_PATHS[bot_mode] if table_path is None else table_path)
    feature_set = FEATURE_SET_BY_BOT_MODE[bot_mode]

    def make_bot(engine, random_source):
        # Evaluation Mode never learns or saves, so the table is never changed.
        return QLearningBot(
            engine, random_source=random_source, evaluation_mode=True,
            q_table_file=table_path, feature_set=feature_set,
        )

    # Built once up front, like RunExperiment, to check the table and identify it.
    reference_bot = make_bot(make_engine(games.config, games.base_seed), random.Random(0))
    return EvaluationSession(
        bot_mode, game_count, make_bot, q_learning_identity(reference_bot), "app_training",
        games=games, report_directory=report_directory,
    )
