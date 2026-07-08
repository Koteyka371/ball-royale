import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.game_modes import ClanTournamentMode

class MockBall:
    def __init__(self, id, alive=True):
        self.id = id
        self.alive = alive
        self.hp = 100.0
        self.max_hp = 100.0

class MockWorld:
    def __init__(self):
        self.balls = []

def test_clan_tournament_mode():
    mode = ClanTournamentMode()
    world = MockWorld()

    # 4 balls: 2 for ClanA, 2 for ClanB
    b1 = MockBall(1)
    b2 = MockBall(2)
    b3 = MockBall(3)
    b4 = MockBall(4)
    world.balls = [b1, b2, b3, b4]

    mode.setup(world, world.balls)
    assert mode.current_round == 1
    assert "ClanA" in mode.scores
    assert mode.clans["ClanA"] == [1, 2]
    assert mode.clans["ClanB"] == [3, 4]

    # Round 1: ClanA wins
    b3.alive = False
    b4.alive = False
    mode._tick(1.0)

    assert mode.scores["ClanA"] == 1
    assert mode.current_round == 2
    # Check reset
    assert b3.alive == True
    assert b4.alive == True

    # Round 2: ClanA wins again
    b3.alive = False
    b4.alive = False
    mode._tick(1.0)

    assert mode.scores["ClanA"] == 2
    assert mode.tournament_over == True
    assert mode.winner_clan == "ClanA"
