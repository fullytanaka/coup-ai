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
        
    def get_next_state(self, state, response, player):
        """Returns the state after the action is played."""
        current_game_state = state
        match state["current_action"]:
            case "coup":
                if current_game_state["coins"] >= 7:
                    current_game_state["coins"] -= 7
                    current_game_state["opponent_influence_count"] -= 1
                else:
                    pass
            case "income":
                current_game_state["coins"] += 1
            case "foreign_aid":
                if not state["block_attempted"]:
                    state["playable_actions"] = ["allow", "block"]     
        # Switch turns
        current_game_state["turn"] = self.game.players[(self.game.players.index(player) + 1) % len(self.players)]
        return current_game_state