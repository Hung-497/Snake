"""Live Training keeps DQN's best game as a Replay that plays back on the board."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


pytest.importorskip("torch")

from snake.engine.GameConfig import GameConfig
from snake.sessions.LiveTraining import start_live_training
from snake.sessions.LiveTrainingSession import LiveTrainingSession
from snake.sessions.ReplaySession import load_replay_session
from snake.sessions.SessionSettings import SessionSettings
from snake.storage.ReplayManager import ReplayManager


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class FakeClock:
    """A clock that moves forward one second every time it is read."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        self.now += 1.0
        return self.now


class WatchingReplayManager(ReplayManager):
    """A real replay manager that also remembers each finished game's board."""

    def __init__(self, folder_name):
        super().__init__(folder_name)
        self.session = None
        self.finished_games = []

    def save_replay(self, player, score, game_won=False):
        self.finished_games.append((score, self.session.engine.state))
        super().save_replay(player, score, game_won)


def make_session(tmp_path, folder="replays", replay_manager=None):
    replay_manager = replay_manager or ReplayManager(str(tmp_path / folder))
    return LiveTrainingSession(
        GameConfig(6, 6, 20), seed=7, max_moves=200,
        checkpoint_path=tmp_path / "save.pt", replay_manager=replay_manager,
    )


def play_games(session, games):
    while session.stats().games_played < games:
        session.make_move()


def play_to_the_end(replay_session):
    while not replay_session.finished:
        replay_session.advance()


def test_the_best_dqn_game_is_kept_and_worse_games_do_not_replace_it(tmp_path):
    session = make_session(tmp_path)

    play_games(session, 12)

    replay = session.replay_manager.load_replay("dqn")
    best_game = session.scores.index(max(session.scores))
    assert replay["player"] == "dqn"
    assert replay["final_score"] == max(session.scores)
    # A later, lower game was played, and the best replay was kept anyway.
    assert min(session.scores[best_game + 1:]) < replay["final_score"]
    assert (tmp_path / "replays" / "dqn_best.json").exists()


def test_the_replay_plays_back_to_the_same_final_board(tmp_path):
    replay_manager = WatchingReplayManager(str(tmp_path / "replays"))
    session = make_session(tmp_path, replay_manager=replay_manager)
    replay_manager.session = session

    play_games(session, 6)

    best_score = max(session.scores)
    final_state = next(state for score, state in replay_manager.finished_games
                       if score == best_score)
    replay_session, message = load_replay_session(ReplayManager(str(tmp_path / "replays")), "dqn")
    assert message is None
    play_to_the_end(replay_session)
    assert replay_session.score == best_score
    assert replay_session.snake_position == final_state.snake_position
    assert list(replay_session.snake_body) == list(final_state.snake_body)


def test_background_play_saves_the_same_best_replay(tmp_path):
    in_batches = make_session(tmp_path, folder="background")
    one_at_a_time = make_session(tmp_path, folder="live")

    moves = 0
    while in_batches.stats().games_played < 6:
        moves += in_batches.make_moves_for(25.0, clock=FakeClock())
    for _ in range(moves):
        one_at_a_time.make_move()

    live_replay = (tmp_path / "live" / "dqn_best.json").read_text()
    background_replay = (tmp_path / "background" / "dqn_best.json").read_text()
    assert json.loads(background_replay) == json.loads(live_replay)


def test_opening_live_training_saves_replays_in_the_replays_folder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")

    session = start_live_training(settings, checkpoint_path=tmp_path / "save.pt")
    play_games(session, 1)

    assert (tmp_path / "replays" / "dqn_best.json").exists()


def test_a_dqn_replay_plays_without_pytorch(tmp_path):
    session = make_session(tmp_path)
    play_games(session, 3)
    blocker = tmp_path / "blocked_dependency"
    blocker.mkdir()
    (blocker / "torch.py").write_text(
        "raise ImportError('Replay must not import PyTorch')\n", encoding="utf-8"
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join((str(blocker), str(PROJECT_ROOT)))
    script = (
        "from snake.sessions.ReplaySession import load_replay_session\n"
        "from snake.storage.ReplayManager import ReplayManager\n"
        "session, message = load_replay_session(ReplayManager('replays'), 'dqn')\n"
        "assert message is None, message\n"
        "while not session.finished:\n"
        "    session.advance()\n"
        "print(session.score)\n"
    )

    result = subprocess.run(
        [sys.executable, "-c", script], cwd=tmp_path, env=environment,
        capture_output=True, text=True, timeout=120,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == str(max(session.scores))
