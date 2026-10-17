"""Exercise app startup and Settings changes without a graphical window."""

from types import SimpleNamespace

import SnakeApp
from snake.sessions.SessionSettings import SessionSettings
from snake.storage.SettingsFile import SettingsFile
from snake.ui.views.SettingsView import SettingsView


class FakeWindow:
    def update_board_minimum(self, config):
        self.config = config

    def show_view(self, view):
        self.current_view = view


class SettingsControls:
    """Use the real change handler, replacing only graphical construction."""

    change_setting = SettingsView.change_setting

    def __init__(self, shell, settings, settings_file):
        self.shell = shell
        self.settings = settings
        self.settings_file = settings_file
        self.message_text = ""
        self.message_label = SimpleNamespace(text="")


def test_app_restores_preferences_and_saves_dropdown_changes(tmp_path, monkeypatch):
    settings_file = SettingsFile(tmp_path / "settings.json")
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")
    settings_file.save(settings)
    monkeypatch.setattr(SnakeApp, "SnakeWindow", FakeWindow)
    monkeypatch.setattr(SnakeApp, "SettingsFile", lambda: settings_file)
    monkeypatch.setattr(SnakeApp, "SettingsView", SettingsControls)

    shell = SnakeApp.create_app()
    shell.show_view("settings")
    controls = shell.window.current_view

    assert shell.window.config.width == 16
    assert controls.settings.selected_board_size_name == "Small 16 x 16"
    controls.change_setting(controls.settings.select_speed, "Normal")

    restarted = SnakeApp.create_app()
    restarted.show_view("settings")
    assert restarted.window.current_view.settings.selected_speed_name == "Normal"
    assert controls.message_label.text == ""


def test_save_failure_keeps_the_current_choice_and_can_be_retried(tmp_path, monkeypatch):
    settings_file = SettingsFile(tmp_path / "settings.json")
    settings = SessionSettings()
    shell = SimpleNamespace(window=FakeWindow())
    controls = SettingsControls(shell, settings, settings_file)

    def cannot_save(settings):
        raise PermissionError("Read-only folder")

    with monkeypatch.context() as patch:
        patch.setattr(settings_file, "save", cannot_save)
        controls.change_setting(settings.select_speed, "Normal")

    assert settings.selected_speed_name == "Normal"
    assert controls.message_label.text == "Could not save settings. Choices apply until the app closes."
    assert not settings_file.path.exists()

    controls.change_setting(settings.select_tile_size, "Small tiles 20 px")

    assert controls.message_label.text == ""
    assert settings_file.load().selected_speed_name == "Normal"
    assert settings_file.load().selected_tile_size_name == "Small tiles 20 px"
