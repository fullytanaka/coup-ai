import game
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--player", help="Play against another player", action="store_true")
parser.add_argument("-c", "--computer", help="Play against the computer", action="store_true")
args = parser.parse_args()

class GameState:
    """
    The state of the game.
    """ 
    def get_player_state(self, name):
        """
        Returns a dictionary of the state from the perspective of the player.
        """
        return {
            # Player information
            "hand": game.players.index(name).hand,
            "coins": game.players.index(name).coins,
            "influence_count": len(game.players.index(name).hand),

            # Opponent information
            "opponent_coins": game.players[(game.players.index(name) + 1) % len(game.players)].coins,
            "opponent_influence_count": len(game.players[(game.players.index(name) + 1) % len(game.players)].hand),

            # Game information
            "game_won": game.game_won,
            "round": game.round, 
        }

    def get_playable_actions(self):
        """
        Returns a list of actions that can be played.
        """
        return game.playable_actions

def game_loop_pvp():
    """
    The game loop for player vs player.
    """
    while game.game_won == False:
        game.round += 1
        random.shuffle(game.deck)
        print(f"==================== Round {game.round} ====================")
        for i in range(len(game.players)):
            influence_count = [len(player.hand) for player in game.players]

            if min(influence_count) == 0: # Check if a player has no more influences
                print(f"{game.players[influence_count.index(min(influence_count))]} has no more influences!")
                print("Game over!")
                print(f"{game.players[influence_count.index(max(influence_count))]} wins!")
                game.game_won = True
                break

            print(f"{game.players[i].name}'s turn.")
            print(game.players[i].print_information())

            # Player chooses an action
            while True:
                game.playable_actions = ["coup", "income", "foreign_aid", "tax", "steal", "assassinate", "exchange"]
                game.challenge_attempted = False
                game.block_attempted = False

                try:
                    action = input(f"Choose an action from {', '.join(game.playable_actions)}: ").lower().replace(" ", "_")
                    if action not in game.playable_actions:
                        raise ValueError

                    # If the action is challengeable/blockable, target chooses to allow, challenge or block
                    if action in game.challengeable_actions and action in game.blockable_actions:
                        game.playable_actions = ["allow", "challenge", "block"]
                    elif action in game.challengeable_actions:
                        game.playable_actions = ["allow", "challenge"]
                    elif action in game.blockable_actions:
                        game.playable_actions = ["allow", "block"]

                    if action in game.challengeable_actions or action in game.blockable_actions:
                        print(f"{game.players[(i + 1) % len(game.players)]}, choose to {', '.join(game.playable_actions)}: ")
                        match input().lower().replace(" ", "_"):
                            case "challenge":
                                game.challenge_attempted = True
                            case "block":
                                game.block_attempted = True
                            case default:
                                pass

                    if game.block_attempted:
                        # Player can challenge a block attempt
                        game.playable_actions = ["allow", "challenge"]
                        match input(f"{game.players[i]}, choose to challenge or allow: "):
                            case "challenge":
                                game.challenge_attempted = True
                            case default:
                                pass
                        game.block(game.players[i], game.players[(i + 1) % len(game.players)], action)
                        break
                    else: # Action is allowed
                        if game.challenge_attempted:
                            if game.challenge(game.players[i], game.players[(i + 1) % len(game.players)], action):
                                break

                        print(f"{game.players[i].name} chose {action}.")
                        if action in ["coup", "assassinate", "steal"]: # Actions that require a target
                            getattr(game, action)(game.players[i], game.players[(i + 1) % len(game.players)])
                        else:
                            getattr(game, action)(game.players[i])
                        break

                except ValueError:
                    print("Invalid input. Try again.")
                except Exception as e:
                    print(f"An error occurred: {e}")
                    raise e

def game_loop_pvc():
    """
    The game loop for player vs computer.
    """
    

if __name__ == "__main__":
    game = game.Game()

    print("Welcome to Coup!")

    game.add_player("Player 1")
    game.add_player("Player 2")

    if args.player:
        print("Player vs Player")
        game.initial_draw()
        game_loop_pvp()
    elif args.computer:
        print("Player vs Computer")
        # game_loop_pvc()
    else:
        print("Player vs Player")
        game.initial_draw()
        game_loop_pvp()
