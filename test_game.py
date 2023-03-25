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