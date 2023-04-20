import random
from copy import deepcopy
from contextlib import contextmanager
import sys, os
import pprint

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

class Game():
    """Game of Coup."""

    class Player():
        """A player in the game."""
        def __init__(self, name):
            """Initialize the player."""
            self.name = name
            self.hand = []
            self.coins = 2

        def add_card(self, card):
            """Add a card to the player's hand."""
            self.hand.append(card)
        
        def remove_card(self, card):
            """Attempt to remove a card from the player's hand."""
            if card not in self.hand:
                return
            self.hand.remove(card)

        def print_information(self):
            """print information about the player."""
            return f"{self.name} has {self.coins} coins and {self.hand} in their hand."
        
        def __str__(self):
            """Return the name of the player."""
            return self.name
        
        def __repr__(self):
            """Return the name of the player."""
            return self.name
        
        def __eq__(self, name):
            """Return whether the player is equal to a name."""
            return self.name == name
        
    def __init__(self):
        """Initialize the game."""
        self.players = [self.Player("Player"), self.Player("Computer")]
        self.is_simulation = False
        self.deck = ["duke", "assassin", "ambassador", "captain", "contessa"] * 3
        self.round = 0
        self.turn = self.players[0]
        self.current_action = ""
        self.game_won = False
        self.winner = ""
        self.playable_actions = []
        self.blockable_actions = ["assassinate", "steal", "foreign_aid"]
        self.challengeable_actions = ["tax", "assassinate", "steal", "exchange", "block"]
        self.block_attempted = False
        self.challenge_attempted = False

    def add_player(self, name):
        """Add a player to the game."""
        self.players.append(self.Player(name))

    def remove_player(self, name):
        """Remove a player from the game."""
        self.players.remove(self.Player(name))

    def initial_draw(self):
        """Initial draw. Shuffle the deck and each the player choose two cards from the top three cards, as per the rules of two-player Coup."""
        for player in self.players:
            random.shuffle(self.deck)
            draw = self.deck[:3]
            print(f"{player.name} choose a card from {draw} by entering the index of the card.")
            while True:
                try:
                    card = int(input())
                    player.hand.append(draw[card])
                    print(f"{player.name} chose {draw[card]}")
                    draw.pop(card)
                    break
                except ValueError:
                    print("Invalid input. Try again.")
            for card in draw:
                self.deck.append(card)
                draw.remove(card)
            random.shuffle(self.deck)
            player.hand.append(self.deck.pop())

    def initial_draw_computer(self):
        """Initial draw if playing against a computer."""
        # Player
        random.shuffle(self.deck)
        draw = self.deck[:3]
        print(f"{self.players[0]} choose a card from {draw} by entering the index of the card.")
        while True:
            try:
                card = int(input())
                self.players[0].hand.append(draw[card])
                print(f"{self.players[0]} chose {draw[card]}")
                draw.pop(card)
                break
            except ValueError:
                print("Invalid input. Try again.")
        for card in draw:
            self.deck.append(card)
            draw.remove(card)
        random.shuffle(self.deck)
        self.players[0].hand.append(self.deck.pop())

        # Computer
        random.shuffle(self.deck)
        draw = self.deck[:3]
        print("Computer is choosing their initial card...")

        # Computer will prioritise the duke, then the assassin, then a random card
        if "duke" in draw:
            card = draw.index("duke")
        elif "assassin" in draw:
            card = draw.index("assassin")
        else:
            card = random.randint(0, 2)
        self.players[1].hand.append(draw[card])
