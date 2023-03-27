import game
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--player", help="Play against another player", action="store_true")
parser.add_argument("-c", "--computer", help="Play against the computer", action="store_true")
args = parser.parse_args()

game = game.Game()
if __name__ == "__main__":
    if args.player:
        print("Player vs Player")
    elif args.computer:
        print("Player vs Computer")
    else:
        print("Player vs Player")

    print("Welcome to Coup!")

    game.add_player("Player 1")
    game.add_player("Player 2")

    game.initial_draw()
    while game.game_won == False:
        game.game_loop()