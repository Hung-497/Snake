import tkinter as tk

class Window:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size

        self.WINDOW_WIDTH = self.width * self.tile_size
        self.WINDOW_HEIGHT = self.height * self.tile_size

        # game window 
        self.window = tk.Tk()
        self.window.title('Snake Game')
        self.window.resizable(False, False)
    
    def center_window(self):
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        window_x = int((screen_width / 2) - (window_width / 2))
        window_y = int((screen_height / 2) - (window_height / 2))
        # format "(w)x(h)+(x)+(y)"
        self.window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}") # update the geometry of the window to center it on the screen

    def create_canvas(self):
        self.canvas = tk.Canvas(
            self.window, 
            bg = 'black', 
            width = self.WINDOW_WIDTH, 
            height = self.WINDOW_HEIGHT,
            borderwidth = 0,
            highlightthickness = 0
            )
        self.canvas.pack()
        self.window.update() # update the window to display the canvas
    
    def draw_game_over(self, score):
        self.canvas.create_text(
            self.WINDOW_WIDTH // 2, 
            self.WINDOW_HEIGHT // 2, 
            text = f'Game Over! \nYour score: {score}', 
            fill = 'red', 
            font = ('consolas', 70),
            tag = 'gameover'
            )
    
    def draw_game_won(self, score):
        self.canvas.create_text(
            self.WINDOW_WIDTH // 2, 
            self.WINDOW_HEIGHT // 2, 
            text = f'You won! \nYour score: {score}', 
            fill = 'Yellow', 
            font = ('consolas', 70),
            tag = 'gamewon'
            )
        
    def draw_score_label(self):
        self.score_label = tk.Label(
            self.window,
            text = 'Score: 0 Match: 0 Best score: 0',
            font = ('consolas', 40),
            fg = 'black',
            bg = 'white'
        )
        self.score_label.pack(fill = 'x', side = 'top')
    
    def update_score_label(self, score, games_played, best_score):
        self.score_label.config(text = f'Score: {score} Match: {games_played} Best score: {best_score}')

    def clear_canvas(self):
        self.canvas.delete("all")

    def after(self, delay, callback):
        self.window.after(delay, callback)
    
    def start(self):
        self.window.mainloop()