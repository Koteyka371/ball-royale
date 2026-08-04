import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.game_modes import AllianceTournamentMode

class MockBall:
    def __init__(self, id, alive=True):
        self.id = id
        self.alive = alive
        self.hp = 100.0
        self.max_hp = 100.0

class MockWorld:
    def __init__(self):
        self.balls = []

def test_alliance_tournament_mode():
    mode = AllianceTournamentMode()
    world = MockWorld()

    # 4 balls: 2 for AllianceA, 2 for AllianceB
    b1 = MockBall(1)
    b2 = MockBall(2)
    b3 = MockBall(3)
    b4 = MockBall(4)
    world.balls = [b1, b2, b3, b4]

    mode.setup(world, world.balls)
    assert mode.current_round == 1
    assert "AllianceA" in mode.scores
    assert mode.alliances["AllianceA"] == [1, 2]
    assert mode.alliances["AllianceB"] == [3, 4]

    # Round 1: AllianceA wins
    b3.alive = False
    b4.alive = False
    mode._tick(1.0)

    assert mode.scores["AllianceA"] == 1
    assert mode.current_round == 2
    # Check reset
    assert b3.alive == True
    assert b4.alive == True

    # Round 2: AllianceA wins again
    b3.alive = False
    b4.alive = False
    mode._tick(1.0)

    assert mode.scores["AllianceA"] == 2
    assert mode.tournament_over == True
    assert mode.winner_alliance == "AllianceA"

    # Assert survival/elimination points
    assert mode.survival_points["AllianceA"] > 0
    assert mode.elimination_points["AllianceA"] == 2  # they get reset or only 2 happened in the tick that triggered end tournament

def test_alliance_draw_scenario():
    mode = AllianceTournamentMode()
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    world.balls = [b1, b2]
    mode.setup(world, world.balls)

    b1.alive = False
    b2.alive = False
    mode._tick(1.0)

    # Draw logic should be triggered, scores remain 0
    assert mode.scores["AllianceA"] == 0
    assert mode.scores["AllianceB"] == 0
    assert mode.current_round == 2
