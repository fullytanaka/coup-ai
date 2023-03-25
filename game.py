import random

class Game():
    """Alpha game of Coup."""

    class Player():
        """A player in the game."""
        def __init__(self, name):
            """Initialize the player."""
            self.name = name
            self.hand = []
            self.coins = 2

        def __str__(self):
            """Return a string representation of the player."""
            return self.name

        def __repr__(self):
            """Return a string representation of the player."""
            return self.name

        def __eq__(self, other):
            """Return True if the players are equal."""
            return self.name == other.name
        
    def __init__(self):
        """Initialize the game."""
        self.players = []
        self.deck = ["Duke", "Assassin", "Ambassador", "Captain", "Contessa"] * 3
        self.discard = []
        self.turn = 0

    def add_player(self, name):
        """Add a player to the game."""
        self.players.append(self.Player(name))

    def remove_player(self, name):
        """Remove a player from the game."""
        self.players.remove(self.Player(name))

    def initial_draw(self):
        """Initial draw. Shuffle the deck and each the player choose two cards from the top three cards."""
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
        """Coup a player."""
        if player.coins < 7:
            print("You don't have enough coins to coup.")
            return
        print(f"{player} coup {target}!")
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
        """Duke influence. Gain 3 coins."""
        player.coins += 3
        print(f"{player} gained 3 coins.")
    
    def exchange(self, player):
        """Ambassador influence. Exchange two cards with the deck."""
        random.shuffle(self.deck)
        top = self.deck[:2]
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
        """Steal coins from a player."""
        if player.coins < 7:
            print("You don't have enough coins to steal.")
            return
        print(f"{player} steal from {target}!")
        if target.coins > 0:
            player.coins += 1
            target.coins -= 1
            print(f"{player} gained 1 coin from {target}.")
        else:
            print(f"{target} has no coins to steal.")
    
    def game_loop(self):
        """The game loop."""
        while len(self.players) > 1:
            self.turn += 1
            self.exchange(self.players[self.turn % len(self.players)])
    
    def start(self):
        """Start the game."""
        self.initial_draw()
        self.turn = 0
        self.game_loop()


main = Game()
main.add_player("Player 1")
main.add_player("Player 2")
main.start()