"""Write a Bot Report's files, and rebuild the local one after an evaluation.

AnalyseBots, the Bot Experiment commands, and the app's Evaluate all write
reports through here, so a new evaluation always shows up next to every bot
that played the same games. Only the git-ignored local report is rebuilt
automatically; the committed Showcase Report changes only on purpose.
"""

from pathlib import Path

from snake.analysis.BotReport import build_bot_report, chart_files, write_markdown
from snake.analysis.ExperimentRuns import read_experiment_runs
from snake.analysis.ReportPage import write_html


LOCAL_REPORT_NAME = "bot_report"
LOCAL_REPORT_FOLDER = Path("reports")


def write_report_files(report, name, output):
    """Write the Markdown, the HTML, and the charts; return the HTML file's path."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    chart_folder = f"{name}_charts"
    (output / f"{name}.md").write_text(write_markdown(report, chart_folder), encoding="utf-8")
    html_path = output / f"{name}.html"
    html_path.write_text(write_html(report), encoding="utf-8")
    write_charts(report, output / chart_folder)
    return html_path


def write_charts(report, folder):
    """Save each group's chart, removing charts of groups that no longer exist."""
    folder.mkdir(exist_ok=True)
    for old_chart in folder.glob("scores_*.svg"):
        old_chart.unlink()
    for name, svg in chart_files(report):
        (folder / name).write_text(svg, encoding="utf-8")


def print_bot_report(report_path):
    """After a terminal command saves a run, rebuild the local report and say where."""
    page = write_local_report(Path(report_path).parent)
    if page is not None:
        print(f"Bot Report: {page}")


def write_local_report(experiments, output=LOCAL_REPORT_FOLDER):
    """Rebuild the local Bot Report from every saved run.

    Returns the HTML file's path, or None when there is no usable run yet.
    """
    runs, skipped = read_experiment_runs(experiments)
    if not runs:
        return None
    return write_report_files(build_bot_report(runs, skipped), LOCAL_REPORT_NAME, output)
