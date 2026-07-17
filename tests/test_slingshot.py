import pytest
from ai.slingshot import SlingshotMode

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = 5.0
        self.base_damage = 10.0
        self.damage = 10.0

class MockWorld:
    def __init__(self):
        pass

def test_slingshot_mode():
    mode = SlingshotMode()
    ball = MockBall()
    world = MockWorld()

    # Initial tick sets timer and speed to 0
    mode.tick(world, [ball], 0.1)
    assert ball.speed == 0.0
    assert hasattr(ball, "slingshot_timer")

    # Fast forward timer to pull
    ball.slingshot_timer = 0.0
    ball.slingshot_pulling = False
    mode.tick(world, [ball], 0.1)
    assert ball.slingshot_pulling == True

    # Fast forward to release
    ball.slingshot_timer = 0.0
    ball.vx = 0.0
    ball.vy = 0.0
    mode.tick(world, [ball], 0.1)
    assert ball.slingshot_pulling == False
    assert abs(ball.vx) > 0.0 or abs(ball.vy) > 0.0

    # Check damage scaling
    ball.vx = 1000.0
    ball.vy = 0.0
    mode.tick(world, [ball], 0.1)
    assert ball.damage > 10.0
