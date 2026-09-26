"""Versioned, data-only files for DQN training and evaluation."""

import hashlib
import json
import math
from pathlib import Path
import pickle
import random

import torch

from snake.bots.DQNBot import DEFAULT_DQN_SETTINGS, make_network


ARTIFACT_VERSION = 2
SUPPORTED_ARTIFACT_VERSIONS = (1, ARTIFACT_VERSION)
FEATURE_SCHEMA = "q_learning_space_state_v2"
ACTIONS = ["Straight", "Turn_Left", "Turn_Right"]


def board_details(config):
    return {
        "width": config.width,
        "height": config.height,
        "tile_size": config.tile_size,
    }


def dqn_details(settings):
    """Describe the complete V1 CPU learning recipe saved with each artifact."""
    hidden_size = settings["hidden_size"]
    return {
        "device": "cpu",
        "network": {
            "input_size": 9,
            "hidden_sizes": [hidden_size, hidden_size],
            "output_size": 3,
            "activation": "ReLU",
        },
        "optimizer": {
            "name": "Adam",
            "learning_rate": settings["learning_rate"],
        },
        "experience_replay": {
            "capacity": settings["replay_capacity"],
            "batch_size": settings["batch_size"],
            # Learning starts as soon as one complete batch can be sampled.
            "warmup_size": settings["batch_size"],
            "sampling": "uniform",
        },
        "target_network": {
            "update_interval_optimizer_steps": settings["target_update_steps"],
        },
    }


