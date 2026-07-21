import pytest
from ai.action import Action

class MockHazard:
    def __init__(self):
        self.kind = "low_gravity"
        self.x = 100
        self.y = 100
        self.radius = 50

class MockArena:
    def __init__(self):
        self.hazards = [MockHazard()]
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

class MockBall:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.is_frictionless = False
        self.speed = 100.0
        self.base_speed = 100.0

def test_low_gravity_effect():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    action = Action(ball, world)

    action.execute("none", 0.016)

    assert ball.is_frictionless is True
    assert getattr(ball, "bounciness_multiplier", 1.0) == 2.0
    assert getattr(ball, "speed") != 100.0  # Speed was randomly modified
