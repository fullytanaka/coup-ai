from copy import deepcopy
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

class MCTS:

    """
    Imperfect game state information
    """
    def get_game_state(self, game, name):
        """Returns a dictionary of the state from the perspective of the player."""
        player = game.players[game.players.index(name)]
        opponent = game.players[(game.players.index(name) + 1) % len(game.players)]
        return {
            # Player information
            "hand": player.hand,
            "coins": player.coins,
            "influence_count": len(player.hand),

            # Opponent information
            "opponent_coins": opponent.coins,
            "opponent_influence_count": len(opponent.hand),

            # Game information
            "round": game.round,
            "turn": game.turn,
            "game_won": game.game_won,
            "winner": None,
            "playable_actions": game.playable_actions,
            "block_attempted": game.block_attempted,
            "challenge_attempted": game.challenge_attempted,
            "current_action": game.current_action,
        }
        
    def get_next_state(self, game, player, action):
        """
        Returns the state after an action is played.
        """
        with suppress_stdout():
            game_temp = deepcopy(game)
            game_temp.is_simulation = True
            match action:
                case "coup" | "income" | "foreign_aid" | "tax" | "steal" | "assassinate" | "exchange":
                    game_temp.current_action = action
                    if action in game_temp.challengeable_actions and action in game_temp.blockable_actions:
                        game_temp.playable_actions = ["allow","block", "challenge"]
                    elif action in game_temp.challengeable_actions:
                        game_temp.playable_actions = ["allow", "challenge"]
                    elif action in game_temp.blockable_actions:
                        game_temp.playable_actions = ["allow", "block"]
                case "block":
                    game_temp.playable_actions = ["allow", "challenge"]
                    game_temp.block_attempted = True
                case "challenge":
                    game_temp.playable_actions = ["coup", "income", "foreign_aid", "tax", "steal", "assassinate", "exchange"]
                    game_temp.challenge_attempted = True
                    if game_temp.block_attempted:
                        game_temp.block(game_temp.players[game_temp.players.index(player)], game_temp.players[(game_temp.players.index(player) + 1) % len(game_temp.players)], game_temp.current_action)
                    else:
                        challenge_successful = game_temp.challenge(game_temp.players[game_temp.players.index(player)], game_temp.players[(game_temp.players.index(player) + 1) % len(game_temp.players)], game_temp.current_action)
                        if not challenge_successful: # If challenge is unsuccessful, or there is no challenge, play the action
                            match game_temp.current_action:
                                case "coup" | "assassinate" | "steal":
                                    getattr(game_temp, game_temp.current_action)(game.players[game_temp.players.index(player)], game_temp.players[(game_temp.players.index(player) + 1) % len(game_temp.players)])
                                case default:
                                    getattr(game_temp, game_temp.current_action)(game_temp.players[game_temp.players.index(player)])
                        # Reset flags
                        game_temp.challenge_attempted = False
                        game_temp.block_attempted = False
                case default:
                    challenge_successful = False
                    if game_temp.challenge_attempted:
                        challenge_successful = game_temp.challenge(game_temp.players[game_temp.players.index(player)], game_temp.players[(game_temp.players.index(player) + 1) % len(game_temp.players)], game_temp.current_action)
                    if not challenge_successful: # If challenge is unsuccessful, or there is no challenge, play the action
                        match game_temp.current_action:
                            case "coup" | "assassinate" | "steal":
                                getattr(game_temp, game_temp.current_action)(game.players[game_temp.players.index(player)], game_temp.players[(game_temp.players.index(player) + 1) % len(game_temp.players)])
                            case default:
                                getattr(game_temp, game_temp.current_action)(game_temp.players[game_temp.players.index(player)])
                    # Reset flags
                    game_temp.challenge_attempted = False
                    game_temp.block_attempted = False
    
            next_game_state = self.get_game_state(game_temp, player)

            # Swap turn and increase round if necessary
            next_game_state["turn"] = game_temp.players[(game_temp.players.index(player) + 1) % len(game_temp.players)]
            if not game_temp.block_attempted and not game_temp.challenge_attempted and game_temp.playable_actions == ["coup", "income", "foreign_aid", "tax", "steal", "assassinate", "exchange"]:
                next_game_state["round"] += 1

            # Check who is the winner
            if next_game_state["opponent_influence_count"] == 0:
                next_game_state["winner"] = player
                next_game_state["game_won"] = True
            if next_game_state["influence_count"] == 0:
                next_game_state["winner"] = game_temp.players[(game_temp.players.index(player) + 1) % len(game_temp.players)]
                next_game_state["game_won"] = True
            return next_game_state