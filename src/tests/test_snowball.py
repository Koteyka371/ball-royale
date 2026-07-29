import pytest
from ai.action import Action

class MockBall:
    def __init__(self):
        self.cosmetic = "snowball"
        self.vx = 150.0
        self.vy = 0.0
        self.x = 0.0
        self.y = 0.0
        self.radius = 15.0
        self.mass = 1.0
        self.damage = 10.0

class MockHazard:
    def __init__(self, kind="ice_patch"):
        self.kind = kind
        self.x = 0.0
        self.y = 0.0
        self.radius = 50.0
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = [MockHazard()]
        self.is_snowing = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_snowball_grows_on_ice():
    ball = MockBall()
    world = MockWorld()
    action = Action(ball, world)

    # Tick to let snowball grow
    action.execute("idle", 1.0)

    assert ball.snowball_size_multiplier > 1.0
    assert ball.radius > 15.0
    assert ball.mass > 1.0
    assert ball.damage > 10.0

def test_snowball_melts_off_ice():
    ball = MockBall()
    world = MockWorld()
    # Move ball off ice
    ball.x = 1000.0
    ball.snowball_size_multiplier = 2.0
    action = Action(ball, world)

    # Tick to let snowball melt
    action.execute("idle", 1.0)

    assert ball.snowball_size_multiplier < 2.0


def test_normal_ball_turns_into_snowball():
    ball = MockBall()
    ball.cosmetic = "default"
    world = MockWorld()
    action = Action(ball, world)

    # Should turn into snowball on ice and moving
    action.execute("idle", 1.0)

    assert ball.cosmetic == "snowball"
    assert ball.snowball_size_multiplier > 1.0

def test_ball_reverts_cosmetic_when_melted():
    ball = MockBall()
    ball.cosmetic = "default"
    world = MockWorld()
    action = Action(ball, world)

    # Grow
    action.execute("idle", 1.0)
    assert ball.cosmetic == "snowball"

    # Move off ice to melt
    ball.x = 1000.0
    action.execute("idle", 20.0) # wait long enough to melt back to 1.0

    assert ball.cosmetic == "default"
    assert ball.snowball_size_multiplier <= 1.0
