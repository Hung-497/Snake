"""Deterministic sample states for local screenshots, stored only in a temporary folder."""

import csv
import json
import inspect
import random
from types import SimpleNamespace
from unittest.mock import patch

from snake.sessions.EvaluationSession import EvaluationProgress
from snake.sessions.ReplaySession import ReplaySession
from snake.sessions.TrainingSaves import SavedTraining
from snake.storage.RecordManager import RECORD_COLUMNS
from snake.ui.EvaluationBrowser import EvaluationBrowser
from snake.ui.views.EvaluateView import EvaluateView
from snake.ui.views.GameView import GameView
from snake.ui.views.LiveTrainingView import LiveTrainingView
from snake.ui.views.MenuView import MenuView
from snake.ui.views.PlayView import PlayView
from snake.ui.views.RecordsView import RecordsView
from snake.ui.views.ReplayPlaybackView import ReplayPlaybackView
from snake.ui.views.ReplayView import ReplayView
from snake.ui.views.SettingsView import SettingsView
from snake.ui.views.TrainingSetupView import TrainingSetupView
from snake.ui.views.TrainingStartView import TrainingStartView
from snake.ui.views.VersionView import VersionView


def prepare_files(root):
    for folder in ("records", "experiments", "learning_data", "replays", "empty"):
        (root / folder).mkdir()
    with (root / "records" / "game_records.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=RECORD_COLUMNS)
        writer.writeheader()
        for player in ("rule", "q_learning", "q_learning_v3", "dqn", "human"):
            for number in range(12):
                writer.writerow(dict(zip(RECORD_COLUMNS, (
                    "2026-10-17 12:30:00", player, number + 1, 10 + number,
                    21, 15.5, 100, 2, 24, 24, 25, 25, 1, "died",
                ))))
    for number in range(12):
        player = "q_learning_v3" if number % 2 else "dqn"
        games = [{"seed": 200000 + n, "score": 40 + number, "moves": 100,
                  "outcome": "collision"} for n in range(20)]
        report = {
            "schema_version": 3, "created_at": f"2026-10-{number + 1:02}T12:30:00Z",
            "evaluated": "showcase" if number % 2 else "app_training",
            "selected_bot_modes": [player], "game_count": 20, "base_seed": 200000,
            "max_moves": 5000, "board": {"width": 24, "height": 25},
            "bots": {player: {"games": games, "summary": {
                "mean_score": 40 + number, "best_score": 40 + number,
            }}},
        }
        (root / "experiments" / f"sample_{number}.json").write_text(json.dumps(report))
    (root / "experiments" / "damaged.json").write_text("{sample damaged report")
    for number in (1, 2):
        (root / "learning_data" / f"q_table_app_v3_2026-10-17_12300{number}.json").write_text("sample backup")


def record_view(shell, settings, root, tab, empty=False):
    from snake.storage.RecordManager import RecordManager
    directory = root / ("empty" if empty else "experiments")
    record_path = root / ("empty" if empty else "records") / "game_records.csv"
    view = RecordsView(shell, settings, RecordManager(record_path), EvaluationBrowser(directory))
    view.selected_tab = tab
    view.refresh()
    return view


def game_view(shell, settings, state):
    random.seed(42)
    view = GameView(shell, settings, "rule" if state == "bot" else "human")
    # A sample game ending must not append a current timestamp to the fixed
    # CSV fixtures that the Records screenshots use later.
    view.session.record_manager = SimpleNamespace(save_game_result=lambda *args, **kwargs: None)
    if state in ("paused", "over"):
        from snake.engine.GameTypes import Direction
        view.session.press_direction(Direction.RIGHT)
        if state == "paused":
            view.session.pause()
        else:
            while not view.session.game_over:
                view.session.advance()
    return view


def replay_view(shell, state):
    data = {
        "coordinate_system": "grid", "board_width": 16, "board_height": 16,
        "tile_size": 25, "start_snake": [5, 5], "foods": [[7, 5], [7, 7]],
        "moves": [4, 4, 3, 3], "final_score": 2,
    }
    session = ReplaySession(data)
    session.advance()
    session.advance()
    if state == "paused":
        session.toggle_pause()
    elif state == "finished":
        while not session.finished:
            session.advance()
    return ReplayPlaybackView(shell, session, "human")


def evaluation_view(shell, root, finished):
    progress = EvaluationProgress(20 if finished else 8, 20, 48.5, 71, 0)
    session = SimpleNamespace(
        finished=finished, progress=lambda: progress,
        report_path="experiments/experiment_" + "a" * 32 + ".json",
    )
    with patch.object(EvaluateView, "start_session", return_value=session):
        return EvaluateView(shell, "q_learning_v3", 20, source="showcase")


def live_view(shell, settings, root, state):
    if state == "missing":
        from snake.sessions.LiveTraining import MISSING_PYTORCH_MESSAGE
        with patch("snake.ui.views.LiveTrainingView.missing_dependency_message",
                   return_value=MISSING_PYTORCH_MESSAGE):
            return LiveTrainingView(shell, settings)
    from snake.sessions.LiveTrainingSession import LiveTrainingSession
    session = LiveTrainingSession(settings.build_game_config(), seed=42,
                                  checkpoint_path=root / "learning_data" / "capture.pt")
    for _ in range(12):
        session.make_move()
    with patch("snake.ui.views.LiveTrainingView.start_live_training", return_value=session):
        view = LiveTrainingView(shell, settings)
    view.paused = True
    view.background_mode = state == "background"
    view.focus_layout = state == "focus"
    return view


def view_builders(shell, settings, root):
    builders = {
        "menu": lambda: MenuView(shell),
        "play": lambda: PlayView(shell, settings),
        "settings": lambda: settings_view(shell, settings, root),
        "version_q_learning": lambda: VersionView(shell, "q_learning", lambda mode: None, lambda: None),
        "version_dqn": lambda: VersionView(shell, "dqn", lambda mode: None, lambda: None),
        "training_start_empty": lambda: TrainingStartView(shell, "q_learning_v3", None, lambda: None),
        "training_start_saved": lambda: TrainingStartView(shell, "q_learning_v3", SavedTraining(2000, 118, 2000), lambda: None),
        "training_setup": lambda: TrainingSetupView(shell, "q_learning_v3", lambda: None),
        "replay_menu": lambda: ReplayView(shell),
        "evaluate_running": lambda: evaluation_view(shell, root, False),
        "evaluate_finished": lambda: evaluation_view(shell, root, True),
        "live_missing": lambda: live_view(shell, settings, root, "missing"),
    }
    def game_count_view():
        view = TrainingStartView(shell, "q_learning_v3", None, lambda: None)
        view.evaluating = "showcase"
        view.build_ui()
        return view
    builders["evaluate_game_count"] = game_count_view
    for state in ("human", "bot", "paused", "over"):
        builders[f"game_{state}"] = lambda state=state: game_view(shell, settings, state)
    for state in ("playing", "paused", "finished"):
        builders[f"replay_{state}"] = lambda state=state: replay_view(shell, state)
    for tab in ("compare", "trends", "games", "evaluate"):
        builders[f"records_{tab}"] = lambda tab=tab: record_view(shell, settings, root, tab)
    builders["records_empty"] = lambda: record_view(shell, settings, root, "compare", True)
    builders["records_evaluate_empty"] = lambda: record_view(shell, settings, root, "evaluate", True)
    for state in ("training", "background", "focus"):
        builders[f"live_{state}"] = lambda state=state: live_view(shell, settings, root, state)
    return builders


def settings_view(shell, settings, root):
    # Keep captures compatible with the separate, still-open Settings PR #182.
    if "settings_file" in inspect.signature(SettingsView).parameters:
        from snake.storage.SettingsFile import SettingsFile
        return SettingsView(shell, settings, SettingsFile(root / "settings.json"))
    return SettingsView(shell, settings)
