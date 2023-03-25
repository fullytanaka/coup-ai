import pytest
import random
import game

@pytest.fixture
def coup():
    coup = game.Game()
    coup.add_player("Player 1")
    coup.add_player("Player 2")
    return coup 

def test_can_add_and_remove_player(coup):
    coup.remove_player("Player 2")
    assert len(coup.players) == 1
    coup.add_player("Player 2")
    assert coup.players[1].name == "Player 2"
    assert coup.players[1].hand == []

def test_initial_draw(coup, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: 0)
    coup.initial_draw()
    assert len(coup.players[0].hand) == 2
    assert len(coup.players[1].hand) == 2

def test_lose_card(coup, capfd, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: 0)
    coup.players[1].hand = ["duke", "captain"]
    coup.lose_card(coup.players[1])
    out, err = capfd.readouterr()
    assert out == "Player 2 choose a card to lose by entering the index of the card.\nPlayer 2 lost duke\n"
    assert err == ""

def test_coup(coup, capfd, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: 0)
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

def test_income(coup, capfd, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: 0)
    coup.players[0].coins = 0
    coup.income(coup.players[0])
    out, err = capfd.readouterr()
    assert out == "Player 1 gained 1 coin.\n"
    assert err == ""

def test_foreign_aid(coup, capfd, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: 0)
    coup.players[0].coins = 0
    coup.foreign_aid(coup.players[0])
    out, err = capfd.readouterr()
    assert out == "Player 1 gained 2 coins.\n"
    assert err == ""