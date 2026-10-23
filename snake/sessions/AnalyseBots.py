"""Write a Bot Report from saved Bot Experiment reports (ADR 0020).

It only reads the reports that Evaluate and the Bot Experiment commands saved;
it never plays a game or changes a saved file. With --showcase it writes the
committed Showcase Report instead of a local Bot Report.
"""

import argparse
from pathlib import Path
import sys

from snake.analysis.BotReport import build_bot_report, chart_files, write_markdown
from snake.analysis.ExperimentRuns import read_experiment_runs
from snake.analysis.ReportPage import write_html
from snake.analysis.Showcase import select_showcase_runs


LOCAL_REPORT = ("bot_report", Path("reports"))
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
    output.mkdir(parents=True, exist_ok=True)
    chart_folder = f"{name}_charts"
    markdown_path = output / f"{name}.md"
    html_path = output / f"{name}.html"
    markdown_path.write_text(write_markdown(report, chart_folder), encoding="utf-8")
    html_path.write_text(write_html(report), encoding="utf-8")
    write_charts(report, output / chart_folder)

    print(
        f"{report.title}: {count(report.run_count, 'run')} in "
        f"{count(len(report.groups), 'group')}, {skipped} skipped report files"
        + (f", {left_out} runs left out." if options.showcase else ".")
    )
    print(f"Wrote {markdown_path} and {html_path}")
    return 0


def count(number, noun):
    return f"{number} {noun}" + ("" if number == 1 else "s")


def write_charts(report, folder):
    """Save each group's chart, removing charts of groups that no longer exist."""
    folder.mkdir(exist_ok=True)
    for old_chart in folder.glob("scores_*.svg"):
        old_chart.unlink()
    for name, svg in chart_files(report):
        (folder / name).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
