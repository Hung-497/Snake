from statistics import median

from snake.sessions.SessionSettings import SessionSettings
from snake.storage.RecordManager import RecordManager
from snake.ui.PlayerLabels import PLAYER_LABELS


ALL_PLAYERS = "All Players"
ALL_BOARDS = "All boards"
ALL_SPEEDS = "All speeds"


class RecordsBrowser:
    """
    Reads saved game records and prepares them for the Records App View.

    The browser filters by Game Conditions (board size and speed name) and by
    Player, summarises what is left, and hands back one page of records at a
    time, newest first. It never writes anything: the
    CSV file and its format stay entirely RecordManager's responsibility.
    """

    # The newest records the view offers, matching the old menu's limit.
    DISPLAY_LIMIT = 50
    PAGE_SIZE = 10
    # Recent form compares this many latest games with the overall average.
    RECENT_GAMES = 20
    # A trend line covers this many latest games, each point averaging the
    # games in a window of this size up to it.
    TREND_GAMES = 100
    TREND_WINDOW = 10

    def __init__(self, record_manager=None, display_limit=None, page_size=None, settings=None):
        self.record_manager = RecordManager() if record_manager is None else record_manager
        self.display_limit = self.DISPLAY_LIMIT if display_limit is None else display_limit
        self.page_size = self.PAGE_SIZE if page_size is None else page_size
        # The settings know the board sizes and speeds the app offers.
        self.settings = SessionSettings() if settings is None else settings

        self.records = []
        self.selected_filter = ALL_PLAYERS
        # Start with the conditions the user plays under now.
        self.board_filter = self.settings.selected_board_size_name
        self.speed_filter = self.settings.selected_speed_name
        self.page_index = 0

    def load(self):
        """Read the stored records once, so paging does not re-read the file."""
        self.records = self.record_manager.read_game_records()
        self.page_index = 0

    def select_filter(self, selected_filter):
        self.selected_filter = selected_filter
        # A new filter shows a different set of records, so start again at the newest.
        self.page_index = 0

    def select_board(self, board_filter):
        self.board_filter = board_filter
        self.page_index = 0

    def select_speed(self, speed_filter):
        self.speed_filter = speed_filter
        self.page_index = 0

    def board_filter_names(self):
        return [ALL_BOARDS] + self.settings.board_size_names()

    def speed_filter_names(self):
        return [ALL_SPEEDS] + self.settings.speed_names()

    def matches_conditions(self, record):
        """Was this game played under the selected board size and speed name?"""
        try:
            board = (int(record["board_width"]), int(record["board_height"]))
            speed_delay = int(record["speed_delay"])
        except (KeyError, TypeError, ValueError):
            # A record without readable conditions can only appear under "All".
            return self.board_filter == ALL_BOARDS and self.speed_filter == ALL_SPEEDS

        if (self.board_filter != ALL_BOARDS
                and board != self.settings.board_size_options.get(self.board_filter)):
            return False

        if (self.speed_filter != ALL_SPEEDS
                and self.settings.speed_name_for_delay(speed_delay) != self.speed_filter):
            return False

        return True

    def matches_player(self, record):
        if (self.selected_filter == ALL_PLAYERS):
            return True

        return player_group(record["player"]) == self.selected_filter

    def player_statistics(self):
        """
        One row of statistics per Player with games under the Board and Speed
        filters, for the Compare tab. It uses every matching record, and the
        Player filter does not apply: Compare always shows Players side by side.
        """
        return [
            self.statistics_for(player, records)
            for player, records in self.records_by_player().items()
        ]

    def player_trends(self):
        """
        One smoothed score line per Player with games under the Board and
        Speed filters, for the Trends tab: the last 100 games in the order they
        were played, each point averaging up to 10 games ending at it.
        """
        trends = []

        for player, records in self.records_by_player().items():
            scores = [int(record["score"]) for record in records][-self.TREND_GAMES:]
            points = []

            for index in range(len(scores)):
                window = scores[max(0, index - self.TREND_WINDOW + 1):index + 1]
                points.append(sum(window) / len(window))

            trends.append({"player": player, "points": points})

        return trends

    def records_by_player(self):
        """
        The records under the Board and Speed filters, grouped by Player,
        oldest first. Records whose numbers cannot be read are left out, so
        one damaged row never stops the statistics or trends.
        """
        records_by_player = {}

        for record in self.records:
            if (self.matches_conditions(record) and has_readable_numbers(record)):
                records_by_player.setdefault(player_group(record["player"]), []).append(record)

        # Known Players in the order the app lists them, then any others by name.
        known_order = list(PLAYER_LABELS)
        players = sorted(records_by_player, key=lambda player: (
            known_order.index(player) if player in known_order else len(known_order), player))

        return {player: records_by_player[player] for player in players}

    def statistics_for(self, player, records):
        scores = [int(record["score"]) for record in records]
        moves = [int(record["total_moves"]) for record in records]
        game_times = [float(record["game_time"]) for record in records]
        # An empty outcome is unknown, so it is left out of the win rate.
        outcomes = [record.get("outcome") for record in records if record.get("outcome")]

        average_score = sum(scores) / len(scores)
        recent_scores = scores[-self.RECENT_GAMES:]
        recent_average = sum(recent_scores) / len(recent_scores)

        return {
            "player": player,
            "games": len(records),
            "best_score": max(scores),
            "average_score": average_score,
            "median_score": median(scores),
            "win_rate": outcomes.count("won") / len(outcomes) if outcomes else None,
            "known_outcomes": len(outcomes),
            "average_moves": sum(moves) / len(moves),
            "average_game_time": sum(game_times) / len(game_times),
            "recent_average": recent_average,
            "recent_form": compare_form(recent_average, average_score),
        }

    def set_page_size(self, page_size):
        """Keep the first visible record nearby when the window height changes."""
        first_record_index = self.page_index * self.page_size
        self.page_size = page_size
        self.page_index = min(first_record_index // page_size, self.page_count - 1)

    def filtered_records(self):
        """The stored records the filters select, oldest first, as stored."""
        return [
            record for record in self.records
            if self.matches_conditions(record) and self.matches_player(record)
        ]

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
        # The list still shows unreadable records; only the numbers leave them out.
        selected_records = [record for record in self.filtered_records()
                            if has_readable_numbers(record)]

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


def has_readable_numbers(record):
    """Can the score, moves and game time of this record be read as numbers?"""
    try:
        int(record["score"])
        int(record["total_moves"])
        float(record["game_time"])
    except (KeyError, TypeError, ValueError):
        return False

    return True


def player_group(player):
    """The Player a saved name counts as: Q Learning saved names like "q_learning_v2"."""
    if (player.startswith("q_learning")):
        return "q_learning"

    return player


def compare_form(recent_average, overall_average):
    """Above, below or level, judged at the one decimal place the view shows."""
    recent = round(recent_average, 1)
    overall = round(overall_average, 1)

    if (recent > overall):
        return "above"

    if (recent < overall):
        return "below"

    return "level"
