import pytest
import random
import game

@pytest.fixture
def coup():
    coup = game.Game()
    return coup 

def test_can_add_and_remove_player(coup):
    coup.add_player("Player 1")
    assert coup.players[0].name == "Player 1"
    assert coup.players[0].hand == []
    coup.remove_player("Player 1")
    assert coup.players == []

def test_initial_draw_gives_two_cards(coup, monkeypatch):
    coup.add_player("Player 1")
    coup.add_player("Player 2")
    monkeypatch.setattr("builtins.input", lambda: 0)
    coup.initial_draw()
    assert len(coup.players[0].hand) == 2
    assert len(coup.players[1].hand) == 2

def test_coup(coup, capfd, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: 0)
    coup.add_player("Player 1")
    coup.add_player("Player 2")
    coup.players[0].hand = ["duke", "captain"]
    coup.players[1].hand = ["duke"]

    # Not enough coins to coup
    coup.coup(coup.players[0], coup.players[1])
    out, err = capfd.readouterr()
    assert out == "You don't have enough coins to coup.\n"
    assert err == ""

    # Coup is successful with one card
    coup.players[0].coins = 7
    coup.coup(coup.players[0], coup.players[1])
    out, err = capfd.readouterr()
    assert out == "Player 1 coup Player 2!\nPlayer 2 lost duke\n"
    assert err == ""

    # Coup is successful with two cards
    coup.players[0].coins = 7
    coup.players[1].hand = ["duke", "captain"]
    coup.coup(coup.players[0], coup.players[1])
    out, err = capfd.readouterr()
    assert out == "Player 1 coup Player 2!\nPlayer 2 choose a card to lose by entering the index of the card.\nPlayer 2 lost duke\n"
    assert err == ""