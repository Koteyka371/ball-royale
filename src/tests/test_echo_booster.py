import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

class MockBall:
    def __init__(self, id="p1", x=0, y=0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.alive = True

class MockBooster:
    def __init__(self, x=0, y=0, kind="echo_booster"):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []

class MockWorld:
    def __init__(self, boosters=None, arena=None):
        self.boosters = boosters or []
        self.arena = arena or MockArena()

def test_echo_booster_collection():
    ball = MockBall()
    booster = MockBooster(x=5, y=5)
    world = MockWorld(boosters=[booster], arena=MockArena(hazards=[booster]))
    action = Action(ball, world)
    action._get_boosters = lambda: [booster]

    action._collect_booster(0.1)

    assert getattr(ball, "echo_booster_timer", 0.0) > 0.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

if __name__ == "__main__":
    pytest.main([__file__])
