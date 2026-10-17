"""Saved preferences can be restored without opening an Arcade window."""

import json
from pathlib import Path

import pytest

from snake.sessions.SessionSettings import SessionSettings
from snake.storage.SettingsFile import SettingsFile


def test_choices_survive_loading_a_new_settings_object(tmp_path):
    settings_file = SettingsFile(tmp_path / "settings.json")
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")
    settings.select_tile_size("Large tiles 30 px")
    settings.select_speed("Normal")

    settings_file.save(settings)
    restored = settings_file.load()

    assert restored.selected_board_size_name == "Small 16 x 16"
    assert restored.selected_tile_size_name == "Large tiles 30 px"
    assert restored.selected_speed_name == "Normal"
    # Values do not depend on the wording of dropdown labels.
    assert json.loads(settings_file.path.read_text()) == {
        "schema_version": 1,
        "board_size": [16, 16],
        "tile_size": 30,
        "speed": "Normal",
    }


@pytest.mark.parametrize("contents", [None, "{broken", "[]", "null", '{"schema_version": 2}', '\ufeff{}'])
def test_missing_or_unreadable_settings_use_defaults_without_rewriting(tmp_path, contents):
    path = tmp_path / "settings.json"
    if contents is not None:
        path.write_text(contents, encoding="utf-8")

    settings = SettingsFile(path).load()

    assert settings.selected_board_size_name == "Medium 24 x 25"
    assert settings.selected_tile_size_name == "Medium tiles 25 px"
    assert settings.selected_speed_name == "Fast"
    if contents is None:
        assert not path.exists()
    else:
        assert path.read_text(encoding="utf-8") == contents


@pytest.mark.parametrize("field,value", [
    ("board_size", [99, 99]),
    ("board_size", [16.0, 16.0]),
    ("board_size", "Small 16 x 16"),
    ("tile_size", 99),
    ("tile_size", "30"),
    ("speed", "Ludicrous"),
    ("speed", []),
])
def test_an_invalid_choice_does_not_discard_other_valid_choices(tmp_path, field, value):
    path = tmp_path / "settings.json"
    data = {"schema_version": 1, "board_size": [16, 16], "tile_size": 30, "speed": "Normal"}
    data[field] = value
    path.write_text(json.dumps(data))

    restored = SettingsFile(path).load()

    assert restored.selected_board_size_name == ("Medium 24 x 25" if field == "board_size" else "Small 16 x 16")
    assert restored.selected_tile_size_name == ("Medium tiles 25 px" if field == "tile_size" else "Large tiles 30 px")
    assert restored.selected_speed_name == ("Fast" if field == "speed" else "Normal")


def test_read_errors_use_defaults(tmp_path, monkeypatch):
    def unreadable(*args, **kwargs):
        raise PermissionError("Cannot read this file")

    monkeypatch.setattr(Path, "open", unreadable)

    assert SettingsFile(tmp_path / "settings.json").load().selected_speed_name == "Fast"


def test_default_location_does_not_depend_on_the_launch_folder(tmp_path, monkeypatch):
    expected = Path(__file__).resolve().parents[1] / "settings.json"
    monkeypatch.chdir(tmp_path)

    assert SettingsFile().path == expected
    assert not (tmp_path / "settings.json").exists()


def test_a_failed_atomic_save_preserves_the_previous_choices(tmp_path, monkeypatch):
    settings_file = SettingsFile(tmp_path / "settings.json")
    settings = SessionSettings()
    settings_file.save(settings)
    original = settings_file.path.read_bytes()
    settings.select_speed("Slow")

    def interrupted_dump(data, file, **kwargs):
        file.write('{"schema_version":')
        raise OSError("Disk full")

    monkeypatch.setattr("snake.storage.JsonFile.json.dump", interrupted_dump)
    with pytest.raises(OSError, match="Disk full"):
        settings_file.save(settings)

    assert settings_file.path.read_bytes() == original
    assert not settings_file.path.with_suffix(".json.saving").exists()
