import game
import random
import argparse
import pprint
import mcts

from contextlib import contextmanager
import sys, os
# Code from: https://thesmithfam.org/blog/2012/10/25/temporarily-suppress-console-output-in-python/
@contextmanager
def suppress_stdout():
    """
    Suppresses stdout for the duration of the context. 
    This is for copying the game state and playing out an action without printing to the console.
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--player", help="Play against another player", action="store_true")
parser.add_argument("-c", "--computer", help="Play against the computer", action="store_true")
args = parser.parse_args()

def game_loop_pvp():
    """
    The game loop for player vs player.

    This is largely for debugging purposes. It's not very fun to play.
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
                print(f"{game.players[influence_count.index(max(influence_count))]} wins on round {game.round}!")
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
    
    def check_win(): 
        winner, loser = game.check_win()
        if winner: # Check if a player has no more influences
            print('!' * 80)
            print(f"{loser} has no more influences!".center(80))
            print(f"Game over on round {game.round}!".center(80))
            print(f"{winner} wins!".center(80))
            print('!' * 80)
            return True
        return False
    
    def get_computer_action():
        """
        Performs MCTS search to get the best computer action.

        However, there are some hardcoded strategies that the computer will prioritise before performing a search.
        """
        if game.playable_actions == ["allow"]:
            return "allow"
        
        print("Computer is thinking...")

        # Computer will coup if it has more than 7 coins.
        if computer.coins >= 7:
            return "coup"

        # Last ditch efforts
        if game.playable_actions == game.playable_actions == ["allow", "block", "challenge"]:
            if game.current_action == "assassinate" and len(computer.hand) == 1:
                if "contessa" in computer.hand:
                    return "block"
                return "challenge"

        # Worst case scenario, computer doesn't have a hardcoded strategy so it will try to find the best move.
        with suppress_stdout():
            mcts_module = mcts.MCTS(game, args={'C':1.41, 'num_simulations':1000, 'max_depth':100})
            mcts_probs = mcts_module.search()
        # print(mcts_probs)
        
        action_prob = {game.playable_actions[i]: mcts_probs[i] for i in range(len(mcts_probs))}

        if game.playable_actions == ["coup", "income", "foreign_aid", "tax", "steal", "assassinate", "exchange"]:

            # Add more weighting to actions that are legal
            if "duke" in computer.hand:
                action_prob['tax'] += 0.1
            if "captain" in computer.hand:
                action_prob['steal'] += 0.1
            if "assassin" in computer.hand:
                action_prob['assassinate'] += 0.1
            if "ambassador" in computer.hand:
                action_prob['exchange'] += 0.1

            # Remove more weighting to actions that are illegal
            if "duke" not in computer.hand:
                action_prob['tax'] -= 0.2
            if "captain" not in computer.hand:
                action_prob['steal'] -= 0.2
            if "assassin" not in computer.hand:
                action_prob['assassinate'] -= 0.2
            if "ambassador" not in computer.hand:
                action_prob['exchange'] -= 0.2

            # Computer more likely to assassinate if it has more than 3 coins, and has the Assassin influence.
            if computer.coins >= 3 and "assassin" in computer.hand:
                action_prob['assassinate'] += 0.1

            # Computer is more likely to steal if player is almost able to coup.
            if player.coins >= 4:
                if len(computer.hand) == 1:
                    action_prob['steal'] += 0.9
                action_prob['steal'] += 0.1
        
        return random.choices(list(action_prob.keys()), weights=list(action_prob.values()), k=1)[0]
    
    def print_game_status():
        print(f" {game.turn}'s turn ".center(80, "."))
        print('#' * 80)
        print(player.print_information())
        # print(computer.print_information()) # Debug
        print(f"Your opponent has {len(computer.hand)} influence(s) and {computer.coins} coins.")
        print('#' * 80)
        
    player = game.players[game.players.index("Player")]
    computer = game.players[game.players.index("Computer")]    
    while True:
        game.round += 1
        random.shuffle(game.deck)
        print(f" Round {game.round} ".center(80, "="))
        print_game_status()

        # Player's Action Turn
        game.turn = player
        game.playable_actions = game.get_playable_actions()

        # Player chooses an action        
        while True:
            try:
                action = input(f"Choose an action from {', '.join(game.playable_actions)}: ").lower().replace(" ", "_")
                if action not in game.playable_actions:
                    raise ValueError
                break
            except ValueError:
                    print("Invalid input. Try again.")
            except Exception as e:
                print(f"An error occurred: {e}")
                raise e
        
        game.current_action = action
        print(f"Player chose {action}.")
        game.play_action(action=action)

        # Ask computer to block/challenge
        response = get_computer_action()
        print(f"Computer chose to {response}.")
        game.play_action(player, computer, action=response)

        # If computer blocks, ask player to challenge or allow
        if game.block_attempted:
            print(f"Player, choose to challenge or allow: ")
            response = input().lower().replace(" ", "_")
            game.play_action(player, computer, action=response)

        if check_win():
            break

        # Computer's Action Turn
        game.playable_actions = game.get_playable_actions()
        game.turn = computer
        print_game_status()

        # Computer chooses an action
        action = get_computer_action() 
        print(f"Computer chose {action}.")
        game.current_action = action
        game.play_action(action=action)
                    
        # Ask player to block/challenge
        print(f"Player, choose to {', '.join(game.playable_actions)}: ")
        response = input().lower().replace(" ", "_")
        print(f"Player chose {response}.")
        game.play_action(computer, player, action=response)

        # If player blocks, ask computer to challenge or allow
        if game.block_attempted:
            response = get_computer_action()
            print(f"Computer chose to {response}.")
            game.play_action(computer, player, action=response)
        
        if check_win():
            break
        


if __name__ == "__main__":
    game = game.Game()

    print("Welcome to Coup!")

    if args.player:
        print("Player vs Player")
        game.initial_draw()
        game_loop_pvp()
    else:
        print("Player vs Computer")
        game.initial_draw_computer()
        game_loop_pvc()

    exit = input("Press Enter to exit.")