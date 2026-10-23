"""Write a Bot Report's files, and rebuild the local one after an evaluation.

AnalyseBots, the Bot Experiment commands, and the app's Evaluate all write
reports through here, so a new evaluation always shows up next to every bot
that played the same games. The local report also gets a run page for every
saved run, in runs/. Only the git-ignored local report is rebuilt
automatically; the committed Showcase Report changes only on purpose and has
no run pages.
"""

from pathlib import Path

from snake.analysis.BotReport import (
    RUN_PAGE_FOLDER, build_bot_report, chart_files, write_markdown,
)
from snake.analysis.ExperimentRuns import read_experiment_runs
from snake.analysis.ReportPage import write_html
from snake.analysis.RunPage import write_run_html
from snake.analysis.RunReport import build_run_reports


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


def run_page_path(report_path, output=LOCAL_REPORT_FOLDER):
    """Where the run page of a saved report is written: named after its file."""
    return Path(output) / RUN_PAGE_FOLDER / f"{Path(report_path).stem}.html"


def print_bot_report(report_path):
    """After a terminal command saves a run, rebuild the local report and say where.

    The run page shows the run just saved; the Bot Report shows every run.
    """
    page = write_local_report(Path(report_path).parent)
    if page is not None:
        print(f"Bot Report: {page}")
        print(f"Run report: {run_page_path(report_path)}")


def write_local_report(experiments, output=LOCAL_REPORT_FOLDER):
    """Rebuild the local Bot Report from every saved run.

    Returns the HTML file's path, or None when there is no usable run yet.
    """
    runs, skipped = read_experiment_runs(experiments)
    if not runs:
        return None
    return write_local_files(runs, build_bot_report(runs, skipped), output)


def write_local_files(runs, report, output):
    """Write the local Bot Report and a run page for every run; return the report's HTML path."""
    page = write_report_files(report, LOCAL_REPORT_NAME, output)
    write_run_pages(runs, report, Path(output) / RUN_PAGE_FOLDER)
    return page


def write_run_pages(runs, report, folder):
    """Write a page for every saved run, removing pages of runs no longer saved."""
    folder.mkdir(exist_ok=True)
    for old_page in folder.glob("*.html"):
        old_page.unlink()
    for run_report in build_run_reports(runs, report):
        page = write_run_html(run_report)
        (folder / f"{run_report.source}.html").write_text(page, encoding="utf-8")
