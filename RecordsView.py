import arcade.gui

from RecordsBrowser import ALL_BOTS, RecordsBrowser
from ViewStyle import (
    BACKGROUND_COLOR,
    BUTTON_COLOR,
    SECONDARY_BUTTON_COLOR,
    center_in_view,
    create_button,
    create_muted_label,
    create_text_label,
    create_title_label,
)


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
        self.background_color = BACKGROUND_COLOR

        self.browser = RecordsBrowser(record_manager=record_manager)
        self.browser.load()

        self.refresh()

    def refresh(self):
        """Rebuild the screen after the filter or the page changed."""
        self.ui.clear()

        records_box = arcade.gui.UIBoxLayout(space_between=6)
        records_box.add(create_title_label("Game Records", font_size=40))
        records_box.add(arcade.gui.UISpace(height=12, color=BACKGROUND_COLOR))
        records_box.add(self.create_filter_row())
        records_box.add(arcade.gui.UISpace(height=10, color=BACKGROUND_COLOR))
        records_box.add(self.create_summary_row())
        records_box.add(arcade.gui.UISpace(height=14, color=BACKGROUND_COLOR))
        records_box.add(self.create_record_rows())
        records_box.add(arcade.gui.UISpace(height=10, color=BACKGROUND_COLOR))
        records_box.add(self.create_paging_row())
        records_box.add(arcade.gui.UISpace(height=14, color=BACKGROUND_COLOR))
        records_box.add(
            create_button(
                "Back",
                lambda: self.shell.show_view("menu"),
                button_color=SECONDARY_BUTTON_COLOR,
                button_width=170,
            )
        )

        center_in_view(self.ui, records_box)

    def create_filter_row(self):
        filter_row = arcade.gui.UIBoxLayout(vertical=False, space_between=8)

        for button_text, filter_value in FILTER_CHOICES:
            is_selected = self.browser.selected_filter == filter_value
            filter_row.add(
                create_button(
                    button_text,
                    self.change_filter(filter_value),
                    button_color=BUTTON_COLOR if is_selected else SECONDARY_BUTTON_COLOR,
                    button_width=150,
                    button_height=38,
                    font_size=15,
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
        summary_row = arcade.gui.UIBoxLayout(vertical=False, space_between=30)

        for title, value in (
            ("Games", summary["total_games"]),
            ("Best", summary["best_score"]),
            ("Average Score", summary["average_score"]),
            ("Average Moves", summary["average_moves"]),
        ):
            summary_row.add(self.create_summary_box(title, value))

        return summary_row

    def create_summary_box(self, title, value):
        summary_box = arcade.gui.UIBoxLayout(space_between=2)
        summary_box.add(create_muted_label(title, font_size=13, bold=True))
        summary_box.add(create_text_label(self.format_summary_value(value), font_size=20, bold=True))

        return summary_box

    def format_summary_value(self, value):
        """A missing value has nothing to average, so it is shown as a dash."""
        if (value is None):
            return NOTHING_TO_SHOW

        if (isinstance(value, float)):
            return f"{value:.1f}"

        return str(value)

    def create_record_rows(self):
        rows = arcade.gui.UIBoxLayout(space_between=7)
        visible_records = self.browser.visible_records()

        if (len(visible_records) == 0):
            rows.add(create_muted_label("No games recorded yet.", font_size=16))
            return rows

        for record in visible_records:
            rows.add(self.create_record_row(record))

        return rows

    def create_record_row(self, record):
        board_width = record.get("board_width") or "?"
        board_height = record.get("board_height") or "?"
        tile_size = record.get("tile_size") or "?"
        speed_delay = record.get("speed_delay") or "?"

        row = arcade.gui.UIBoxLayout(space_between=1)
        row.add(
            create_text_label(
                f"{record['date_time']} | "
                f"{record['bot_name']} | "
                f"Score: {record['score']} | "
                f"Moves: {record['total_moves']} | "
                f"Time: {record['game_time']}s",
                font_size=13,
                bold=True,
            )
        )
        row.add(
            create_muted_label(
                f"Board: {board_width} x {board_height} | "
                f"Tile: {tile_size}px | "
                f"Speed Delay: {speed_delay}",
                font_size=12,
            )
        )

        return row

    def create_paging_row(self):
        paging_row = arcade.gui.UIBoxLayout(vertical=False, space_between=12)
        paging_row.add(
            create_button(
                "Newer",
                self.show_page(self.browser.show_newer_records),
                button_color=SECONDARY_BUTTON_COLOR,
                button_width=120,
                button_height=34,
                font_size=14,
            )
        )
        paging_row.add(
            create_muted_label(
                f"Page {self.browser.page_number} of {self.browser.page_count}   "
                f"(latest {len(self.browser.latest_records())} "
                f"of {len(self.browser.filtered_records())} records)",
                font_size=13,
            )
        )
        paging_row.add(
            create_button(
                "Older",
                self.show_page(self.browser.show_older_records),
                button_color=SECONDARY_BUTTON_COLOR,
                button_width=120,
                button_height=34,
                font_size=14,
            )
        )

        return paging_row

    def show_page(self, change_page):
        def show():
            change_page()
            self.refresh()

        return show
