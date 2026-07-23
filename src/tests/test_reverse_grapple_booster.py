import pytest
from ai.action import Action

class MockTarget:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.team = 2

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.team = 1
        self.reverse_grapple_booster_timer = 5.0
        self.reverse_grapple_target = MockTarget(200.0, 200.0)
        self._base_speed_set = True
        self.base_speed = 100.0
        self.base_damage = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

def test_reverse_grapple_booster():
    ball = MockBall(100.0, 100.0)
    world = MockWorld()
    action = Action(ball, world)

    # Run the execute loop which should pull the target
    action.execute("idle", 0.1)

    # Target starts at 200, 200 and ball at 100, 100
    # Expected: target moves closer to ball
    assert ball.reverse_grapple_target.x < 200.0
    assert ball.reverse_grapple_target.y < 200.0
