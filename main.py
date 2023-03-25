import game
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--player", help="Play against another player", action="store_true")
parser.add_argument("-c", "--computer", help="Play against the computer", action="store_true")
args = parser.parse_args()

game = game.Game()
if args.player:
    game.add_player("Player 1")
    game.add_player("Player 2")
    game.start()
elif args.computer:
    game.add_player("Player 1")
    game.add_player("Computer")
    game.start()