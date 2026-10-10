"""Protect PATH from an Arcade bug on Windows.

Arcade 3.3 runs `os.environ["PATH"] += str(lib_location)` when it is imported
on Windows, without a ";" in front. That glues Arcade's lib folder onto the
last folder in PATH, so programs there (for example Git) can no longer be
found by anything started afterwards. Ending PATH with ";" first turns
Arcade's folder into a separate entry. Other systems are not affected.
"""

import os
import sys


def end_path_with_separator(environ=None, platform=None):
    """On Windows, make sure PATH ends with ";" before Arcade adds to it."""
    environ = os.environ if environ is None else environ
    platform = sys.platform if platform is None else platform

    if platform != "win32" or "PATH" not in environ:
        return
    if not environ["PATH"].endswith(";"):
        environ["PATH"] += ";"
