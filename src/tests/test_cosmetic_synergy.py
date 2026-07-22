import pytest
from ai.game_modes import GameMode

class MockWorld:
    pass

class MockBall:
    def __init__(self, name, team, cosmetic, speed=100, damage=10):
        self.name = name
        self.team = team
        self.cosmetic = cosmetic
        self.alive = True
        self.speed = speed
        self.damage = damage
        self.base_speed = speed
        self.base_damage = damage

def test_cosmetic_synergy():
    mode = GameMode()
    world = MockWorld()

    # Team 1: matching cosmetics
    b1 = MockBall("A", "Team1", "sunglasses")
    b2 = MockBall("B", "Team1", "sunglasses")
    b3 = MockBall("C", "Team1", "hat")

    # Team 2: no matching
    b4 = MockBall("D", "Team2", "sunglasses")
    b5 = MockBall("E", "Team2", "scarf")

    balls = [b1, b2, b3, b4, b5]

    mode.tick(world, balls, 0.016)

    # Team 1's sunglasses wearers should get a buff
    assert abs(b1.speed - 105.0) < 0.001
    assert abs(b2.speed - 105.0) < 0.001
    assert abs(b1.damage - 10.5) < 0.001
    assert abs(b2.damage - 10.5) < 0.001

    # Team 1's hat wearer gets no buff (only 1 member)
    assert b3.speed == 100
    assert b3.damage == 10

    # Team 2 members get no buff
    assert b4.speed == 100
    assert b5.speed == 100
