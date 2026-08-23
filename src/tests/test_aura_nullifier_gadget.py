import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, radius=20, team=1):
        self.x = x
        self.y = y
        self.radius = radius
        self.team = team
        self.hp = 100
        self.aura_booster_timer = 10.0
        self.vampiric_aura_timer = 5.0

class MockHazard:
    def __init__(self, x=0, y=0, radius=50, kind=""):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.duration = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()

def test_aura_nullifier_gadget():
    world = MockWorld()
    b1 = MockBall(x=0, y=0)
    world.balls.append(b1)

    hazard = MockHazard(x=10, y=10, radius=100, kind="aura_nullifier_gadget")
    world.arena.hazards.append(hazard)

    action = Action(b1, world)
    action.execute("opportunistic", 0.1)

    # Assert timers are removed or nullified
    assert getattr(b1, "aura_booster_timer", 0.0) <= 0.0
    assert getattr(b1, "vampiric_aura_timer", 0.0) <= 0.0
    assert getattr(b1, "in_aura_nullifier_zone", False) == True

if __name__ == "__main__":
    test_aura_nullifier_gadget()
    print("Test passed.")
