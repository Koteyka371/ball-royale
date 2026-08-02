import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.max_hp = 200.0
        self.hp = 200.0
        self.team = "A"

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 30.0
        self.active = True
        self.used = False
        self.id = 99

class MockArena:
    def __init__(self):
        self.hazards = []
        self.items = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.time = 0.0
        self.boosters = []
        self.projectiles = []

def test_cursed_shrine_interaction():
    world = MockWorld()
    ball = MockBall(1, 50, 50)
    world.balls.append(ball)

    shrine = MockHazard(50, 50, "cursed_shrine")
    world.arena.hazards.append(shrine)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert shrine.used == True
    assert shrine.active == False
    assert ball.base_damage == pytest.approx(12.0)
    assert ball.damage == pytest.approx(12.0)
    assert ball.base_speed == pytest.approx(120.0)
    assert ball.speed == pytest.approx(120.0)
    assert ball.max_hp == pytest.approx(100.0)
    assert ball.hp == pytest.approx(100.0)

    # Test second interaction doesn't double buff
    action.execute("idle", 0.1)
    assert ball.base_damage == pytest.approx(12.0)
    assert ball.max_hp == pytest.approx(100.0)
