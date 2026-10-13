"""Open Live Training without making the app need PyTorch.

Nothing here imports PyTorch when the module loads, so the App View can use
it while the app still starts on installs without the dqn group (ADR 0007).
"""

MISSING_PYTORCH_MESSAGE = (
    "Live Training needs PyTorch, which is not installed.\n"
    "Install it with: uv sync --group dqn"
)


def missing_dependency_message():
    """Return why Live Training cannot start, or None when it can."""
    try:
        import torch  # noqa: F401
    except ImportError:
        return MISSING_PYTORCH_MESSAGE
    return None


def start_live_training(settings):
    """Start a fresh Live Training session on the board chosen in Settings."""
    from snake.sessions.LiveTrainingSession import LiveTrainingSession

    return LiveTrainingSession(settings.build_game_config())
