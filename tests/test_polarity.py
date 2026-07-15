import pytest
import math

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.radius = 10.0
        self.polarity = 0
        self.polarity_cooldown = 0.0

class MockHazard:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "polarity_inverter"
        self.radius = 50.0
        self.duration = 10.0
        self.emp_disabled_timer = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

def test_polarity_inverter_hazard():
    from ai.action import Action
    world = MockWorld()

    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 105, 105)

    h = MockHazard(100, 100)
    world.arena.hazards.append(h)
    world.balls.extend([b1, b2])

    action1 = Action(b1, world)

    action1.execute("idle", 0.0)
    assert b1.polarity == 1

    b1.x, b1.y = 100, 100
    b2.x, b2.y = 110, 100

    b1.polarity = 1
    b2.polarity = 1

    action1.execute("idle", 0.016)

    assert b1.x < 100

    b1.x, b1.y = 100, 100
    b2.polarity = -1

    action1.execute("idle", 0.016)

    assert b1.x > 100
