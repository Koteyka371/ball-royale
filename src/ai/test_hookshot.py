import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000
        self.balls = []
        self.items = []
        self.events = []
        self.boosters = []

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.team = 1
        self.id = 1
        self.hp = 100
        self.inventory = ["hookshot"]

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 100

def test_hookshot_saves_from_lava():
    world = MockWorld()
    ball = MockBall(500, 500)
    world.balls.append(ball)
    lava = MockHazard(500, 500, "lava")
    world.arena.hazards.append(lava)

    action = Action(ball, world)
    action.execute("flee", 0.1)

    assert "hookshot" not in ball.inventory
    # Ball should have moved away from lava (to a wall)
    assert ball.x != 500 or ball.y != 500
