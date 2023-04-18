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
    
    def __init__(self):
        pass

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
            "game_won": game.game_won,
            "playable_actions": game.playable_actions,
            "block_attempted": game.block_attempted,
            "challenge_attempted": game.challenge_attempted,
            "current_action": game.current_action,
            "turn": game.turn
        }
        
    def get_next_state(self, game, player, action):
        """Returns the state after the action is played."""
        with suppress_stdout():
            game_temp = deepcopy(game)
            match action:
                case "coup" | "assassinate" | "steal":
                    getattr(game_temp, action)(game.players[game_temp.players.index(player)], game_temp.players[(game_temp.players.index(player) + 1) % len(game_temp.players)])
                    next_game_state["round"] += 1
                case _:
                    getattr(game_temp, action)(game_temp.players[game_temp.players.index(player)])
                    next_game_state["round"] += 1
            next_game_state = self.get_game_state(game_temp, player)

            # Swap turn and increase round
            next_game_state["turn"] = game_temp.players[(game_temp.players.index(player) + 1) % len(game_temp.players)]
            return next_game_state