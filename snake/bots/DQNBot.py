"""A CPU Deep Q Learning Bot Mode using the shared learning rules."""

from collections import deque
import random

import torch
from torch import nn

from snake.bots.LearningBot import LearningBot


DEFAULT_DQN_SETTINGS = {
    "hidden_size": 64,
    "learning_rate": 0.001,
    "batch_size": 32,
    "replay_capacity": 10000,
    "target_update_steps": 100,
}


def make_network(hidden_size):
    """Nine existing features go in; one value for each relative action comes out."""
    return nn.Sequential(
        nn.Linear(9, hidden_size),
        nn.ReLU(),
        nn.Linear(hidden_size, hidden_size),
        nn.ReLU(),
        nn.Linear(hidden_size, 3),
    )


class DQNBot(LearningBot):
    def __init__(
        self, engine, random_source=None, replay_random_source=None,
        settings=None, evaluation_mode=False,
    ):
        super().__init__(engine, random_source)
        self.settings = dict(DEFAULT_DQN_SETTINGS if settings is None else settings)
        self.evaluation_mode = evaluation_mode
        self.network = make_network(self.settings["hidden_size"])
        self.target_network = None
        self.optimizer = None
        self.replay = deque(maxlen=self.settings["replay_capacity"])
        self.replay_random_source = (
            replay_random_source if replay_random_source is not None else random.Random()
        )
        self.optimizer_steps = 0
        self.game_trained = 0
        self.current_features = None
        self.current_action = None
        self.distance_before_move = 0
        self.game_losses = []

        if not evaluation_mode:
            self.target_network = make_network(self.settings["hidden_size"])
            self.target_network.load_state_dict(self.network.state_dict())
            self.optimizer = torch.optim.Adam(
                self.network.parameters(), lr=self.settings["learning_rate"]
            )

    def choose_action(self, state):
        self.current_features = self.features(state)
        features = torch.tensor(self.current_features, dtype=torch.float32)
        with torch.no_grad():
            values = self.network(features).tolist()
        action_values = dict(zip(self.actions, values))
        self.current_action = self.select_action(
            state, action_values, self.evaluation_mode
        )
        self.distance_before_move = self.get_food_distance(state)
        return self.action_direction(state, self.current_action)

    def observe(self, transition):
        if self.evaluation_mode:
            return

        next_state = self.engine.state
        next_distance = self.get_food_distance(next_state)
        space_level = self.action_space_level(
            self.current_features, self.current_action
        )
        reward = self.reward(
            transition.game_over, transition.ate_food,
            self.distance_before_move, next_distance, space_level,
        )
        next_features = None if transition.game_over else self.features(next_state)
        self.replay.append((
            self.current_features,
            self.actions.index(self.current_action),
            float(reward),
            next_features,
            transition.game_over,
        ))
        if len(self.replay) >= self.settings["batch_size"]:
            self._learn_from_replay()

    def _learn_from_replay(self):
        batch = self.replay_random_source.sample(
            list(self.replay), self.settings["batch_size"]
        )
        current_features = torch.tensor(
            [experience[0] for experience in batch], dtype=torch.float32
        )
        actions = torch.tensor(
            [experience[1] for experience in batch], dtype=torch.int64
        ).unsqueeze(1)
        rewards = torch.tensor(
            [experience[2] for experience in batch], dtype=torch.float32
        )
        # Terminal moves have no future value, as in tabular Q Learning.
        next_features = torch.tensor(
            [experience[3] if experience[3] is not None else (0,) * 9
             for experience in batch],
            dtype=torch.float32,
        )
        still_playing = torch.tensor(
            [not experience[4] for experience in batch], dtype=torch.float32
        )

        chosen_values = self.network(current_features).gather(1, actions).squeeze(1)
        with torch.no_grad():
            best_next_values = self.target_network(next_features).max(dim=1).values
            targets = rewards + self.discount_rate * best_next_values * still_playing

        loss = nn.functional.smooth_l1_loss(chosen_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.optimizer_steps += 1
        self.game_losses.append(float(loss.item()))
        if self.optimizer_steps % self.settings["target_update_steps"] == 0:
            self.target_network.load_state_dict(self.network.state_dict())

    def on_game_end(self, result):
        if self.evaluation_mode:
            return
        self.game_trained += 1
        self.decay_epsilon()

    def take_game_loss(self):
        mean_loss = sum(self.game_losses) / len(self.game_losses) if self.game_losses else None
        self.game_losses.clear()
        return mean_loss
