import arcade.gui

from snake.ui.RecordsBrowser import ALL_BOTS, RecordsBrowser
from snake.ui import Theme
from snake.ui.WindowLayout import layout_step, record_rows_per_page


# Button label -> the filter value the browser uses.
FILTER_CHOICES = (
    ("All", ALL_BOTS),
    ("Rule", "rule"),
    ("Q-Learning", "q_learning"),
    ("Hamiltonian", "hamiltonian"),
)

NOTHING_TO_SHOW = "-"


class RecordsView(arcade.gui.UIView):
    """
    The Records App View: summary statistics and recent games.

    Arcade has no scrolling widget, so the records are shown one page at a
    time instead of one long scrolling list. Reading, filtering and paging all
    belong to RecordsBrowser; this view only lays the result out.
    """

    def __init__(self, shell, record_manager=None):
        super().__init__()
        self.shell = shell
        self.background_color = Theme.SURFACE

        self.current_layout_step = layout_step(self.window.width)
        self.current_page_size = record_rows_per_page(self.window.height)
        self.browser = RecordsBrowser(record_manager=record_manager,
                                      page_size=self.current_page_size)
        self.browser.load()

        self.refresh()

    def refresh(self):
        """Rebuild the screen after the filter or the page changed."""
        self.ui.clear()
        self.sizes = Theme.type_sizes(self.window.width)

        records_box = arcade.gui.UIBoxLayout(space_between=Theme.SPACE_UNIT)
        records_box.add(Theme.create_label("Game Records", font_size=self.sizes.display,
                                           semibold=True))
        records_box.add(Theme.create_spacer(Theme.SPACE_CONTROL))
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
                    button_width=Theme.FILTER_BUTTON_WIDTH,
                    button_height=Theme.FILTER_BUTTON_HEIGHT,
                    font_size=self.sizes.body,
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
            rows.add(Theme.create_label("No games recorded yet.",
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
                f"{record['bot_name']} | "
                f"Score: {record['score']} | "
                f"Moves: {record['total_moves']}" + time_detail,
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

    def on_resize(self, width, height):
        new_step = layout_step(width)
        new_page_size = record_rows_per_page(height)
        if new_step != self.current_layout_step or new_page_size != self.current_page_size:
            self.current_layout_step = new_step
            self.current_page_size = new_page_size
            self.browser.set_page_size(new_page_size)
            self.refresh()

    def on_update(self, delta_time):
        self.ui.on_update(delta_time)
