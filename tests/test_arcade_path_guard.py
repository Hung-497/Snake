"""Arcade 3.3 appends its lib folder to PATH on Windows without a ";" first.

That glues Arcade's folder onto whatever folder was last on PATH, so a program
there (for example Git) can no longer be found. The guard ends PATH with ";"
before Arcade is imported, so Arcade's folder becomes a separate entry.
"""

from snake.ArcadePathGuard import end_path_with_separator


GIT = r"C:\Program Files\Git\cmd"
ARCADE_LIB = r"C:\venv\Lib\site-packages\arcade\lib"


def test_windows_path_gets_a_trailing_separator():
    environ = {"PATH": rf"C:\Windows;{GIT}"}

    end_path_with_separator(environ, "win32")

    assert environ["PATH"] == rf"C:\Windows;{GIT};"


def test_arcade_append_after_the_guard_keeps_every_folder_intact():
    environ = {"PATH": rf"C:\Windows;{GIT}"}

    end_path_with_separator(environ, "win32")
    environ["PATH"] += ARCADE_LIB  # exactly what Arcade 3.3 does on Windows

    assert environ["PATH"].split(";") == [r"C:\Windows", GIT, ARCADE_LIB]


def test_path_that_already_ends_with_a_separator_is_unchanged():
    environ = {"PATH": rf"C:\Windows;{GIT};"}

    end_path_with_separator(environ, "win32")

    assert environ["PATH"] == rf"C:\Windows;{GIT};"


def test_missing_path_is_left_alone():
    environ = {}

    end_path_with_separator(environ, "win32")

    assert environ == {}


def test_macos_and_linux_are_left_alone():
    for platform in ("darwin", "linux"):
        environ = {"PATH": "/usr/bin:/opt/git/bin"}

        end_path_with_separator(environ, platform)

        assert environ["PATH"] == "/usr/bin:/opt/git/bin"


def test_loading_the_snake_package_applies_the_guard(monkeypatch):
    import importlib
    import os
    import sys

    import snake

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("PATH", rf"C:\Windows;{GIT}")

    importlib.reload(snake)

    assert os.environ["PATH"] == rf"C:\Windows;{GIT};"
