import customtkinter as ctk
from Food import Food
from Snake import Snake
from Window import Window
from Game import Game
from Movement import Movement
from RecordManager import RecordManager
from ReplayManager import ReplayManager
from ReplayPlayer import ReplayPlayer

class MenuApp:
    def __init__(self, width, height, tile_size):
        ctk.set_appearance_mode("dark")  # Set the appearance mode to "dark"
        ctk.set_default_color_theme("dark-blue")  # Set the color theme to "dark-blue"

        self.width = width
        self.height = height
        self.tile_size = tile_size

        self.selected_bot_mode = None
        self.current_frame = None
        self.record_manager = RecordManager()
        self.replay_manager = ReplayManager()
        self.selected_log_filter = "All Bots"

        self.background_color = "#071A2D"
        self.button_color = "#2F80ED"
        self.button_hover_color = "#56CCF2"
        self.secondary_button_color = "#334155"
        self.warning_text_color = "#FCA5A5"
        self.option_color = "#0E2A47"
        self.option_button_color = "#1D4ED8"
        self.option_dropdown_color = "#082033"
        self.text_color = "#F2F7FF"
        self.muted_text_color = "#A8B3C7"

        self.WINDOW_WIDTH = self.width * self.tile_size
        self.WINDOW_HEIGHT = self.height * self.tile_size

        # game window 
        self.window = ctk.CTk()
        self.window.title('Snake Game 🐍')
        self.window.resizable(False, False)
        self.window.configure(fg_color=self.background_color)
        self.window.protocol("WM_DELETE_WINDOW", self.close_menu)
        
        # Set up error handler to suppress harmless CustomTkinter animation errors
        self.window.tk.call('proc', 'bgerror', 'err', 'return')

        self.name_label = ctk.CTkLabel(
            self.window,
            text="Created by Nhism",
            font=("Arial", 14),
            text_color=self.muted_text_color
        )
        self.name_label.place(relx=0.98, rely=0.99, anchor="se")

        self.board_size_options = {
            "Small 16 x 16": (16, 16),
            "Medium 24 x 25": (24, 25),
            "Large 30 x 30": (30, 30),
            "Square 25 x 25": (25, 25)
        }
        self.selected_board_size_name = "Medium 24 x 25"

        self.tile_size_options = {
            "Small tiles 20 px": 20,
            "Medium tiles 25 px": 25,
            "Large tiles 30 px": 30
        }
        self.selected_tile_size_name = "Medium tiles 25 px"

        self.speed_options = {
            "Slow": 10,
            "Normal": 5,
            "Fast": 1
        }
        self.selected_speed_name = "Fast"

    def center_window(self):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        window_x = int((screen_width / 2) - (self.WINDOW_WIDTH / 2))
        window_y = int((screen_height / 2) - (self.WINDOW_HEIGHT / 2))

        self.window.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{window_x}+{window_y}"
        )

    def draw_menu(self):
        self.clear_screen()

        self.current_frame = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )
        self.current_frame.place(relx=0.5, rely=0.45, anchor="center")

        self.title_menu_label = ctk.CTkLabel(
            self.current_frame,
            text="Snake Game 🐍",
            font=("Arial", 52, "bold"),
            text_color=self.text_color
        )
        self.title_menu_label.pack(pady=(0, 8))

        self.subtitle_menu_label = ctk.CTkLabel(
            self.current_frame,
            text="Choose a bot, adjust settings, and compare results",
            font=("Arial", 15),
            text_color=self.muted_text_color
        )
        self.subtitle_menu_label.pack(pady=(0, 34))

        self.start_button = self.create_menu_button("Play", self.open_play)
        self.settings_button = self.create_menu_button("Settings", self.open_settings)
        self.replay_button = self.create_menu_button("Replay", self.open_replay)
        self.logs_button = self.create_menu_button("Logs", self.open_logs)

    def create_menu_button(self, button_text, command, button_color=None, button_width=230):
        if button_color is None:
            button_color = self.button_color

        button = ctk.CTkButton(
            self.current_frame,
            text=button_text,
            font=("Arial", 26, "bold"),
            width=button_width,
            height=48,
            corner_radius=12,
            fg_color=button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color,
            command=command
        )
        button.pack(pady=9)

        return button

    def start(self):
        self.center_window()
        self.draw_menu()
        self.window.mainloop()

        board_width, board_height = self.board_size_options[self.selected_board_size_name]
        tile_size = self.tile_size_options[self.selected_tile_size_name]
        speed_delay = self.speed_options[self.selected_speed_name]

        self.window.destroy()

        return self.selected_bot_mode, board_width, board_height, tile_size, speed_delay

    def open_play(self):
        self.clear_screen()

        self.current_frame = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )
        self.current_frame.place(relx=0.5, rely=0.45, anchor="center")

        self.title_play_label = ctk.CTkLabel(
            self.current_frame,
            text="Choose Bot Mode:",
            font=("Arial", 44, "bold"),
            text_color=self.text_color
        )
        self.title_play_label.pack(pady=(0, 8))

        self.subtitle_play_label = ctk.CTkLabel(
            self.current_frame,
            text="Current settings are applied when the game starts",
            font=("Arial", 15),
            text_color=self.muted_text_color
        )
        self.subtitle_play_label.pack(pady=(0, 28))

        self.RuleBased_Bot_button = self.create_menu_button(
            "Rule Based Bot",
            lambda: self.start_game_with_bot("rule"),
            button_width=280
        )

        self.QLearning_Bot_button = self.create_menu_button(
            "Q Learning Bot",
            lambda: self.start_game_with_bot("q_learning"),
            button_width=280
        )

        self.Hamiltonian_Bot_button = self.create_menu_button(
            "Hamiltonian Bot",
            lambda: self.start_game_with_bot("hamiltonian"),
            button_width=280
        )

        self.error_label = ctk.CTkLabel(
            self.current_frame,
            text="",
            font=("Arial", 14),
            text_color=self.warning_text_color
        )
        self.error_label.pack(pady=(8, 0))

        self.Back_button = self.create_menu_button(
            "Back",
            self.draw_menu,
            button_color=self.secondary_button_color,
            button_width=170
        )

    def open_settings(self):
        self.clear_screen()

        self.current_frame = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )
        self.current_frame.place(relx=0.5, rely=0.45, anchor="center")

        self.title_settings_label = ctk.CTkLabel(
            self.current_frame,
            text="Settings",
            font=("Arial", 46),
            text_color=self.text_color
        )
        self.title_settings_label.pack(pady=(0, 26))

        self.speed_option_menu = self.create_option_box(
            "Game Speed",
            list(self.speed_options.keys()),
            self.selected_speed_name,
            self.change_speed
        )

        self.board_size_option_menu = self.create_option_box(
            "Board Size",
            list(self.board_size_options.keys()),
            self.selected_board_size_name,
            self.change_board_size
        )

        self.tile_size_option_menu = self.create_option_box(
            "Tile Size",
            list(self.tile_size_options.keys()),
            self.selected_tile_size_name,
            self.change_tile_size
        )
        
        self.Back_button = self.create_menu_button(
            "Back",
            self.draw_menu,
            button_color=self.secondary_button_color,
            button_width=170
        )

    def open_replay(self):
        self.clear_screen()

        self.current_frame = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )
        self.current_frame.place(relx=0.5, rely=0.45, anchor="center")

        title_label = ctk.CTkLabel(
            self.current_frame,
            text="Choose Replay:",
            font=("Arial", 44, "bold"),
            text_color=self.text_color
        )
        title_label.pack(pady=(0, 8))

        subtitle_label = ctk.CTkLabel(
            self.current_frame,
            text="Load the saved best replay for each bot",
            font=("Arial", 15),
            text_color=self.muted_text_color
        )
        subtitle_label.pack(pady=(0, 28))

        self.create_menu_button(
            "Rule Based Replay",
            lambda: self.start_replay_with_bot("rule"),
            button_width=300
        )

        self.create_menu_button(
            "Q Learning Replay",
            lambda: self.start_replay_with_bot("q_learning"),
            button_width=300
        )

        self.create_menu_button(
            "Hamiltonian Replay",
            lambda: self.start_replay_with_bot("hamiltonian"),
            button_width=300
        )

        self.replay_status_label = ctk.CTkLabel(
            self.current_frame,
            text="",
            font=("Arial", 14),
            text_color=self.muted_text_color
        )
        self.replay_status_label.pack(pady=(8, 0))

        self.Back_button = self.create_menu_button(
            "Back",
            self.draw_menu,
            button_color=self.secondary_button_color,
            button_width=170
        )

    def create_option_box(self, label_text, option_values, selected_value, command):
        label = ctk.CTkLabel(
            self.current_frame,
            text=label_text,
            font=("Arial", 16, "bold"),
            text_color=self.muted_text_color
        )
        label.pack(anchor="w", padx=8, pady=(8, 4))

        option_menu = ctk.CTkOptionMenu(
            self.current_frame,
            values=option_values,
            command=command,
            width=280,
            height=42,
            corner_radius=10,
            fg_color=self.option_color,
            button_color=self.option_button_color,
            button_hover_color=self.button_hover_color,
            dropdown_fg_color=self.option_dropdown_color,
            dropdown_hover_color=self.option_button_color,
            dropdown_text_color=self.text_color,
            text_color=self.text_color,
            font=("Arial", 16),
            dropdown_font=("Arial", 15)
        )
        option_menu.set(selected_value)
        option_menu.pack(pady=(0, 8))

        return option_menu

    def open_logs(self):
        self.clear_screen()

        self.current_frame = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )
        self.current_frame.place(relx=0.5, rely=0.5, anchor="center")

        title_label = ctk.CTkLabel(
            self.current_frame,
            text="Game Records",
            font=("Arial", 42, "bold"),
            text_color=self.text_color
        )
        title_label.pack(pady=(0, 20))

        records = self.record_manager.read_game_records()
        filtered_records = self.get_filtered_records(records)
        
        filter_frame = ctk.CTkFrame(
            self.current_frame,
            fg_color="transparent"
        )
        filter_frame.pack(pady=(0, 14))

        self.create_log_filter_buttons(filter_frame)

        total_games, best_score, average_score, best_moves = self.get_log_stats(filtered_records)

        stats_frame = ctk.CTkFrame(
            self.current_frame,
            fg_color="transparent"
        )
        stats_frame.pack(pady=(0, 12))

        self.create_stat_label(stats_frame, "Games", total_games)
        self.create_stat_label(stats_frame, "Best", best_score)
        self.create_stat_label(stats_frame, "Average", f"{average_score:.1f}")
        self.create_stat_label(stats_frame, "Best Moves", best_moves)

        self.create_records_section(filtered_records)

        self.Back_button = self.create_menu_button(
            "Back",
            self.draw_menu,
            button_color=self.secondary_button_color,
            button_width=170
        )

    def get_filtered_records(self, records):
        if (self.selected_log_filter == "All Bots"):
            return records

        filtered_records = []

        for record in records:
            if (
                self.selected_log_filter == "q_learning" and
                record["bot_name"].startswith("q_learning")
            ):
                filtered_records.append(record)
            elif (record["bot_name"] == self.selected_log_filter):
                filtered_records.append(record)

        return filtered_records

    def create_log_filter_buttons(self, parent):
        self.create_log_filter_button(parent, "All", "All Bots")
        self.create_log_filter_button(parent, "Rule", "rule")
        self.create_log_filter_button(parent, "Q-Learning", "q_learning")
        self.create_log_filter_button(parent, "Hamiltonian", "hamiltonian")

    def get_log_stats(self, records):
        total_games = len(records)

        if (total_games == 0):
            return 0, "-", 0, "-"

        scores = []
        moves = []

        for record in records:
            scores.append(int(record["score"]))
            moves.append(int(record["total_moves"]))

        best_score = max(scores)
        average_score = sum(scores) / len(scores)
        best_moves = min(moves)

        return total_games, best_score, average_score, best_moves

    def create_records_section(self, records):
        records_frame = ctk.CTkScrollableFrame(
            self.current_frame,
            width=520,
            height=260,
            corner_radius=12,
            fg_color=self.option_dropdown_color
        )
        records_frame.pack(pady=(0, 18))

        latest_records = records[-50:]

        for record in reversed(latest_records):
            self.create_record_card(records_frame, record)

        summary_label = ctk.CTkLabel(
            self.current_frame,
            text=f"Showing latest {len(latest_records)} of {len(records)} records",
            font=("Arial", 14),
            text_color=self.muted_text_color
        )
        summary_label.pack(pady=(0, 10))

    def create_record_card(self, parent, record):
        board_width = record.get("board_width") or "?"
        board_height = record.get("board_height") or "?"
        tile_size = record.get("tile_size") or "?"
        speed_delay = record.get("speed_delay") or "?"

        record_frame = ctk.CTkFrame(
            parent,
            fg_color=self.background_color,
            corner_radius=8
        )
        record_frame.pack(fill="x", padx=8, pady=5)

        main_text = (
            f"{record['date_time']} | "
            f"{record['bot_name']} | "
            f"Score: {record['score']} | "
            f"Moves: {record['total_moves']} | "
            f"Time: {record['game_time']}s"
        )

        detail_text = (
            f"Board: {board_width} x {board_height} | "
            f"Tile: {tile_size}px | "
            f"Speed Delay: {speed_delay}"
        )

        main_label = ctk.CTkLabel(
            record_frame,
            text=main_text,
            font=("Arial", 13, "bold"),
            text_color=self.text_color,
            anchor="w",
            justify="left"
        )
        main_label.pack(fill="x", padx=12, pady=(8, 1))

        detail_label = ctk.CTkLabel(
            record_frame,
            text=detail_text,
            font=("Arial", 12),
            text_color=self.muted_text_color,
            anchor="w",
            justify="left"
        )
        detail_label.pack(fill="x", padx=12, pady=(1, 8))

    def create_log_filter_button(self, parent, button_text, filter_value):
        if (self.selected_log_filter == filter_value):
            button_color = self.button_color
        else:
            button_color = self.secondary_button_color

        button = ctk.CTkButton(
            parent,
            text=button_text,
            font=("Arial", 14, "bold"),
            width=110,
            height=34,
            corner_radius=10,
            fg_color=button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color,
            command=lambda: self.change_log_filter(filter_value)
        )
        button.pack(side="left", padx=5)

        return button

    def change_log_filter(self, selected_filter):
        self.selected_log_filter = selected_filter
        self.open_logs()
    
    def create_stat_label(self, parent, title, value):
        stat_frame = ctk.CTkFrame(
            parent,
            fg_color=self.option_dropdown_color,
            corner_radius=10
        )
        stat_frame.pack(side="left", padx=5)

        title_label = ctk.CTkLabel(
            stat_frame,
            text=title,
            font=("Arial", 12),
            text_color=self.muted_text_color
        )
        title_label.pack(padx=12, pady=(6, 0))

        value_label = ctk.CTkLabel(
            stat_frame,
            text=str(value),
            font=("Arial", 18, "bold"),
            text_color=self.text_color
        )
        value_label.pack(padx=12, pady=(0, 6))

    def start_game_with_bot(self, bot_mode):
        if (not self.is_valid_board_for_bot(bot_mode)):
            self.error_label.configure(
                text="Hamiltonian Bot needs at least one even board side."
            )
            return
        
        self.selected_bot_mode = bot_mode
        self.window.quit()

    def start_replay_with_bot(self, bot_name):
        replay_data = self.replay_manager.load_replay(bot_name)

        if (replay_data is None):
            self.replay_status_label.configure(
                text=f"No replay found for {bot_name}"
            )
            return

        self.selected_bot_mode = f"replay:{bot_name}"
        self.window.quit()

    def clear_screen(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def close_menu(self):
        self.selected_bot_mode = None
        self.window.quit()

    def is_valid_board_for_bot(self, bot_mode):
        board_width, board_height = self.board_size_options[self.selected_board_size_name]

        if bot_mode == "hamiltonian":
            if board_width % 2 == 1 and board_height % 2 == 1:
                return False

        return True
    
    def change_board_size(self, selected_name):
        self.selected_board_size_name = selected_name

    def change_tile_size(self, selected_name):
        self.selected_tile_size_name = selected_name
    
    def change_speed(self, selected_name):
        self.selected_speed_name = selected_name

if __name__ == "__main__":
    while True:
        menu = MenuApp(24, 25, 25)
        bot_mode, board_width, board_height, tile_size, speed_delay = menu.start()

        if bot_mode is None:
            break

        if (bot_mode.startswith("replay:")):
            replay_bot_name = bot_mode.replace("replay:", "")
            replay_manager = ReplayManager()
            replay_data = replay_manager.load_replay(replay_bot_name)

            if (replay_data is None):
                continue

            replay_window = Window(
                replay_data["board_width"],
                replay_data["board_height"],
                replay_data["tile_size"]
            )
            replay_player = ReplayPlayer(replay_window, replay_data)
            replay_player.run()

            if not replay_player.return_to_menu:
                break

            continue

        game_window = Window(board_width, board_height, tile_size)
        snake = Snake(game_window)
        food = Food(game_window, snake)
        movement = Movement()

        game = Game(game_window, snake, food, movement, bot_mode, speed_delay)
        game.run()

        if not game.return_to_menu:
            break
