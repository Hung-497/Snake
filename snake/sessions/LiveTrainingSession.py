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
from snake.sessions.LiveTraining import DEFAULT_CHECKPOINT_PATH, LiveTrainingCheckpointError
from snake.sessions.TrainQLearning import play_move
from snake.storage.DQNArtifacts import (
    artifact_feature_set, checkpoint_data, common_metadata, load_artifact,
    save_torch_data,
)


FEATURE_SET = "v3"
# The Player name DQN games are saved under in Records.
PLAYER = "dqn"
# The average score covers this many of the most recent games.
RECENT_GAMES = 50
# The run id and checkpoint interval saved with the checkpoint; TrainDQN reads
# both when it resumes a Live Training save.
LIVE_TRAINING_RUN_ID = "live_training"
CHECKPOINT_EVERY = 25


@dataclass(frozen=True)
class LiveTrainingStats:
    games_played: int
    score: int
    best_score: int
    average_score: float
    epsilon: float


@dataclass(frozen=True)
class NetworkSnapshot:
    # One list per layer: the inputs, each hidden layer after ReLU, the Q-values.
    activations: list
    # One matrix per pair of layers, as weights[layer][to_neuron][from_neuron].
    weights: list
    actions: list
    chosen_action: str
    explored: bool


class LiveTrainingSession:
    def __init__(
        self, config, seed=0, max_moves=5000,
        checkpoint_path=DEFAULT_CHECKPOINT_PATH, settings=None,
        record_manager=None, speed_delay=None, player=PLAYER, now=time.perf_counter,
        replay_manager=None,
    ):
        self.config = config
        self.seed = seed
        self.max_moves = max_moves
        self.checkpoint_path = checkpoint_path
        self.moves_this_game = 0
        self.scores = []
        # Games are saved as Records only when a record manager is given, with
        # the Settings speed, like every other Bot Mode in Play.
        self.record_manager = record_manager
        # The best game is kept as a Replay only when a replay manager is given.
        self.replay_manager = replay_manager
        self.speed_delay = speed_delay
        self.player = player
        self.now = now
        self.session_start_time = now()
        self.game_start_time = now()

        # The same CPU settings and seed offsets as TrainDQN keep runs repeatable.
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        torch.manual_seed(seed + 3)
        self.engine = self._make_engine(game_number=0)
        self.bot = DQNBot(
            self.engine,
            random_source=random.Random(seed + 1),
            replay_random_source=random.Random(seed + 2),
            settings=dict(DEFAULT_DQN_SETTINGS if settings is None else settings),
            feature_set=FEATURE_SET,
        )
        self._start_replay()

    @classmethod
    def load(cls, checkpoint_path, config, **session_options):
        """Continue a saved Live Training on this board, starting its next game.

        Raises LiveTrainingCheckpointError, leaving the file untouched, when
        the save cannot be read or was made for another Feature Set.
        """
        try:
            data = load_artifact(checkpoint_path, "dqn_training_checkpoint")
        except ValueError as error:
            raise LiveTrainingCheckpointError(
                f"Saved Live Training could not be read.\n"
                f"Delete {checkpoint_path} to start over."
            ) from error
        metadata = data["metadata"]
        feature_set = artifact_feature_set(metadata, checkpoint_path)
        if feature_set != FEATURE_SET:
            raise LiveTrainingCheckpointError(
                f"Saved Live Training uses Feature Set {feature_set}, "
                f"but Live Training uses Feature Set {FEATURE_SET}.\n"
                f"Delete {checkpoint_path} to start over."
            )
        # The save may come from another board size. Feature Set inputs do not
        # depend on the board, so the same DQN keeps learning here (ADR 0012),
        # and the next save records this board.

        session = cls(
            config, seed=metadata["base_seed"], max_moves=metadata["max_moves"],
            checkpoint_path=checkpoint_path, settings=metadata["learning_settings"],
            **session_options,
        )
        state = data["state"]
        bot = session.bot
        bot.network.load_state_dict(state["online_weights"])
        bot.target_network.load_state_dict(state["target_weights"])
        bot.optimizer.load_state_dict(state["optimizer"])
        bot.replay.extend(state["replay"])
        bot.epsilon = state["epsilon"]
        bot.game_trained = state["game_trained"]
        bot.optimizer_steps = state["optimizer_steps"]
        bot.random_source.setstate(state["bot_random_state"])
        bot.replay_random_source.setstate(state["replay_random_state"])
        torch.set_rng_state(state["torch_random_state"])

        scores = metadata.get("live_training_scores")
        valid_scores = (
            isinstance(scores, list) and len(scores) == bot.game_trained
            and all(type(score) is int for score in scores)
        )
        session.scores = list(scores) if valid_scores else []
        # Like TrainDQN's resume, the next game starts fresh; a game left
        # halfway keeps what it taught the network.
        session.engine = session._make_engine(game_number=bot.game_trained)
        bot.engine = session.engine
        session._start_replay()
        return session

    def save(self):
        """Save this Live Training as a DQN Training Checkpoint at its own path."""
        metadata = common_metadata(
            self.config, self.bot.settings, self.seed, self.max_moves,
            LIVE_TRAINING_RUN_ID, None, FEATURE_SET,
        )
        metadata["checkpoint_every"] = CHECKPOINT_EVERY
        metadata["live_training_scores"] = list(self.scores)
        save_torch_data(
            self.checkpoint_path, checkpoint_data(self.bot, self.engine, metadata)
        )

    def make_move(self):
        """Make one training move, and start the next game if this one ended."""
        score_before = self.engine.score
        game_ended = play_move(self.engine, self.bot)
        self.moves_this_game += 1
        if self.replay_manager is not None:
            # A replay plays back one direction per move; after the move the
            # snake faces the direction it really moved in.
            self.replay_manager.record_move(self.engine.state.direction)
            if self.engine.score > score_before and self.engine.food_position is not None:
                self.replay_manager.record_food(self.engine.food_position)
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

    def network_snapshot(self):
        """What the network saw and decided on the last move, for drawing.

        Activations and weights use the network as it is now. Whether the move
        was exploration compares it with the best safe action when it was
        chosen, because learning after the move may already change that.
        Returns None before the first move.
        """
        features = self.bot.current_features
        if features is None:
            return None

        with torch.no_grad():
            values = torch.tensor(features, dtype=torch.float32)
            activations = [values.tolist()]
            for layer in self.bot.network:
                values = layer(values)
                if not isinstance(layer, torch.nn.Linear):
                    # Replace the Linear output with the value after its ReLU.
                    activations.pop()
                activations.append(values.tolist())
            weights = [
                layer.weight.tolist() for layer in self.bot.network
                if isinstance(layer, torch.nn.Linear)
            ]

        actions = list(self.bot.actions)
        # Every Feature Set starts with one danger flag per action.
        safe_actions = [
            action for action, danger in zip(actions, features) if not danger
        ] or actions
        decision_values = self.bot.current_action_values
        best_action = max(safe_actions, key=lambda action: decision_values[action])
        return NetworkSnapshot(
            activations=activations,
            weights=weights,
            actions=actions,
            chosen_action=self.bot.current_action,
            explored=self.bot.current_action != best_action,
        )

    def stats(self):
        recent_scores = self.scores[-RECENT_GAMES:]
        average_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        return LiveTrainingStats(
            games_played=self.bot.game_trained,
            score=self.engine.score,
            best_score=max(self.scores, default=0),
            average_score=average_score,
            epsilon=self.bot.epsilon,
        )

    def _finish_game(self):
        self.bot.on_game_end(self.engine.state)
        self.bot.take_game_loss()
        self.scores.append(self.engine.score)
        self._save_record()
        if self.replay_manager is not None:
            self.replay_manager.save_replay(
                self.player, self.engine.score, self.engine.game_won
            )
        self.engine = self._make_engine(game_number=self.bot.game_trained)
        self.bot.engine = self.engine
        self.moves_this_game = 0
        self._start_replay()

    def _start_replay(self):
        if self.replay_manager is None:
            return
        self.replay_manager.start_recording(
            self.player, self.config.width, self.config.height, self.config.tile_size,
            # Replays need a delay; Replay plays back at its own Replay Speed.
            self.speed_delay if self.speed_delay is not None else 0,
            engine=self.engine,
        )

    def _save_record(self):
        if self.record_manager is None:
            return
        if self.engine.game_won:
            outcome = "won"
        elif self.engine.game_over:
            outcome = "died"
        else:
            # Stopped at the move limit: neither won nor died, so unknown.
            outcome = ""
        stats = self.stats()
        now = self.now()
        self.record_manager.save_game_result(
            self.player,
            stats.games_played,
            self.engine.score,
            stats.best_score,
            stats.average_score,
            self.moves_this_game,
            now - self.game_start_time,
            now - self.session_start_time,
            self.config.width,
            self.config.height,
            self.config.tile_size,
            self.speed_delay,
            outcome=outcome,
        )
        self.game_start_time = now

    def _make_engine(self, game_number):
        return SnakeEngine(
            self.config, start_position=None,
            random_source=random.Random(self.seed + game_number),
        )
