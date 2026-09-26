import arcade.gui

from snake.sessions.HumanPlayer import HUMAN_PLAY
from snake.ui.RecordsBrowser import ALL_PLAYERS, RecordsBrowser
from snake.ui import Theme
from snake.ui.PlayerLabels import player_label
from snake.ui.Charts import ScoreBarChart, TrendChart
from snake.ui.WindowLayout import (
    CHART_WIDTH,
    TREND_LEGEND_PER_ROW,
    compare_chart_height,
    layout_step,
    record_rows_per_page,
    trend_chart_height,
    trend_legend_rows,
)


# Button label -> the filter value the browser uses.
FILTER_CHOICES = (
    ("All Players", ALL_PLAYERS),
    ("Rule", "rule"),
    ("Q-Learning", "q_learning"),
    ("Hamiltonian", "hamiltonian"),
    ("Search-Based", "search_based"),
    ("Human", HUMAN_PLAY),
)

NOTHING_TO_SHOW = "-"

# Tab label -> the tab it opens. Compare opens first.
TABS = (
    ("Compare", "compare"),
    ("Trends", "trends"),
    ("Games", "games"),
)

# The Compare table's columns: heading and width in pixels. Together they fit
# the 700 px minimum window width.
COMPARE_COLUMNS = (
    ("Player", 120),
    ("Games", 60),
    ("Best", 55),
    ("Average", 65),
    ("Median", 60),
    ("Win rate", 90),
    ("Moves", 60),
    ("Time", 60),
    ("Recent", 80),
)
SWATCH_SIZE = 12

# How recent form is marked next to the recent average.
RECENT_FORM_MARKS = {"above": "\u2191", "below": "\u2193", "level": "="}
RECENT_FORM_COLORS = {"above": Theme.SNAKE_BODY, "below": Theme.WARNING, "level": Theme.TEXT_MUTED}

# Game Outcome saved in a record -> the word shown; old records have none.
OUTCOME_LABELS = {"won": "Won", "died": "Died"}
UNKNOWN_OUTCOME = "Outcome unknown"


