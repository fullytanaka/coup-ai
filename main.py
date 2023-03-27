import game
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--player", help="Play against another player", action="store_true")
parser.add_argument("-c", "--computer", help="Play against the computer", action="store_true")
args = parser.parse_args()

game = game.Game()
class GameState:
    """
    The state of the game.
    """

    def get_global_state(self):
        """
        Returns a dictionary of the global state.
        """
        return {
            "players": game.players,
            "game_won": game.game_won,
        }

    def get_playable_actions(self):
        """
        Returns a list of actions that can be played.
        """
        return game.playable_actions

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