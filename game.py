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
    
    def coup(self, player, target):
        """Coup a player."""
        print(f"{player} coup {target}!")
        print(f"{target} choose a card to lose by entering the index of the card.")
        while True:
            try:
                card = int(input())
                print(f"{player} lost {player.hand[card]}")
                player.hand.pop(card)
                break
            except:
                print("Invalid input. Try again.")

    def start(self):
        """Start the game."""
        self.initial_draw()
        self.turn = 0
        self.game_loop()
    
    def game_loop(self):
        """The game loop."""
        while len(self.players) > 1:
            self.turn += 1
            self.coup(self.players[0], self.players[1])


main = Game()
main.add_player("Player 1")
main.add_player("Player 2")
main.start()