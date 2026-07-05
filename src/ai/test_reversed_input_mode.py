import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.id = "p1"

class MockWorld:
    pass

def test_reversed_input_mode():
    mode = GAME_MODES["reversed_input"]
    assert mode.name == "Reversed Input"

    world = MockWorld()

    # Simulate a ball that has just moved based on its velocity
    # e.g. started at (10, 10) with vx=100, vy=0
    # delta = 0.1s -> dx = 10 -> current pos = (20, 10)
    ball = MockBall(20.0, 10.0, 100.0, 0.0)
    balls = [ball]

    # Tick mode until interval reached (10.0 seconds)
    # Not reversed yet
    mode.tick(world, balls, delta=5.0)
    assert not mode.is_reversed

    # Still not reversed
    mode.tick(world, balls, delta=4.9)
    assert not mode.is_reversed

    # Tick to cross interval, should also apply the reverse action immediately since is_reversed becomes True
    mode.tick(world, balls, delta=0.1) # reaches 10.0 exactly
    assert mode.is_reversed

    # The tick above triggers is_reversed, so it applies the reverse action for delta=0.1.
    # ball.x was 20.0, vx is 100.0, delta is 0.1
    # bx -= 100.0 * 0.1 * 2 = 20.0
    # so ball.x becomes 0.0
    assert ball.x == 0.0
    assert ball.y == 10.0

    # Tick until duration (5.0 seconds) ends
    mode.tick(world, balls, delta=4.8)
    assert mode.is_reversed

    # Tick to cross duration
    mode.tick(world, balls, delta=0.2)
    assert not mode.is_reversed
