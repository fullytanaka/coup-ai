import random

class Game():
    """Game of Coup."""

    class Player():
        """A player in the game."""
        def __init__(self, name):
            """Initialize the player."""
            self.name = name
            self.hand = []
            self.coins = 2

        def print_information(self):
            """print information about the player."""
            return f"{self.name} has {self.coins} coins and {self.hand} in their hand."
        
        def __str__(self):
            """Return the name of the player."""
            return self.name
        
        def __repr__(self):
            """Return the name of the player."""
            return self.name
        
        def __eq__(self, other):
            """Return whether the player is equal to another player."""
            return self.name == other.name
        
    def __init__(self):
        """Initialize the game."""
        self.players = []
        self.deck = ["Duke", "Assassin", "Ambassador", "Captain", "Contessa"] * 3
        self.discard = []
        self.turn = 0
        self.game_won = False
        self.actions = ["coup", "income", "foreign_aid", "tax", "assassinate", "exchange", "steal", "block", "challenge"]
        self.blockable_actions = ["assassinate", "steal", "coup", "foreign_aid"]
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
            print(f"{player.name} choose two cards from {draw} by entering the index of the card.")
            while len(draw) > 1:
                try:
                    card = int(input())
                    player.hand.append(draw[card])
                    print(f"{player.name} chose {draw[card]}")
                    draw.pop(card)
                except:
                    print("Invalid input. Try again.")
            self.deck.append(draw[0])
    
    """
    Game actions
    """
    def coup(self, player, target):
        """
        Coup a player.
        
        Coup a player by paying 7 coins. The target must choose a card to lose."""
        if player.coins < 7:
            print("You don't have enough coins to coup.")
            return
        print(f"{player} coup {target}!")
        player.coins -= 7
        if len(target.hand) == 1:
            print(f"{target} lost {target.hand[0]}")
            target.hand.pop(0)
            return
        print(f"{target} choose a card to lose by entering the index of the card.")
        while True:
            try:
                card = int(input())
                print(f"{target} lost {target.hand[card]}")
                target.hand.pop(card)
                break
            except:
                print("Invalid input. Try again.")
    
    def income(self, player):
        """Gain 1 coin."""
        player.coins += 1
        print(f"{player} gained 1 coin.")

    def foreign_aid(self, player):
        """Gain 2 coins."""
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
        if player.coins < 3:
            print("You don't have enough coins to assassinate.")
            return
        print(f"{player} assassinate {target}!")
        player.coins -= 3
        if len(target.hand) == 1:
            print(f"{target} lost {target.hand[0]}")
            target.hand.pop(0)
            return
        print(f"{target} choose a card to lose by entering the index of the card.")
        while True:
            try:
                card = int(input())
                print(f"{target} lost {target.hand[card]}")
                target.hand.pop(card)
                break
            except:
                print("Invalid input. Try again.")

    
    def exchange(self, player):
        """
        Ambassador influence. Exchange their own cards with cards the deck.
        """
        random.shuffle(self.deck)
        top = self.deck[:len(player.hand)]
        while True:
            print(f"{player} exchange {player.hand} with {top} by entering the index of the card to replace and the card to swap with, if any. Enter nothing to keep your hand.")
            try:
                card_to_replace = int(input("Card to replace: "))
                card = int(input("Card to swap with: "))
                if card == "":
                    break
                player.hand.append(top.pop(card))
                top.append(player.hand.pop(card_to_replace))
                print(f"{player} exchanged {top[card]} with {player.hand[card_to_replace]}")
            except:
                print("Invalid input. Try again.")

    def steal(self, player, target):
        """Captain influence. Steal up to 2 coins from a target."""
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
               
    def game_loop(self):
        """
        The game loop.
        
        The game loop will continue until a player has no more influences.
        
        Each player will take a turn, choosing an action to take, and the opposing player chooses to allow the action, challenge or block.
        """
        for i in range(len(self.players)):
            influence_count = [len(player.hand) for player in self.players]
            if min(influence_count) == 0: # Check if a player has no more influences
                print(f"{self.players[influence_count.index(min(influence_count))]} has no more influences!")
                print("Game over!")
                print(f"{self.players[influence_count.index(max(influence_count))]} wins!")
                self.game_won = True
                break
            print(f"{self.players[i].name}'s turn.")
            print(self.players[i].print_information())
            while True:
                try:
                    action = input(f"Choose an action from {', '.join(self.actions)}: ").lower().replace(" ", "_")
                    if action not in self.actions:
                        raise ValueError

                    # Target chooses to allow, challenge or block
                    if action in self.challengeable_actions and self.blockable_actions:
                        print(f"{self.players[(i + 1) % len(self.players)]}, choose to challenge, block or allow:")
                    elif action in self.challengeable_actions:
                        print(f"{self.players[(i + 1) % len(self.players)]}, choose to challenge or allow:")
                    elif action in self.blockable_actions:
                        print(f"{self.players[(i + 1) % len(self.players)]}, choose to block or allow:")

                    match input().lower().replace(" ", "_"):
                        case "challenge":
                            self.challenge_attempted = True
                        case "block":
                            self.block_attempted = True
                        case default:
                            pass

                    # Player can challenge a block attempt
                    if self.block_attempted:
                        match input(f"{self.players[i]}, choose to challenge or allow:"):
                            case "challenge":
                                self.challenge_attempted = True
                            case default:
                                pass

                    print(f"{self.players[i].name} chose {action}.")
                    if action in ["coup", "assassinate", "steal"]: # Actions that require a target
                        getattr(self, action)(self.players[i], self.players[(i + 1) % len(self.players)])
                    else:
                        getattr(self, action)(self.players[i])
                    break
                    self.challenge_attempted = False
                    self.block_attempted = False
                except ValueError:
                    print("Invalid input. Try again.")
                except Exception as e:
                    print(f"An error occurred: {e}")
                    raise e
            
    
    def start(self):
        """Start the game."""
        self.initial_draw()
        while self.game_won == False:
            self.game_loop()


main = Game()
main.add_player("Player 1")
main.add_player("Player 2")
main.start()