"""The app always uses the Snake folder's data, wherever it is started from."""

from pathlib import Path

import SnakeApp


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_the_app_uses_its_own_folder_when_started_from_elsewhere(tmp_path, monkeypatch):
    # Like running `python ~/Snake/SnakeApp.py` from another folder.
    monkeypatch.chdir(tmp_path)

    SnakeApp.use_project_folder()

    assert Path.cwd() == PROJECT_ROOT
    assert (Path("starter_data") / "showcase").is_dir()
