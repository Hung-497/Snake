import customtkinter as ctk
from Food import Food
from Snake import Snake
from Window import Window
from Game import Game
from Movement import Movement

class MenuApp:
    def __init__(self, width, height, tile_size):
        ctk.set_appearance_mode("dark")  # Set the appearance mode to "dark"
        ctk.set_default_color_theme("dark-blue")  # Set the color theme to "dark-blue"

        self.width = width
        self.height = height
        self.tile_size = tile_size

        self.selected_bot_mode = None
        self.current_frame = None

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
        pass

    def start_game_with_bot(self, bot_mode):
        if (not self.is_valid_board_for_bot(bot_mode)):
            self.error_label.configure(
                text="Hamiltonian Bot needs at least one even board side."
            )
            return
        
        self.selected_bot_mode = bot_mode
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
    menu = MenuApp(24, 25, 25)
    bot_mode, board_width, board_height, tile_size, speed_delay = menu.start()

    if bot_mode is not None:
        game_window = Window(board_width, board_height, tile_size)
        snake = Snake(game_window)
        food = Food(game_window, snake)
        movement = Movement()

        game = Game(game_window, snake, food, movement, bot_mode, speed_delay)
        game.run()
