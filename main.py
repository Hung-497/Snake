from Food import Food
from Snake import Snake
from Window import Window
from Game import Game
from Movement import Movement

if __name__ == "__main__":
    window = Window(24,25,25)
    snake = Snake(window)
    food = Food(window, snake)
    movement = Movement()
    game = Game(window, snake, food, movement)

    game.run()