##        print(f"{self.players[1]} chose {draw[card]}")
        draw.pop(card)
        for card in draw:
            self.deck.append(card)
            draw.remove(card)
        random.shuffle(self.deck)
        self.players[1].hand.append(self.deck.pop())
    
    def get_playable_actions(self, action=None):
        """
        Returns a list of playable actions based on the current action.
        """
        match action:
            case None:
                return ["coup", "income", "foreign_aid", "tax", "steal", "assassinate", "exchange"]
            case "block":
                self.block_attempted = True
                return ["allow", "challenge"]
            case "challenge":
                self.challenge_attempted = True
                return ["coup", "income", "foreign_aid", "tax", "steal", "assassinate", "exchange"]
            case default:
                if action in self.challengeable_actions and action in self.blockable_actions:
                    return ["allow", "challenge", "block"]
                elif action in self.challengeable_actions:
                    return ["allow", "challenge"]
                elif action in self.blockable_actions:
                    return ["allow", "block"]
                else:
                    return ["allow"]
    """
    Game actions
    """
    def lose_card(self, target):
        """Target choose a card to lose."""
        if len(target.hand) == 0:
            return
        if len(target.hand) == 1:
            target.hand.pop()
            return
        
        if not self.is_simulation:
            if target.name == "Computer":
                # Computer will try to save Duke or Contessa. Otherwise, choose a random card
                if "duke" in target.hand:
                    card = (target.hand.index("duke") + 1) % len(target.hand)
                elif "contessa" in target.hand:
                    card = (target.hand.index("contessa") + 1) % len(target.hand)
                else:
                    card = random.randint(0, len(target.hand) - 1)
                print(f"{target} lost {card}")
                target.hand.pop(card)
                return
            else: 
                print(f"{target} choose a card to lose by entering the index of the card.")
                while True:
                    try:
                        card = int(input())
                        print(f"{target} lost {target.hand[card]}")
                        target.hand.pop(card)
                        break
                    except IndexError:
                        print("Invalid input. Try again.")
                    except ValueError:
                            print("Invalid input. Try again.")
        else:
            card = random.randint(0, len(target.hand) - 1)
            print(f"{target} lost {target.hand[card]}")
            target.hand.pop(card)

    def coup(self, player, target):
        """
        Coup a player.
        
        Coup a player by paying 7 coins. The target must choose a card to lose.
        """
        if player.coins < 7:
            print("You don't have enough coins to coup.")
            return
        print(f"{player} coup {target}!")
        player.coins -= 7
        self.lose_card(target)
    
    def income(self, player):
        """
        Gain 1 coin.
        """
        player.coins += 1
        print(f"{player} gained 1 coin.")

    def foreign_aid(self, player):
        """
        Gain 2 coins.
        """
        player.coins += 2
        print(f"{player} gained 2 coins.")

    def tax(self, player):
        """
        Duke influence. Gain 3 coins.
        """
        player.coins += 3
        print(f"{player} gained 3 coins.")

    def assassinate(self, player, target):
        """
        Assassin influence. Assassinate a player.
        
        Assassinate a player by paying 3 coins. The target must choose a card to lose.
        
        Assassinate can be blocked by the Contessa.
        """
        if len(target.hand) == 0:
            print("Target has no cards.")
            return
        if player.coins < 3:
            print("You don't have enough coins to assassinate.")
            return
        print(f"{player} assassinate {target}!")
        player.coins -= 3
        if len(target.hand) == 1:
            print(f"{target} lost {target.hand[0]}")
            target.hand.pop(0)
            return
        self.lose_card(target)

    
    def exchange(self, player):
        """
        Ambassador influence. Exchange their own cards with cards the deck.
        """
        if len(player.hand) == 0:
            return
        
        random.shuffle(self.deck)
        top = self.deck[:len(player.hand)]
        if not self.is_simulation:
            if player.name == "Computer":
                if "duke" in top:
                    card = top.index("duke")
                elif "assassin" in top:
                    card = top.index("assassin")
                else:
                    card = random.randint(0, len(top) - 1)
                
                if "ambassador" in player.hand:
                    card_to_replace = player.hand.index("ambassador")
                elif "contessa" in player.hand:
                    card_to_replace = player.hand.index("contessa")
                else:
                    card_to_replace = random.randint(0, len(player.hand) - 1)

                player.hand.append(top.pop(card))
                top.append(player.hand.pop(card_to_replace))
                print(f"{player} exchanged cards!")
            
            else:
                while True:
                    print(f"{player} exchange {player.hand} with {top} by entering the index of the card to replace and the card to swap with, if any.")
                    try:
                        match input("Keep hand? (y/n): "):
                            case "y":
                                break
                            case default:
                                pass
                        card_to_replace = int(input("Card to replace: "))
                        card = int(input("Card to swap with: "))
                        player.hand.append(top.pop(card))
                        top.append(player.hand.pop(card_to_replace))
                        print(f"{player} exchanged {top[card]} with {player.hand[card_to_replace]}")
                    except ValueError:
                            print("Invalid input. Try again.") 
        else:
            card = random.randint(0, len(top) - 1)
            card_to_replace = random.randint(0, len(player.hand) - 1)
            player.hand.append(top.pop(card))
            top.append(player.hand.pop(card_to_replace))
            print(f"{player} exchanged cards!")

    def steal(self, player, target):
        """
        Captain influence. Steal up to 2 coins from a target.
        """
        if target.coins == 0:
            print(f"{target} has no coins to steal.")
            return
        print(f"{player} steal from {target}!")
        coins_stolen = 0
        for i in range(2):
            if target.coins == 0:
                break
            coins_stolen += 1
            target.coins -= 1
        player.coins += coins_stolen
        print(f"{player} gained {coins_stolen} coins.")

    def block(self, player, target, action):
        """
        Process the blocking of an action.

        If a challenge on the block is attempted, the Player must have the card that can block the action. Otherwise, they lose an influence.

        Blockable actions: 
            assassinate     by the contessa
            steal           by the ambassador or captain
            foreign_aid     by the duke
        """
        print("Processing block...")
        if self.challenge_attempted:
            match action:
                case "assassinate":
                    if "contessa" in target.hand:
                        print(f"{target} had the contessa and blocked the assassination! The challenge was unsuccessful!")
                        self.lose_card(player)
                        target.remove_card("contessa")
                        self.deck.append("contessa")
                        target.add_card(self.deck.pop())
                    else:
                        print(f"{target} didn't have the contessa and the challenge was successful!")
                        self.lose_card(target)
                case "steal":
                    if "ambassador" in target.hand or "captain" in target.hand:
                        print(f"{target} had the ambassador or captain and blocked the steal! The challenge was unsuccessful!")
                        self.lose_card(player)
                        if "ambassador" in target.hand:
                            target.remove_card("ambassador")
                            self.deck.append("ambassador")
                        elif "captain" in target.hand:
                            target.remove_card("captain")
                            self.deck.append("captain")
                        target.add_card(self.deck.pop())
                    else:
                        print(f"{target} didn't have the ambassador or captain and the challenge was successful!")
                        self.lose_card(target)
                case "foreign_aid":
                    if "duke" in target.hand:
                        print(f"{player} had the duke and blocked the foreign aid! The challenge was unsuccessful!")
                        self.lose_card(target)
                        player.remove_card("duke")
                        self.deck.append("duke")
                        player.add_card(self.deck.pop())
                    else:
                        print(f"{target} didn't have duke and the challenge was successful!")
                        self.lose_card(target)
                case default:
                    print(f"{player} did not have the card to block the action! The challenge was unsuccessful!")
                    self.lose_card(target)
        else:
            print(f"{target} blocked the action!")
    
    def challenge(self, player, target, action):
        """
        Process the challenging of an action.

        Challengeable actions: tax, assassinate, steal, exchange, block
        
        Return True if the challenge was successful, False otherwise.
        """
        print("Processing challenge...")
        match action:
            case "tax":
                if "duke" in player.hand:
                    print(f"{player} had the duke! The tax was successful!")
                    self.lose_card(target)
                    player.remove_card("duke")
                    player.add_card(self.deck.pop())
                    self.deck.append("duke")
                    return False
                else:
                    print(f"{player} did not have the duke! The challenge was successful!")
                    self.lose_card(player)
                    return True
            case "steal":
                if "captain" in player.hand:
                    print(f"{player} had the captain! The steal was successful!")
                    player.remove_card("captain")
                    player.add_card(self.deck.pop())
                    self.deck.append("captain")
                    self.lose_card(target)
                    return False
                else:
                    print(f"{player} did not have the captain! The challenge was successful!")
                    self.lose_card(player)
                    return True
            case "exchange":
                if "ambassador" in player.hand:
                    print(f"{player} had the ambassador! The exchange was successful!")
                    self.lose_card(target)
                    player.remove_card("ambassador")
                    player.add_card(self.deck.pop())
                    self.deck.append("ambassador")
                    return False
                else:
                    print(f"{player} did not have the ambassador! The challenge was successful!")
                    self.lose_card(player)
                    return True
            case "assassinate":
                if "assassin" in player.hand:
                    print(f"{player} had the assassin! The assassination was successful!")
                    player.remove_card("assassin")
                    player.add_card(self.deck.pop())
                    self.deck.append("assassin")
                    self.lose_card(target)
                    return False
                else:
                    print(f"{player} did not have the assassin! The challenge was successful!")
                    self.lose_card(player)
                    return True
            case default:
                pass
    
    def play_action(self, player=None, target=None, action="allow"):
        """
        Process the playing of an action.
        """
        match action:
            case "coup" | "income" | "foreign_aid" | "tax" | "exchange" | "assassinate" | "steal":
                self.current_action = action
                self.playable_actions = self.get_playable_actions(action)
            case "block":
                self.block_attempted = True
                self.playable_actions = self.get_playable_actions(action)
            case "challenge":
                self.challenge_attempted = True
                self.play_action(player, target)
            case default:
                if self.block_attempted: # If block is attempted, attempt block 
                    self.block(player, target, self.current_action)
                else: # Action is allowed
                    challenge_successful = False
                    if self.challenge_attempted:
                        challenge_successful = self.challenge(player, target, self.current_action)
                    if not challenge_successful: # If challenge is unsuccessful, or there is no challenge, play the action
                        match self.current_action:
                            case "coup" | "assassinate" | "steal":
                                getattr(self, self.current_action)(player, target)
                            case default:
                                getattr(self, self.current_action)(player)
        
                # Reset flags
                self.reset_flags()

        # Swap turn
        if self.current_action != "":
            self.swap_turn()

        # Increment round
        if self.current_action == "" and self.turn == self.players[0]:
            self.round += 1

        # Check if there is a winner
        winner, loser = self.check_win()
        if winner:
            self.winner = winner

            

    
    def reset_flags(self):
        """
        Reset all flags.
        """
        self.current_action = ""
        self.playable_actions = self.get_playable_actions()
        self.block_attempted = False
        self.challenge_attempted = False
    """
    Imperfect game state information
    """
    def get_game_state(self, name):
        """
        Returns a dictionary of the state from the perspective of the player.
        """
        player = self.players[self.players.index(name)]
        opponent = self.players[(self.players.index(name) + 1) % len(self.players)]
        return {
            # Player information
            "hand": player.hand,
            "coins": player.coins,
            "influence_count": len(player.hand),

            # Opponent information
            "opponent_coins": opponent.coins,
            "opponent_influence_count": len(opponent.hand),

            # Game information
            "round": self.round,
            "turn": self.turn,
            "game_won": self.game_won,
            "winner": None,
            "playable_actions": self.playable_actions,
            "block_attempted": self.block_attempted,
            "challenge_attempted": self.challenge_attempted,
            "current_action": self.current_action,
        }
    
    def get_next_state(self, player, action):
        """
        Returns the state after an action is played.
        """
        temp = deepcopy(self)
        temp.is_simulation = True
        opponent = temp.players[(temp.players.index(player) + 1) % len(temp.players)]
        temp.play_action(player=player, target=opponent, action=action)
        next_game_state = temp.get_game_state(player)
        return next_game_state
                
    def get_winner_and_terminated(self):
        """
        Returns the winner and whether the game is terminated.
        """
        return self.winner, self.game_won
    
    def check_win(self):
        """
        Checks if the game is won.
        """
        influence_count = [len(player.hand) for player in self.players]
        if 0 in influence_count:
            self.game_won = True
            winner = self.players[influence_count.index(max(influence_count))]
            loser = self.players[influence_count.index(min(influence_count))]
            return winner, loser
        return None, None

    def get_opponent(self, player):
        """
        Returns the opponent of the player.
        """
        return self.players[(self.players.index(player) + 1) % len(self.players)]
    
    def swap_turn(self):
        """
        Swaps the turn.
        """
        self.turn = self.players[(self.players.index(self.turn) + 1) % len(self.players)]
