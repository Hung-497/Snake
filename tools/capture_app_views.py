"""Capture real App Views with temporary sample data; run locally before a release."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
from tempfile import TemporaryDirectory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Run the project's PATH guard before importing Arcade.
import snake  # noqa: F401
import arcade
from snake.sessions.SessionSettings import SessionSettings
from snake.ui.AppShell import AppShell
from snake.ui.WindowLayout import minimum_window_size
from tools.capture_fixtures import prepare_files, view_builders


class CaptureWindow(arcade.Window):
    def update_board_minimum(self, config):
        self.set_minimum_size(*minimum_window_size(config.width, config.height, config.tile_size))


def capture(window, view, path):
    window.show_view(view)
    window.switch_to()
    # Several draws let Arcade upload text and finish widget layout. Only
    # widgets advance here; gameplay and training remain at their sample state.
    for _ in range(6):
        window.dispatch_events()
        view.ui.on_update(1 / 60)
        view.ui.execute_layout()
        view.ui.trigger_render()
        window.clear()
        view.on_draw()
        window.flip()
        time.sleep(0.01)
    window.clear()
    view.ui.trigger_render()
    view.on_draw()
    arcade.get_image().save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "screenshots")
    parser.add_argument("--only", nargs="+", help="Capture only these screen names (see manifest.json)")
    options = parser.parse_args()
    output = options.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"sample_data": True, "captures": [], "skipped": [], "failed": []}
    original_folder = Path.cwd()
    try:
        with TemporaryDirectory(prefix="snake-captures-") as directory:
            root = Path(directory)
            prepare_files(root)
            os.chdir(root)
            for width, height in ((700, 700), (900, 960)):
                window = CaptureWindow(width, height, visible=False)
                try:
                    settings = SessionSettings()
                    builders = view_builders(AppShell(window, {}), settings, root)
                    unknown = set(options.only or ()) - builders.keys()
                    if unknown:
                        parser.error(f"Unknown screens: {', '.join(sorted(unknown))}")
                    for name, build in builders.items():
                        if options.only and name not in options.only:
                            continue
                        if name in ("live_training", "live_background", "live_focus") and importlib.util.find_spec("torch") is None:
                            manifest["skipped"].append({"screen": name, "requested_size": [width, height], "reason": "PyTorch is not installed"})
                            continue
                        view = None
                        try:
                            # Live Training may raise the minimum while shown.
                            window.set_minimum_size(700, 700)
                            window.set_size(width, height)
                            view = build()
                            path = output / f"{name}_{width}x{height}.png"
                            capture(window, view, path)
                            manifest["captures"].append({"screen": name, "file": path.name,
                                "requested_size": [width, height], "actual_size": [window.width, window.height]})
                        except Exception as error:
                            manifest["failed"].append({"screen": name, "requested_size": [width, height], "error": str(error)})
                        finally:
                            if view is not None:
                                view.on_hide_view()
                finally:
                    window.close()
    finally:
        os.chdir(original_folder)
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Captured {len(manifest['captures'])} screens; skipped {len(manifest['skipped'])}; failed {len(manifest['failed'])}. Output: {output}")
    return 1 if manifest["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
