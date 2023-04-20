import numpy as np
from copy import copy, deepcopy
import math
import game

class Node:
    """
    Node class for the Monte Carlo Tree Search Tree
    """
    def __init__(self, game: game, args, parent=None, action=None):
        self.game = game
        self.args = args
        self.state = self.game.get_game_state(game.turn)
        self.parent = parent
        self.action = action

        self.children = []
        self.untried_actions = copy(self.game.playable_actions)

        # Remove actions that can't be played
        if "coup" in self.untried_actions or "assassinate" in self.untried_actions:
            if self.state['coins'] < 3:
                self.untried_actions.remove('assassinate')
            if self.state['coins'] < 7:
                self.untried_actions.remove('coup')

        self.visits = 0
        self.value_sum = 0

    def is_fully_expanded(self):
        """
        Check if the node has been fully expanded
        """
        return len(self.untried_actions) == 0 and len(self.children) > 0
    
    def select(self):
        """
        Select the child with the highest UCB score
        """
        best_child = None
        best_score = -np.inf

        for child in self.children:
            score = self.get_ucb(child)
            if score > best_score:
                best_child = child
                best_score = score

        return best_child

    
    def get_ucb(self, child):
        """
        Calculate the UCB score for a child node
        """
        q_value = 1 - ((child.value_sum / child.visits) + 1) / 2
        return q_value + self.args['C'] * math.sqrt(math.log(self.visits) / child.visits)

    def expand(self):
        action = np.random.choice(self.untried_actions)
        self.untried_actions.remove(action)

        child_state = self.game.get_next_state(self.state["turn"], action)

        child = Node(self.game, self.args, self, action)
        self.children.append(child)
        return child

    def simulate(self):
        winner, terminated = self.game.get_winner_and_terminated()
        if winner != "":
            winner = self.game.players[(self.game.players.index(winner) + 1) % len(self.game.players)]

        if terminated:
            return winner
        
        rollout_game = deepcopy(self.game)
        rollout_player = self.game.turn
        rollout_opponent = self.game.players[(self.game.players.index(rollout_player) + 1) % len(self.game.players)]
        for i in range(self.args['max_depth']):
            action = np.random.choice(rollout_game.playable_actions)
            rollout_game.play_action(rollout_player, rollout_opponent, action)
            winner, terminated = rollout_game.get_winner_and_terminated()
            # Rewards
            self.value_sum += rollout_player.coins
            if len(rollout_opponent.hand) == 1:
                self.value_sum += 300
            if len(rollout_opponent.hand) == 0:
                self.value_sum += 900

            # Punishments
            if rollout_opponent.coins >=7:
                self.value_sum -= 100
            else:
                self.value_sum -= rollout_opponent.coins
            if len(rollout_player.hand) == 1:
                self.value_sum -= 100
            if len(rollout_player.hand) == 0:
                self.value_sum -= 300

            rollout_player = self.game.players[(self.game.players.index(rollout_player) + 1) % len(self.game.players)]
        return self.value_sum
    def backpropagate(self, value_sum):
        self.visits += 1
        if self.state['winner'] == "Player":
            self.value_sum = -value_sum
        self.value_sum += value_sum

        if self.parent is not None:
            self.parent.backpropagate(value_sum)
    
class MCTS:
    """
    Monte Carlo Tree Search Algorithm

    The code is based on the code from this repository, but has been adapted to fit the needs of this project:
    https://github.com/foersterrobert/AlphaZeroFromScratch/blob/main/2.MCTS.ipynb 
    """
    def __init__(self, game, args):
        self.game = game
        self.args = args

    def search(self):
        game_simulation = deepcopy(self.game)
        game_simulation.is_simulation = True
        root = Node(game_simulation, self.args)

        for simulation in range(self.args['num_simulations']):
            node = root
            # Selection
            while node.is_fully_expanded():
                node = node.select()
            winner, terminated = game_simulation.get_winner_and_terminated()
            if winner != '':
                winner = game_simulation.players[(game_simulation.players.index(winner) + 1) % len(game_simulation.players)]
            if not terminated:
                # Expansion
                node = node.expand()
                # Simulation
                value_sum = node.simulate()

            # Backpropagation
            node.backpropagate(value_sum)

        # return visits
        action_probs = game_simulation.playable_actions
        for child in root.children:
            action_probs[action_probs.index(child.action)] = child.visits
        if 'coup' in action_probs:
            action_probs[action_probs.index('coup')] = 0
        if 'assassinate' in action_probs:
            action_probs[action_probs.index('assassinate')] = 0
        
        for i in range(len(action_probs)):
            action_probs[i] /= self.args['num_simulations']
        return(action_probs)