def save_torch_data(path, data):
    """Replace only this run's file after the complete data has been written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(path.name + ".tmp")
    torch.save(data, temporary_path)
    temporary_path.replace(path)


def save_json_data(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(path.name + ".tmp")
    temporary_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary_path.replace(path)


def common_metadata(config, settings, seed, max_moves, run_id, source_checkpoint):
    return {
        "run_id": run_id,
        "source_checkpoint": source_checkpoint,
        "training_board": board_details(config),
        "learning_settings": dict(settings),
        "dqn_details": dqn_details(settings),
        "base_seed": seed,
        "max_moves": max_moves,
        "feature_schema": FEATURE_SCHEMA,
        "actions": list(ACTIONS),
        "bot_seed_offset": 1,
        "replay_seed_offset": 2,
        "torch_seed_offset": 3,
        "torch_version": str(torch.__version__),
    }


def checkpoint_data(bot, engine, metadata):
    return {
        "schema_version": ARTIFACT_VERSION,
        "artifact_type": "dqn_training_checkpoint",
        "metadata": dict(metadata),
        "state": {
            "online_weights": bot.network.state_dict(),
            "target_weights": bot.target_network.state_dict(),
            "optimizer": bot.optimizer.state_dict(),
            "epsilon": bot.epsilon,
            "game_trained": bot.game_trained,
            "optimizer_steps": bot.optimizer_steps,
            "replay": list(bot.replay),
            "engine_random_state": engine.random_source.getstate(),
            "bot_random_state": bot.random_source.getstate(),
            "replay_random_state": bot.replay_random_source.getstate(),
            "torch_random_state": torch.get_rng_state(),
        },
    }


def evaluation_model_data(bot, metadata):
    return {
        "schema_version": ARTIFACT_VERSION,
        "artifact_type": "dqn_evaluation_model",
        "metadata": {**metadata, "game_trained": bot.game_trained},
        "online_weights": bot.network.state_dict(),
    }


def load_artifact(path, expected_type):
    """Load plain tensors and values, never arbitrary saved Python objects."""
    try:
        data = torch.load(path, map_location="cpu", weights_only=True)
    except (OSError, RuntimeError, ValueError, EOFError, pickle.UnpicklingError) as error:
        raise ValueError(f"Missing or invalid DQN artifact: {path}") from error
    if not isinstance(data, dict):
        raise ValueError(f"Invalid DQN artifact: {path}")
    artifact_version = data.get("schema_version")
    if artifact_version not in SUPPORTED_ARTIFACT_VERSIONS:
        raise ValueError(f"Unsupported DQN artifact version: {path}")
    if data.get("artifact_type") != expected_type:
        raise ValueError(f"Wrong DQN artifact type: {path}")
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"Invalid DQN artifact metadata: {path}")
    if metadata.get("feature_schema") != FEATURE_SCHEMA or metadata.get("actions") != ACTIONS:
        raise ValueError(f"Incompatible DQN feature or action contract: {path}")
    settings = metadata.get("learning_settings")
    if not valid_settings(settings):
        raise ValueError(f"Invalid DQN learning settings: {path}")
    if (
        artifact_version >= 2
        and metadata.get("dqn_details") != dqn_details(settings)
    ):
        raise ValueError(f"Invalid DQN architecture or training details: {path}")
    board = metadata.get("training_board")
    if not isinstance(board, dict) or not all(
        type(board.get(key)) is int and board[key] > 0
        for key in ("width", "height", "tile_size")
    ):
        raise ValueError(f"Invalid DQN training board: {path}")
    if (
        type(metadata.get("base_seed")) is not int
        or type(metadata.get("max_moves")) is not int
        or metadata["max_moves"] <= 0
        or not isinstance(metadata.get("run_id"), str)
    ):
        raise ValueError(f"Invalid DQN artifact metadata: {path}")
    if expected_type == "dqn_training_checkpoint" and (
        type(metadata.get("checkpoint_every")) is not int
        or metadata["checkpoint_every"] <= 0
    ):
        raise ValueError(f"Invalid DQN checkpoint metadata: {path}")
    if expected_type == "dqn_evaluation_model" and (
        type(metadata.get("game_trained")) is not int
        or metadata["game_trained"] < 0
    ):
        raise ValueError(f"Invalid DQN model metadata: {path}")
    state = data.get("state")
    if expected_type == "dqn_training_checkpoint" and not isinstance(state, dict):
        raise ValueError(f"Invalid DQN checkpoint: {path}")
    weights = (
        data.get("online_weights") if expected_type == "dqn_evaluation_model"
        else state.get("online_weights")
    )
    try:
        make_network(settings["hidden_size"]).load_state_dict(weights, strict=True)
    except (RuntimeError, TypeError, ValueError) as error:
        raise ValueError(f"Invalid DQN network weights: {path}") from error
    if expected_type == "dqn_training_checkpoint":
        validate_checkpoint_state(state, settings, path)
    return data


def validate_checkpoint_state(state, settings, path):
    """Check that resume can restore every piece before a new run is made."""
    required = {
        "online_weights", "target_weights", "optimizer", "epsilon",
        "game_trained", "optimizer_steps", "replay", "engine_random_state",
        "bot_random_state", "replay_random_state", "torch_random_state",
    }
    if not required.issubset(state):
        raise ValueError(f"Invalid DQN checkpoint: {path}")
    if (
        type(state["game_trained"]) is not int or state["game_trained"] < 0
        or type(state["optimizer_steps"]) is not int or state["optimizer_steps"] < 0
        or type(state["epsilon"]) not in (int, float)
        or not math.isfinite(state["epsilon"])
        or not 0 <= state["epsilon"] <= 1
    ):
        raise ValueError(f"Invalid DQN checkpoint: {path}")
    replay = state["replay"]
    if not isinstance(replay, list) or len(replay) > settings["replay_capacity"]:
        raise ValueError(f"Invalid DQN checkpoint: {path}")
    for experience in replay:
        if not isinstance(experience, (tuple, list)) or len(experience) != 5:
            raise ValueError(f"Invalid DQN checkpoint replay: {path}")
        features, action, reward, next_features, game_over = experience
        if (
            not valid_features(features)
            or type(action) is not int or action not in (0, 1, 2)
            or type(reward) not in (int, float) or not math.isfinite(reward)
            or type(game_over) is not bool
            or (next_features is None) != game_over
            or (next_features is not None and not valid_features(next_features))
        ):
            raise ValueError(f"Invalid DQN checkpoint replay: {path}")
    try:
        network = make_network(settings["hidden_size"])
        network.load_state_dict(state["target_weights"], strict=True)
        optimizer = torch.optim.Adam(
            network.parameters(), lr=settings["learning_rate"]
        )
        optimizer.load_state_dict(state["optimizer"])
        for name in ("engine_random_state", "bot_random_state", "replay_random_state"):
            random.Random().setstate(state[name])
        torch_state = state["torch_random_state"]
        if (
            not isinstance(torch_state, torch.Tensor)
            or torch_state.dtype != torch.uint8
            or torch_state.ndim != 1
            or torch_state.numel() != torch.get_rng_state().numel()
        ):
            raise ValueError("invalid torch random state")
    except (KeyError, RuntimeError, TypeError, ValueError) as error:
        raise ValueError(f"Invalid DQN checkpoint: {path}") from error


def valid_features(features):
    return (
        isinstance(features, (tuple, list))
        and len(features) == 9
        and all(type(value) is int and value in (0, 1, 2) for value in features)
    )


def valid_settings(settings):
    if not isinstance(settings, dict) or set(settings) != set(DEFAULT_DQN_SETTINGS):
        return False
    for name in ("hidden_size", "batch_size", "replay_capacity", "target_update_steps"):
        if type(settings[name]) is not int or settings[name] <= 0:
            return False
    return (
        type(settings["learning_rate"]) in (float, int)
        and math.isfinite(settings["learning_rate"])
        and 0 < settings["learning_rate"] < 1
        and settings["batch_size"] <= settings["replay_capacity"]
    )


def model_identity(path, artifact):
    return {
        **artifact["metadata"],
        "model_path": str(path),
        "model_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
    }
