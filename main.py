from Food import Food
from Snake import Snake
from Window import Window
from Game import Game
from Movement import Movement

def choose_bot_mode():
    print("Choose bot:")
    print("1. Rule-based bot")
    print("2. Q-learning bot")
    print("3. Hamiltonian bot")

    choice = input("Enter 1, 2, or 3: ")
    bot = None

    if (choice == "1"):
        bot = "rule"
        print("Using a rule-based bot\n")
    elif (choice == "2"):
        bot = "q_learning"
        print("Using Q-learning bot\n")
    elif (choice == "3"):
        bot = "hamiltonian"
        print("Using Hamiltonian bot\n")
    else:
        print("Invalid choice, using Hamiltonian bot.")
        bot = "hamiltonian"
    
    return bot

if __name__ == "__main__":
    bot_mode = choose_bot_mode()
    
    window = Window(24,25,25)
    snake = Snake(window)
    food = Food(window, snake)
    movement = Movement()
    game = Game(window, snake, food, movement, bot_mode)

    game.run()