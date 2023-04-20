import numpy as np
from copy import deepcopy
import math
import game

class Node:
    """
    Node class for the Monte Carlo Tree Search Tree
    """
    def __init__(self, game: game, args, parent=None, action=None):
        self.game = game
        self.args = args
        self.state = self.game.get_game_state("Computer")
        print(self.state)
        self.parent = parent
        self.action = action

        self.children = []
        self.untried_actions = self.game.playable_actions

        self.visits = 0
        self.wins = 0

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
            score = self.get_ucb(self, child)
            if score > best_score:
                best_child = child
                best_score = score

        return best_child

    
    def get_ucb(self, child):
        """
        Calculate the UCB score for a child node
        """
        q_value = 1 - ((child.wins / child.visits) + 1) / 2
        return q_value + self.args['C'] * math.sqrt(math.log(self.visit_count) / child.visit_count)

    def expand(self):
        action = np.random.choice(self.untried_actions)
        self.untried_actions.remove(action)

        child_state = self.game.get_next_state(self.game, self.state["turn"], action)

        child = Node(self.game, self.args, self, action)
        self.children.append(child)
        return child

    def simulate(self):
        winner, terminated = self.game.get_winner_and_terminated(self.state)
        if winner != None:
            winner = self.game.players[(self.game.players.index(winner) + 1) % len(self.game.players)]

        if terminated:
            return winner
        
        rollout_state = deepcopy(self.state)
        rollout_player = self.state["turn"]
        while True:
            action = np.random.choice(self.game.playable_actions)
            rollout_state = self.game.get_next_state(self.game, rollout_player, action)
            winner, terminated = self.game.get_winner_and_terminated(rollout_state)
            if terminated:
                if rollout_player == self.game.players[(self.game.players.index(winner) + 1) % len(self.game.players)]:
                    winner = self.game.players[(self.game.players.index(winner) + 1) % len(self.game.players)]
                return winner
            rollout_player = self.game.players[(self.game.players.index(rollout_player) + 1) % len(self.game.players)]
    
    def backpropagate(self, wins):
        self.visits += 1
        if self.state["winner"] == "Computer":
            self.wins += 1
        else:
            self.wins -= 1

        if self.parent is not None:
            print(self.parent)
            self.parent.backpropagate(wins)
    
class MCTS:
    """
    Monte Carlo Tree Search Algorithm

    The code is based on the code from this repository, but has been adapted to fit the needs of this project:
    https://github.com/foersterrobert/AlphaZeroFromScratch/blob/main/2.MCTS.ipynb 
    """
    def __init__(self, game, args):
        self.game = game
        self.args = args

    def search(self, state):
        root = Node(self.game, self.args)

        for search in range(self.args['num_simulations']):
            node = root
            # Selection
            while node.is_fully_expanded():
                node = self.select()
            winner, terminated = self.game.get_winner_and_terminated(node.state)
            if winner != None:
                winner = self.game.players[(self.game.players.index(winner) + 1) % len(self.game.players)]
            if not terminated:
                # Expansion
                node = node.expand()
                # Simulation
                wins = node.simulate()

            # Backpropagation
            node.backpropagate(wins)

        # return visits
        action_probs = self.game.playable_actions
        print(action_probs)
        for child in root.children:
            print(child.action)
            action_probs[action_probs.index(child.action)] = child.visits
        action_probs /= np.sum(action_probs)