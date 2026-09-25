from snake.storage.RecordManager import RecordManager


ALL_BOTS = "All Bots"


class RecordsBrowser:
    """
    Reads saved game records and prepares them for the Records App View.

    The browser filters by Bot Mode, summarises what is left, and hands back
    one page of records at a time, newest first. It never writes anything: the
    CSV file and its format stay entirely RecordManager's responsibility.
    """

    # The newest records the view offers, matching the old menu's limit.
    DISPLAY_LIMIT = 50
    PAGE_SIZE = 10

    def __init__(self, record_manager=None, display_limit=None, page_size=None):
        self.record_manager = RecordManager() if record_manager is None else record_manager
        self.display_limit = self.DISPLAY_LIMIT if display_limit is None else display_limit
        self.page_size = self.PAGE_SIZE if page_size is None else page_size

        self.records = []
        self.selected_filter = ALL_BOTS
        self.page_index = 0

    def load(self):
        """Read the stored records once, so paging does not re-read the file."""
        self.records = self.record_manager.read_game_records()
        self.page_index = 0

    def select_filter(self, selected_filter):
        self.selected_filter = selected_filter
        # A new filter shows a different set of records, so start again at the newest.
        self.page_index = 0

    def set_page_size(self, page_size):
        """Keep the first visible record nearby when the window height changes."""
        first_record_index = self.page_index * self.page_size
        self.page_size = page_size
        self.page_index = min(first_record_index // page_size, self.page_count - 1)

    def filtered_records(self):
        """The stored records this filter selects, oldest first, as stored."""
        if (self.selected_filter == ALL_BOTS):
            return list(self.records)

        selected_records = []

        for record in self.records:
            bot_name = record["bot_name"]

            # Q Learning has saved records under names like "q_learning_v2".
            if (self.selected_filter == "q_learning" and bot_name.startswith("q_learning")):
                selected_records.append(record)
            elif (bot_name == self.selected_filter):
                selected_records.append(record)

        return selected_records

    def latest_records(self):
        """The newest records within the display limit, newest first."""
        selected_records = self.filtered_records()

        return list(reversed(selected_records[-self.display_limit:]))

    def visible_records(self):
        """The page of records the view is currently showing."""
        latest_records = self.latest_records()
        first = self.page_index * self.page_size

        return latest_records[first:first + self.page_size]

    @property
    def page_count(self):
        record_count = len(self.latest_records())

        if (record_count == 0):
            return 1

        # Round up, so a part-full last page still counts.
        return (record_count + self.page_size - 1) // self.page_size

    @property
    def page_number(self):
        """The page the view is showing, counting from 1 for the newest."""
        return self.page_index + 1

    def show_older_records(self):
        if (self.page_index + 1 < self.page_count):
            self.page_index += 1

    def show_newer_records(self):
        if (self.page_index > 0):
            self.page_index -= 1

    def summary(self):
        """Totals for the selected records, with None where there is nothing to average."""
        selected_records = self.filtered_records()

        if (len(selected_records) == 0):
            return {
                "total_games": 0,
                "best_score": None,
                "average_score": None,
                "average_moves": None,
            }

        scores = [int(record["score"]) for record in selected_records]
        moves = [int(record["total_moves"]) for record in selected_records]

        return {
            "total_games": len(selected_records),
            "best_score": max(scores),
            "average_score": sum(scores) / len(scores),
            "average_moves": sum(moves) / len(moves),
        }
