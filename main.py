import game
import random
import argparse
import pprint
import mcts

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
        
    player = game.players[game.players.index("Player")]
    computer = game.players[game.players.index("Computer")]    
    computer.hand = ["assassin", "captain"]
    while True:
        game.round += 1
        random.shuffle(game.deck)
        print(f" Round {game.round} ".center(80, "="))

        # Player's Action Turn
        game.turn = player
        game.playable_actions = game.get_playable_actions()

        print(f" {game.turn}'s turn ".center(80, "."))
        print('#' * 80)
        print(player.print_information())
        print(computer.print_information()) # Debug
        print(f"Your opponent has {len(computer.hand)} influence(s) and {computer.coins} coins.")
        print('#' * 80)

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
        print("Computer is thinking...")
        # mcts_probs = mcts.search() # TODO: MCTS search for best action
        # print(mcts_probs)
        # response = game.playable_actions[mcts_probs.index(max(mcts_probs))]
        response="allow"
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
        print(f" {game.turn}'s turn ".center(80, "."))

        # Computer chooses an action
        mcts_probs = mcts.search() # TODO: MCTS search for best action
        print(mcts_probs)
        action = game.playable_actions[mcts_probs.index(max(mcts_probs))]
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
            response = random.choice(game.playable_actions) # TODO: MCTS search for best action
            print(f"Computer chose to {response}.")
            game.play_action(computer, player, action=response)
        
        if check_win():
            break
        


if __name__ == "__main__":
    game = game.Game()
    mcts = mcts.MCTS(game, args={'C':1.41, 'num_simulations':1000, 'max_depth':500})

    print("Welcome to Coup!")

    if args.player:
        print("Player vs Player")
        # game.add_player("Player 1")
        # game.add_player("Player 2")
        game.initial_draw()
        game_loop_pvp()
    else:
        print("Player vs Computer")
        # game.add_player("Player")
        # game.add_player("Computer")
        game.initial_draw_computer()
        game_loop_pvc()
