import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []

class MockArena:
    def __init__(self):
        self.items = []

class MockBall:
    def __init__(self, x=0, y=0, traits=None):
        self.x = x
        self.y = y
        self.traits = traits or []

def test_storm_chaser_trait():
    world = MockWorld()
    ball = MockBall(x=0, y=0, traits=["storm_chaser"])
    action = Action(ball, world)

    world.boosters.append({"x": 100, "y": 0})
    world.arena.items.append({"x": 0, "y": 100, "kind": "material"})

    # Run execute multiple times to simulate pulling
    for _ in range(10):
        action.execute("default", 0.1)

    # Check if they are pulled closer
    assert world.boosters[0]["x"] < 100
    assert world.arena.items[0]["y"] < 100
