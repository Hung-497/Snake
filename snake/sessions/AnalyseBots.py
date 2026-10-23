"""Write a Bot Report from saved Bot Experiment reports (ADR 0020).

It only reads the reports that Evaluate and the Bot Experiment commands saved;
it never plays a game or changes a saved file. With --showcase it writes the
committed Showcase Report instead of a local Bot Report.
"""

import argparse
from pathlib import Path
import sys

from snake.analysis.BotReport import build_bot_report
from snake.analysis.ExperimentRuns import read_experiment_runs
from snake.analysis.LocalReport import LOCAL_REPORT_FOLDER, LOCAL_REPORT_NAME, write_report_files
from snake.analysis.Showcase import select_showcase_runs


LOCAL_REPORT = (LOCAL_REPORT_NAME, LOCAL_REPORT_FOLDER)
SHOWCASE_REPORT = ("showcase", Path("docs") / "results")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Write a Bot Report from saved Bot Experiments")
    parser.add_argument("--experiments", default="experiments",
                        help="Folder of saved Bot Experiment reports")
    parser.add_argument("--output", help="Folder to write the report to")
    parser.add_argument(
        "--showcase", action="store_true",
        help="Write the Showcase Report from full study evaluations of the Showcase Bots",
    )
    options = parser.parse_args(argv)

    runs, skipped = read_experiment_runs(options.experiments)
    if options.showcase:
        name, default_output = SHOWCASE_REPORT
        selected, not_evaluated = select_showcase_runs(runs)
        left_out = len(runs) - len(selected)
        if not selected:
            print(
                "No study evaluations of a Showcase Bot or Baseline in "
                f"{options.experiments}/ ({skipped} skipped, {left_out} runs left out). "
                "Evaluate them on the 200 study games first.",
                file=sys.stderr,
            )
            return 1
        report = build_bot_report(selected, skipped, showcase=True, not_evaluated=not_evaluated)
    else:
        name, default_output = LOCAL_REPORT
        left_out = 0
        if not runs:
            print(
                f"No usable Bot Experiment reports in {options.experiments}/ "
                f"({skipped} skipped). Run Evaluate or a Bot Experiment first.",
                file=sys.stderr,
            )
            return 1
        report = build_bot_report(runs, skipped)

    output = Path(options.output) if options.output else default_output
    html_path = write_report_files(report, name, output)
    markdown_path = html_path.with_suffix(".md")

    print(
        f"{report.title}: {count(report.run_count, 'run')} in "
        f"{count(len(report.groups), 'group')}, {skipped} skipped report files"
        + (f", {left_out} runs left out." if options.showcase else ".")
    )
    print(f"Wrote {markdown_path} and {html_path}")
    return 0


def count(number, noun):
    return f"{number} {noun}" + ("" if number == 1 else "s")


if __name__ == "__main__":
    raise SystemExit(main())
