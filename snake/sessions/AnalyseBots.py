"""Write a Bot Report from saved Bot Experiment reports (ADR 0020).

It only reads the reports that Evaluate and the Bot Experiment commands saved;
it never plays a game or changes a saved file.
"""

import argparse
from pathlib import Path
import sys

from snake.analysis.BotReport import (
    CHART_FOLDER, build_bot_report, chart_files, write_html, write_markdown,
)
from snake.analysis.ExperimentRuns import read_experiment_runs


REPORT_NAME = "bot_report"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Write a Bot Report from saved Bot Experiments")
    parser.add_argument("--experiments", default="experiments",
                        help="Folder of saved Bot Experiment reports")
    parser.add_argument("--output", default="reports", help="Folder to write the Bot Report to")
    options = parser.parse_args(argv)

    runs, skipped = read_experiment_runs(options.experiments)
    if not runs:
        print(
            f"No usable Bot Experiment reports in {options.experiments}/ "
            f"({skipped} skipped). Run Evaluate or a Bot Experiment first.",
            file=sys.stderr,
        )
        return 1

    report = build_bot_report(runs, skipped)
    output = Path(options.output)
    output.mkdir(parents=True, exist_ok=True)
    markdown_path = output / f"{REPORT_NAME}.md"
    html_path = output / f"{REPORT_NAME}.html"
    markdown_path.write_text(write_markdown(report), encoding="utf-8")
    html_path.write_text(write_html(report), encoding="utf-8")
    write_charts(report, output / CHART_FOLDER)

    print(
        f"Bot Report: {report.run_count} runs in {len(report.groups)} groups, "
        f"{skipped} skipped report files."
    )
    print(f"Wrote {markdown_path} and {html_path}")
    return 0


def write_charts(report, folder):
    """Save each group's chart, removing charts of groups that no longer exist."""
    folder.mkdir(exist_ok=True)
    for old_chart in folder.glob("scores_*.svg"):
        old_chart.unlink()
    for name, svg in chart_files(report):
        (folder / name).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