class RecordsView(arcade.gui.UIView):
    """
    The Records App View, Records Analytics: a Compare tab that puts every
    Player side by side, a Trends tab with each Player's recent scores, and a
    Games tab with the recent games list, all for the games played under the
    chosen Game Conditions (board size and speed).

    Arcade has no scrolling widget, so the records are shown one page at a
    time instead of one long scrolling list. Reading, filtering and paging all
    belong to RecordsBrowser; this view only lays the result out.
    """

    def __init__(self, shell, settings=None, record_manager=None):
        super().__init__()
        self.shell = shell
        self.background_color = Theme.SURFACE

        self.current_layout_step = layout_step(self.window.width)
        self.current_page_size = record_rows_per_page(self.window.height)
        # How many Player rows the Compare table has; the bar chart's height
        # depends on it. Kept up to date whenever the screen is rebuilt.
        self.compare_row_count = 0
        # Likewise for the Trends legend rows and the trend chart's height.
        self.trend_legend_row_count = 1
        self.browser = RecordsBrowser(record_manager=record_manager,
                                      page_size=self.current_page_size,
                                      settings=settings)
        self.browser.load()
        self.current_chart_heights = self.chart_heights(self.window.height)
        # A dropdown choice rebuilds the screen on the next frame, not inside
        # the dropdown's own change event.
        self.needs_refresh = False
        self.selected_tab = "compare"

        self.refresh()

    def refresh(self):
        """Rebuild the screen after the filter or the page changed."""
        self.ui.clear()
        self.sizes = Theme.type_sizes(self.window.width)

        records_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_UNIT)
        records_box.add(Theme.create_label("Game Records", font_size=self.sizes.display,
                                           semibold=True))
        records_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))
        records_box.add(self.create_conditions_row())
        records_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))
        records_box.add(self.create_tab_row())
        records_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))

        if (self.selected_tab == "compare"):
            records_box.add(self.create_compare_table())
        elif (self.selected_tab == "trends"):
            records_box.add(self.create_trends())
        else:
            records_box.add(self.create_filter_row())
            records_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))
            records_box.add(self.create_summary_row())
            records_box.add(Theme.create_spacer(Theme.SPACE_INNER))
            records_box.add(self.create_record_rows())
            records_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))
            records_box.add(self.create_paging_row())

        records_box.add(Theme.create_spacer(Theme.SPACE_INNER))
        records_box.add(
            Theme.create_secondary_button(
                "Back",
                lambda: self.shell.show_view("menu"),
                button_width=Theme.BACK_BUTTON_WIDTH,
                font_size=self.sizes.heading,
            )
        )

        Theme.center_focusable(self.ui, records_box)

    def create_conditions_row(self):
        """The Board and Speed dropdowns: only games under these conditions count."""
        conditions_row = arcade.gui.UIBoxLayout(vertical=False,
                                                space_between=Theme.SPACE_TIGHT)
        conditions_row.add(Theme.create_label("Board", font_size=self.sizes.body,
                                              color=Theme.TEXT_MUTED))
        conditions_row.add(self.create_condition_dropdown(
            self.browser.board_filter, self.browser.board_filter_names(),
            Theme.BOARD_DROPDOWN_WIDTH, self.browser.select_board,
        ))
        conditions_row.add(Theme.create_label("   Speed", font_size=self.sizes.body,
                                              color=Theme.TEXT_MUTED))
        conditions_row.add(self.create_condition_dropdown(
            self.browser.speed_filter, self.browser.speed_filter_names(),
            Theme.SPEED_DROPDOWN_WIDTH, self.browser.select_speed,
        ))

        return conditions_row

    def create_condition_dropdown(self, selected_name, option_names, width, select_option):
        dropdown = arcade.gui.UIDropdown(
            default=selected_name,
            options=option_names,
            width=width,
            height=Theme.OPTION_HEIGHT,
            primary_style=Theme.create_dropdown_style(font_size=self.sizes.body),
            dropdown_style=Theme.create_dropdown_style(font_size=self.sizes.body),
            active_style=Theme.create_dropdown_style(
                Theme.PRIMARY, Theme.PRIMARY_HOVER, Theme.PRIMARY_PRESS,
                font_size=self.sizes.body,
            ),
        )

        def change(event):
            select_option(event.new_value)
            self.needs_refresh = True

        dropdown.on_change = change
        return dropdown

    def create_tab_row(self):
        tab_row = arcade.gui.UIBoxLayout(vertical=False, space_between=Theme.SPACE_TIGHT)

        for tab_text, tab in TABS:
            create_button = (Theme.create_primary_button if self.selected_tab == tab
                             else Theme.create_secondary_button)
            tab_row.add(
                create_button(
                    tab_text,
                    self.change_tab(tab),
                    button_width=Theme.filter_button_width(self.window.width),
                    button_height=Theme.FILTER_BUTTON_HEIGHT,
                    font_size=self.sizes.body,
                )
            )

        return tab_row

    def change_tab(self, tab):
        def change():
            self.selected_tab = tab
            self.refresh()

        return change

    def create_compare_table(self):
        """One row per Player with games under the chosen Game Conditions."""
        table = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_TIGHT)
        rows = self.browser.player_statistics()
        self.compare_row_count = len(rows)
        self.current_chart_heights = self.chart_heights(self.window.height)

        if (len(rows) == 0):
            message = ("No games recorded yet." if len(self.browser.records) == 0
                       else "No games match these filters.")
            table.add(Theme.create_label(message, font_size=self.sizes.body,
                                         color=Theme.TEXT_MUTED))
            return table

        heading_row = arcade.gui.UIBoxLayout(vertical=False)
        for heading, width in COMPARE_COLUMNS:
            heading_row.add(self.create_cell(heading, width, color=Theme.TEXT_MUTED))
        table.add(heading_row)

        for row in rows:
            table.add(self.create_player_row(row))

        table.add(Theme.create_spacer(Theme.SPACE_CONTROL))
        chart_height = compare_chart_height(self.window.height, len(rows))

        if (chart_height is None):
            # The table already has every number; the chart only returns when there is room.
            table.add(Theme.create_label("Make the window taller to see the bar chart.",
                                         font_size=self.sizes.caption, color=Theme.TEXT_MUTED))
        else:
            table.add(ScoreBarChart(rows, CHART_WIDTH, chart_height, self.sizes.caption))
            table.add(Theme.create_label(
                "Bars show the average score; the white line is the best.",
                font_size=self.sizes.caption, color=Theme.TEXT_MUTED))

        return table

    def create_trends(self):
        """One smoothed score line per Player, with a legend of Player colours."""
        trends_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_TIGHT)
        trends = self.browser.player_trends()
        self.trend_legend_row_count = trend_legend_rows(len(trends))
        self.current_chart_heights = self.chart_heights(self.window.height)

        if (len(trends) == 0):
            message = ("No games recorded yet." if len(self.browser.records) == 0
                       else "No games match these filters.")
            trends_box.add(Theme.create_label(message, font_size=self.sizes.body,
                                              color=Theme.TEXT_MUTED))
            return trends_box

        trends_box.add(TrendChart(
            trends, CHART_WIDTH,
            trend_chart_height(self.window.height, self.trend_legend_row_count),
            self.sizes.caption,
        ))

        # The legend wraps into rows, so many Players never run off the window's sides.
        for first in range(0, len(trends), TREND_LEGEND_PER_ROW):
            legend_row = arcade.gui.UIBoxLayout(vertical=False, space_between=Theme.SPACE_WIDE)

            for trend in trends[first:first + TREND_LEGEND_PER_ROW]:
                entry = arcade.gui.UIBoxLayout(vertical=False, space_between=Theme.SPACE_UNIT)
                entry.add(arcade.gui.UISpace(width=SWATCH_SIZE, height=SWATCH_SIZE,
                                             color=Theme.player_color(trend["player"])))
                entry.add(Theme.create_label(player_label(trend["player"]),
                                             font_size=self.sizes.caption))
                legend_row.add(entry)

            trends_box.add(legend_row)
        trends_box.add(Theme.create_label("Each point averages up to 10 games.",
                                          font_size=self.sizes.caption, color=Theme.TEXT_MUTED))

        return trends_box

    def create_player_row(self, row):
        player = row["player"]
        values = (
            str(row["games"]),
            self.format_summary_value(row["best_score"]),
            self.format_summary_value(row["average_score"]),
            f"{row['median_score']:.1f}",
            self.format_win_rate(row),
            # Whole moves keep this column narrow; long games reach five digits.
            f"{row['average_moves']:.0f}",
            f"{row['average_game_time']:.1f}s",
        )
        player_row = arcade.gui.UIBoxLayout(vertical=False)

        # The Player cell: its colour swatch, then its name.
        player_width = COMPARE_COLUMNS[0][1]
        player_cell = arcade.gui.UIBoxLayout(vertical=False, space_between=Theme.SPACE_UNIT)
        player_cell.add(arcade.gui.UISpace(width=SWATCH_SIZE, height=SWATCH_SIZE,
                                           color=Theme.player_color(player)))
        player_cell.add(self.create_cell(player_label(player),
                                         player_width - SWATCH_SIZE - Theme.SPACE_UNIT,
                                         align="left", semibold=True))
        player_row.add(player_cell)

        for value, (_, width) in zip(values, COMPARE_COLUMNS[1:-1]):
            player_row.add(self.create_cell(value, width))

        recent_form = row["recent_form"]
        player_row.add(self.create_cell(
            f"{RECENT_FORM_MARKS[recent_form]} {row['recent_average']:.1f}",
            COMPARE_COLUMNS[-1][1],
            color=RECENT_FORM_COLORS[recent_form],
        ))

        return player_row

    def create_cell(self, text, width, color=Theme.TEXT, align="center", semibold=False):
        cell = arcade.gui.UILabel(
            text=text,
            width=width,
            align=align,
            font_name=Theme.FONT_SEMIBOLD if semibold else Theme.FONT_REGULAR,
            font_size=self.sizes.caption,
            text_color=color,
        )
        # A box layout shrinks a label to its text unless told otherwise, and
        # the table's columns only line up if every cell keeps its width.
        cell.size_hint_min = (width, cell.size_hint_min[1])
        return cell

    def format_win_rate(self, row):
        """The win rate and how many games with a known outcome it is based on."""
        if (row["win_rate"] is None):
            return NOTHING_TO_SHOW

        return f"{row['win_rate'] * 100:.0f}% of {row['known_outcomes']}"

    def create_filter_row(self):
        filter_row = arcade.gui.UIBoxLayout(vertical=False,
                                            space_between=Theme.SPACE_TIGHT)

        for button_text, filter_value in FILTER_CHOICES:
            is_selected = self.browser.selected_filter == filter_value
            create_button = (Theme.create_primary_button if is_selected
                             else Theme.create_secondary_button)
            filter_row.add(
                create_button(
                    button_text,
                    self.change_filter(filter_value),
                    button_width=Theme.filter_button_width(self.window.width),
                    button_height=Theme.FILTER_BUTTON_HEIGHT,
                    font_size=self.sizes.caption,
                )
            )

        return filter_row

    def change_filter(self, filter_value):
        def change():
            self.browser.select_filter(filter_value)
            self.refresh()

        return change

    def create_summary_row(self):
        summary = self.browser.summary()
        summary_row = arcade.gui.UIBoxLayout(vertical=False,
                                             space_between=Theme.SPACE_WIDE)

        for title, value in (
            ("Games", summary["total_games"]),
            ("Best", summary["best_score"]),
            ("Average Score", summary["average_score"]),
            ("Average Moves", summary["average_moves"]),
        ):
            summary_row.add(self.create_summary_box(title, value))

        return summary_row

    def create_summary_box(self, title, value):
        summary_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_UNIT)
        summary_box.add(Theme.create_label(title, font_size=self.sizes.caption,
                                           color=Theme.TEXT_MUTED, semibold=True))
        summary_box.add(Theme.create_label(self.format_summary_value(value),
                                           font_size=self.sizes.heading, semibold=True))

        return summary_box

    def format_summary_value(self, value):
        """A missing value has nothing to average, so it is shown as a dash."""
        if (value is None):
            return NOTHING_TO_SHOW

        if (isinstance(value, float)):
            return f"{value:.1f}"

        return str(value)

    def create_record_rows(self):
        rows = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_TIGHT)
        visible_records = self.browser.visible_records()

        if (len(visible_records) == 0):
            message = ("No games recorded yet." if len(self.browser.records) == 0
                       else "No games match these filters.")
            rows.add(Theme.create_label(message,
                                        font_size=self.sizes.body,
                                        color=Theme.TEXT_MUTED))
            return rows

        for record in visible_records:
            rows.add(self.create_record_row(record))

        return rows

    def create_record_row(self, record):
        board_width = record.get("board_width") or "?"
        board_height = record.get("board_height") or "?"
        tile_size = record.get("tile_size") or "?"
        speed_delay = record.get("speed_delay") or "?"
        time_detail = (f" | Time: {record['game_time']}s"
                       if self.current_layout_step == "regular" else "")

        row = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_UNIT)
        row.add(
            Theme.create_label(
                f"{record['date_time']} | "
                f"{player_label(record['player'])} | "
                f"Score: {record['score']} | "
                f"Moves: {record['total_moves']} | "
                f"{OUTCOME_LABELS.get(record.get('outcome'), UNKNOWN_OUTCOME)}" + time_detail,
                font_size=self.sizes.caption,
                semibold=True,
            )
        )
        row.add(
            Theme.create_label(
                f"Board: {board_width} x {board_height} | "
                f"Tile: {tile_size}px | "
                f"Speed Delay: {speed_delay}",
                font_size=self.sizes.caption,
                color=Theme.TEXT_MUTED,
            )
        )

        return row

    def create_paging_row(self):
        paging_row = arcade.gui.UIBoxLayout(vertical=False,
                                            space_between=Theme.SPACE_CONTROL)
        paging_row.add(
            Theme.create_secondary_button(
                "Newer",
                self.show_page(self.browser.show_newer_records),
                button_width=Theme.PAGE_BUTTON_WIDTH,
                button_height=Theme.PAGE_BUTTON_HEIGHT,
                font_size=self.sizes.body,
            )
        )
        paging_row.add(
            Theme.create_label(
                f"Page {self.browser.page_number} of {self.browser.page_count}   "
                f"(latest {len(self.browser.latest_records())} "
                f"of {len(self.browser.filtered_records())} records)",
                font_size=self.sizes.caption,
                color=Theme.TEXT_MUTED,
            )
        )
        paging_row.add(
            Theme.create_secondary_button(
                "Older",
                self.show_page(self.browser.show_older_records),
                button_width=Theme.PAGE_BUTTON_WIDTH,
                button_height=Theme.PAGE_BUTTON_HEIGHT,
                font_size=self.sizes.body,
            )
        )

        return paging_row

    def show_page(self, change_page):
        def show():
            change_page()
            self.refresh()

        return show

    def chart_heights(self, window_height):
        return (compare_chart_height(window_height, self.compare_row_count),
                trend_chart_height(window_height, self.trend_legend_row_count))

    def on_resize(self, width, height):
        new_step = layout_step(width)
        new_page_size = record_rows_per_page(height)
        new_chart_heights = self.chart_heights(height)
        if (new_step != self.current_layout_step or new_page_size != self.current_page_size
                or new_chart_heights != self.current_chart_heights):
            self.current_layout_step = new_step
            self.current_page_size = new_page_size
            self.current_chart_heights = new_chart_heights
            self.browser.set_page_size(new_page_size)
            self.refresh()

    def on_update(self, delta_time):
        if (self.needs_refresh):
            self.needs_refresh = False
            self.refresh()

        self.ui.on_update(delta_time)
