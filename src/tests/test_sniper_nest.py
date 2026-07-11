import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.perception_radius = 100.0
        self.base_perception_radius = 100.0
        self.in_sniper_nest = False
        self.damage_multiplier = 1.0
        self.show_sniper_nest_indicator = False

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0
        self.radius = 50.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_sniper_nest_active():
    b = MockBall()
    w = MockWorld()
    h = MockHazard('sniper_nest')
    w.arena.hazards.append(h)

    a = Action(b, w)
    a.execute("none", 0.1)

    assert b.in_sniper_nest == True
    assert math.isclose(b.perception_radius, 125.0)
    assert math.isclose(b.damage_multiplier, 1.15)
    assert b.show_sniper_nest_indicator == True

def test_sniper_nest_inactive():
    b = MockBall()
    w = MockWorld()
    h = MockHazard('sniper_nest')
    h.x = 200 # Out of range
    w.arena.hazards.append(h)

    a = Action(b, w)
    a.execute("none", 0.1)

    assert b.in_sniper_nest == False
    assert math.isclose(b.perception_radius, 100.0)
    assert math.isclose(b.damage_multiplier, 1.0)
    assert b.show_sniper_nest_indicator == False
