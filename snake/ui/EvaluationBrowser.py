"""Paging for saved evaluation results, separate from watched-game Records."""

from snake.storage.EvaluationReports import DEFAULT_REPORT_DIRECTORY, read_evaluation_reports


class EvaluationBrowser:
    def __init__(self, directory=DEFAULT_REPORT_DIRECTORY, page_size=5):
        self.directory = directory
        self.page_size = page_size
        self.page_index = 0
        self.results = []
        self.skipped = 0

    def load(self):
        self.results, self.skipped = read_evaluation_reports(self.directory)
        self.page_index = 0

    def visible_results(self):
        first = self.page_index * self.page_size
        return self.results[first:first + self.page_size]

    @property
    def page_count(self):
        return max(1, (len(self.results) + self.page_size - 1) // self.page_size)

    def set_page_size(self, page_size):
        first = self.page_index * self.page_size
        self.page_size = page_size
        self.page_index = min(first // page_size, self.page_count - 1)

    def newer(self):
        self.page_index = max(0, self.page_index - 1)

    def older(self):
        self.page_index = min(self.page_count - 1, self.page_index + 1)
