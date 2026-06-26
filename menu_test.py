import customtkinter as ctk
from Food import Food
from Snake import Snake
from Window import Window
from Game import Game
from Movement import Movement

class MenuTestApp:
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
            font=("Arial", 50),
            text_color=self.text_color
        )
        self.title_menu_label.pack(pady=(0, 35))

        self.start_button = ctk.CTkButton(
            self.current_frame,
            text="Play",
            font=("Arial", 30),
            width=180,
            height=48,
            corner_radius=10,
            fg_color=self.button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color,
            command=self.draw_play_button
        )
        self.start_button.pack(pady=10)

        self.settings_button = ctk.CTkButton(
            self.current_frame,
            text="Settings",
            font=("Arial", 30),
            width=160,
            height=44,
            fg_color=self.button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color,
            command=self.open_settings
        )
        self.settings_button.pack(pady=10)

        self.logs_button = ctk.CTkButton(
            self.current_frame,
            text="Logs",
            font=("Arial", 30),
            width=140,
            height=40,
            fg_color=self.button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color,
            command=self.open_logs
        )
        self.logs_button.pack(pady=10)

        self.name_label = ctk.CTkLabel(
            self.current_frame,
            text="Created by Nhism",
            font=("Arial", 14),
            text_color=self.muted_text_color
        )
        self.name_label.place(relx=0.98, rely=0.99, anchor="se")

    def start(self):
        self.center_window()
        self.draw_menu()
        self.window.mainloop()
        self.window.withdraw()
        self.window.destroy()
        return self.selected_bot_mode

    def draw_play_button(self):
        self.clear_screen()

        self.current_frame = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )
        self.current_frame.place(relx=0.5, rely=0.45, anchor="center")

        self.title_play_label = ctk.CTkLabel(
            self.current_frame,
            text="Choose Bot Mode:",
            font=("Arial", 50),
            text_color=self.text_color
        )
        self.title_play_label.pack(pady=(0, 35))

        self.RuleBased_Bot_button = ctk.CTkButton(
            self.current_frame,
            text="Rule Based Bot",
            font=("Arial", 30),
            width=250,
            height=48,
            corner_radius=10,
            fg_color=self.button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color,
            command=lambda: self.start_game_with_bot("rule")
        )
        self.RuleBased_Bot_button.pack(pady=10)

        self.QLearning_Bot_button = ctk.CTkButton(
            self.current_frame,
            text="Q Learning Bot",
            font=("Arial", 30),
            width=250,
            height=48,
            corner_radius=10,
            fg_color=self.button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color,
            command=lambda: self.start_game_with_bot("q_learning")
        )
        self.QLearning_Bot_button.pack(pady=10)

        self.Hamiltonian_Bot_button = ctk.CTkButton(
            self.current_frame,
            text="Hamiltonian Bot",
            font=("Arial", 30),
            width=250,
            height=48,
            corner_radius=10,
            fg_color=self.button_color,
            hover_color=self.button_hover_color,
            text_color=self.text_color,
            command=lambda: self.start_game_with_bot("hamiltonian")
        )
        self.Hamiltonian_Bot_button.pack(pady=10)

    def open_settings(self):
        pass

    def open_logs(self):
        pass

    def start_game_with_bot(self, bot_mode):
        self.selected_bot_mode = bot_mode
        self.window.quit()

    def clear_screen(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def close_menu(self):
        self.selected_bot_mode = None
        self.window.quit()

bot_mode = MenuTestApp(24, 25, 25).start()

if bot_mode is not None:
    game_window = Window(24, 25, 25)
    snake = Snake(game_window)
    food = Food(game_window, snake)
    movement = Movement()

    game = Game(game_window, snake, food, movement, bot_mode)
    game.run()