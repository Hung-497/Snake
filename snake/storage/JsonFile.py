"""Save JSON files so an interrupted save never leaves a broken file."""

import json
import os


def save_json_atomically(path, data):
    """
    Write data to a temporary file first, then swap it in with os.replace.

    The swap is all-or-nothing, so the file at path is always either the
    complete old version or the complete new one. If the save stops part-way
    (Ctrl+C, a crash), the old file is left as it was and the half-written
    temporary file is removed.
    """
    temporary_path = f"{path}.saving"
    try:
        with open(temporary_path, "w") as file:
            json.dump(data, file, indent=4)
        os.replace(temporary_path, path)
    except BaseException:
        # BaseException also catches Ctrl+C (KeyboardInterrupt).
        if (os.path.exists(temporary_path)):
            os.remove(temporary_path)
        raise
